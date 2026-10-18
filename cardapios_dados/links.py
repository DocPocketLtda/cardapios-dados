"""Menu link recognition, validation and the incremental link cache (data/links-cache.csv).

One check gives an *outcome*; the cache turns outcomes from several days into a *status*:

  outcome        meaning                                         status after it
  ok             2xx/3xx, not parked, not a soft 404              ok
  blocked        401/403/429 or robots.txt disallows (anti-bot)   incerto (never broken)
  dead           404/410                                          falhando -> quebrado after 2 days
  parked         domain parked or for sale                        falhando -> quebrado after 2 days
  soft404        200 but "page not found"/generic platform page   falhando -> quebrado after 2 days
  redirect_home  a store/menu URL redirects to a home page        falhando -> quebrado after 2 days
  conn           DNS, TLS or connection error                     falhando -> quebrado after 2 days
  server         5xx or timeout                                   falhando -> quebrado after 3 days

Failures only count once per calendar day (UTC), so "quebrado" always means failures seen on
different days. Any ok resets the counter.
"""

import hashlib
import html as htmllib
import random
import re
import socket
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque

from .common import BOT_USER_AGENT, days_between, fold, host_of, log, read_csv, site_of, today, utc_now, write_csv

# MARK: - Recognition

# Menu and delivery platforms (report 3.2, item 3), in preference order.
# `store`: regex on host+path that a store page (not the platform's home) must match.
# `generic_titles`: <title> of the platform's "not found"/home page, i.e. a soft 404 on a store URL.
PLATFORMS = [
    ("goomer", r"(^|\.)goomer\.app$", r"goomer\.app/[^/?#]+|^(?!www\.|app\.)[^.]+\.goomer\.app", []),
    ("anota.ai", r"(^|\.)anota\.ai$", r"anota\.ai/(loja|m|c)/[^/?#]+|anota\.ai/[^/?#]{3,}", []),
    ("menudino", r"(^|\.)menudino\.com$", r"^(?!app\.|www\.)[^.]+\.menudino\.com|menudino\.com/[^/?#]+", []),
    ("cardapioweb", r"(^|\.)cardapioweb\.com$", r"cardapioweb\.com/[^/?#]+", ["cardapio web"]),
    ("ifood", r"(^|\.)ifood\.com\.br$", r"ifood\.com\.br/delivery/[^/]+/[^/]+/[0-9a-f-]{20,}", []),
    ("whatsmenu", r"(^|\.)whatsmenu\.com\.br$", r"whatsmenu\.com\.br/[^/?#]+", []),
    ("cardapiodigital", r"(^|\.)(super)?cardapiodigital\.(io|com\.br)$", r"cardapiodigital\.(io|com\.br)/[^?#]+", []),
    ("instadelivery", r"(^|\.)instadelivery\.com\.br$", r"instadelivery\.com\.br/[^/?#]+", []),
    ("pedir.delivery", r"(^|\.)pedir\.delivery$", r"pedir\.delivery/[^?#]+", ["pedir delivery"]),
    ("brendi", r"(^|\.)brendi\.com\.br$", r"brendi\.com\.br/[^/?#]+|^(?!www\.)[^.]+\.brendi\.com\.br", []),
    ("yooga", r"(^|\.)yooga\.app$", r"yooga\.app/[^/?#]+", []),
    ("clicoupizza", r"(^|\.)clicoupizza\.com(\.br)?$", r"clicoupizza\.com(\.br)?/[^/?#]+|^(?!www\.)[^.]+\.clicoupizza", []),
    ("aiqfome", r"(^|\.)aiqfome\.com$", r"aiqfome\.com/[^?#]+", []),
    ("livemenu", r"(^|\.)livemenu\.app$", r"livemenu\.app/[^?#]+", []),
    ("saipos", r"(^|\.)saipos\.com$", r"saipos\.com/[^?#]+|^(?!www\.)[^.]+\.saipos\.com", []),
    ("ola.click", r"(^|\.)ola\.click$", r"ola\.click/[^/?#]+", []),
    ("deliverydireto", r"(^|\.)deliverydireto\.com\.br$", r"deliverydireto\.com\.br/[^?#]+", []),
    ("neemo", r"(^|\.)neemo\.com\.br$", r"neemo\.com\.br/[^?#]+|^(?!www\.)[^.]+\.neemo\.com\.br", []),
    ("dualfood", r"(^|\.)dualfood\.com\.br$", r"^(?!www\.)[^.]+\.dualfood\.com\.br", []),
    ("cocobambu", r"^cardapio\.cocobambu\.com$", r"cardapio\.cocobambu\.com/cardapio/", []),
]
_PLATFORMS = [(name, re.compile(host_re), re.compile(store_re), titles) for name, host_re, store_re, titles in PLATFORMS]

