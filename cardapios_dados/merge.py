"""merge: sheet + automatic sources -> work/merged.csv (one row per menu link, app columns + internals).

Rules (report 4.3, steps 4 and 5):
- Sheet rows keep `name` and `address` byte-identical (Menu.id = "name|address" keys favorites).
- The sheet wins on every field it fills; a matched source only fills empty fields. Coarse sheet
  coordinates (<= 2 decimals, ~1 km) are replaced by the source's only on a strong match.
- A sheet restaurant with only available=FALSE rows is a blacklist: its matched source records are dropped.
- New places take their frozen name|address from data/ids.csv when they have one (publish freezes
  them the first time they are published), so a source rewriting an address never changes an id.
- OSM (website:menu, cuisine, opening_hours) is a TODO hook: see osm.py.
"""

from collections import defaultdict

from . import osm
from .address import city_from_address, format_address, format_phone
from .common import (APP_COLUMNS, DATA, EXTRA_COLUMNS, OPTIONAL_APP_COLUMNS, WORK, decimals, in_bbox, is_true,
                     log, read_csv, read_csv_header, restaurant_key, site_of, to_float, write_csv)
from .cuisine import cuisine_column
from .links import clean_url, is_platform_or_social, link_kind, link_rank
from .match import Place, coarse_coordinate, dedupe_sources, match_places
from .overture import load_overture

INTERNAL_COLUMNS = ["_origin", "_key", "_area", "_municipality", "_alt_links", "_lock_link", "_sheet_line"]
IDS_COLUMNS = ["id_fonte", "name", "address", "origem", "first_seen"]


def output_columns(sheet_header):
    columns = list(sheet_header) or list(APP_COLUMNS)
    for column in APP_COLUMNS + OPTIONAL_APP_COLUMNS + EXTRA_COLUMNS:
        if column not in columns and not (column == "cuisine" and "culinaria" in columns) \
                and not (column == "neighborhood" and "bairro" in columns) \
                and not (column == "opening_hours" and "horario" in columns):
            columns.append(column)
    return columns


def _own_domains(*urls):
    return {site_of(u) for u in urls if u and link_kind(u) in ("site", "pdf")}


def load_ids(path=None):
    return {row["id_fonte"]: row for row in read_csv(path or DATA / "ids.csv")}


def area_of(lat, lon, areas):
    for area_id, area in areas.items():
        if in_bbox(lat, lon, area["bbox"]):
            return area_id
    return next(iter(areas))


def sheet_anchors(sheet_rows):
    """One Place per sheet restaurant (name|address), plus the keys whose rows are all FALSE."""
    by_key = defaultdict(list)
    for row in sheet_rows:
        if (row.get("name") or "").strip():
            by_key[restaurant_key(row["name"], row.get("address"))].append(row)
    anchors, blacklist = [], set()
    for key, rows in by_key.items():
        if not any(is_true(r.get("available")) for r in rows):
            blacklist.add(key)
        with_point = next((r for r in rows if to_float(r.get("latitude")) is not None
                           and to_float(r.get("longitude")) is not None), None)
        if with_point is None:
            continue
        anchors.append(Place(
            key, rows[0]["name"], rows[0].get("address"), to_float(with_point["latitude"]),
            to_float(with_point["longitude"]), phones=[r.get("phone") for r in rows],
            domains=_own_domains(*[r.get("website") for r in rows], *[r.get("menu_link") for r in rows]),
            coarse=coarse_coordinate(with_point["latitude"], with_point["longitude"])))
    return anchors, blacklist, by_key


def source_places(records):
    places = []
    for record in records:
        websites = record["websites"].split()
        places.append(Place(f"ovt:{record['id']}", record["name"], record["freeform"], to_float(record["lat"]),
                            to_float(record["lon"]), phones=record["phones"].split(),
                            domains=_own_domains(*websites)))
    return places


def best_link(urls):
    urls = [clean_url(u) for u in urls if link_kind(u) != "invalido"]
    return min(urls, key=link_rank) if urls else ""


def new_place_row(record, area, ids):
    source_id = f"ovt:{record['id']}"
    frozen = ids.get(source_id)
    name = frozen["name"] if frozen else record["name"].strip()
    address = frozen["address"] if frozen else format_address(record["freeform"], record["locality"],
                                                              record["postcode"], area["uf"])
    links = record["websites"].split() + record["socials"].split()
    menu_link = best_link(links)
    website = next((clean_url(u) for u in record["websites"].split() if link_kind(u) == "site"), "")
    phones = record["phones"].split()
    return {
        "name": name, "logo": "", "address": address,
        "latitude": f"{float(record['lat']):.5f}", "longitude": f"{float(record['lon']):.5f}",
        "city": record["locality"], "state": area["state_name"], "country": "Brazil", "available": "TRUE",
        "phone": format_phone(phones[0]) if phones else "", "email": "", "website": website,
        "type": "Cardapio", "menu_link": menu_link,
        "cuisine": cuisine_column(record["name"], record["taxonomy"]), "neighborhood": "", "opening_hours": "",
        "id_fonte": source_id, "fonte": "overture", "confianca": record["confidence"],
        "_origin": "overture", "_key": restaurant_key(name, address), "_municipality": record["locality"],
        "_alt_links": " ".join(dict.fromkeys(clean_url(u) for u in links if clean_url(u) != menu_link)),
        "_lock_link": "",
    }


