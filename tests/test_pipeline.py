"""Unit tests (standard library unittest): python -m unittest discover -s tests"""

import tempfile
import unittest
from pathlib import Path

from cardapios_dados.address import city_from_address, format_address, format_phone, house_number
from cardapios_dados.common import fold, restaurant_key
from cardapios_dados.cuisine import classify_name, cuisine_column
from cardapios_dados.links import (FetchResult, LinkCache, Robots, classify, extract_hints, interleave_by_host,
                                   is_publishable, is_store_url, link_kind, link_rank, update_entry)
from cardapios_dados.match import (Place, dedupe_sources, jaro_winkler, match_places, name_similarity, names_match,
                                   phone_key, token_set_ratio)
from cardapios_dados.publish import coverage_cells, file_for, guard, region_entry, robust_bbox

CONFIG = {"publish": {"max_row_loss": 0.2, "min_rows_for_guard": 50}}


class NormalizationTests(unittest.TestCase):
    def test_fold(self):
        self.assertEqual(fold(" São Paulo "), "sao paulo")
        self.assertEqual(fold("Açaí"), "acai")

    def test_key_is_trimmed_like_the_app(self):
        self.assertEqual(restaurant_key(" Bar ", "Rua X, 1 "), "Bar|Rua X, 1")

    def test_city_like_app_address_parser(self):
        self.assertEqual(city_from_address("R. Bela Cintra, 2305 - Consolação, São Paulo - SP, 01415-002"), "São Paulo")
        self.assertEqual(city_from_address("Rua Doutor Mário Ferraz , 32, Jardim Europa, São Paulo, SP, Brasil"),
                         "São Paulo")
        self.assertEqual(city_from_address("Av. Brasil 10, Campinas, Estado de São Paulo 13010-000 Brasil"), "Campinas")
        self.assertIsNone(city_from_address("Rua sem cidade 10"))

    def test_generated_address_round_trips_to_city(self):
        address = format_address("Av. Odorindo Perenha, 1500", "Araçatuba", "16013230", "SP")
        self.assertEqual(address, "Av. Odorindo Perenha, 1500, Araçatuba - SP, 16013-230")
        self.assertEqual(city_from_address(address), "Araçatuba")

    def test_phone(self):
        self.assertEqual(format_phone("+5518988205616"), "(18) 98820-5616")
        self.assertEqual(format_phone("+551831177010"), "(18) 3117-7010")
        self.assertEqual(phone_key("(11) 3088-0276"), phone_key("+55 11 3088 0276"))
        self.assertIsNone(phone_key("0800 123 4567"))

    def test_house_number(self):
        self.assertEqual(house_number("R. Bela Cintra, 2305 - Consolação"), "2305")

    def test_cuisine_only_when_name_says_nothing(self):
        self.assertEqual(classify_name("Burger King"), "Hamburgueria")
        self.assertEqual(cuisine_column("Pizzaria Bella", "brazilian_restaurant"), "")
        self.assertEqual(cuisine_column("Casa Zezé", "japanese_restaurant"), "Japonesa")
        self.assertEqual(cuisine_column("Casa Zezé", "restaurant"), "")