SOCIAL_HOSTS = ("4sq.com", "foursquare.com", "abnb.me", "airbnb.com", "instagram.com", "facebook.com", "fb.com", "fb.me", "wa.me", "whatsapp.com", "api.whatsapp.com",
                "tiktok.com", "twitter.com", "x.com", "youtube.com", "youtu.be", "google.com", "goo.gl",
                "g.page", "maps.app.goo.gl", "tripadvisor.com", "tripadvisor.com.br", "t.me", "threads.net")
LINKTREE_HOSTS = ("linktr.ee", "beacons.ai", "linkr.bio", "bio.link", "linkin.bio", "taplink.cc", "campsite.bio")
SHORTENER_HOSTS = ("bit.ly", "tinyurl.com", "cutt.ly", "abre.ai", "encurtador.com.br", "rebrand.ly", "is.gd")

PARKED_MARKERS = ("domain is for sale", "domínio está à venda", "dominio esta a venda", "this domain may be for sale",
                  "hugedomains", "sedoparking", "parkingcrew", "domain for sale", "registro.br/dominio",
                  "este domínio pode estar à venda", "buy this domain", "comprar este domínio", "dan.com",
                  "afternic", "bodis.com", "domain parking", "parked free", "is parked", "godaddy.com/domains",
                  "este dominio esta disponivel", "domínio registrado e estacionado")
PARKING_HOSTS = ("sedo.com", "sedoparking.com", "hugedomains.com", "dan.com", "afternic.com", "bodis.com",
                 "parkingcrew.net", "above.com", "undeveloped.com", "godaddy.com", "domainmarket.com",
                 "registro.br", "uniregistry.com", "squadhelp.com", "atom.com")
SOFT_404_MARKERS = ("pagina nao encontrada", "page not found", "404 not found", "erro 404", "error 404",
                    "nao encontrada", "not found", "loja nao encontrada", "estabelecimento nao encontrado",
                    "estabelecimento fechado", "restaurante nao encontrado", "esta pagina nao existe",
                    "this page doesn t exist", "pagina inexistente", "conta suspensa", "account suspended",
                    "site em construcao", "site em manutencao", "under construction", "loja indisponivel",
                    "estabelecimento indisponivel")
MENU_WORDS = re.compile(r"card[aá]pio|\bmenu\b|r\$\s?\d|pre[cç]os?\b", re.I)
MENU_LINK_WORDS = re.compile(r"card[aá]pio|\bmenu\b|nosso-menu|\bcarta\b", re.I)
TRIVIAL_PATHS = {"", "/", "/index.html", "/index.htm", "/index.php", "/home", "/inicio", "/pt", "/pt-br", "/br"}


def platform_of(url):
    host = host_of(url)
    for name, host_re, _, _ in _PLATFORMS:
        if host_re.search(host):
            return name
    return None


def is_store_url(url):
    """A platform URL that points at one store (not the platform's home or a search page)."""
    host = host_of(url)
    target = host + urllib.parse.urlsplit(url).path
    for _, host_re, store_re, _ in _PLATFORMS:
        if host_re.search(host):
            return bool(store_re.search(target) or store_re.search(host))
    return False


def _host_in(host, hosts):
    return any(host == h or host.endswith("." + h) for h in hosts)


