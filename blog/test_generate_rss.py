"""Regression checks for the static RSS generator."""
import pathlib
import sys
import tempfile
import unittest
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import generate_rss


CONTENT = {"content": generate_rss.CONTENT_NS, "media": generate_rss.MEDIA_NS}


class RssGenerationTests(unittest.TestCase):
    def test_generated_feed_has_full_content_and_stable_post_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = pathlib.Path(tmpdir) / "rss.xml"
            generate_rss.generate_rss(output)
            first = ET.parse(output).getroot()
            generate_rss.generate_rss(output)
            second = ET.parse(output).getroot()

        self.assertEqual(first.tag, "rss")
        self.assertEqual(first.attrib["version"], "2.0")
        first_items = first.findall("./channel/item")
        second_items = second.findall("./channel/item")
        self.assertTrue(first_items)
        self.assertTrue(first.findtext("./channel/lastBuildDate").endswith("+0900"))
        self.assertEqual(
            [item.findtext("guid") for item in first_items],
            [item.findtext("guid") for item in second_items],
        )
        for item in first_items:
            self.assertEqual(item.findtext("guid"), item.findtext("link"))
            self.assertIsNotNone(parsedate_to_datetime(item.findtext("pubDate")))
            self.assertTrue(item.findtext("pubDate").endswith("+0900"))
            self.assertTrue(item.findtext("description"))
            self.assertIn("<p>", item.findtext("content:encoded", namespaces=CONTENT))

        spherical_harmonics = next(
            item for item in first_items if item.findtext("title") == "Waves on a Sphere, Spherical Harmonics"
        )
        cover = spherical_harmonics.find("media:content", namespaces=CONTENT)
        self.assertIsNotNone(cover)
        self.assertEqual(cover.attrib["medium"], "image")
        self.assertEqual(cover.attrib["url"], "https://wityworks.com/static/img/blog/spherical-harmonics-cover.png")

    def test_portable_html_absolutizes_urls_and_removes_active_content(self):
        rendered = generate_rss.markdown_to_html(
            '![diagram](/images/diagram.png) [post](/blog/other) <script>alert(1)</script>',
            "https://example.test",
            "https://example.test/blog/?post=notes/example",
        )
        self.assertIn('src="https://example.test/images/diagram.png"', rendered)
        self.assertIn('href="https://example.test/blog/other"', rendered)
        self.assertNotIn("script", rendered)


if __name__ == "__main__":
    unittest.main()
