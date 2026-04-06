import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORMAT_PATH = REPO_ROOT / "scripts" / "format.py"
PUBLISH_PATH = REPO_ROOT / "scripts" / "publish.py"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "sample_article.md"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FormatSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.format_mod = load_module("wechat_format_test", FORMAT_PATH)
        cls.publish_mod = load_module("wechat_publish_test", PUBLISH_PATH)
        cls.fixture_text = FIXTURE_PATH.read_text(encoding="utf-8")

    def test_non_minimal_theme_rejects_variant_args(self):
        with self.assertRaises(ValueError):
            self.format_mod.build_style_selection("newspaper", accent="blue")

    def test_default_output_dir_is_article_sibling_wechat_output(self):
        output_dir = self.format_mod.resolve_output_dir(FIXTURE_PATH, None)
        self.assertEqual(output_dir, FIXTURE_PATH.parent / "wechat output")

    def test_minimal_variant_theme_application(self):
        base_theme = self.format_mod.load_theme(self.format_mod.MINIMAL_FLEX_THEME_ID)
        selection = self.format_mod.build_style_selection(
            self.format_mod.MINIMAL_FLEX_THEME_ID,
            accent="blue",
            heading_align="center",
            divider_style="solid-short",
        )
        final_theme = self.format_mod.apply_theme_variants(
            self.format_mod.MINIMAL_FLEX_THEME_ID,
            base_theme,
            selection,
        )

        self.assertEqual(
            final_theme["styles"]["h1"]["color"],
            self.format_mod.MINIMAL_FLEX_ACCENTS["blue"]["hex"],
        )
        self.assertEqual(final_theme["styles"]["h5"]["text_align"], "center")
        self.assertEqual(final_theme["styles"]["h2"]["text_align"], "center")
        self.assertEqual(final_theme["styles"]["hr"]["width"], "72px")

    def test_format_output_contains_variant_styles(self):
        base_theme = self.format_mod.load_theme(self.format_mod.MINIMAL_FLEX_THEME_ID)
        selection = self.format_mod.build_style_selection(
            self.format_mod.MINIMAL_FLEX_THEME_ID,
            accent="green",
            heading_align="center",
            divider_style="solid-short",
        )
        final_theme = self.format_mod.apply_theme_variants(
            self.format_mod.MINIMAL_FLEX_THEME_ID,
            base_theme,
            selection,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.format_mod.format_for_output(
                self.fixture_text,
                FIXTURE_PATH,
                final_theme,
                Path(tmpdir),
                REPO_ROOT,
                "wechat",
            )

        self.assertIn(self.format_mod.MINIMAL_FLEX_ACCENTS["green"]["hex"], result["html"])
        self.assertIn("text-align:center", result["html"])
        self.assertIn("width:72px", result["html"])

    def test_selection_files_keep_backward_compatibility(self):
        selection = self.format_mod.build_style_selection(
            self.format_mod.MINIMAL_FLEX_THEME_ID,
            accent="red",
            heading_align="right",
            divider_style="none",
            font_size=16,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            self.format_mod.write_selected_style(selection, out_dir)
            style_path = out_dir / "selected-style.json"
            theme_path = out_dir / "selected-theme.txt"

            self.assertTrue(style_path.exists())
            self.assertTrue(theme_path.exists())

            payload = json.loads(style_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["theme_id"], self.format_mod.MINIMAL_FLEX_THEME_ID)
            self.assertEqual(payload["accent"], "red")
            self.assertEqual(theme_path.read_text(encoding="utf-8").strip(), self.format_mod.MINIMAL_FLEX_THEME_ID)

    def test_publish_can_read_structured_selection(self):
        payload = {
            "theme_id": self.format_mod.MINIMAL_FLEX_THEME_ID,
            "accent": "gray",
            "heading_align": "left",
            "divider_style": "solid-full",
            "font_size": 15,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "selected-style.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            loaded = self.publish_mod.load_selected_style(path)

        self.assertEqual(loaded["theme_id"], self.format_mod.MINIMAL_FLEX_THEME_ID)
        self.assertEqual(loaded["accent"], "gray")

    def test_templates_are_assistant_neutral(self):
        gallery_html = (REPO_ROOT / "templates" / "gallery.html").read_text(encoding="utf-8")
        preview_html = (REPO_ROOT / "templates" / "preview.html").read_text(encoding="utf-8")
        self.assertNotIn("Claude", gallery_html)
        self.assertNotIn("Claude", preview_html)


if __name__ == "__main__":
    unittest.main()