def link_kind(url):
    """invalido | plataforma | pdf | linktree | encurtador | rede social | site."""
    url = (url or "").strip()
    if not re.match(r"^https?://[^/\s]+\.[^/\s]+", url, re.I):
        return "invalido"
    host = host_of(url)
    if platform_of(url):
        return "plataforma"
    if _host_in(host, LINKTREE_HOSTS):
        return "linktree"
    if _host_in(host, SHORTENER_HOSTS):
        return "encurtador"
    if _host_in(host, SOCIAL_HOSTS):
        return "rede social"
    if urllib.parse.urlsplit(url).path.lower().endswith(".pdf"):
        return "pdf"
    return "site"


def is_platform_or_social(url):
    return link_kind(url) not in ("site", "pdf")


def link_rank(url):
    """Preference order of report 3.2 (lower is better) for choosing among a place's links."""
    kind = link_kind(url)
    if kind == "plataforma":
        return 0 if is_store_url(url) else 5
    if kind == "pdf":
        return 1
    if kind == "site":
        path = urllib.parse.urlsplit(url).path.lower().rstrip("/")
        return 1 if MENU_LINK_WORDS.search(path) else 2
    return {"linktree": 3, "encurtador": 4, "rede social": 6}.get(kind, 9)


def clean_url(url):
    """Trim, drop tracking parameters (fbclid, utm_*) and fragments."""
    url = (url or "").strip()
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return url
    query = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
             if not (k.lower().startswith("utm_") or k.lower() in ("fbclid", "gclid", "igshid", "mc_cid", "mc_eid"))]
    return urllib.parse.urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path,
                                    urllib.parse.urlencode(query), ""))


# MARK: - HTML

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
ANCHOR_RE = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.I | re.S)
HREF_RE = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.I)
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style)\b.*?</\1>", re.I | re.S)


def text_of(fragment):
    return re.sub(r"\s+", " ", htmllib.unescape(TAG_RE.sub(" ", fragment or ""))).strip()


def page_title(html):
    match = TITLE_RE.search(html or "")
    return text_of(match.group(1))[:200] if match else ""


def visible_text(html):
    return text_of(SCRIPT_RE.sub(" ", html or ""))


def is_parked(html):
    lowered = (html or "").lower()
    return any(marker in lowered for marker in PARKED_MARKERS)


def is_soft_404(html, platform=None):
    """Title or <h1> says "not found" (only those: SPA bundles carry such strings in their JS)."""
    heads = [page_title(html)] + [text_of(h) for h in H1_RE.findall(html or "")[:3]]
    folded = [re.sub(r"[^a-z0-9]+", " ", fold(h)).strip() for h in heads if h]
    if any(marker in h for h in folded for marker in SOFT_404_MARKERS):
        return True
    if platform:
        titles = next((t for name, _, _, t in _PLATFORMS if name == platform), [])
        title = folded[0] if folded and heads[0] else ""
        if title and title in titles:
            return True
    return False


def has_menu_words(html):
    return bool(MENU_WORDS.search(visible_text(html)[:200_000]))


def extract_hints(html, base_url):
    """(best platform store link, best menu page/PDF link) found in a page's anchors."""
    platform_links, menu_links = [], []
    base_site = site_of(base_url)
    for attrs, inner in ANCHOR_RE.findall(html or ""):
        href_match = HREF_RE.search(attrs)
        if not href_match:
            continue
        href = htmllib.unescape(href_match.group(1)).strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:", "whatsapp:")):
            continue
        url = clean_url(urllib.parse.urljoin(base_url, href))
        if not url.startswith(("http://", "https://")):
            continue
        if platform_of(url) and is_store_url(url):
            platform_links.append(url)
            continue
        label = text_of(inner)
        path = urllib.parse.urlsplit(url).path.lower()
        same_site = site_of(url) == base_site
        if path.endswith(".pdf") and (MENU_LINK_WORDS.search(path) or MENU_LINK_WORDS.search(label)):
            menu_links.append((0, url))
        elif same_site and MENU_LINK_WORDS.search(path) and path.rstrip("/") not in TRIVIAL_PATHS:
            menu_links.append((1, url))
        elif same_site and MENU_LINK_WORDS.search(label) and path.rstrip("/") not in TRIVIAL_PATHS:
            menu_links.append((2, url))
    if not platform_links and link_kind(base_url) == "linktree":
        # Link-in-bio pages (Next.js) keep their links in JSON as well as in anchors.
        for raw in re.findall(r"https?://[^\s\"'<>\\]+", (html or "").replace("\\/", "/")):
            url = clean_url(raw)
            if platform_of(url) and is_store_url(url):
                platform_links.append(url)
    platform_links.sort(key=lambda u: next(i for i, (n, *_) in enumerate(PLATFORMS) if n == platform_of(u)))
    menu_links.sort(key=lambda item: item[0])
    return (platform_links[0] if platform_links else ""), (menu_links[0][1] if menu_links else "")


