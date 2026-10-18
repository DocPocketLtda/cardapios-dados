"""repair-links: replacement for broken links (and better links for new places), report 3.2 order.

For each row whose menu link is broken, candidates are tried in this order:
  1. manual sheet link: rows with travar_link=TRUE are never touched;
  2. OSM website:menu (TODO, see osm.py);
  3. a menu/delivery platform store link: from the place's other links (Overture websites/socials),
     from the anchors of its own site's home page, or from a Linktree/beacons page;
  4. a menu page on its own site: a "cardápio/menu" anchor or a PDF found in the home page, or
     /cardapio, /menu, /cardapio.pdf when the home page is alive;
  5. the site's home page, when it answers 200 and is not parked;
  6. a social network link (sheet rows only, last resort).
Every candidate is validated by the same checker and cache as check-links. New places whose link is
only a home page (or a Linktree) are also "upgraded" to a platform/menu link found the same way.
Results go to data/repairs.csv; publish applies those whose replacement is still ok.
"""

import urllib.parse

from .common import DATA, home_of, log, read_csv, today, utc_now, write_csv
from .links import (TRIVIAL_PATHS, LinkCache, is_store_url, link_kind, link_rank, run_checks, save_cache)

REPAIR_COLUMNS = ["key", "original_url", "replacement", "method", "reason", "found_at"]
PROBE_PATHS = ("cardapio", "menu", "cardapio.pdf")


def load_repairs(path=None):
    return {(r["key"], r["original_url"]): r for r in read_csv(path or DATA / "repairs.csv")}


def needs_repair(row, cache):
    """"quebrado", "melhorar" or None."""
    if row.get("_lock_link"):
        return None
    link = row.get("menu_link", "")
    entry = cache.get(link) if link else None
    if link and entry and entry["status"] == "quebrado":
        return "quebrado"
    if row["_origin"] != "planilha":
        kind = link_kind(link)
        if not link and row.get("_alt_links"):
            return "quebrado"
        path = urllib.parse.urlsplit(link).path.rstrip("/").lower() if link else ""
        if kind == "linktree" or (kind == "site" and path in TRIVIAL_PATHS):
            if entry and entry["status"] == "ok" and (entry["hint_platform"] or entry["hint_menu"]):
                return "melhorar"
    return None


def _alive(cache, url):
    entry = cache.get(url)
    return entry is not None and entry["status"] == "ok"


def first_round_urls(row):
    link = row.get("menu_link", "")
    urls = [u for u in row.get("_alt_links", "").split() if link_kind(u) not in ("rede social", "invalido")]
    if link and link_kind(link) in ("site", "pdf"):
        urls.append(home_of(link))
    return [u for u in dict.fromkeys(urls) if u != link]


def candidates(row, cache, with_probes=False):
    """(method, url) in preference order."""
    link = row.get("menu_link", "")
    alt = [u for u in row.get("_alt_links", "").split() if u != link]
    found = []
    for url in sorted(alt, key=link_rank):
        if link_kind(url) == "plataforma" and is_store_url(url):
            found.append(("plataforma", url))
    pages = [link] + ([home_of(link)] if link and link_kind(link) in ("site", "pdf") else [])
    pages += [u for u in alt if link_kind(u) in ("site", "linktree")]
    pages += [home_of(u) for u in alt if link_kind(u) == "site"]
    homes_alive = []
    for page in dict.fromkeys(p for p in pages if p):
        entry = cache.get(page)
        if not entry or entry["status"] != "ok":
            continue
        if entry["hint_platform"]:
            found.append(("plataforma-no-site", entry["hint_platform"]))
        if entry["hint_menu"]:
            found.append(("pagina-cardapio", entry["hint_menu"]))
        if link_kind(page) == "site" and urllib.parse.urlsplit(page).path.rstrip("/") in TRIVIAL_PATHS:
            homes_alive.append(page)
    if with_probes:
        for home in homes_alive[:1]:
            found += [("pagina-cardapio", urllib.parse.urljoin(home, p)) for p in PROBE_PATHS]
    found += [("site", home) for home in homes_alive]
    if row["_origin"] == "planilha":
        found += [("rede social", u) for u in alt if link_kind(u) == "rede social"]
    seen, result = set(), []
    for method, url in found:
        if url not in seen and url != link:
            seen.add(url)
            result.append((method, url))
    return result


def choose(row, reason, cache):
    current_rank = link_rank(row.get("menu_link", "")) if row.get("menu_link") else 99
    for method, url in candidates(row, cache, with_probes=reason == "quebrado"):
        if method == "rede social":
            return method, url  # unvalidated by design: last resort for sheet rows
        if not _alive(cache, url):
            continue
        if reason == "melhorar" and link_rank(url) >= current_rank:
            continue
        return method, url
    return None


def repair(merged_rows, cache_path, repairs_path=None, budget_seconds=None, limit=None, workers=24,
           respect_robots=True):
    repairs_path = repairs_path or DATA / "repairs.csv"
    cache = LinkCache(cache_path)
    existing = load_repairs(repairs_path)
    todo = [(row, reason) for row in merged_rows if (reason := needs_repair(row, cache))]
    log(f"repair-links: {sum(1 for _, r in todo if r == 'quebrado')} links quebrados, "
        f"{sum(1 for _, r in todo if r == 'melhorar')} a melhorar")
    day = today()

    def check(urls):
        pending = []
        for url in dict.fromkeys(urls):
            cache.register(url, "reparo")
        due = set(cache.due(day))
        pending = [u for u in dict.fromkeys(urls) if u in due]
        if limit:
            pending = pending[:limit]
        if pending:
            counts = run_checks(cache, pending, workers=workers, budget_seconds=budget_seconds,
                                respect_robots=respect_robots)
            log(f"  {len(pending)} candidatos verificados: {counts}")

    check([u for row, _ in todo for u in first_round_urls(row)])
    check([u for row, reason in todo for _, u in candidates(row, cache, with_probes=reason == "quebrado")
           if link_kind(u) != "rede social"])

    stamp = utc_now().isoformat().replace("+00:00", "Z")
    keys_in_use = {(row["_key"], row.get("menu_link", "")) for row in merged_rows}
    result = {k: v for k, v in existing.items() if k in keys_in_use}
    fixed = {"quebrado": 0, "melhorar": 0}
    for row, reason in todo:
        choice = choose(row, reason, cache)
        key = (row["_key"], row.get("menu_link", ""))
        if choice:
            method, url = choice
            previous = result.get(key)
            result[key] = {"key": key[0], "original_url": key[1], "replacement": url, "method": method,
                           "reason": reason,
                           "found_at": previous["found_at"] if previous and previous["replacement"] == url else stamp}
            fixed[reason] += 1
    write_csv(repairs_path, sorted(result.values(), key=lambda r: (r["key"], r["original_url"])), REPAIR_COLUMNS)
    save_cache(cache)
    log(f"repair-links: {fixed['quebrado']} reparados, {fixed['melhorar']} melhorados -> {repairs_path}")
    return fixed
