import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import _hosted_fragments
from android2harmony.pipeline import _discover_routes
from android2harmony.model import AndroidModule


class HostedFragmentsTest(unittest.TestCase):
    def test_maps_class_name_to_page_name_reversed(self):
        # Activity code references class `HomeFragment`; the generated page is `FragmentHome`
        # (named after layout fragment_home). Must resolve to the page name, in source order.
        src = """
            mFragments.add(new HomeFragment());
            mFragments.add(new VideoFragment());
            mFragments.add(new MineFragment());
        """
        pages = {"FragmentHome", "FragmentVideo", "FragmentMine", "MainActivity"}
        self.assertEqual(
            _hosted_fragments(src, pages, "MainActivity"),
            ["FragmentHome", "FragmentVideo", "FragmentMine"],
        )

    def test_direct_class_name_match(self):
        src = "getSupportFragmentManager().beginTransaction().replace(R.id.c, new SettingsFragment()).commit();"
        self.assertEqual(_hosted_fragments(src, {"SettingsFragment"}, "X"), ["SettingsFragment"])

    def test_ignores_unknown_and_self(self):
        src = "new HomeFragment(); new GhostFragment();"
        self.assertEqual(_hosted_fragments(src, {"FragmentHome", "FragmentHost"}, "FragmentHost"), ["FragmentHome"])


class DiscoverRoutesNonStandardDirTest(unittest.TestCase):
    def test_fragment_in_custom_resource_dir_becomes_route(self):
        # layouts under a custom resource root (res/home/layout) must still become pages,
        # else the content fragments behind an Activity shell are never generated (TouTiao case)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "src" / "main" / "res" / "home" / "layout"
            d.mkdir(parents=True)
            (d / "fragment_home.xml").write_text("<x/>", encoding="utf-8")
            (d / "fragment_video.xml").write_text("<x/>", encoding="utf-8")
            (d / "include_fragment_content.xml").write_text("<x/>", encoding="utf-8")  # include -> skipped
            module = AndroidModule(name="app", path=root, kind="application")
            routes = _discover_routes(module)
            self.assertIn("pages/FragmentHome", routes)
            self.assertIn("pages/FragmentVideo", routes)
            self.assertNotIn("pages/FragmentContent", routes)  # include_* is not a screen


class DiscoverRoutesDeadActivityTest(unittest.TestCase):
    def test_manifest_activity_without_layout_or_source_is_skipped(self):
        # A <activity> declared in the manifest but with NEITHER a layout NOR a backing class
        # (e.g. a template-leftover `.ui.login.LoginActivity`) must NOT become a route, or other
        # screens navigate to its "no layout" placeholder instead of the real login page.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            main = root / "src" / "main"
            (main / "java" / "com" / "example").mkdir(parents=True)
            (main / "java" / "com" / "example" / "Login_in.java").write_text(
                "package com.example; public class Login_in {}", encoding="utf-8"
            )
            manifest = main / "AndroidManifest.xml"
            manifest.write_text(
                """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.example">
  <application>
    <activity android:name=".Login_in" />
    <activity android:name=".ui.login.LoginActivity" />
  </application>
</manifest>
""",
                encoding="utf-8",
            )
            module = AndroidModule(
                name="app", path=main, kind="application", manifest=manifest,
                source_files=[main / "java" / "com" / "example" / "Login_in.java"],
            )
            routes = _discover_routes(module)
            self.assertIn("pages/LoginIn", routes)          # backed by Login_in.java -> kept
            self.assertNotIn("pages/LoginActivity", routes)  # dead declaration -> dropped


if __name__ == "__main__":
    unittest.main()
