import json
import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import (
    _media_store_compat_ets,
    _module_json,
    _uses_mediastore,
)
from android2harmony.model import AndroidModule, AndroidProject


def _project(root: Path, src_text: str) -> AndroidProject:
    src = root / "app" / "src" / "main" / "java" / "Fetcher.kt"
    src.parent.mkdir(parents=True)
    src.write_text(src_text, encoding="utf-8")
    module = AndroidModule(name="app", path=root / "app", kind="application", source_files=[src])
    return AndroidProject(root=root, name="App", modules=[module], settings_file=None, gradle_files=[])


class MediaStoreMappingTest(unittest.TestCase):
    def test_detects_mediastore_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = _project(Path(tmp), "val uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI")
            self.assertTrue(_uses_mediastore(proj))

    def test_no_mediastore_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = _project(Path(tmp), "class Fetcher { fun load() { } }")
            self.assertFalse(_uses_mediastore(proj))

    def test_compat_uses_real_harmony_photo_api(self):
        code = _media_store_compat_ets()
        # maps to the real HarmonyOS Kit, not a mock
        self.assertIn("photoAccessHelper", code)
        self.assertIn("getPhotoAccessHelper", code)
        self.assertIn("getAssets", code)
        self.assertIn("READ_IMAGEVIDEO", code)
        self.assertIn("MediaLibraryKit", code)

    def test_module_json_adds_media_permission_only_when_used(self):
        with_media = _module_json(None, "App", uses_mediastore=True)
        without = _module_json(None, "App", uses_mediastore=False)
        self.assertIn("ohos.permission.READ_IMAGEVIDEO", with_media)
        self.assertNotIn("ohos.permission.READ_IMAGEVIDEO", without)
        # still valid json (parse the module config)
        json.loads(with_media)


if __name__ == "__main__":
    unittest.main()