class MatchingTests(unittest.TestCase):
    def test_similarity(self):
        self.assertGreater(jaro_winkler("martha", "marhta"), 0.95)
        self.assertGreaterEqual(token_set_ratio("bella pizzaria", "pizzaria bella"), 0.99)
        self.assertEqual(token_set_ratio("bar", "bar do ze"), 0.0)  # too short to mean anything
        self.assertTrue(names_match("Corrientes 348 - Bela Cintra", "Corrientes 348"))
        self.assertTrue(names_match("Restaurante Família Mancini", "Família Mancini"))
        self.assertFalse(names_match("Família Mancini", "Bráz Pizzaria"))
        self.assertGreater(name_similarity("Mocotó", "Mocoto Restaurante"), 0.95)

    def test_coarse_sheet_point_matches_with_strong_signal(self):
        sheet = Place("Mocotó|Av. Nossa Sra. do Loreto, 1100", "Mocotó", "Av. Nossa Sra. do Loreto, 1100 - Vila Medeiros",
                      -23.49, -46.58, phones=["(11) 2951-3056"], coarse=True)
        far_same_name = Place("ovt:1", "Mocotó Restaurante", "Av. Nossa Senhora do Loreto, 1100", -23.4952, -46.5871,
                              phones=["+551129513056"])
        other = Place("ovt:2", "Padaria Real", "Rua A, 5", -23.4901, -46.5801)
        result = match_places([sheet], [far_same_name, other])
        self.assertEqual(result["ovt:1"][0], sheet.ref)
        self.assertTrue(result["ovt:1"][2])
        self.assertNotIn("ovt:2", result)

    def test_second_branch_of_a_chain_is_not_absorbed(self):
        sheet = Place("Madero Itaim|Rua X, 10", "Madero Itaim", "Rua X, 10", -23.58, -46.68, coarse=True)
        branch_a = Place("ovt:a", "Madero", "Rua X, 10", -23.5801, -46.6799)
        branch_b = Place("ovt:b", "Madero", "Rua Y, 999", -23.5830, -46.6830)
        result = match_places([sheet], [branch_a, branch_b])
        self.assertIn("ovt:a", result)
        self.assertNotIn("ovt:b", result)  # left as a new place

    def test_precise_point_needs_proximity(self):
        sheet = Place("Bar|Rua Z, 1", "Bar Brahma", "Rua Z, 1", -23.5440, -46.6420, coarse=False)
        near = Place("ovt:n", "Bar Brahma", "Av. São João, 677", -23.5445, -46.6425)
        far = Place("ovt:f", "Bar Brahma", "Rua W, 9", -23.5600, -46.6600)
        result = match_places([sheet], [near, far])
        self.assertIn("ovt:n", result)
        self.assertNotIn("ovt:f", result)

    def test_pinned_ids_win(self):
        sheet = Place("A|B", "Nome antigo", "B", -23.5, -46.6, coarse=True)
        renamed = Place("ovt:x", "Nome totalmente novo", "C", -23.6, -46.7)
        result = match_places([sheet], [renamed], pinned={"ovt:x": "A|B"})
        self.assertEqual(result["ovt:x"][0], "A|B")

    def test_internal_dedupe(self):
        a = Place("ovt:1", "Café Girondino", "", -23.5450, -46.6340)
        b = Place("ovt:2", "Cafe Girondino", "", -23.5451, -46.6341)
        c = Place("ovt:3", "Café Girondino", "", -23.5600, -46.6340)
        self.assertEqual([p.ref for p in dedupe_sources([a, b, c])], ["ovt:1", "ovt:3"])


def result(status, url, body="", final=None, content_type="text/html", error=""):
    return FetchResult(status, final or url, content_type, body, error)


