"""Shared helpers: paths, CSV I/O, text normalization and small geo utilities."""

import csv
import datetime as dt
import gzip
import io
import json
import math
import os
import re
import unicodedata
import urllib.parse
from pathlib import Path

ROOT = Path(os.environ.get("CARDAPIOS_DADOS_ROOT", Path(__file__).resolve().parent.parent))
CONFIG_PATH = ROOT / "config" / "regions.json"
DATA = ROOT / "data"          # committed: caches, frozen ids, last publish
WORK = ROOT / "work"          # ignored: downloads and intermediate files
PUBLIC = ROOT / "public"      # ignored: the GitHub Pages site
REPORTS = ROOT / "reports"    # committed: the latest diff report

BOT_USER_AGENT = "CardapiosBot/1.0 (+https://github.com/DocPocketLtda/cardapios-dados)"

# Columns the app reads (RestaurantParser.swift). Extra columns are ignored by the app.
APP_COLUMNS = ["name", "logo", "address", "latitude", "longitude", "city", "state", "country",
               "available", "phone", "email", "website", "type", "menu_link"]
OPTIONAL_APP_COLUMNS = ["cuisine", "neighborhood", "opening_hours"]
# Informational columns added by the pipeline (the app ignores them).
EXTRA_COLUMNS = ["id_fonte", "fonte", "confianca", "link_status", "link_verificado_em"]

csv.field_size_limit(10_000_000)


def load_config(path=None):
    with open(path or CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def area_config(config, area_id):
    try:
        return config["areas"][area_id]
    except KeyError:
        raise SystemExit(f"Área desconhecida: {area_id}. Opções: {', '.join(config['areas'])}")


# MARK: - CSV

def _open_text(path, mode):
    path = Path(path)
    if path.suffix == ".gz" or path.name.endswith(".gz.tmp"):
        return gzip.open(path, mode + "t", encoding="utf-8", newline="")
    return open(path, mode, encoding="utf-8", newline="")


def read_csv(path):
    path = Path(path)
    if not path.exists():
        return []
    with _open_text(path, "r") as f:
        return list(csv.DictReader(f))


def read_csv_header(path):
    with _open_text(path, "r") as f:
        return next(csv.reader(f), [])


def parse_csv_text(text):
    return list(csv.DictReader(io.StringIO(text)))


def write_csv(path, rows, columns):
    """Atomic write (tmp + rename) so a cancelled job never leaves half a cache."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with _open_text(tmp, "w") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


# MARK: - Text

def fold(text):
    """Lowercase without accents: "São Paulo " -> "sao paulo"."""
    text = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(c for c in text if not unicodedata.combining(c)).strip()


def words(text):
    return re.findall(r"[a-z0-9]+", fold(text))


def is_true(value):
    return (value or "").strip().upper() == "TRUE"


def restaurant_key(name, address):
    """Menu.id in the app: "name|address" (both trimmed, as the app's CSV parser does)."""
    return f"{(name or '').strip()}|{(address or '').strip()}"


# MARK: - URLs

def host_of(url):
    try:
        return (urllib.parse.urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def site_of(url):
    host = host_of(url)
    return host[4:] if host.startswith("www.") else host


def home_of(url):
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/"


# MARK: - Geo and time

def distance_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def to_float(value):
    try:
        return float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def decimals(value):
    """Number of decimal places written in a coordinate ("-23.56" -> 2)."""
    text = str(value or "").strip().replace(",", ".")
    return len(text.split(".", 1)[1]) if "." in text else 0


def in_bbox(lat, lon, bbox):
    return (lat is not None and lon is not None
            and bbox["min_lat"] <= lat <= bbox["max_lat"] and bbox["min_lon"] <= lon <= bbox["max_lon"])


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def today():
    return utc_now().date().isoformat()


def days_between(day_a, day_b):
    """Days from ISO date (or datetime) a to b; None if a is empty."""
    if not day_a:
        return None
    return (dt.date.fromisoformat(day_b[:10]) - dt.date.fromisoformat(day_a[:10])).days


def log(message):
    print(message, flush=True)
