from android2harmony.llm_page_agent import (
    apply_arkts_fixups,
    generate_arkui_page,
    sanitize_page,
    validate_page,
)


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
