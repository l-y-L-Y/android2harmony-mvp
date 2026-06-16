from android2harmony.llm_page_agent import (
    apply_arkts_fixups,
    build_page_prompt,
    generate_arkui_page,
    sanitize_page,
    validate_page,
)


def test_hoist_nested_interface_out_of_struct():
    # interface declared inside the struct body (illegal in ArkTS) must move to top level
    bad = (
        "@Entry\n@Component\nexport struct Title {\n"
        "  interface Basic {\n    cityName: string\n  }\n"
        "  @State weather: Basic = { cityName: '北京' }\n"
        "  build() {\n    Row() {\n      Text(this.weather.cityName)\n    }\n  }\n}\n"
    )
    out = apply_arkts_fixups(bad)
    # interface no longer sits between struct '{' and build()
    struct_pos = out.index("struct Title")
    iface_pos = out.index("interface Basic")
    assert iface_pos < struct_pos  # hoisted above the struct
    # struct body keeps the state + build, no nested interface
    body = out[out.index("struct Title"):]
    assert "interface Basic" not in body
    assert "@State weather" in body and "build()" in body


def test_hoist_keeps_interface_dependency_order():
    bad = (
        "@Component\nstruct W {\n"
        "  interface Update {\n    time: string\n  }\n"
        "  interface Basic {\n    u: Update\n  }\n"
        "  build() {\n    Column() {}\n  }\n}\n"
    )
    out = apply_arkts_fixups(bad)
    assert out.index("interface Update") < out.index("interface Basic") < out.index("struct W")


def test_fixups_noop_without_nested_interface():
    good = "@Entry\n@Component\nstruct P {\n  build() {\n    Column() {\n      Text('hi')\n    }\n  }\n}\n"
    assert "interface" not in apply_arkts_fixups(good)


def test_prompt_includes_navigation_catalog():
    prompt = build_page_prompt(
        "MainActivity", "<x/>", "App",
        routes=["pages/Index", "pages/MainActivity", "pages/DetailActivity", "pages/SettingsActivity"],
    )
    assert "router.pushUrl" in prompt
    assert "DetailActivity" in prompt and "SettingsActivity" in prompt
    assert "MainActivity" not in prompt.split("Navigation:")[1].split("\n")[0]  # current page excluded from catalog


def test_prompt_no_navigation_when_alone():
    prompt = build_page_prompt("Solo", "<x/>", "App", routes=["pages/Index", "pages/Solo"])
    assert "Navigation: the real pages" not in prompt


def test_fixups_cover_known_arkui_mistakes():
    code = (
        "Blank()\n"
        "Spacer()\n"
        ".backgroundImageSize(ImageSize.Stretch)\n"
        "Image($r('app.media.startIcon'))\n"
        "Image($r('app.media.starticon'))\n"
        ".margin({ start: 8, top: 4 })\n"
        ".padding({ end: 16 })\n"
    )
    out = apply_arkts_fixups(code)
    assert "Spacer(" not in out
    assert "ImageSize.Stretch" not in out
    assert "start[Ii]con" not in out and "startIcon" not in out and "starticon" not in out
    assert "$r('app.media.foreground')" in out
    assert "left: 8" in out and "right: 16" in out
    assert "start:" not in out and "end:" not in out


def test_fixups_do_not_touch_legend_or_lengthmetrics():
    code = ".margin({ start: LengthMetrics.vp(8) })\nconst legend: string = 'x';\n"
    out = apply_arkts_fixups(code)
    assert "start: LengthMetrics.vp(8)" in out  # non-numeric start untouched
    assert "legend: string" in out  # word boundary protects 'legend'


def test_validate_accepts_complete_page():
    code = "@Entry\n@Component\nstruct About {\n  build() {\n    Text('hi')\n  }\n}\n"
    ok, reason = validate_page(code, "About")
    assert ok, reason


def test_validate_rejects_truncated_page():
    code = "@Entry\n@Component\nstruct About {\n  build() {\n    Button('x').onClick(() => {\n      //"
    ok, reason = validate_page(code, "About")
    assert not ok
    assert "truncated" in reason or "brace" in reason


def test_validate_rejects_wrong_struct_name():
    code = "@Entry\n@Component\nstruct Other {\n  build() {\n  }\n}\n"
    ok, _ = validate_page(code, "About")
    assert not ok


