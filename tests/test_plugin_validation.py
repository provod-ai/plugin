import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from validate_plugin import ENDPOINT, PLACEHOLDER, check


class PluginValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in ("README.md", "LICENSE", "SECURITY.md", ".codex-plugin/plugin.json",
                    ".claude-plugin/marketplace.json", "plugins/provod/.claude-plugin/plugin.json"):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text("public\n", encoding="utf-8")
        self.write_json(".codex-plugin/plugin.json", {"mcp": {"transport": "streamable_http", "url": ENDPOINT, "auth": "oauth", "install": "on_install", "client_id": PLACEHOLDER}})
        self.write_json(".claude-plugin/marketplace.json", {"plugins": [{"source": "./plugins/provod"}]})
        self.write_json("plugins/provod/.claude-plugin/plugin.json", {"mcp": {"type": "streamable_http", "url": ENDPOINT, "auth": {"type": "oauth", "install": "on_install", "client_id": PLACEHOLDER}}})

    def tearDown(self):
        self.tmp.cleanup()

    def write_json(self, rel, value):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_valid_dual_layout(self):
        self.assertEqual(check(self.root), [])

    def test_rejects_wrong_endpoint(self):
        value = json.loads((self.root / ".codex-plugin/plugin.json").read_text())
        value["mcp"]["url"] = "https://example.invalid/mcp"
        self.write_json(".codex-plugin/plugin.json", value)
        self.assertTrue(any("url" in error for error in check(self.root)))

    def test_rejects_credentials_and_private_paths(self):
        (self.root / ".env").write_text("TOKEN=secret", encoding="utf-8")
        self.assertTrue(any("private credential-like path" in error for error in check(self.root)))


if __name__ == "__main__":
    unittest.main()
