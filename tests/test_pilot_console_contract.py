import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSOLE = ROOT / "pilot_console"


class ConsoleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.scripts = []
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"])
        if tag == "link" and values.get("rel") == "stylesheet":
            self.stylesheets.append(values.get("href"))


class PilotConsoleContractTests(unittest.TestCase):
    def test_console_has_required_workflow_controls(self):
        parser = ConsoleParser()
        parser.feed((CONSOLE / "index.html").read_text(encoding="utf-8"))
        required = {
            "connection-form",
            "api-url",
            "api-key",
            "metrics-grid",
            "queue-list",
            "decision-detail",
            "review-form",
            "reviewer-id",
            "download-metrics",
            "evidence-package-form",
            "evidence-decision-id",
            "evidence-event-limit",
            "generate-evidence-package",
            "download-evidence-json",
            "download-evidence-markdown",
        }
        self.assertTrue(required.issubset(parser.ids))
        self.assertEqual(parser.scripts, ["app.js?v=1"])
        self.assertEqual(parser.stylesheets, ["styles.css?v=1"])

    def test_console_avoids_secret_persistence_and_html_injection_apis(self):
        source = (CONSOLE / "app.js").read_text(encoding="utf-8")
        for forbidden in ("localStorage", "sessionStorage", "document.cookie", "innerHTML"):
            self.assertNotIn(forbidden, source)
        self.assertIn("redirect: 'error'", source)
        self.assertIn("crypto.randomUUID()", source)

    def test_console_has_no_third_party_runtime_assets(self):
        parser = ConsoleParser()
        parser.feed((CONSOLE / "index.html").read_text(encoding="utf-8"))
        for asset in parser.scripts + parser.stylesheets:
            self.assertNotIn("://", asset)
