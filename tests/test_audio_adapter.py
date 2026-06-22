import json
import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import (
    _audio_recorder_compat_ets,
    _av_player_compat_ets,
    _CAPABILITY_ADAPTERS,
    _detect_capabilities,
    _module_json,
)
from android2harmony.model import AndroidModule, AndroidProject


def _project(root: Path, src_text: str) -> AndroidProject:
    src = root / "app" / "src" / "main" / "java" / "Recorder.kt"
    src.parent.mkdir(parents=True)
    src.write_text(src_text, encoding="utf-8")
    module = AndroidModule(name="app", path=root / "app", kind="application", source_files=[src])
    return AndroidProject(root=root, name="App", modules=[module], settings_file=None, gradle_files=[])


class AudioAdapterTest(unittest.TestCase):
    def test_recorder_adapter_uses_real_avrecorder_kit(self):
        code = _audio_recorder_compat_ets()
        self.assertIn("@kit.MediaKit", code)
        self.assertIn("createAVRecorder", code)
        self.assertIn("AUDIO_SOURCE_TYPE_MIC", code)
        self.assertIn("ohos.permission.MICROPHONE", code)

    def test_player_adapter_uses_real_avplayer_kit(self):
        code = _av_player_compat_ets()
        self.assertIn("createAVPlayer", code)
        self.assertIn("stateChange", code)

    def test_detect_audio_record_capability_from_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = _project(Path(tmp), "val r = MediaRecorder(); r.setAudioSource(MediaRecorder.AudioSource.MIC)")
            caps = _detect_capabilities(proj)
            self.assertIn("audio_record", caps)

    def test_detect_playback_capability_from_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = _project(Path(tmp), "val p = MediaPlayer(); p.setDataSource(path); p.start()")
            caps = _detect_capabilities(proj)
            self.assertIn("av_playback", caps)

    def test_no_audio_caps_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = _project(Path(tmp), "class Plain { fun hi() {} }")
            caps = _detect_capabilities(proj)
            self.assertNotIn("audio_record", caps)
            self.assertNotIn("av_playback", caps)

    def test_registry_maps_caps_to_adapter_modules(self):
        self.assertEqual(_CAPABILITY_ADAPTERS["audio_record"][0], "AudioRecorderCompat")
        self.assertEqual(_CAPABILITY_ADAPTERS["av_playback"][0], "AVPlayerCompat")

    def test_microphone_permission_reason_resolves(self):
        out = _module_json(None, "App", permissions=["ohos.permission.MICROPHONE"])
        cfg = json.loads(out)
        perms = cfg["module"]["requestPermissions"]
        mic = next(p for p in perms if p["name"] == "ohos.permission.MICROPHONE")
        self.assertEqual(mic["reason"], "$string:permission_microphone_reason")


if __name__ == "__main__":
    unittest.main()
