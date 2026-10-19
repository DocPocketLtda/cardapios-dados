"""Addresses and phones in the format the app expects.

`city_from_address` mirrors `AddressParser.city(from:)` in the app's RestaurantParser.swift, so the
pipeline assigns a row to the same city the app will show.
"""

import re

from .common import fold


def city_from_address(address):
    """City in "…, Pinheiros, São Paulo, Estado de São Paulo 05415-040 Brasil" or "… - Consolação, São Paulo - SP, 01415-002"."""
    parts = [p.strip() for p in (address or "").split(",")]
    for index, part in enumerate(parts):
        nxt = parts[index + 1] if index + 1 < len(parts) else ""
        if part.endswith(" - SP") or nxt.startswith("Estado de") or nxt == "SP" or nxt.startswith("SP "):
            name = part[:-5] if part.endswith(" - SP") else part
            if " - " in name:
                name = name.rsplit(" - ", 1)[1]
            name = name.strip()
            if not name or any(c.isdigit() for c in name):
                return None
            return name
    return None


def format_address(freeform, locality, postcode, uf):
    """"Rua X, 123, Campinas - SP, 13010-000": the app's AddressParser finds the city before " - SP"."""
    parts = [(freeform or "").strip().strip(",")]
    if locality:
        parts.append(f"{locality.strip()} - {uf}")
    if postcode and re.fullmatch(r"\d{5}-?\d{3}", postcode.strip()):
        code = re.sub(r"\D", "", postcode)
        parts.append(f"{code[:5]}-{code[5:]}")
    return ", ".join(p for p in parts if p)


def phone_digits(phone):
    """Digits without the country code and leading trunk zero: "+55 (11) 3088-0276" -> "1130880276"."""
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]
    if digits.startswith("0") and len(digits) in (11, 12):
        digits = digits[1:]
    return digits


def format_phone(phone):
    """"+5511930880276" -> "(11) 93088-0276"; anything else is returned as is."""
    digits = phone_digits(phone)
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return (phone or "").strip()


def house_number(address):
    """First house number after the street: "R. Bela Cintra, 2305 - Consolação" -> "2305"."""
    match = re.search(r"(?:,|\bn[º°o]\.?)\s*(\d{1,5})\b", address or "")
    if match:
        return match.group(1)
    # Overture/Foursquare style without the comma: "Rua Tutoia 312 Paraiso, São Paulo" -> "312".
    # A number followed by "de" is part of the street name ("Rua 25 de Março").
    first = (address or "").split(",")[0]
    match = re.search(r"[^\W\d]\.?\s+(\d{1,5})\b(?!\s+de\b)", first)
    return match.group(1) if match else None


STREET_TYPES = {"r", "rua", "av", "avenida", "al", "alameda", "pca", "praca", "tv", "travessa", "rod", "rodovia",
                "estr", "estrada", "lgo", "largo", "dr", "doutor", "prof", "professor", "de", "da", "do", "dos", "das"}


def street_words(address):
    street = fold((address or "").split(",")[0])
    return {w for w in re.findall(r"[a-z0-9]+", street) if w not in STREET_TYPES and not w.isdigit()}
