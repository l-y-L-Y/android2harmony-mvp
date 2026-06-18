from android2harmony.diff_report import render_md


def test_render_md_covers_key_sections():
    d = {
        "android": "/a", "harmony": "/h",
        "screens": {"expected": 10, "translated": 8, "missing": ["FooActivity", "BarActivity"], "coverage": 0.8},
        "blankLikePages": ["FragmentHome.ets"],
        "strings": {"android": 120, "harmony": 118},
        "media": {"android": 40, "harmony": 38},
        "apiByStatus": {"generated": 30, "adapter-required": 12, "partially-generated": 8},
    }
    md = render_md(d)
    assert "屏幕覆盖" in md
    assert "覆盖率:80%" in md
    assert "FooActivity" in md and "BarActivity" in md
    assert "FragmentHome.ets" in md            # blank-like surfaced
    assert "安卓 120 → 鸿蒙 118" in md           # strings diff
    assert "adapter-required:12" in md          # api status


def test_render_md_handles_empty_gaps():
    d = {
        "android": "/a", "harmony": "/h",
        "screens": {"expected": 3, "translated": 3, "missing": [], "coverage": 1.0},
        "blankLikePages": [],
        "strings": {"android": 5, "harmony": 5},
        "media": {"android": 0, "harmony": 0},
        "apiByStatus": {},
    }
    md = render_md(d)
    assert "覆盖率:100%" in md
    assert "未生成:无" in md
    assert "空白/占位嫌疑(已转译但内容空):无" in md


if __name__ == "__main__":
    import unittest
    unittest.main()
