"""Deduplication: does a source record (Overture, later OSM) describe a restaurant already in the sheet?

Blocking: a grid of ~1.1 km cells (0.01°) and a radius that depends on how precise the sheet's
coordinates are (many sheet rows have only 2 decimals, ~1 km). Inside the radius a pair matches
when the names are similar (Jaro-Winkler or token-set) and, unless the points are very close, there
is a second signal: same phone, same own-site domain or same house number on the same street.
"""

import math
import re
from collections import defaultdict
from difflib import SequenceMatcher

from .address import house_number, phone_digits, street_words
from .common import decimals, distance_km, fold, site_of

NAME_NOISE = {"restaurante", "restaurant", "rest", "ltda", "me", "eireli", "epp", "sa", "cia", "e", "&", "o", "a",
              "the", "de", "da", "do", "dos", "das", "unidade", "loja", "filial"}
# Phones shared by many branches (call centers) say nothing about a single place.
SHARED_PHONE_PREFIXES = ("0800", "0300", "4003", "4004", "4020", "3003", "4002")

COARSE_RADIUS_KM = 1.2     # sheet point with <= 2 decimals (rounding error up to ~0.8 km)
COARSE_CLOSE_KM = 0.8
PRECISE_RADIUS_KM = 0.3
PRECISE_CLOSE_KM = 0.15
# Sheet points with 4+ decimals still come from geocoders that miss by a few hundred meters: with a
# strong signal (phone, own site or house number) a pair up to this far apart is the same place.
STRONG_RADIUS_KM = 0.6
PHONE_ONLY_KM = 0.08


def name_tokens(name):
    text = fold(name)
    text = re.sub(r"[^a-z0-9& ]+", " ", text)
    return [t for t in text.split() if t not in NAME_NOISE]


def name_variants(name):
    """Full name and the part before a branch suffix: "Corrientes 348 - Bela Cintra" -> also "Corrientes 348"."""
    variants = {" ".join(name_tokens(name))}
    for separator in (" - ", " | ", " – ", "("):
        if separator in (name or ""):
            base = " ".join(name_tokens(name.split(separator)[0]))
            if base:
                variants.add(base)
    return {v for v in variants if v}


