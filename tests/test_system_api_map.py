import json
import unittest
from pathlib import Path

from android2harmony import system_api_map as m


class SystemApiMapTest(unittest.TestCase):
    def test_json_is_valid_and_nonempty(self):
        data = json.loads((Path(m.__file__).parent / "data" / "system_api_map.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["capabilities"]), 18)  # bounded but comprehensive

    def test_every_capability_has_required_fields(self):
        for cap in m.load_capabilities():
            for field in ("id", "title_cn", "harmony_kit", "adapter_module", "status", "priority"):
                self.assertIn(field, cap, f"{cap.get('id')} missing {field}")

    def test_photos_is_the_done_adapter(self):
        photos = m.capability("photos_video")
        self.assertEqual(photos["status"], "done")
        self.assertEqual(photos["adapter_module"], "MediaStoreCompat")

    def test_detects_capability_from_android_api(self):
        # the recorder probe: MediaRecorder source -> audio_record capability
        ids = m.detect_capabilities("val r = MediaRecorder(); r.setAudioSource(MIC)")
        self.assertIn("audio_record", ids)
        # a notes app touching prefs + sqlite -> both storage capabilities
        ids2 = m.detect_capabilities("@Dao interface NoteDao { } ; getSharedPreferences('p', 0)")
        self.assertIn("database", ids2)
        self.assertIn("key_value", ids2)

    def test_permissions_strip_parenthetical_notes(self):
        # MICROPHONE is clean; ACTIVITY_MOTION carries a note in the data and must be stripped
        perms = m.permissions_for(["audio_record", "sensors"])
        self.assertIn("ohos.permission.MICROPHONE", perms)
        self.assertIn("ohos.permission.ACTIVITY_MOTION", perms)
        self.assertTrue(all(p.startswith("ohos.permission.") and " " not in p for p in perms))

    def test_coverage_reports_done_and_compiled(self):
        cov = m.coverage()
        # device-verified capabilities
        self.assertIn("图片/视频库", cov.get("done", []))
        self.assertIn("录音/音频采集", cov.get("done", []))
        # device-verified ("done") set keeps growing as we validate on hardware
        self.assertGreaterEqual(len(cov.get("done", [])), 5)
        # the bulk of capabilities have a real adapter that compiles against the SDK,
        # whether still pending-device (compiled), bound (wired), or device-verified (done)
        real = len(cov.get("done", [])) + len(cov.get("wired", [])) + len(cov.get("compiled", []))
        self.assertGreaterEqual(real, 15)


if __name__ == "__main__":
    unittest.main()
