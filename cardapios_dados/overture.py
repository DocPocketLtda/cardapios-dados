"""Overture Maps Places, read straight from the public S3 bucket with DuckDB (no credentials).

The latest release is discovered by listing `s3://overturemaps-us-west-2/release/`. The query keeps
only food places of the area (report 2.2 and 4.3): core `basic_category`, BR + region, the area's
bbox, confidence >= 0.8 or >= 0.7 with a website, minus non-restaurant taxonomies (ice cream,
candy...). The result goes to work/overture/<area>-<release>.parquet (ignored by git) and to a
normalized work/overture/<area>.csv.gz that `merge` reads with the standard library.
"""


import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from .common import WORK, log, write_csv, write_json

# Columns the query relies on: fail loudly (without publishing) if the schema changes again
# (it already replaced `categories` by `basic_category`/`taxonomy` in 2025).
REQUIRED_COLUMNS = {"id", "names", "confidence", "websites", "socials", "phones", "addresses", "basic_category",
                    "taxonomy", "brand", "sources", "geometry", "bbox"}
RELEASE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.(\d+)$")
NORMALIZED_COLUMNS = ["id", "name", "freeform", "locality", "postcode", "region", "lat", "lon", "confidence",
                      "basic_category", "taxonomy", "phones", "websites", "socials", "brand", "brand_wikidata",
                      "datasets", "release"]


def _list(bucket, prefix, delimiter="/", max_keys=1000):
    query = urllib.parse.urlencode({"list-type": "2", "prefix": prefix, "delimiter": delimiter,
                                    "max-keys": str(max_keys)})
    url = f"https://{bucket}.s3.us-west-2.amazonaws.com/?{query}"
    with urllib.request.urlopen(url, timeout=60) as response:
        root = ET.fromstring(response.read())
    ns = {"s3": root.tag.split("}")[0].strip("{")} if root.tag.startswith("{") else {}
    find = (lambda path: root.findall(f"s3:{path}", ns)) if ns else (lambda path: root.findall(path))
    prefixes = [p.find("s3:Prefix", ns).text if ns else p.find("Prefix").text for p in find("CommonPrefixes")]
    keys = [c.find("s3:Key", ns).text if ns else c.find("Key").text for c in find("Contents")]
    return prefixes, keys


def release_sort_key(name):
    match = RELEASE_RE.match(name)
    return (match.group(1), int(match.group(2))) if match else ("", -1)


def latest_release(bucket):
    """Newest release that already has places files (a release being uploaded is skipped)."""
    prefixes, _ = _list(bucket, "release/")
    releases = sorted((p.split("/")[1] for p in prefixes if RELEASE_RE.match(p.split("/")[1])),
                      key=release_sort_key, reverse=True)
    for release in releases:
        _, keys = _list(bucket, f"release/{release}/theme=places/type=place/", delimiter="", max_keys=2)
        if any(k.endswith(".parquet") for k in keys):
            return release
    raise SystemExit("Nenhuma release do Overture com places encontrada no S3.")


def _sql_list(values):
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)


def build_query(source, area, overture_config, limit=None):
    bbox = area["bbox"]
    filters = area.get("overture", {})
    min_conf = filters.get("min_confidence", overture_config["min_confidence"])
    min_conf_web = filters.get("min_confidence_with_website", overture_config["min_confidence_with_website"])
    localities = filters.get("localities")
    where = [
        f"bbox.xmin BETWEEN {bbox['min_lon']} AND {bbox['max_lon']}",
        f"bbox.ymin BETWEEN {bbox['min_lat']} AND {bbox['max_lat']}",
        f"basic_category IN ({_sql_list(overture_config['basic_categories'])})",
        f"coalesce(taxonomy.\"primary\", '') NOT IN ({_sql_list(overture_config['exclude_taxonomy'])})",
        "addresses[1].country = 'BR'",
        f"addresses[1].region = '{filters.get('region', area['uf'])}'",
        f"(confidence >= {min_conf} OR (confidence >= {min_conf_web} AND len(websites) > 0))",
        "names.\"primary\" IS NOT NULL",
    ]
    if localities:
        where.append(f"addresses[1].locality IN ({_sql_list(localities)})")
    return f"""
SELECT id, names."primary" AS name, confidence, websites, socials, phones,
       addresses[1].freeform AS freeform, addresses[1].locality AS locality,
       addresses[1].postcode AS postcode, addresses[1].region AS region,
       basic_category, taxonomy."primary" AS taxonomy,
       brand.names."primary" AS brand, brand.wikidata AS brand_wikidata,
       list_distinct(list_transform(sources, s -> s.dataset)) AS datasets,
       ST_Y(geometry) AS lat, ST_X(geometry) AS lon
FROM read_parquet('{source}', hive_partitioning = 1)
WHERE {' AND '.join(where)}
ORDER BY confidence DESC, id
{f'LIMIT {int(limit)}' if limit else ''}"""