def jaro_winkler(a, b):
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    window = max(max(len(a), len(b)) // 2 - 1, 0)
    a_flags, b_flags = [False] * len(a), [False] * len(b)
    matches = 0
    for i, ch in enumerate(a):
        for j in range(max(0, i - window), min(i + window + 1, len(b))):
            if not b_flags[j] and b[j] == ch:
                a_flags[i] = b_flags[j] = True
                matches += 1
                break
    if not matches:
        return 0.0
    transpositions, k = 0, 0
    for i, flagged in enumerate(a_flags):
        if flagged:
            while not b_flags[k]:
                k += 1
            transpositions += a[i] != b[k]
            k += 1
    m = matches
    jaro = (m / len(a) + m / len(b) + (m - transpositions / 2) / m) / 3
    prefix = 0
    for x, y in zip(a[:4], b[:4]):
        if x != y:
            break
        prefix += 1
    return jaro + prefix * 0.1 * (1 - jaro)


def _ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


def token_set_ratio(a, b):
    """fuzzywuzzy-style token set ratio; 0 when the shared part is too short to mean anything."""
    ta, tb = set(a.split()), set(b.split())
    inter = " ".join(sorted(ta & tb))
    if len(inter.replace(" ", "")) < 4:
        return 0.0
    rest_a = " ".join(sorted(ta - tb))
    rest_b = " ".join(sorted(tb - ta))
    t1 = (inter + " " + rest_a).strip()
    t2 = (inter + " " + rest_b).strip()
    return max(_ratio(inter, t1), _ratio(inter, t2), _ratio(t1, t2))


def name_similarity(name_a, name_b):
    best = 0.0
    for a in name_variants(name_a):
        for b in name_variants(name_b):
            best = max(best, jaro_winkler(a, b), token_set_ratio(a, b))
    return best


def names_match(name_a, name_b):
    best_jw = best_ts = 0.0
    for a in name_variants(name_a):
        for b in name_variants(name_b):
            best_jw = max(best_jw, jaro_winkler(a, b))
            best_ts = max(best_ts, token_set_ratio(a, b))
    return best_jw >= 0.88 or best_ts >= 0.8


def phone_key(phone):
    raw = re.sub(r"\D", "", phone or "")
    raw = raw[2:] if raw.startswith("55") and len(raw) >= 12 else raw
    digits = phone_digits(phone)
    if len(digits) < 10 or raw.startswith(SHARED_PHONE_PREFIXES) or len(set(digits[2:])) == 1:
        return None
    return digits[-8:] if len(digits) >= 8 else None


def same_street_number(address_a, address_b):
    number_a, number_b = house_number(address_a), house_number(address_b)
    if not number_a or number_a != number_b:
        return False
    words_a, words_b = street_words(address_a), street_words(address_b)
    return bool(words_a and words_b) and len(words_a & words_b) / min(len(words_a), len(words_b)) >= 0.5


class Place:
    """What the matcher needs from either side."""

    __slots__ = ("ref", "name", "address", "lat", "lon", "phones", "domains", "coarse")

    def __init__(self, ref, name, address, lat, lon, phones=(), domains=(), coarse=None):
        self.ref = ref
        self.name = name or ""
        self.address = address or ""
        self.lat, self.lon = lat, lon
        self.phones = {p for p in (phone_key(x) for x in phones) if p}
        self.domains = {d for d in domains if d}
        self.coarse = coarse if coarse is not None else False


def coarse_coordinate(lat_text, lon_text):
    return min(decimals(lat_text), decimals(lon_text)) <= 2


class GridIndex:
    CELL = 0.01  # degrees (~1.1 km)

    def __init__(self, places):
        self.cells = defaultdict(list)
        for place in places:
            if place.lat is not None and place.lon is not None:
                self.cells[self._cell(place.lat, place.lon)].append(place)

    def _cell(self, lat, lon):
        return math.floor(lat / self.CELL), math.floor(lon / self.CELL)

    def near(self, lat, lon, radius_km):
        steps = int(math.ceil(radius_km / 1.1)) + 1
        ci, cj = self._cell(lat, lon)
        for di in range(-steps, steps + 1):
            for dj in range(-steps, steps + 1):
                for place in self.cells.get((ci + di, cj + dj), ()):
                    d = distance_km(lat, lon, place.lat, place.lon)
                    if d <= radius_km:
                        yield place, d


def evaluate(anchor, candidate, distance, shared_domains=frozenset()):
    """Score of `candidate` describing the same place as `anchor` (a sheet place), or None."""
    phone_eq = bool(anchor.phones & candidate.phones)
    domain_eq = bool((anchor.domains & candidate.domains) - shared_domains)
    number_eq = same_street_number(anchor.address, candidate.address)
    strong = phone_eq or domain_eq or number_eq
    similarity = name_similarity(anchor.name, candidate.name)
    name_ok = names_match(anchor.name, candidate.name)
    if anchor.coarse:
        ok = name_ok and (strong or distance <= COARSE_CLOSE_KM)
        radius = COARSE_RADIUS_KM
    else:
        ok = (name_ok and ((strong and distance <= STRONG_RADIUS_KM) or distance <= PRECISE_CLOSE_KM)) \
            or (phone_eq and distance <= PHONE_ONLY_KM)
        radius = STRONG_RADIUS_KM
    if not ok:
        return None
    score = similarity + (0.5 if strong else 0.0) + 0.3 * max(0.0, 1 - distance / radius)
    return score, strong


def match_places(anchors, candidates, shared_domains=frozenset(), pinned=None):
    """Assign candidates (source records) to anchors (sheet restaurants).

    Returns {candidate.ref: (anchor.ref, score, primary, strong)}. Every candidate goes to its best anchor.
    The best candidate of an anchor is its primary (used for enrichment); further candidates are
    absorbed as duplicates only with a strong signal, so two branches of a chain near a coarse
    sheet point don't collapse into one. `pinned` ({candidate.ref: anchor.ref}) comes from ids.csv
    and wins over scoring.
    """
    pinned = pinned or {}
    anchor_by_ref = {a.ref: a for a in anchors}
    index = GridIndex(anchors)
    best = {}
    for candidate in candidates:
        if candidate.ref in pinned and pinned[candidate.ref] in anchor_by_ref:
            best[candidate.ref] = (pinned[candidate.ref], 99.0, True)  # pinned counts as strong
            continue
        if candidate.lat is None:
            continue
        found = None
        for anchor, distance in index.near(candidate.lat, candidate.lon, COARSE_RADIUS_KM):
            if not anchor.coarse and distance > STRONG_RADIUS_KM:
                continue
            result = evaluate(anchor, candidate, distance, shared_domains)
            if result and (found is None or result[0] > found[1]):
                found = (anchor.ref, result[0], result[1])
        if found:
            best[candidate.ref] = found
    by_anchor = defaultdict(list)
    for ref, (anchor_ref, score, strong) in best.items():
        by_anchor[anchor_ref].append((score, ref, strong))
    result = {}
    for anchor_ref, items in by_anchor.items():
        items.sort(reverse=True)
        for position, (score, ref, strong) in enumerate(items):
            if position == 0:
                result[ref] = (anchor_ref, score, True, strong)
            elif strong or score >= 99:
                result[ref] = (anchor_ref, score, False, strong)
    return result


def dedupe_sources(records, radius_km=0.08):
    """Within one source: same normalized name within ~80 m -> keep the first (callers sort by confidence)."""
    kept, seen = [], GridIndex([])
    for record in records:
        duplicate = False
        if record.lat is not None:
            for other, _ in seen.near(record.lat, record.lon, radius_km):
                if name_variants(other.name) & name_variants(record.name):
                    duplicate = True
                    break
        if not duplicate:
            kept.append(record)
            if record.lat is not None:
                seen.cells[seen._cell(record.lat, record.lon)].append(record)
    return kept


def own_domain(url, platform_or_social):
    """Domain of a restaurant's own site, or None for platforms and social networks."""
    if not url or platform_or_social(url):
        return None
    return site_of(url) or None