def enrich_sheet_row(row, record, strong, columns):
    """Fills empty sheet fields from the matched source record. Never touches name/address."""
    phones = record["phones"].split()
    if not (row.get("phone") or "").strip() and phones:
        row["phone"] = format_phone(phones[0])
    if not (row.get("website") or "").strip():
        row["website"] = next((clean_url(u) for u in record["websites"].split() if link_kind(u) == "site"), "")
    cuisine_col = "culinaria" if "culinaria" in columns else "cuisine"
    if not (row.get(cuisine_col) or "").strip():
        row[cuisine_col] = cuisine_column(row["name"], record["taxonomy"])
    if strong and coarse_coordinate(row.get("latitude"), row.get("longitude")):
        row["latitude"], row["longitude"] = f"{float(record['lat']):.5f}", f"{float(record['lon']):.5f}"
    if not (row.get("id_fonte") or "").strip():
        row["id_fonte"] = f"ovt:{record['id']}"
    row["fonte"] = "planilha+overture"
    row["confianca"] = record["confidence"]
    links = record["websites"].split() + record["socials"].split()
    existing = row.get("_alt_links", "").split()
    row["_alt_links"] = " ".join(dict.fromkeys(existing + [clean_url(u) for u in links]))


def merge(config, area_ids, sheet_path=None, out_path=None, ids_path=None):
    sheet_path = sheet_path or WORK / "sheet.csv"
    if not sheet_path.exists():
        raise SystemExit("Rode fetch-sheet antes (work/sheet.csv não existe).")
    sheet_rows = read_csv(sheet_path)
    columns = output_columns(read_csv_header(sheet_path))
    areas = {a: config["areas"][a] for a in area_ids}
    ids = load_ids(ids_path)
    anchors, blacklist, by_key = sheet_anchors(sheet_rows)
    pinned = {r["id_fonte"]: restaurant_key(r["name"], r["address"]) for r in ids.values() if r["origem"] == "planilha"}
    for row in sheet_rows:
        if (row.get("id_fonte") or "").strip():
            pinned[row["id_fonte"].strip()] = restaurant_key(row["name"], row.get("address"))

    # Sheet rows: available ones, in sheet order, byte-identical name and address.
    out = []
    sheet_by_key = defaultdict(list)
    for line, row in enumerate(sheet_rows, start=2):
        if not is_true(row.get("available")) or not (row.get("name") or "").strip():
            continue
        item = {c: row.get(c, "") for c in columns}
        lat, lon = to_float(row.get("latitude")), to_float(row.get("longitude"))
        item.update({
            "fonte": row.get("fonte") or "planilha",
            "_origin": "planilha", "_key": restaurant_key(row["name"], row.get("address")),
            "_area": area_of(lat, lon, areas),
            "_municipality": city_from_address(row.get("address")) or (row.get("city") or "").strip(),
            "_alt_links": " ".join(u for u in [clean_url(row.get("website", ""))] if u),
            "_lock_link": "1" if is_true(row.get("travar_link")) else "",
            "_sheet_line": str(line),
        })
        out.append(item)
        sheet_by_key[item["_key"]].append(item)

    stats = {"sheet_rows": len(sheet_rows), "sheet_available_rows": len(out), "sheet_restaurants": len(sheet_by_key),
             "blacklisted_keys": len(blacklist)}
    for area_id, area in areas.items():
        records, summary = load_overture(area_id)
        if not records:
            log(f"Aviso: sem dados do Overture para {area_id} (rode fetch-overture). Só a planilha entra.")
            continue
        records = [r for r in records if r["name"].strip() and r["freeform"].strip()]
        records.sort(key=lambda r: -float(r["confidence"] or 0))
        by_id = {f"ovt:{r['id']}": r for r in records}
        places = dedupe_sources(source_places(records))
        domain_count = defaultdict(int)
        for place in places:
            for domain in place.domains:
                domain_count[domain] += 1
        shared = frozenset(d for d, n in domain_count.items() if n > 3)
        matches = match_places(anchors, places, shared, pinned)
        matched_primary = matched_dupes = blacklisted = 0
        blacklist_on = config.get("merge", {}).get("sheet_false_is_blacklist", True)
        for ref, (key, score, primary, strong) in matches.items():
            if key in blacklist and blacklist_on:
                blacklisted += 1
                continue
            if primary:
                matched_primary += 1
                for item in sheet_by_key.get(key, []):
                    enrich_sheet_row(item, by_id[ref], strong, columns)
                    if not item["_municipality"]:
                        item["_municipality"] = by_id[ref]["locality"]
            else:
                matched_dupes += 1
        new_rows = 0
        for place in places:
            if place.ref in matches:
                continue
            row = new_place_row(by_id[place.ref], area, ids)
            row["_area"] = area_id
            out.append(row)
            new_rows += 1
        stats[area_id] = {"overture_release": summary.get("release"), "overture_records": len(records),
                          "after_internal_dedupe": len(places), "matched_sheet": matched_primary,
                          "duplicates_absorbed": matched_dupes, "blacklisted": blacklisted, "new_places": new_rows}
        log(f"{area_id}: {len(records)} do Overture, {len(places)} após dedupe interno, {matched_primary} casados com a "
            f"planilha (+{matched_dupes} duplicados), {blacklisted} na blacklist, {new_rows} novos")
        osm.apply_osm(area_id, out)  # TODO hook (no-op for now)

    out_path = out_path or WORK / "merged.csv"
    write_csv(out_path, out, columns + INTERNAL_COLUMNS)
    log(f"merge: {len(out)} linhas -> {out_path}")
    return stats, columns