# MARK: - Fetching

class Robots:
    """robots.txt with Google semantics (longest match wins, `*` and `$` wildcards), which the
    standard library's robotparser lacks (goomer.app uses "Allow: /$")."""

    def __init__(self, text, agent="cardapiosbot"):
        groups, current, rules_started = [], None, False
        for raw in (text or "").splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            field, value = (part.strip() for part in line.split(":", 1))
            field = field.lower()
            if field == "user-agent":
                if current is None or rules_started:
                    current, rules_started = {"agents": [], "rules": []}, False
                    groups.append(current)
                current["agents"].append(value.lower())
            elif field in ("allow", "disallow") and current is not None:
                rules_started = True
                if value or field == "allow":
                    current["rules"].append((field == "allow", value))
        specific = [g for g in groups if any(a != "*" and a in agent for a in g["agents"])]
        chosen = specific or [g for g in groups if "*" in g["agents"]]
        self.rules = [rule for g in chosen for rule in g["rules"]]

    @staticmethod
    def _pattern(path):
        anchored = path.endswith("$")
        body = re.escape(path[:-1] if anchored else path).replace(r"\*", ".*")
        return re.compile(body + ("$" if anchored else ""))

    def can_fetch(self, url):
        parts = urllib.parse.urlsplit(url)
        target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        best = None
        for allow, path in self.rules:
            if path and self._pattern(path).match(target):
                length = len(path)
                if best is None or length > best[0] or (length == best[0] and allow):
                    best = (length, allow)
        return True if best is None else best[1]


class FetchResult:
    __slots__ = ("status", "final_url", "content_type", "body", "error")

    def __init__(self, status=None, final_url="", content_type="", body="", error=""):
        self.status, self.final_url, self.content_type, self.body, self.error = (
            status, final_url, content_type, body, error)


SECOND_LEVEL = {"com", "net", "org", "gov", "edu", "art", "blog", "eco", "emp", "ind", "inf", "app", "co"}


def limit_key(host):
    """Registrable domain, so "a.placeweb.site" and "b.placeweb.site" share one rate limit."""
    labels = host.split(".")
    if len(labels) >= 3 and labels[-2] in SECOND_LEVEL and len(labels[-1]) == 2:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


class HostLimiter:
    """At most one request per host every `interval` seconds (per-host overrides for big platforms)."""

    def __init__(self, interval=2.0, overrides=None):
        self.interval = interval
        self.overrides = overrides or {}
        self.next_time = defaultdict(float)
        self.locks = defaultdict(threading.Lock)
        self.guard = threading.Lock()

    def wait(self, host):
        host = limit_key(host)
        with self.guard:
            lock = self.locks[host]
        with lock:
            delay = self.next_time[host] - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            interval = next((v for k, v in self.overrides.items() if host == k or host.endswith("." + k)),
                            self.interval)
            self.next_time[host] = time.monotonic() + interval


MAX_BYTES = 300_000


