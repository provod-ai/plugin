import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_plugin import ENDPOINT, check


class PackagingAndSecurityTests(unittest.TestCase):
    def test_all_json_configs_and_manifests_validate(self):
        self.assertEqual(check(ROOT), [])

    def test_git_archive_is_cold_start_valid_and_private_free(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "plugin.tar.gz"
            extract = Path(tmp) / "extract"
            subprocess.run(["git", "archive", "--format=tar.gz", f"--output={archive}", "HEAD"], cwd=ROOT, check=True)
            with tarfile.open(archive, "r:gz") as handle:
                names = handle.getnames()
                self.assertFalse(any(part in {".env", ".env.local", "credentials", "secrets"} for name in names for part in Path(name).parts))
                handle.extractall(extract)
            self.assertEqual(check(extract), [])
            self.assertTrue((extract / "plugin.json").is_file())
            self.assertTrue((extract / ".codex-plugin/plugin.json").is_file())
            self.assertTrue((extract / "plugins/provod/.claude-plugin/plugin.json").is_file())
            self.assertTrue((extract / "plugins/provod/.mcp.json").is_file())

    def test_mcp_and_oauth_configs_are_consistent(self):
        mcp = json.loads((ROOT / "mcp.json").read_text())
        oauth = json.loads((ROOT / "oauth.json").read_text())
        self.assertEqual(mcp["mcpServers"]["provod"]["url"], ENDPOINT)
        self.assertEqual(oauth["authentication"], "ON_INSTALL")
        self.assertNotIn("client_secret", oauth)


if __name__ == "__main__":
    unittest.main()