def fetch_overture(config, area_id, area, release=None, limit=None):
    try:
        import duckdb
    except ImportError:
        raise SystemExit("Instale o duckdb: pip install -r requirements.txt")
    overture_config = config["overture"]
    bucket = overture_config["bucket"]
    release = release or latest_release(bucket)
    log(f"Overture: release {release}, área {area_id}")
    source = f"s3://{bucket}/release/{release}/theme=places/type=place/*"
    out_dir = WORK / "overture"
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = out_dir / f"{area_id}-{release}.parquet"

    con = duckdb.connect()
    con.sql("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;")
    con.sql(f"SET s3_region='{overture_config['s3_region']}';")
    columns = {row[0] for row in con.sql(f"DESCRIBE SELECT * FROM read_parquet('{source}', hive_partitioning = 1)").fetchall()}
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise SystemExit(f"O schema do Overture mudou: faltam {sorted(missing)}. Ajuste overture.py antes de publicar.")

    started = time.monotonic()
    query = build_query(source, area, overture_config, limit)
    con.sql(f"COPY ({query}) TO '{parquet_path}' (FORMAT parquet, COMPRESSION zstd)")
    elapsed = time.monotonic() - started

    stats = con.sql(f"""SELECT count(*) AS total,
        count(*) FILTER (len(websites) > 0) AS with_website,
        count(*) FILTER (len(phones) > 0) AS with_phone,
        count(*) FILTER (list_contains(datasets, 'Foursquare')) AS foursquare,
        count(*) FILTER (freeform IS NULL OR freeform = '') AS without_address
        FROM '{parquet_path}'""").fetchone()
    total, with_website, with_phone, foursquare, without_address = stats

    relation = con.sql(f"SELECT * FROM '{parquet_path}'")
    names = relation.columns
    normalized = []
    for record in relation.fetchall():
        item = dict(zip(names, record))
        normalized.append({
            "id": item["id"], "name": (item["name"] or "").strip(), "freeform": item["freeform"] or "",
            "locality": item["locality"] or "", "postcode": item["postcode"] or "", "region": item["region"] or "",
            "lat": f"{item['lat']:.6f}", "lon": f"{item['lon']:.6f}", "confidence": f"{item['confidence']:.3f}",
            "basic_category": item["basic_category"] or "", "taxonomy": item["taxonomy"] or "",
            "phones": " ".join(item["phones"] or []), "websites": " ".join(item["websites"] or []),
            "socials": " ".join(item["socials"] or []), "brand": item["brand"] or "",
            "brand_wikidata": item["brand_wikidata"] or "", "datasets": " ".join(item["datasets"] or []),
            "release": release,
        })
    csv_path = out_dir / f"{area_id}.csv.gz"
    write_csv(csv_path, normalized, NORMALIZED_COLUMNS)
    summary = {"area": area_id, "release": release, "rows": total, "with_website": with_website,
               "with_phone": with_phone, "foursquare": foursquare, "without_address": without_address,
               "seconds": round(elapsed, 1), "limit": limit}
    write_json(out_dir / f"{area_id}.json", summary)
    log(f"Overture: {total} lugares ({with_website} com site, {with_phone} com telefone, "
        f"{foursquare} da Foursquare, {without_address} sem endereço) em {elapsed:.0f}s -> {csv_path}")
    return summary


def load_overture(area_id):
    from .common import read_csv, read_json
    path = WORK / "overture" / f"{area_id}.csv.gz"
    return read_csv(path), read_json(WORK / "overture" / f"{area_id}.json", {})