class Fetcher:
    def __init__(self, timeout=12.0, limiter=None, respect_robots=True):
        self.timeout = timeout
        self.limiter = limiter or HostLimiter()
        self.respect_robots = respect_robots
        self.robots = {}
        self.robots_lock = threading.Lock()
        self.probes = {}
        self.ssl_context = ssl.create_default_context()

    def _request(self, url, method="GET"):
        self.limiter.wait(host_of(url))
        request = urllib.request.Request(url, method=method, headers={
            "User-Agent": BOT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9",
        })
        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                content_type = response.headers.get("Content-Type", "")
                body = b""
                if method == "GET" and "pdf" not in content_type.lower():
                    body = response.read(MAX_BYTES)
                charset = response.headers.get_content_charset() or "utf-8"
                return FetchResult(response.status, response.geturl(), content_type,
                                   body.decode(charset, errors="ignore"))
        except urllib.error.HTTPError as error:
            body = ""
            try:
                body = error.read(50_000).decode("utf-8", errors="ignore")
            except Exception:
                pass
            return FetchResult(error.code, error.geturl() or url, error.headers.get("Content-Type", "") if error.headers else "", body)
        except (socket.timeout, TimeoutError):
            return FetchResult(error="timeout")
        except urllib.error.URLError as error:
            reason = error.reason
            if isinstance(reason, (socket.timeout, TimeoutError)):
                return FetchResult(error="timeout")
            return FetchResult(error=f"conn:{type(reason).__name__}")
        except (ssl.SSLError, ConnectionError, OSError) as error:
            return FetchResult(error=f"conn:{type(error).__name__}")
        except Exception as error:  # malformed URLs, odd servers
            return FetchResult(error=f"conn:{type(error).__name__}")

    def allowed(self, url):
        if not self.respect_robots:
            return True
        parts = urllib.parse.urlsplit(url)
        root = f"{parts.scheme}://{parts.netloc}"
        with self.robots_lock:
            if root not in self.robots:
                self.robots[root] = threading.Event()
                owner = True
            else:
                owner = False
            entry = self.robots[root]
        if owner:
            result = self._request(root + "/robots.txt")
            if result.status == 200 and result.body and "<html" not in result.body[:500].lower():
                entry.parser = Robots(result.body)
            else:
                entry.parser = None  # no robots.txt (or an HTML page): everything allowed
            entry.set()
        else:
            entry.wait(self.timeout * 2)
        parser = getattr(entry, "parser", None)
        return parser is None or parser.can_fetch(url)

    def get(self, url):
        if urllib.parse.urlsplit(url).path.lower().endswith(".pdf"):
            head = self._request(url, method="HEAD")
            if head.status and head.status < 400:
                return head
        return self._request(url)

    def random_probe(self, url):
        """The same host's answer for a path that can't exist, cached per host (soft-404 baseline)."""
        root = urllib.parse.urljoin(url, "/")
        if root not in self.probes:
            token = hashlib.sha1(f"{root}{random.random()}".encode()).hexdigest()[:12]
            self.probes[root] = self._request(urllib.parse.urljoin(root, f"/cardapios-bot-{token}"))
        return self.probes[root]


def classify(url, result, probe=None):
    """Outcome of one fetch (see the module docstring)."""
    if result.error:
        return "server" if result.error == "timeout" else "conn"
    status = result.status or 0
    platform = platform_of(url)
    if status in (401, 403, 429, 451):
        return "blocked"
    if status in (404, 410):
        return "dead"
    if status >= 500:
        return "server"
    if status >= 400:
        return "dead"
    final = result.final_url or url
    final_host = host_of(final)
    if _host_in(final_host, PARKING_HOSTS) and not _host_in(host_of(url), PARKING_HOSTS):
        return "parked"
    if "pdf" in (result.content_type or "").lower():
        return "ok"
    if is_parked(result.body):
        return "parked"
    if is_soft_404(result.body, platform):
        return "soft404"
    original_path = urllib.parse.urlsplit(url).path.rstrip("/").lower()
    final_parts = urllib.parse.urlsplit(final)
    if original_path not in TRIVIAL_PATHS and final_parts.path.rstrip("/").lower() in TRIVIAL_PATHS \
            and not final_parts.query and (platform is None or not is_store_url(final)):
        return "redirect_home"
    if platform and is_store_url(url) and not is_store_url(final) and platform_of(final) == platform:
        return "redirect_home"
    if probe is not None and probe.status == 200 and not platform and original_path not in TRIVIAL_PATHS \
            and page_title(result.body):
        same_title = page_title(probe.body) == page_title(result.body)
        sizes = len(probe.body), len(result.body)
        if same_title and max(sizes) and abs(sizes[0] - sizes[1]) / max(sizes) < 0.05:
            return "soft404"
    return "ok"


