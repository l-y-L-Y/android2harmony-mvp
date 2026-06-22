import tempfile
import unittest
from pathlib import Path

from android2harmony import generator as g
from android2harmony.generator import _CAPABILITY_ADAPTERS, _detect_capabilities
from android2harmony.model import AndroidModule, AndroidProject


def _project(root: Path, src_text: str) -> AndroidProject:
    src = root / "app" / "src" / "main" / "java" / "Feature.kt"
    src.parent.mkdir(parents=True)
    src.write_text(src_text, encoding="utf-8")
    module = AndroidModule(name="app", path=root / "app", kind="application", source_files=[src])
    return AndroidProject(root=root, name="App", modules=[module], settings_file=None, gradle_files=[])


class SystemAdaptersTest(unittest.TestCase):
    # Each adapter emitter must reference the correct real HarmonyOS Kit.
    KIT_SIGNATURE = {
        "key_value": ("PreferencesCompat", "@kit.ArkData", "getPreferences"),
        "camera": ("CameraCompat", "@kit.CameraKit", "cameraPicker"),
        "sensors": ("SensorCompat", "@kit.SensorServiceKit", "sensor.on"),
        "location": ("LocationCompat", "@kit.LocationKit", "geoLocationManager"),
        "notification": ("NotificationCompat", "@kit.NotificationKit", "notificationManager"),
        "vibration": ("VibratorCompat", "@kit.SensorServiceKit", "vibrator"),
        "clipboard": ("ClipboardCompat", "@kit.BasicServicesKit", "pasteboard"),
        "device_info": ("DeviceInfoCompat", "@kit.BasicServicesKit", "deviceInfo"),
        "connectivity": ("ConnectivityCompat", "@kit.NetworkKit", "connection"),
        "share": ("ShareCompat", "@kit.AbilityKit", "startAbility"),
        "contacts": ("ContactsCompat", "@kit.ContactsKit", "selectContact"),
        "calendar": ("CalendarCompat", "@kit.CalendarKit", "calendarManager"),
        "biometric": ("BiometricCompat", "@kit.UserAuthenticationKit", "userAuth"),
    }

    def test_every_registered_adapter_uses_its_real_kit(self):
        for cap_id, (module_name, kit, symbol) in self.KIT_SIGNATURE.items():
            self.assertIn(cap_id, _CAPABILITY_ADAPTERS, f"{cap_id} not registered")
            reg_name, emitter = _CAPABILITY_ADAPTERS[cap_id]
            self.assertEqual(reg_name, module_name)
            code = emitter()
            self.assertIn(kit, code, f"{module_name} missing {kit}")
            self.assertIn(symbol, code, f"{module_name} missing {symbol}")
            self.assertIn(f"export class {module_name}", code)

    def test_detect_and_emit_preferences_for_settings_app(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = _project(Path(tmp), "val p = getSharedPreferences('cfg', 0); p.getBoolean('dark', false)")
            caps = _detect_capabilities(proj)
            self.assertIn("key_value", caps)

    def test_detect_sensors_and_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = _project(Path(tmp), "val sm = getSystemService() as SensorManager; LocationManager()")
            caps = _detect_capabilities(proj)
            self.assertIn("sensors", caps)
            self.assertIn("location", caps)

    def test_unused_capability_not_emitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = _project(Path(tmp), "class Plain { fun hi() {} }")
            caps = _detect_capabilities(proj)
            for cap in ("camera", "sensors", "location", "vibration", "clipboard"):
                self.assertNotIn(cap, caps)


if __name__ == "__main__":
    unittest.main()
