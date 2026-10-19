"""publish: one CSV per region in the app's format, index.json, regression guard and diff report.

- Sheet rows are published unless their link is confirmed broken with no replacement.
- New places (Overture) are published only with a validated menu link or a valid own website
  (report phase 1): never with only a social network, shortener or an unchecked link.
- Regression guard: if a region that had >= min_rows_for_guard rows loses more than max_row_loss
  (20%) of them, nothing is written to public/ and the command exits with code 2.
- New places get their name|address frozen in data/ids.csv the first time they are published.
"""

import hashlib
import math
import io
import os
import shutil
import statistics
import urllib.request
from collections import Counter, defaultdict

from .common import (DATA, PUBLIC, REPORTS, ROOT, WORK, fold, in_bbox, log, parse_csv_text, read_csv, read_json,
                     restaurant_key, to_float, utc_now, write_csv, write_json)
from .links import LinkCache, is_publishable, link_kind
from .merge import IDS_COLUMNS, INTERNAL_COLUMNS, load_ids
from .repair import load_repairs

GUARD_EXIT_CODE = 2


class RegressionError(SystemExit):
    pass


def resolve_link(row, cache, repairs):
    """(menu_link, cache entry, repair method or "")."""
    link = row.get("menu_link", "")
    entry = cache.get(link) if link else None
    repair = repairs.get((row["_key"], link))
    if repair and not row.get("_lock_link"):
        replacement = repair["replacement"]
        r_entry = cache.get(replacement)
        broken = entry is not None and entry["status"] == "quebrado"
        if repair["method"] == "rede social" and broken:
            return replacement, r_entry, repair["method"]
        if r_entry and r_entry["status"] == "ok" and (broken or repair["reason"] == "melhorar" or not link):
            return replacement, r_entry, repair["method"]
    return link, entry, ""


def publishable(row, link, entry, repaired, require_website):
    if row["_origin"] == "planilha":
        if row.get("_lock_link") or not link:
            return True
        if repaired == "rede social":
            return True
        return is_publishable(entry, require_validated=False)
    if not link:
        return False
    if require_website and link_kind(link) not in ("site", "pdf", "plataforma"):
        return False
    return is_publishable(entry, require_validated=True)


def file_for(row, area_files):
    municipality = fold(row.get("_municipality", ""))
    default = None
    for spec in area_files:
        if spec.get("only_sheet"):
            continue
        if spec.get("default"):
            default = spec
        elif municipality and municipality in {fold(m) for m in spec.get("municipalities", [])}:
            return spec
    return default


def build_rows(merged, cache, repairs, config):
    """{file id: [rows]} plus counters for the report."""
    require_website = config["publish"].get("new_places_need_website", True)
    files = defaultdict(list)
    counters = Counter()
    removed_sheet, repaired_rows = [], []
    for row in merged:
        link, entry, repaired = resolve_link(row, cache, repairs)
        ok = publishable(row, link, entry, repaired, require_website)
        origin = row["_origin"]
        status = (entry["status"] if entry else "") or ("pendente" if link else "sem link")
        counters[f"{origin}:{status}"] += 1
        if not ok:
            counters[f"{origin}:omitidas"] += 1
            if origin == "planilha":
                removed_sheet.append((row, link))
            continue
        out = dict(row)
        if repaired:
            out["menu_link"] = link
            repaired_rows.append((row, link, repaired))
            counters[f"{origin}:reparadas"] += 1
        out["link_status"] = "rede social" if repaired == "rede social" else status
        out["link_verificado_em"] = (entry["checked_at"][:10] if entry and entry.get("checked_at") else "")
        if origin != "planilha":
            menu_like = link_kind(link) in ("plataforma", "pdf") or (entry and entry.get("has_menu") == "1") \
                or repaired in ("pagina-cardapio", "plataforma", "plataforma-no-site")
            out["type"] = "Cardapio" if menu_like else "Site"
        area = config["areas"].get(row["_area"])
        if area is None:
            continue
        for spec in area["files"]:
            if spec.get("only_sheet") and origin == "planilha":
                files[spec["id"]].append(out)
        spec = file_for(row, area["files"])
        if spec:
            files[spec["id"]].append(out)
    return files, counters, removed_sheet, repaired_rows


