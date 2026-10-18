"""Pipeline de dados do app Cardápios.

Comandos (rode na raiz do repositório):
  fetch-sheet                      baixa a planilha (camada manual) para work/sheet.csv
  fetch-overture --region sp-estado
                                   lê o Overture Places do S3 público (última release) para work/overture/
  merge [--region sp-estado]       planilha + Overture -> work/merged.csv (dedupe, ids congelados, blacklist)
  check-links [--limit N] [--budget-minutes M] [--origin planilha|overture|reparo]
                                   checagem incremental com cache em data/links-cache.csv
  repair-links                     troca links quebrados (ordem do relatório 3.2) -> data/repairs.csv
  publish [--force]                CSVs por região + index.json em public/, trava de regressão, relatório
  all                              tudo acima, em ordem
"""

import argparse
import sys

from .common import DATA, WORK, load_config, log, read_csv, write_json
from .links import LinkCache, PRIORITY, link_kind, run_checks

HOST_OVERRIDES = {"ifood.com.br": 3.0}


def _areas(config, region):
    return [region] if region else list(config["areas"])


def cmd_fetch_sheet(args, config):
    from .sheet import fetch_sheet
    fetch_sheet(config["sheet_csv_url"])


def cmd_fetch_overture(args, config):
    from .common import area_config
    from .overture import fetch_overture
    for area_id in _areas(config, args.region):
        fetch_overture(config, area_id, area_config(config, area_id), release=args.release, limit=args.limit)


def cmd_merge(args, config):
    from .merge import merge
    stats, _ = merge(config, _areas(config, args.region))
    write_json(WORK / "merge-stats.json", stats)


def register_merged(cache, config):
    merged = read_csv(WORK / "merged.csv")
    need_site = config["publish"].get("new_places_need_website", True)
    added = 0
    for row in merged:
        link = row.get("menu_link", "")
        if not link:
            continue
        if row["_origin"] != "planilha" and need_site and link_kind(link) in ("rede social", "encurtador"):
            continue
        if row.get("_lock_link"):
            continue
        before = len(cache.entries)
        cache.register(link, row["_origin"])
        added += len(cache.entries) - before
    return len(merged), added


def cmd_check_links(args, config):
    cache = LinkCache(DATA / "links-cache.csv")
    if not args.cache_only and (WORK / "merged.csv").exists():
        rows, added = register_merged(cache, config)
        log(f"check-links: {rows} linhas do merge, {added} URLs novas no cache")
    due = cache.due(only_priority=PRIORITY[args.origin] if args.origin else None)
    if args.limit:
        due = due[:args.limit]
    log(f"check-links: {len(due)} URLs a verificar agora (cache com {len(cache.entries)} URLs)")
    counts = run_checks(cache, due, workers=args.workers, timeout=args.timeout,
                        budget_seconds=args.budget_minutes * 60 if args.budget_minutes else None,
                        host_interval=args.host_interval, host_overrides=HOST_OVERRIDES,
                        respect_robots=not args.ignore_robots)
    statuses = {}
    for entry in cache.entries.values():
        statuses[entry["status"] or "pendente"] = statuses.get(entry["status"] or "pendente", 0) + 1
    log(f"check-links: resultados desta execução {counts}; cache por status {statuses}")


def cmd_repair_links(args, config):
    from .repair import repair
    merged = read_csv(WORK / "merged.csv")
    if not merged:
        raise SystemExit("Rode merge antes.")
    repair(merged, DATA / "links-cache.csv", budget_seconds=args.budget_minutes * 60 if args.budget_minutes else None,
           limit=args.limit, workers=args.workers, respect_robots=not args.ignore_robots)


def cmd_publish(args, config):
    from .publish import publish
    publish(config, force=args.force)


def cmd_all(args, config):
    link_limit, args.limit = args.limit, None  # --limit is for links here, not for the Overture fetch
    cmd_fetch_sheet(args, config)
    cmd_fetch_overture(args, config)
    cmd_merge(args, config)
    args.limit = link_limit
    cmd_check_links(args, config)
    cmd_repair_links(args, config)
    cmd_publish(args, config)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m cardapios_dados", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", help="caminho do config (padrão: config/regions.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    def link_options(p, budget):
        p.add_argument("--limit", type=int, default=0, help="máximo de URLs verificadas nesta execução")
        p.add_argument("--budget-minutes", type=float, default=budget, help="para de verificar depois de M minutos")
        p.add_argument("--workers", type=int, default=24)
        p.add_argument("--timeout", type=float, default=12.0)
        p.add_argument("--host-interval", type=float, default=2.0, help="segundos entre requisições ao mesmo host")
        p.add_argument("--ignore-robots", action="store_true")

    sub.add_parser("fetch-sheet").set_defaults(func=cmd_fetch_sheet)
    p = sub.add_parser("fetch-overture")
    p.add_argument("--region", help="área do config (ex.: sp-estado); padrão: todas")
    p.add_argument("--release", help="release do Overture (padrão: a mais recente)")
    p.add_argument("--limit", type=int, help="máximo de lugares (para testes)")
    p.set_defaults(func=cmd_fetch_overture)
    p = sub.add_parser("merge")
    p.add_argument("--region")
    p.set_defaults(func=cmd_merge)
    p = sub.add_parser("check-links")
    link_options(p, 0)
    p.add_argument("--origin", choices=sorted(PRIORITY), help="só URLs desta origem")
    p.add_argument("--cache-only", action="store_true", help="não lê work/merged.csv (job diário)")
    p.set_defaults(func=cmd_check_links)
    p = sub.add_parser("repair-links")
    link_options(p, 0)
    p.set_defaults(func=cmd_repair_links)
    p = sub.add_parser("publish")
    p.add_argument("--force", action="store_true", help="publica mesmo se a trava de regressão disparar")
    p.set_defaults(func=cmd_publish)
    p = sub.add_parser("all")
    p.add_argument("--region")
    p.add_argument("--release")
    p.add_argument("--force", action="store_true")
    p.add_argument("--origin", default=None)
    p.add_argument("--cache-only", action="store_true")
    link_options(p, 90)
    p.set_defaults(func=cmd_all)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    args.func(args, config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