def check_url(fetcher, url):
    """(outcome, http_status, final_url, has_menu, title, hint_platform, hint_menu, error)."""
    if link_kind(url) == "invalido":
        return dict(outcome="dead", http_status="", final_url=url, has_menu="", title="", hint_platform="",
                    hint_menu="", error="url invalida")
    if not fetcher.allowed(url):
        return dict(outcome="blocked", http_status="", final_url=url, has_menu="", title="", hint_platform="",
                    hint_menu="", error="robots.txt")
    result = fetcher.get(url)
    probe = None
    kind = link_kind(url)
    if (result.status == 200 and kind == "site"
            and urllib.parse.urlsplit(url).path.rstrip("/").lower() not in TRIVIAL_PATHS):
        probe = fetcher.random_probe(result.final_url or url)
    outcome = classify(url, result, probe)
    hint_platform = hint_menu = ""
    has_menu = ""
    if outcome == "ok" and result.body:
        hint_platform, hint_menu = extract_hints(result.body, result.final_url or url)
        has_menu = "1" if (has_menu_words(result.body) or kind == "plataforma") else "0"
    elif outcome == "ok":
        has_menu = "1" if "pdf" in (result.content_type or "").lower() or kind == "plataforma" else ""
    return dict(outcome=outcome, http_status=str(result.status or ""), final_url=result.final_url or url,
                has_menu=has_menu, title=page_title(result.body)[:120], hint_platform=hint_platform,
                hint_menu=hint_menu, error=result.error)


# MARK: - Cache

CACHE_COLUMNS = ["url", "kind", "platform", "priority", "status", "outcome", "http_status", "final_url",
                 "fail_days", "last_fail_day", "first_checked_at", "checked_at", "last_ok_at", "has_menu",
                 "title", "hint_platform", "hint_menu", "error"]
FAIL_THRESHOLD = {"dead": 2, "parked": 2, "soft404": 2, "redirect_home": 2, "conn": 2, "server": 3}
RECHECK_DAYS = {"ok": 30, "incerto": 7, "falhando": 1, "quebrado": 30}
PRIORITY = {"planilha": 0, "reparo": 1, "overture": 2, "osm": 2}


class LinkCache:
    def __init__(self, path):
        self.path = path
        self.entries = {row["url"]: row for row in read_csv(path)}
        self.lock = threading.Lock()

    def get(self, url):
        return self.entries.get(url)

    def status(self, url):
        entry = self.entries.get(url)
        return entry["status"] if entry else ""

    def register(self, url, origin):
        """Adds a URL to check (status empty = pending); keeps the best priority seen."""
        if link_kind(url) == "invalido":
            return
        priority = PRIORITY.get(origin, 2)
        entry = self.entries.get(url)
        if entry is None:
            self.entries[url] = {c: "" for c in CACHE_COLUMNS} | {
                "url": url, "kind": link_kind(url), "platform": platform_of(url) or "", "priority": str(priority)}
        elif int(entry.get("priority") or 9) > priority:
            entry["priority"] = str(priority)

    def due(self, day=None, only_priority=None):
        """URLs to check today, most urgent first: failing (to confirm on a new day), new, then stale."""
        day = day or today()
        due = []
        for url, entry in self.entries.items():
            if only_priority is not None and int(entry.get("priority") or 9) != only_priority:
                continue
            status = entry["status"]
            if entry["kind"] in ("rede social",):
                continue  # social networks need login: not validated, never broken
            age = days_between(entry["checked_at"], day)
            if not status:
                rank = 1
            elif age is not None and age >= RECHECK_DAYS.get(status, 30):
                rank = 0 if status == "falhando" else 2
            else:
                continue
            # Hash instead of URL as the tie-breaker: a --limit sample (or a time budget) spreads over
            # many domains instead of 300 subdomains of one host in alphabetical order.
            spread = hashlib.md5(url.encode()).hexdigest()
            due.append((rank, int(entry.get("priority") or 9), -(age or 0), spread, url))
        due.sort()
        return [url for *_, url in due]

    def apply(self, url, result, now=None):
        now = now or utc_now()
        day = now.date().isoformat()
        stamp = now.isoformat().replace("+00:00", "Z")
        with self.lock:
            entry = self.entries.setdefault(url, {c: "" for c in CACHE_COLUMNS} | {
                "url": url, "kind": link_kind(url), "platform": platform_of(url) or "", "priority": "2"})
            update_entry(entry, result, day, stamp)