class LinkClassificationTests(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(link_kind("https://www.instagram.com/x"), "rede social")
        self.assertEqual(link_kind("https://linktr.ee/x"), "linktree")
        self.assertEqual(link_kind("https://app.cardapioweb.com/loja"), "plataforma")
        self.assertEqual(link_kind("https://site.com.br/cardapio.pdf"), "pdf")
        self.assertEqual(link_kind("https://site.com.br/"), "site")
        self.assertEqual(link_kind("site.com.br"), "invalido")

    def test_store_urls(self):
        self.assertTrue(is_store_url("https://www.ifood.com.br/delivery/sao-paulo-sp/x-centro/31763335-3ce8-4041-95d4-9df4b15bd163"))
        self.assertFalse(is_store_url("https://www.ifood.com.br/"))
        self.assertTrue(is_store_url("https://pedido.anota.ai/loja/pizza-shopping-1"))
        self.assertTrue(is_store_url("https://imperio.menudino.com/"))
        self.assertFalse(is_store_url("https://app.menudino.com/"))

    def test_preference(self):
        links = ["https://www.instagram.com/x", "https://x.com.br/", "https://www.goomer.app/x"]
        self.assertEqual(min(links, key=link_rank), "https://www.goomer.app/x")
        self.assertLess(link_rank("https://x.com.br/cardapio"), link_rank("https://x.com.br/"))

    def test_outcomes(self):
        url = "https://restaurante.com.br/cardapio"
        self.assertEqual(classify(url, result(200, url, "<title>Cardápio</title> R$ 30")), "ok")
        self.assertEqual(classify(url, result(404, url)), "dead")
        self.assertEqual(classify(url, result(403, url)), "blocked")
        self.assertEqual(classify(url, result(429, url)), "blocked")
        self.assertEqual(classify(url, result(503, url)), "server")
        self.assertEqual(classify(url, result(None, url, error="timeout")), "server")
        self.assertEqual(classify(url, result(None, url, error="conn:gaierror")), "conn")
        self.assertEqual(classify(url, result(200, url, "<p>This domain is for sale</p>")), "parked")
        self.assertEqual(classify(url, result(200, url, final="https://www.hugedomains.com/x")), "parked")
        self.assertEqual(classify(url, result(200, url, "<title>Página não encontrada</title>")), "soft404")
        self.assertEqual(classify(url, result(200, url, "<title>Home</title>", final="https://restaurante.com.br/")),
                         "redirect_home")
        self.assertEqual(classify("https://restaurante.com.br", result(200, "https://restaurante.com.br",
                                                                      final="https://www.restaurante.com.br/")), "ok")

    def test_platform_soft_404_and_redirect(self):
        store = "https://app.cardapioweb.com/nao_existe"
        self.assertEqual(classify(store, result(200, store, "<title>Cardápio Web</title>")), "soft404")
        self.assertEqual(classify(store, result(200, store, "<title>Pizzaria Fiamme</title>")), "ok")
        goomer = "https://www.goomer.app/loja-x"
        self.assertEqual(classify(goomer, result(200, goomer, final="https://www.goomer.app/")), "redirect_home")

    def test_random_path_probe(self):
        url = "https://restaurante.com.br/menu"
        page = "<title>Restaurante</title>" + "x" * 1000
        probe = result(200, "https://restaurante.com.br/cardapios-bot-1", page)
        self.assertEqual(classify(url, result(200, url, page), probe), "soft404")
        self.assertEqual(classify(url, result(200, url, "<title>Menu</title>" + "y" * 5000), probe), "ok")

    def test_hints(self):
        html = """<a href="/sobre">Sobre</a><a href="/nosso-cardapio">Ver</a>
                  <a href="https://pedido.anota.ai/loja/casa-x?utm_source=site">Peça já</a>
                  <a href="/files/menu.pdf">Cardápio PDF</a>"""
        platform, menu = extract_hints(html, "https://casa.com.br/")
        self.assertEqual(platform, "https://pedido.anota.ai/loja/casa-x")
        self.assertEqual(menu, "https://casa.com.br/files/menu.pdf")

    def test_linktree_json_links(self):
        html = '{"links":[{"url":"https:\\/\\/app.cardapioweb.com\\/casa_x"}]}'
        platform, _ = extract_hints(html, "https://linktr.ee/casax")
        self.assertEqual(platform, "https://app.cardapioweb.com/casa_x")

    def test_robots_google_semantics(self):
        goomer = Robots("user-agent: *\nAllow: /$\nDisallow: /\n")
        self.assertTrue(goomer.can_fetch("https://loja.goomer.app/"))
        self.assertFalse(goomer.can_fetch("https://loja.goomer.app/x"))
        specific = Robots("User-agent: *\nDisallow: /\n\nUser-agent: CardapiosBot\nDisallow:\n")
        self.assertTrue(specific.can_fetch("https://a.com/cardapio"))

    def test_interleave(self):
        urls = ["https://a.com/1", "https://a.com/2", "https://b.com/1", "https://a.com/3"]
        self.assertEqual(interleave_by_host(urls)[:2], ["https://a.com/1", "https://b.com/1"])


class CacheStateTests(unittest.TestCase):
    def entry(self):
        return {"url": "https://x.com.br/", "status": "", "fail_days": "", "last_fail_day": "", "last_ok_at": "",
                "first_checked_at": "", "checked_at": "", "kind": "site"}

    def test_broken_only_after_failures_on_different_days(self):
        e = self.entry()
        update_entry(e, {"outcome": "dead"}, "2026-10-01", "2026-10-01T10:00:00Z")
        self.assertEqual(e["status"], "falhando")
        update_entry(e, {"outcome": "dead"}, "2026-10-01", "2026-10-01T18:00:00Z")  # same day: no count
        self.assertEqual((e["status"], e["fail_days"]), ("falhando", "1"))
        update_entry(e, {"outcome": "conn"}, "2026-10-02", "2026-10-02T10:00:00Z")
        self.assertEqual(e["status"], "quebrado")

    def test_server_errors_need_three_days_and_ok_resets(self):
        e = self.entry()
        for day in ("2026-10-01", "2026-10-02"):
            update_entry(e, {"outcome": "server"}, day, day + "T00:00:00Z")
        self.assertEqual(e["status"], "falhando")
        update_entry(e, {"outcome": "ok"}, "2026-10-03", "2026-10-03T00:00:00Z")
        self.assertEqual((e["status"], e["fail_days"]), ("ok", "0"))

    def test_blocked_is_uncertain_never_broken(self):
        e = self.entry()
        for day in ("2026-10-01", "2026-10-02", "2026-10-03"):
            update_entry(e, {"outcome": "blocked"}, day, day + "T00:00:00Z")
        self.assertEqual(e["status"], "incerto")

    def test_publishable(self):
        self.assertTrue(is_publishable(None, require_validated=False))
        self.assertFalse(is_publishable(None, require_validated=True))
        ifood = {"url": "https://www.ifood.com.br/delivery/sp/x/31763335-3ce8-4041-95d4-9df4b15bd163", "status": "incerto"}
        self.assertTrue(is_publishable(ifood, True))
        self.assertFalse(is_publishable({"url": "https://x.com/", "status": "incerto"}, True))
        self.assertFalse(is_publishable({"url": "https://x.com/", "status": "quebrado"}, False))
        self.assertTrue(is_publishable({"url": "https://x.com/", "status": "falhando", "last_ok_at": "2026"}, True))

    def test_due_order_and_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = LinkCache(Path(tmp) / "cache.csv")
            cache.register("https://novo.com.br/", "overture")
            cache.register("https://planilha.com.br/", "planilha")
            cache.register("https://www.instagram.com/x", "overture")
            self.assertEqual(cache.due("2026-10-01"), ["https://planilha.com.br/", "https://novo.com.br/"])
            cache.entries["https://novo.com.br/"].update(status="ok", checked_at="2026-09-01T00:00:00Z")
            self.assertEqual(cache.due("2026-09-15"), ["https://planilha.com.br/"])
            self.assertIn("https://novo.com.br/", cache.due("2026-10-05"))


class PublishTests(unittest.TestCase):
    def test_regression_guard(self):
        previous = {"sp/grande-sp": {"rows": 2478}, "sp/tiny": {"rows": 10}}
        ok = [{"id": "sp/grande-sp", "rows": 2100}, {"id": "sp/tiny", "rows": 1}]
        self.assertEqual(guard(ok, previous, CONFIG), [])
        bad = [{"id": "sp/grande-sp", "rows": 1900}, {"id": "sp/tiny", "rows": 1}]
        self.assertEqual(guard(bad, previous, CONFIG), [("sp/grande-sp", 2478, 1900)])
        self.assertEqual(guard([], {"sp/capital": {"rows": 100}}, CONFIG), [("sp/capital", 100, 0)])

    def test_region_by_municipality(self):
        files = [{"id": "sp/grande-sp", "only_sheet": True}, {"id": "sp/capital", "municipalities": ["São Paulo"]},
                 {"id": "sp/campinas", "municipalities": ["Campinas", "Santa Bárbara d'Oeste"]},
                 {"id": "sp/interior", "default": True}]
        self.assertEqual(file_for({"_municipality": "Sao Paulo"}, files)["id"], "sp/capital")
        self.assertEqual(file_for({"_municipality": "Santa Barbara d'Oeste"}, files)["id"], "sp/campinas")
        self.assertEqual(file_for({"_municipality": "Bauru"}, files)["id"], "sp/interior")
        self.assertEqual(file_for({"_municipality": ""}, files)["id"], "sp/interior")

    def test_coverage_cells_and_robust_bbox(self):
        points = [(-23.55, -46.63), (-23.56, -46.64), (-22.91, -47.06)] * 40 + [(0.9, -52.0)]
        self.assertEqual(coverage_cells(points[:3]), ["-236,-467", "-230,-471"])
        box = robust_bbox(points)
        self.assertEqual((box["max_lat"], box["min_lon"]), (-22.91, -47.06))
        self.assertIsNone(robust_bbox([]))

    def test_region_entry_for_the_app(self):
        spec = {"id": "sp/capital", "name": "São Paulo (capital)", "phase": 1, "app_default": True}
        rows = [{"name": "A", "address": "Rua 1", "latitude": "-23.55", "longitude": "-46.63"}]
        entry = region_entry(spec, "sp-estado", rows, b"x", "https://h", {})
        self.assertTrue(entry["app_default"])
        self.assertEqual(entry["cells"], ["-236,-467"])
        self.assertEqual(entry["url"], "https://h/sp/capital.csv")


if __name__ == "__main__":
    unittest.main()
