from pathlib import Path

from android2harmony.build_repair import (
    build_repair_prompt,
    parse_build_errors,
    repair_file,
)

SAMPLE_LOG = """
> hvigor Building...
\x1b[31m172 ERROR: \x1b[31m10505001 ArkTS Compiler Error
Error Message: Property 'justifyContent' does not exist on type 'StackAttribute'. At File: D:/out/v2/entry/src/main/ets/pages/Foo.ets:127:8
\x1b[39m
\x1b[31m173 ERROR: \x1b[31m10505001 ArkTS Compiler Error
Error Message: Cannot find name 'Spacer'. At File: D:/out/v2/entry/src/main/ets/pages/Foo.ets:136:7
\x1b[31m174 ERROR:
Error Message: Cannot find name 'currentTab'. At File: D:/out/v2/entry/src/main/ets/pages/Bar.ets:12:7
COMPILE RESULT:FAIL {ERROR:3 WARN:1}
"""


def test_parse_groups_errors_by_file():
    errors = parse_build_errors(SAMPLE_LOG)
    foo = "D:/out/v2/entry/src/main/ets/pages/Foo.ets"
    bar = "D:/out/v2/entry/src/main/ets/pages/Bar.ets"
    assert set(errors) == {foo, bar}
    assert len(errors[foo]) == 2
    assert len(errors[bar]) == 1
    assert "justifyContent" in errors[foo][0]
    assert errors[foo][0].startswith("L127:8")


def test_parse_strips_ansi_and_dedup_whitespace():
    errors = parse_build_errors(SAMPLE_LOG)
    joined = " ".join(v for vals in errors.values() for v in vals)
    assert "\x1b" not in joined
    assert "Cannot find name 'currentTab'" in joined


def test_repair_prompt_includes_errors_and_rules():
    prompt = build_repair_prompt("Foo.ets", "@Component struct Foo { build() {} }", ["L1:1 Cannot find name 'Spacer'"])
    assert "Spacer" in prompt
    assert "Blank()" in prompt  # rules sheet mentions the fix
    assert "Foo.ets" in prompt


def test_repair_file_writes_valid_fix(tmp_path: Path):
    f = tmp_path / "Foo.ets"
    f.write_text("@Entry\n@Component\nstruct Foo {\n  build() {\n    Spacer()\n  }\n}\n", encoding="utf-8")

    fixed = "@Entry\n@Component\nstruct Foo {\n  build() {\n    Blank()\n  }\n}\n"

    def fake_call(prompt, system, max_tokens):
        return fixed

    ok = repair_file(f, ["L5:5 Cannot find name 'Spacer'"], media={"foreground"}, call_fn=fake_call)
    assert ok
    assert "Blank()" in f.read_text(encoding="utf-8")
    assert "Spacer" not in f.read_text(encoding="utf-8")


def test_repair_file_rejects_unbalanced(tmp_path: Path):
    f = tmp_path / "Foo.ets"
    original = "@Entry\n@Component\nstruct Foo {\n  build() {\n  }\n}\n"
    f.write_text(original, encoding="utf-8")

    def bad_call(prompt, system, max_tokens):
        return "struct Foo { build() {"  # unbalanced

    ok = repair_file(f, ["err"], media=set(), call_fn=bad_call)
    assert not ok
    assert f.read_text(encoding="utf-8") == original  # unchanged
