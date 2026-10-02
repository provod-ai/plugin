import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).parents[1]


class RepositoryContractTests(unittest.TestCase):
    def load_json(self, relative):
        path = ROOT / relative
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_required_public_files_exist(self):
        for relative in (
            "README.md",
            "LICENSE",
            "SECURITY.md",
            ".codex-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            "plugins/provod/.claude-plugin/plugin.json",
            ".github/workflows/validate.yml",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_codex_manifest_uses_hosted_oauth(self):
        manifest = self.load_json(".codex-plugin/plugin.json")
        server = manifest["mcp"]
        self.assertEqual(server["transport"], "streamable_http")
        self.assertEqual(server["url"], "https://api.provod.ai/mcp")
        self.assertEqual(server["auth"], "oauth")
        self.assertEqual(server["install"], "on_install")
        self.assertTrue(server["client_id"].startswith("REPLACE_WITH_"))

    def test_claude_manifest_uses_same_endpoint(self):
        manifest = self.load_json("plugins/provod/.claude-plugin/plugin.json")
        self.assertEqual(manifest["mcp"]["url"], "https://api.provod.ai/mcp")
        self.assertEqual(manifest["mcp"]["type"], "streamable_http")
        self.assertEqual(manifest["mcp"]["auth"]["type"], "oauth")
        self.assertEqual(manifest["mcp"]["auth"]["install"], "on_install")

    def test_public_files_contain_no_obvious_secrets(self):
        secret_terms = ("-" * 5 + "BEGIN RSA PRIVATE KEY" + "-" * 5, "gh" + "p_", "AK" + "IA")
        for path in ROOT.rglob("*"):
            if (
                path.is_file()
                and ".git" not in path.parts
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
                and path.parent.name not in {"tests", "scripts"}
            ):
                text = path.read_text(encoding="utf-8", errors="ignore")
                for term in secret_terms:
                    self.assertNotIn(term, text, str(path))


if __name__ == "__main__":
    unittest.main()