def update_entry(entry, result, day, stamp):
    outcome = result["outcome"]
    for field in ("outcome", "http_status", "final_url", "title", "error"):
        entry[field] = result.get(field, "")
    entry["checked_at"] = stamp
    entry["first_checked_at"] = entry.get("first_checked_at") or stamp
    if outcome == "ok":
        entry["status"] = "ok"
        entry["fail_days"] = "0"
        entry["last_ok_at"] = stamp
        entry["has_menu"] = result.get("has_menu", "")
        entry["hint_platform"] = result.get("hint_platform", "")
        entry["hint_menu"] = result.get("hint_menu", "")
    elif outcome == "blocked":
        entry["status"] = "incerto"
    else:
        fail_days = int(entry.get("fail_days") or 0)
        if entry.get("last_fail_day") != day:
            fail_days += 1
            entry["last_fail_day"] = day
        entry["fail_days"] = str(fail_days)
        entry["status"] = "quebrado" if fail_days >= FAIL_THRESHOLD.get(outcome, 2) else "falhando"
    return entry


def save_cache(cache):
    rows = sorted(cache.entries.values(), key=lambda r: r["url"])
    write_csv(cache.path, rows, CACHE_COLUMNS)


def interleave_by_host(urls):
    """Round-robin over hosts so parallel workers rarely wait on the same host's rate limit."""
    queues = defaultdict(deque)
    order = []
    for url in urls:
        host = limit_key(host_of(url))
        if host not in queues:
            order.append(host)
        queues[host].append(url)
    result = []
    while order:
        remaining = []
        for host in order:
            result.append(queues[host].popleft())
            if queues[host]:
                remaining.append(host)
        order = remaining
    return result


def run_checks(cache, urls, workers=24, timeout=12.0, budget_seconds=None, host_interval=2.0,
               host_overrides=None, save_every=300, respect_robots=True):
    """Checks `urls` in parallel and updates the cache. Returns {outcome: count}."""
    fetcher = Fetcher(timeout=timeout, limiter=HostLimiter(host_interval, host_overrides),
                      respect_robots=respect_robots)
    queue = deque(interleave_by_host(urls))
    deadline = time.monotonic() + budget_seconds if budget_seconds else None
    counts = defaultdict(int)
    done = [0]
    queue_lock = threading.Lock()

    def worker():
        while True:
            with queue_lock:
                if not queue or (deadline and time.monotonic() > deadline):
                    return
                url = queue.popleft()
            try:
                result = check_url(fetcher, url)
            except Exception as error:  # never let one odd URL kill the run
                result = dict(outcome="conn", http_status="", final_url=url, error=f"conn:{type(error).__name__}")
            cache.apply(url, result)
            with queue_lock:
                counts[result["outcome"]] += 1
                done[0] += 1
                if done[0] % save_every == 0:
                    with cache.lock:
                        save_cache(cache)
                    log(f"  {done[0]}/{len(urls)} verificados {dict(counts)}")

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(max(1, workers))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    save_cache(cache)
    if queue:
        log(f"  orçamento de tempo esgotado: {len(queue)} URLs ficam para a próxima execução")
    return dict(counts)


def is_publishable(entry, require_validated):
    """Can a row with this link be published?

    require_validated=False (sheet rows): everything except confirmed-broken links.
    require_validated=True (new places): link ok, still ok recently, or an anti-bot 403 on a
    platform store URL (iFood answers 403 to every bot).
    """
    if entry is None:
        return not require_validated
    status = entry["status"]
    if not require_validated:
        return status != "quebrado"
    if status == "ok":
        return True
    if status == "falhando" and entry.get("last_ok_at"):
        return True
    if status == "incerto" and is_store_url(entry["url"]):
        return True
    return False
