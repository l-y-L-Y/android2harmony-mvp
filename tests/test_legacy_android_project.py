import tempfile
import unittest
from pathlib import Path

from android2harmony.analyzer import analyze_project
from android2harmony.generator import generate_harmony_project


class RootGradleModuleTest(unittest.TestCase):
    def test_single_module_project_with_module_at_repo_root(self):
        # A Gradle project with no `app/` subdir: build.gradle at the root and the source set
        # (incl. the manifest) under src/main. Previously resolved to 0 modules because
        # _discover_modules skips the root gradle and legacy detection wants a root manifest.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                "apply plugin: 'com.android.application'\nandroid { namespace 'com.example.app' }\n",
                encoding="utf-8",
            )
            main = root / "src" / "main"
            (main / "java" / "com" / "example" / "app").mkdir(parents=True)
            (main / "java" / "com" / "example" / "app" / "MainActivity.java").write_text(
                "package com.example.app; public class MainActivity {}", encoding="utf-8"
            )
            (main / "AndroidManifest.xml").write_text(
                """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.example.app">
  <application android:label="App">
    <activity android:name=".MainActivity">
      <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
      </intent-filter>
    </activity>
  </application>
</manifest>
""",
                encoding="utf-8",
            )
            (main / "res" / "layout").mkdir(parents=True)
            (main / "res" / "layout" / "activity_main.xml").write_text(
                '<?xml version="1.0" encoding="utf-8"?>\n<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android" />',
                encoding="utf-8",
            )

            project, _ = analyze_project(root)
            self.assertEqual(len(project.modules), 1)
            self.assertEqual(project.modules[0].kind, "application")
            self.assertGreaterEqual(len(project.modules[0].source_files), 1)


class LegacyAndroidProjectTest(unittest.TestCase):
    def test_legacy_project_generates_clickable_routes(self):
        with tempfile.TemporaryDirectory() as tmp_in, tempfile.TemporaryDirectory() as tmp_out:
            root = Path(tmp_in)
            (root / "AndroidManifest.xml").write_text(
                """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="net.oschina.app">
    <application android:label="@string/app_name">
        <activity android:name=".ui.AppStart">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".ui.Main" />
        <activity android:name=".ui.About" />
    </application>
</manifest>
""",
                encoding="utf-8",
            )
            layout_dir = root / "res" / "layout"
            layout_dir.mkdir(parents=True)
            (layout_dir / "main.xml").write_text(
                """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="资讯" />
</LinearLayout>
""",
                encoding="utf-8",
            )
            (layout_dir / "about.xml").write_text(
                """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <TextView
        android:id="@+id/about"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="关于" />
</LinearLayout>
""",
                encoding="utf-8",
            )
            drawable_dir = root / "res" / "drawable"
            drawable_dir.mkdir(parents=True)
            (drawable_dir / "edit_search_bg.9.png").write_bytes(b"fake-png")
            source_dir = root / "src" / "net" / "oschina" / "app" / "ui"
            source_dir.mkdir(parents=True)
            (source_dir / "Main.java").write_text("package net.oschina.app.ui; public class Main {}", encoding="utf-8")

            project, issues = analyze_project(root)
            self.assertTrue(project.modules)
            self.assertEqual(project.modules[0].kind, "application")
            self.assertGreaterEqual(len(project.modules[0].source_files), 1)
            self.assertGreaterEqual(len(project.modules[0].resource_files), 2)

            output = Path(tmp_out)
            result = generate_harmony_project(project, issues, output, force=True)

            index = (output / "entry" / "src" / "main" / "ets" / "pages" / "Index.ets").read_text(encoding="utf-8")
            route_map = (output / "entry" / "src" / "main" / "ets" / "routes" / "RouteMap.ets").read_text(encoding="utf-8")

            # Index enters the primary screen instead of listing debug-nav buttons.
            self.assertIn("pages/Main", index)
            self.assertIn("NavigationCompat.replace", index)
            self.assertNotIn("navRoutes", index)
            self.assertIn("pages/Main", route_map)
            self.assertIn("pages/About", route_map)
            self.assertNotIn("pages/Feedback", route_map)
            generated_names = "\n".join(Path(p).name for p in result.generated_files)
            copied_names = "\n".join(Path(p).name for p in result.copied_files)
            self.assertIn("Main.ets", generated_names)
            self.assertIn("About.ets", generated_names)
            self.assertIn("main.ets", generated_names)
            self.assertIn("edit_search_bg_9.png", copied_names)


if __name__ == "__main__":
    unittest.main()