def csv_bytes(rows, columns):
    buffer = io.StringIO()
    import csv
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


CELL_SIZE = 0.1  # degrees (~11 km): the app picks regions by the cells around the user
# A region keeps a cell only with this share of the cell's restaurants: a few misfiled rows (an
# interior city parsed from a capital address) must not make the app download the interior too.
CELL_MIN_SHARE = 0.1


def cell_of(point):
    return (math.floor(point[0] / CELL_SIZE), math.floor(point[1] / CELL_SIZE))


def coverage_cells(points, totals=None):
    """Grid cells ("-236,-467" = floor(lat/0.1), floor(lon/0.1)) with restaurants of the region.
    `totals` counts every region's restaurants per cell; then the region needs CELL_MIN_SHARE of them.
    The app downloads the regions whose cells touch the user's cell or its 8 neighbors, and
    treats the user as inside the covered area under the same rule."""
    counts = Counter(cell_of(p) for p in points)
    cells = [c for c, n in counts.items() if totals is None or n >= CELL_MIN_SHARE * totals.get(c, n)]
    return [f"{a},{b}" for a, b in sorted(cells)]


def area_points(rows, area_bbox=None):
    points = [(to_float(r["latitude"]), to_float(r["longitude"])) for r in rows]
    # Sheet typos (lat 0.9, -30.0) would blow up the bbox: only points inside the area count.
    return [(a, b) for a, b in points if a is not None and b is not None
            and (area_bbox is None or in_bbox(a, b, area_bbox))]


def robust_bbox(points):
    """Bounding box from the 1st to the 99th percentile, so a few bad coordinates don't stretch it."""
    if not points:
        return None
    lats = sorted(p[0] for p in points)
    lons = sorted(p[1] for p in points)
    low, high = int(0.01 * (len(points) - 1)), int(0.99 * (len(points) - 1) + 0.5)
    return {"min_lat": round(lats[low], 5), "min_lon": round(lons[low], 5),
            "max_lat": round(lats[high], 5), "max_lon": round(lons[high], 5)}


def region_entry(spec, area_id, rows, data, base_url, previous, area_bbox=None, cell_totals=None):
    points = area_points(rows, area_bbox)
    sha = hashlib.sha256(data).hexdigest()
    now = utc_now().isoformat().replace("+00:00", "Z")
    prev = previous.get(spec["id"], {})
    center = spec.get("center") or ({"lat": round(statistics.median(p[0] for p in points), 5),
                                     "lon": round(statistics.median(p[1] for p in points), 5)} if points else None)
    return {
        "id": spec["id"], "name": spec["name"], "area": area_id, "phase": spec.get("phase", 1),
        "app_default": bool(spec.get("app_default", False)),
        "bbox": robust_bbox(points),
        "center": center,
        "cells": coverage_cells(points, cell_totals),
        "url": f"{base_url}/{spec['id']}.csv",
        "rows": len(rows),
        "restaurants": len({restaurant_key(r["name"], r["address"]) for r in rows}),
        "bytes": len(data), "sha256": sha,
        "updated_at": prev["updated_at"] if prev.get("sha256") == sha and prev.get("updated_at") else now,
    }


def guard(entries, previous, config):
    max_loss = config["publish"]["max_row_loss"]
    min_rows = config["publish"]["min_rows_for_guard"]
    violations = []
    current = {e["id"]: e["rows"] for e in entries}
    for region_id, prev in previous.items():
        before = prev.get("rows", 0)
        if before < min_rows:
            continue
        after = current.get(region_id, 0)
        if after < before * (1 - max_loss):
            violations.append((region_id, before, after))
    return violations


