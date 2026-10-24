"""Real-engine browser regressions. Run after building ts and playground/dist."""
import functools
import importlib.util
import json
import pathlib
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load("playground_builder", ROOT / "playground/build_static.py")
backend = load("playground_server", ROOT / "playground/server.py")
QUERIES = [item["query"] for item in backend.SCENARIOS]
FIELDS = ("query", "terms", "floor", "scored", "grounded", "hits",
          "messages", "stable_prefix", "answer", "corpus_size")


class QuietStatic(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class PlaygroundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servers = [
            ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(
                QuietStatic, directory=str(ROOT / "playground/dist"))),
            ThreadingHTTPServer(("127.0.0.1", 0), backend.Handler),
        ]
        for server in cls.servers:
            threading.Thread(target=server.serve_forever, daemon=True).start()
        cls.urls = [f"http://127.0.0.1:{s.server_port}" for s in cls.servers]
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        for server in cls.servers:
            server.shutdown()
            server.server_close()

    def page(self, width=1280):
        context = self.browser.new_context(
            viewport={"width": width, "height": 900}, reduced_motion="reduce")
        self.addCleanup(context.close)
        page = context.new_page()
        page.set_default_timeout(5000)
        return page

    def ready(self, page, url):
        page.goto(url)
        page.locator("#result:not([hidden])").wait_for()
        self.assertEqual(page.locator("#decision").inner_text(), "Working set returned")

    def test_build_is_offline_deterministic_and_slot_is_fail_closed(self):
        builder.build()
        first = (ROOT / "playground/dist/index.html").read_bytes()
        builder.build()
        self.assertEqual(first, (ROOT / "playground/dist/index.html").read_bytes())
        html = first.decode()
        self.assertNotIn("/api/", html)
        self.assertNotIn("fetch(", html)
        self.assertNotIn(str(ROOT), html)
        self.assertIn((ROOT / "ts/dist/index.js").read_text().strip(), html)
        for template in ("no slots", builder.UI + builder.UI, builder.END + builder.START):
            with self.assertRaises(ValueError):
                builder.replace_adapter(template, "adapter")
        encoded = builder.script_json({"title": "</script><img onerror=alert(1)>"})
        self.assertNotIn("</script>", encoded)
        self.assertEqual(json.loads(encoded)["title"], "</script><img onerror=alert(1)>")

    def test_static_file_works_offline_and_query_is_inert(self):
        page = self.page()
        requests = []
        page.on("request", lambda request: requests.append(request.url))
        self.ready(page, (ROOT / "playground/dist/index.html").as_uri())
        hostile = '<img src=x onerror="window.INJECTED=true">'
        page.get_by_role("textbox", name="Your question").fill(hostile)
        page.get_by_role("textbox", name="Your question").press("Enter")
        page.wait_for_function(
            "q => document.querySelector('#result-query').textContent === q", arg=hostile)
        self.assertEqual(page.locator("#decision").inner_text(), "No working set")
        self.assertFalse(page.evaluate("Boolean(window.INJECTED)"))
        self.assertEqual(page.locator("main img").count(), 0)
        self.assertTrue(all(url.startswith("file:") for url in requests), requests)

    def test_static_adapter_matches_real_python_all_scenarios(self):
        page = self.page()
        self.ready(page, self.urls[0])
        info = page.evaluate("({version: __GW.version, size: __GW.corpus_size})")
        self.assertEqual(info, {"version": backend.gw_pkg.__version__, "size": 24})
        for query in QUERIES:
            actual = page.evaluate("q => __GW.analyze(q)", query)
            expected = backend.analyze(query)
            self.assertEqual({k: actual[k] for k in FIELDS},
                             {k: expected[k] for k in FIELDS})
        refund, abstain, mismatch = [
            page.evaluate("q => __GW.analyze(q)", q) for q in QUERIES[:3]]
        self.assertEqual((refund["answer"]["source"], refund["hits"][0]["score"]),
                         ("returns", 3.8605))
        self.assertFalse(abstain["grounded"])
        self.assertTrue(mismatch["grounded"])
        self.assertEqual((mismatch["answer"]["source"], mismatch["hits"][0]["score"]),
                         ("pause", 2.9429))

    def test_both_adapters_desktop_mobile_controls_and_scenarios(self):
        for url in self.urls:
            for width in (1280, 390):
                with self.subTest(url=url, width=width):
                    page = self.page(width)
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    self.ready(page, url)
                    self.assertIn("unopened bag", page.locator("#source-body").inner_text())
                    self.assertIn("No LLM is called", page.locator("main").inner_text())
                    self.assertFalse(page.locator("#raw").evaluate("el => el.open"))
                    self.assertEqual(page.get_by_role("link", name="Walkthrough").get_attribute("href"),
                                     "./walkthrough/")
                    self.assertLess(page.locator("#query").bounding_box()["y"], 400)
                    for label, query in zip(
                            ("Refund policy", "Out of scope", "Keyword mismatch",
                             "Multiple terms", "Product lookup"), QUERIES):
                        page.get_by_role("button", name=label, exact=True).click()
                        page.wait_for_function(
                            "q => !document.querySelector('#result').hidden && "
                            "document.querySelector('#result-query').textContent === q", arg=query)
                        expected = backend.analyze(query)
                        self.assertEqual(page.locator("#scored li").count(), len(expected["scored"]))
                        self.assertEqual(page.locator(".hit-score").all_inner_texts(),
                                         [f"{hit['score']:.4f}" for hit in expected["scored"]])
                        actual = json.loads(page.locator("#metadata").text_content())
                        self.assertEqual({k: actual[k] for k in FIELDS},
                                         {k: expected[k] for k in FIELDS})
                        if expected["hits"]:
                            self.assertEqual(page.locator("#source-body").inner_text(),
                                             expected["hits"][0]["body"])
                            maximum = max(expected["floor"], *(
                                hit["score"] for hit in expected["scored"]))
                            for marker in page.locator(".floor-marker").all():
                                percent = marker.evaluate("el => parseFloat(el.style.left)")
                                self.assertAlmostEqual(percent, expected["floor"] / maximum * 100,
                                                       places=4)
                        self.assertEqual(page.locator("#query").input_value(), query)
                        self.assertEqual(page.get_by_role("button", name=label, exact=True)
                                         .get_attribute("aria-pressed"), "true")
                        if label == "Keyword mismatch":
                            self.assertIn("wrong source", page.locator("#scenario-note").inner_text())
                            self.assertIn("pause", page.locator("#source-id").inner_text())
                            self.assertIn("2.9429", page.locator("#scored").inner_text())
                        if label == "Out of scope":
                            self.assertEqual(page.locator("#decision").inner_text(), "No working set")
                            self.assertTrue(page.locator("#source").is_hidden())
                    page.get_by_role("textbox", name="Your question").fill("How do I get a refund?")
                    page.get_by_role("textbox", name="Your question").press("Enter")
                    page.wait_for_function(
                        "() => document.querySelector('#source-id').textContent === 'returns'")
                    self.assertEqual(page.evaluate(
                        "document.documentElement.scrollWidth > innerWidth"), False)
                    for box in page.locator("button:visible, a:visible, summary:visible, input:visible").all():
                        self.assertGreaterEqual(box.bounding_box()["height"], 44)
                    page.locator("#query").focus()
                    page.keyboard.press("Tab")
                    self.assertEqual(page.evaluate("document.activeElement.id"), "run")
                    self.assertTrue(page.locator("#run").evaluate("el => el.matches(':focus-visible')"))
                    self.assertEqual(page.locator("#run").evaluate(
                        "el => getComputedStyle(el).outlineStyle"), "solid")
                    self.assertEqual(errors, [])
                    page.close()

    def test_hostile_query_and_backend_documents_stay_text(self):
        page = self.page(390)
        self.ready(page, self.urls[1])
        hostile = '<img src=x onerror="window.INJECTED=true">'
        payload = backend.analyze(QUERIES[0])
        payload["query"] = hostile
        payload["terms"] = [hostile]
        payload["hits"][0].update(title=hostile, body=hostile, id=hostile)
        payload["scored"][0].update(title=hostile, id=hostile)
        payload["messages"][0]["content"] = hostile
        payload["stable_prefix"] = hostile
        payload["answer"]["answer"] = hostile
        payload["answer"]["source"] = hostile
        page.route("**/api/ask", lambda route: route.fulfill(json=payload))
        page.get_by_role("textbox", name="Your question").fill(hostile)
        page.get_by_role("button", name="Run query", exact=True).click()
        page.wait_for_function("() => document.querySelector('#source-body').textContent.includes('<img')")
        self.assertEqual(page.locator("#source-body").inner_text(), hostile)
        self.assertEqual(page.locator("main img, main script").count(), 0)
        self.assertFalse(page.evaluate("Boolean(window.INJECTED)"))
        page.locator("#raw summary").click()
        self.assertEqual(json.loads(page.locator("#messages").inner_text())[0]["content"], hostile)
        self.assertEqual(page.locator("#stable-prefix").inner_text(), hostile)
        self.assertEqual(json.loads(page.locator("#metadata").inner_text())["answer"]["answer"], hostile)
        self.assertFalse(page.evaluate("document.documentElement.scrollWidth > innerWidth"))

    def test_user_runs_have_visible_receipts_and_reveal_results(self):
        for width in (1280, 390):
            page = self.page(width)
            self.ready(page, self.urls[0])
            first = page.locator("#status").inner_text()
            page.get_by_role("button", name="Run query", exact=True).click()
            page.wait_for_function("() => document.querySelector('#status').textContent.includes('Run 2 complete')")
            self.assertNotEqual(page.locator("#status").inner_text(), first)
            self.assertGreater(page.locator("#status").bounding_box()["height"], 20)
            self.assertIn("Run 2", page.locator("#run-receipt").text_content())
            self.assertEqual(page.evaluate("document.activeElement.id"), "result")
            if width == 390:
                self.assertLess(page.locator("#result").bounding_box()["y"], 150)
            page.get_by_role("textbox", name="Your question").fill("What is the capital of France?")
            page.get_by_role("textbox", name="Your question").press("Enter")
            page.wait_for_function("() => document.querySelector('#status').textContent.includes('Run 3 complete')")
            self.assertIn("No documents selected", page.locator("#status").inner_text())
            self.assertEqual(page.locator("#decision").inner_text(), "No working set")
            page.close()

    def test_walkthrough_is_a_prominent_invitation(self):
        page = self.page(390)
        self.ready(page, self.urls[0])
        link = page.get_by_role("link", name="Walkthrough", exact=True)
        self.assertIn("Watch", link.inner_text())
        self.assertIn("30", link.inner_text())
        self.assertGreaterEqual(link.bounding_box()["height"], 44)
        self.assertNotEqual(link.evaluate("el => getComputedStyle(el).backgroundColor"), "rgba(0, 0, 0, 0)")
        self.assertEqual(link.locator("svg").count(), 1)

    def test_bootstrap_and_query_failures_are_visible_and_recoverable(self):
        page = self.page()
        page.route("**/api/version", lambda route: route.fulfill(status=503, body="unavailable"))
        page.goto(self.urls[1])
        page.get_by_role("alert").wait_for()
        self.assertIn("503", page.get_by_role("alert").inner_text())
        self.assertTrue(page.get_by_role("button", name="Retry connection").is_visible())
        page.unroute("**/api/version")
        page.get_by_role("button", name="Retry connection").click()
        page.locator("#result:not([hidden])").wait_for()
        page.route("**/api/ask", lambda route: route.fulfill(
            status=500, json={"error": "deliberate test failure"}))
        page.get_by_role("button", name="Run query", exact=True).click()
        page.get_by_role("alert").wait_for()
        self.assertIn("deliberate test failure", page.get_by_role("alert").inner_text())
        self.assertTrue(page.locator("#result").is_hidden())
        self.assertTrue(page.get_by_role("button", name="Run query", exact=True).is_enabled())

    def test_missing_static_engine_does_not_load_forever(self):
        page = self.page()
        page.route(self.urls[0] + "/", lambda route: route.fulfill(
            content_type="text/html", body=builder.replace_adapter(
                (ROOT / "playground/index.html").read_text(), "")))
        page.goto(self.urls[0])
        page.get_by_role("alert").wait_for(timeout=12000)
        self.assertIn("did not start", page.get_by_role("alert").inner_text())
        self.assertTrue(page.get_by_role("button", name="Retry connection").is_visible())


if __name__ == "__main__":
    unittest.main()
