import pathlib
import unittest


ROOT = pathlib.Path(__file__).parents[1]


class WidgetContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "assets/index.html").read_text(encoding="utf-8")

    def test_media_actions_do_not_send_signed_download_urls(self):
        self.assertIn("resource_link", self.html)
        self.assertIn("resultResourceUri", self.html)
        self.assertNotIn("Use this Provod result in the current conversation: ${resultUrl}", self.html)
        self.assertNotIn("prompt:text+resultUrl", self.html)

    def test_library_uses_server_pagination_and_type_filter(self):
        self.assertIn("next_cursor", self.html)
        self.assertIn("cursor:libraryCursor", self.html)
        self.assertIn("type:libraryFilter", self.html)
        self.assertIn("id=\"load-more\"", self.html)

    def test_video_detection_does_not_require_a_file_extension(self):
        self.assertIn("t.startsWith('video/')", self.html)
        self.assertIn("el= document.createElement", self.html.replace("el=document", "el= document"))


if __name__ == "__main__":
    unittest.main()