def previous_keys(region_id, base_url, previous_dir=None):
    """Restaurant keys of the previously published file: local copy first, then GitHub Pages."""
    text = None
    if previous_dir and (previous_dir / f"{region_id}.csv").exists():
        text = (previous_dir / f"{region_id}.csv").read_text(encoding="utf-8")
    elif base_url and not os.environ.get("CARDAPIOS_OFFLINE"):
        try:
            with urllib.request.urlopen(f"{base_url}/{region_id}.csv", timeout=30) as response:
                text = response.read().decode("utf-8")
        except Exception:
            return None
    if text is None or text.lstrip().startswith("<"):
        return None
    return {restaurant_key(r.get("name"), r.get("address")) for r in parse_csv_text(text)}


def write_report(path, entries, previous, violations, counters, removed_sheet, repaired_rows, diffs, merge_stats,
                 forced):
    lines = [f"# Relatório do build ({utc_now().strftime('%d/%m/%Y %H:%M')} UTC)", ""]
    if violations:
        lines += ["## ⚠️ Publicação recusada (trava de regressão)" if not forced else
                  "## ⚠️ Trava de regressão ignorada (--force)", ""]
        for region_id, before, after in violations:
            lines.append(f"- `{region_id}`: {before} → {after} linhas ({(after - before) / before:+.0%})")
        lines.append("")
    lines += ["## Regiões", "", "| Região | Linhas antes | Linhas agora | Restaurantes | Entraram | Saíram | Tamanho |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for e in entries:
        before = previous.get(e["id"], {}).get("rows", "–")
        added, removed = diffs.get(e["id"], ("?", "?"))
        lines.append(f"| `{e['id']}` | {before} | {e['rows']} | {e['restaurants']} | {added} | {removed} | "
                     f"{e['bytes'] / 1024:.0f} KB |")
    lines += ["", "## Links", "", "| Origem:status | Linhas |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(counters.items())]
    if merge_stats:
        lines += ["", "## Merge", "", "```", *[f"{k}: {v}" for k, v in merge_stats.items()], "```"]
    if removed_sheet:
        lines += ["", f"## Linhas da planilha fora da publicação por link quebrado ({len(removed_sheet)})", "",
                  "Corrija o `menu_link` na planilha ou marque `travar_link=TRUE` se o link estiver certo.", "",
                  "| Linha | Nome | Link |", "|---:|---|---|"]
        lines += [f"| {r.get('_sheet_line', '')} | {r['name']} | {link} |" for r, link in removed_sheet[:300]]
    if repaired_rows:
        lines += ["", f"## Links trocados automaticamente ({len(repaired_rows)})", "", "| Nome | Antes | Depois | Como |",
                  "|---|---|---|---|"]
        lines += [f"| {r['name']} | {r.get('menu_link') or '–'} | {link} | {method} |"
                  for r, link, method in repaired_rows[:300]]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("\n".join(lines[:60]) + "\n")


INDEX_HTML = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Cardápios: dados</title>
<style>body{{font:16px/1.5 -apple-system,system-ui,sans-serif;max-width:720px;margin:2rem auto;padding:0 16px}}
td,th{{padding:4px 8px;text-align:left}}</style></head><body>
<h1>Cardápios: dados</h1><p>Restaurantes e links de cardápio usados pelo app Cardápios. Índice:
<a href="index.json">index.json</a>. Fontes e licenças: <a href="ATTRIBUTION.md">ATTRIBUTION.md</a>.</p>
<table><tr><th>Região</th><th>Linhas</th><th>Atualizado</th></tr>{rows}</table></body></html>
"""


def publish(config, merged_path=None, cache_path=None, out_dir=None, force=False, previous_dir=None,
            ids_path=None):
    merged_path = merged_path or WORK / "merged.csv"
    out_dir = out_dir or PUBLIC
    ids_path = ids_path or DATA / "ids.csv"
    merged = read_csv(merged_path)
    if not merged:
        raise SystemExit("Rode merge antes (work/merged.csv vazio ou ausente).")
    columns = [c for c in merged[0].keys() if c not in INTERNAL_COLUMNS]
    cache = LinkCache(cache_path or DATA / "links-cache.csv")
    repairs = load_repairs()
    files, counters, removed_sheet, repaired_rows = build_rows(merged, cache, repairs, config)
    last = read_json(DATA / "last-publish.json", {}) or {}
    previous = last.get("regions", {})
    base_url = config["pages_base_url"]

    # Restaurants per cell over the regions the app downloads (phase 0 repeats them).
    cell_totals = Counter()
    for area in config["areas"].values():
        for spec in area["files"]:
            if spec.get("phase", 1) >= 1:
                cell_totals.update(cell_of(p) for p in area_points(files.get(spec["id"], []), area["bbox"]))

    entries, payloads = [], {}
    for area_id, area in config["areas"].items():
        for spec in area["files"]:
            rows = files.get(spec["id"], [])
            data = csv_bytes(rows, columns)
            payloads[spec["id"]] = data
            entries.append(region_entry(spec, area_id, rows, data, base_url, previous, area["bbox"], cell_totals))

    violations = guard(entries, previous, config)
    diffs = {}
    for e in entries:
        before = previous_keys(e["id"], base_url if previous else None, previous_dir)
        if before is not None:
            now = {restaurant_key(r["name"], r["address"]) for r in files.get(e["id"], [])}
            diffs[e["id"]] = (len(now - before), len(before - now))
    merge_stats = read_json(WORK / "merge-stats.json", {})
    report_path = REPORTS / "ultimo-build.md"
    write_report(report_path, entries, previous, violations, counters, removed_sheet, repaired_rows, diffs,
                 merge_stats, force)
    if violations and not force:
        for region_id, before, after in violations:
            log(f"TRAVA: {region_id} cairia de {before} para {after} linhas (> {config['publish']['max_row_loss']:.0%})")
        log(f"Nada publicado. Relatório: {report_path}")
        raise RegressionError(GUARD_EXIT_CODE)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    for region_id, data in payloads.items():
        target = out_dir / f"{region_id}.csv"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    generated_at = utc_now().isoformat().replace("+00:00", "Z")
    index = {"version": 1, "generated_at": generated_at, "columns": columns,
             "attribution": "Planilha Cardápios; Overture Maps Foundation (CDLA-Permissive-2.0; Apache-2.0 Foursquare)",
             "regions": entries}
    write_json(out_dir / "index.json", index)
    for name in ("ATTRIBUTION.md", "LICENSE-DATA.md"):
        if (ROOT / name).exists():
            shutil.copy(ROOT / name, out_dir / name)
    (out_dir / ".nojekyll").write_text("")
    table = "".join(f"<tr><td><a href=\"{e['id']}.csv\">{e['name']}</a></td><td>{e['rows']}</td>"
                    f"<td>{e['updated_at'][:10]}</td></tr>" for e in entries)
    (out_dir / "index.html").write_text(INDEX_HTML.format(rows=table), encoding="utf-8")

    write_json(DATA / "last-publish.json", {"generated_at": generated_at, "regions": {
        e["id"]: {k: e[k] for k in ("rows", "restaurants", "sha256", "updated_at")} for e in entries}})
    freeze_ids(files, ids_path)
    for e in entries:
        log(f"  {e['id']}: {e['rows']} linhas, {e['restaurants']} restaurantes, {e['bytes'] / 1024:.0f} KB")
    log(f"publish: {len(entries)} arquivos -> {out_dir}; relatório: {report_path}")
    return entries


def freeze_ids(files, ids_path):
    """Freezes name|address of published new places and records sheet matches (append-only)."""
    ids = load_ids(ids_path)
    day = utc_now().date().isoformat()
    for rows in files.values():
        for row in rows:
            source_id = (row.get("id_fonte") or "").strip()
            if not source_id:
                continue
            origin = "planilha" if row["_origin"] == "planilha" else "gerado"
            current = ids.get(source_id)
            if current is None or (origin == "planilha" and (current["origem"] != "planilha"
                                                              or current["name"] != row["name"]
                                                              or current["address"] != row["address"])):
                ids[source_id] = {"id_fonte": source_id, "name": row["name"], "address": row["address"],
                                  "origem": origin, "first_seen": current["first_seen"] if current else day}
    write_csv(ids_path, sorted(ids.values(), key=lambda r: r["id_fonte"]), IDS_COLUMNS)
