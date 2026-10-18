"""The Google Sheet: manual layer that wins over every automatic source."""

import os
import time
import urllib.request

from .common import WORK, log, parse_csv_text

REQUIRED = {"name", "address", "available", "menu_link"}


def fetch_sheet(url, dest=None, attempts=3):
    """Downloads the sheet's CSV export to work/sheet.csv. An HTML answer (login/error page) is a failure."""
    url = os.environ.get("SHEET_CSV_URL") or url
    dest = dest or WORK / "sheet.csv"
    last_error = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "cardapios-dados/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
            text = data.decode("utf-8-sig")
            if text.lstrip().startswith("<"):
                raise ValueError("a planilha respondeu HTML, não CSV (está pública?)")
            rows = parse_csv_text(text)
            missing = REQUIRED - set(rows[0].keys() if rows else [])
            if missing:
                raise ValueError(f"colunas ausentes na planilha: {sorted(missing)}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
            available = sum(1 for r in rows if (r.get("available") or "").strip().upper() == "TRUE")
            log(f"Planilha: {len(rows)} linhas, {available} disponíveis -> {dest}")
            return rows
        except Exception as error:
            last_error = error
            log(f"  tentativa {attempt + 1}: {error}")
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"Não foi possível baixar a planilha: {last_error}")