def test_sanitize_replaces_unknown_media():
    code = "@Component\nstruct P {\n  build() {\n    Image($r('app.media.about_bg'))\n  }\n}\n"
    out = sanitize_page(code, "P", available_media={"foreground", "background"})
    assert "about_bg" not in out
    assert "$r('app.media.foreground')" in out


def test_sanitize_keeps_known_media():
    code = "@Component\nstruct P {\n  build() {\n    Image($r('app.media.logo'))\n  }\n}\n"
    out = sanitize_page(code, "P", available_media={"logo", "foreground"})
    assert "$r('app.media.logo')" in out


def test_sanitize_renames_struct_to_page_name():
    code = "@Component\nstruct WrongName {\n  build() {\n  }\n}\n"
    out = sanitize_page(code, "About", available_media=set())
    assert "struct About" in out
    assert "WrongName" not in out


def test_sanitize_strips_markdown_fence():
    code = "```typescript\n@Component\nstruct P { build() {} }\n```"
    out = sanitize_page(code, "P", available_media=set())
    assert "```" not in out


def test_generate_uses_fake_call_and_validates():
    page = (
        "@Entry\n@Component\nstruct Login {\n  build() {\n"
        "    Column() {\n      Text('账号:')\n      Button('登录')\n    }\n  }\n}\n"
    )
    calls = []

    def fake_call(prompt, system, max_tokens):
        calls.append((prompt, max_tokens))
        return f"```typescript\n{page}\n```"

    out = generate_arkui_page(
        "Login", "<LinearLayout/>", "开源中国", available_media={"foreground"}, call_fn=fake_call
    )
    assert "struct Login" in out
    assert "账号:" in out  # Chinese preserved
    assert calls[0][1] == 12000  # generous max_tokens for reasoning model


def test_generate_retries_then_raises_on_bad_output():
    attempts = []

    def bad_call(prompt, system, max_tokens):
        attempts.append(1)
        return "struct Login { build() {"  # truncated, unbalanced

    try:
        generate_arkui_page("Login", "<x/>", "App", call_fn=bad_call)
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "Login" in str(exc)
    assert len(attempts) == 3  # up to three attempts before giving up


def test_generate_retries_after_timeout_then_succeeds():
    page = "@Entry\n@Component\nstruct Home {\n  build() {\n    Text('首页')\n  }\n}\n"
    calls = []

    def flaky_call(prompt, system, max_tokens):
        calls.append(1)
        if len(calls) == 1:
            raise TimeoutError("The read operation timed out")
        return page

    out = generate_arkui_page("Home", "<x/>", "App", call_fn=flaky_call)
    assert "struct Home" in out
    assert "首页" in out
    assert len(calls) == 2  # recovered on the second attempt


def test_sanitize_adds_entry_to_routed_component():
    # Regression: a fragment-backed page rendered as a pure component (@Component
    # export struct, no @Entry) fails hvigor's "one and only one @Entry" rule.
    code = "import x\n\n@Component\nexport struct FragmentProject {\n  build() {\n    Column() {}\n  }\n}\n"
    out = sanitize_page(code, "FragmentProject", {"foreground"})
    assert out.count("@Entry") == 1
    assert out.count("@Component") == 1
    assert "export struct FragmentProject" in out


def test_sanitize_dedupes_duplicate_entry():
    code = "@Entry\n@Entry\n@Component\nstruct Home {\n  build() {\n    Text('x')\n  }\n}\n"
    out = sanitize_page(code, "Home", {"foreground"})
    assert out.count("@Entry") == 1


def test_sanitize_entry_only_on_main_struct():
    code = ("@Component\nexport struct Main {\n  build() {}\n}\n\n"
            "@Component\nstruct Row {\n  build() {}\n}\n")
    out = sanitize_page(code, "Main", {"foreground"})
    lines = out.split("\n")
    mi = next(i for i, l in enumerate(lines) if "struct Main" in l)
    ri = next(i for i, l in enumerate(lines) if "struct Row" in l)
    assert lines[mi - 2].strip() == "@Entry"  # @Entry above Main's @Component
    assert lines[ri - 2].strip() != "@Entry"  # Row stays a plain component
    assert out.count("@Entry") == 1
