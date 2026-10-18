"""OpenStreetMap enrichment: TODO (not built yet, no osmium dependency for now).

Plan (report 2.1 and 4.3):
1. `fetch-osm --area sp-estado`: download https://download.geofabrik.de/south-america/brazil/sudeste-latest.osm.pbf
   (≈ 820 MB, cache it in Actions with actions/cache keyed by the ETag), then
   `osmium tags-filter sudeste-latest.osm.pbf nwr/amenity=restaurant,fast_food,cafe -o food.osm.pbf` and
   `osmium export food.osm.pbf -f geojsonseq`. Normalize to work/osm/<area>.csv with columns
   id (osm:n123 / osm:w456), name, lat, lon, website, menu_url (website:menu, menu:url), cuisine,
   opening_hours, phone, brand_wikidata.
2. `apply_osm` below: match those records to the merged rows with match.match_places (precise
   coordinates), then, without overriding the sheet:
   - menu link preference 2 (report 3.2): put `website:menu`/`menu:url` first in `_alt_links`;
   - fill `opening_hours` (the app shows "Aberto agora") and `cuisine` when empty (OSM > Overture);
   - add unmatched OSM places with a website as new rows (fonte=osm).
3. Licensing: OSM data is ODbL 1.0. Once OSM rows or fields are published, the published CSVs are a
   derivative database and must be released under ODbL with "© colaboradores do OpenStreetMap"
   (update ATTRIBUTION.md, LICENSE-DATA.md and the app's "Sobre").
"""

from .common import WORK


def apply_osm(area_id, rows):
    """Hook called by merge. No-op until fetch-osm exists; returns the number of rows enriched."""
    path = WORK / "osm" / f"{area_id}.csv"
    if path.exists():
        raise NotImplementedError("work/osm encontrado, mas o enriquecimento OSM ainda não foi implementado (TODO).")
    return 0
