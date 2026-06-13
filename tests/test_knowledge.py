from android2harmony.knowledge import (
    ARKTS_RULES,
    attribute_hints_for_errors,
    component_cheatsheet,
    valid_attributes,
)


def test_component_reference_loaded():
    # Stack has alignContent but NOT justifyContent (a real error we hit).
    stack = valid_attributes("StackAttribute")
    assert "alignContent" in stack
    assert "justifyContent" not in stack
    # Column does have justifyContent.
    assert "justifyContent" in valid_attributes("Column")


def test_text_excludes_invalid_attrs():
    text = valid_attributes("Text")
    assert "fontColor" in text
    for bad in ["color", "verticalAlign", "singleLine", "maxWidth"]:
        assert bad not in text


def test_cheatsheet_is_compact_and_covers_common():
    sheet = component_cheatsheet()
    assert "Stack:" in sheet and "Text:" in sheet and "List:" in sheet
    assert len(sheet) < 4000  # stays prompt-sized


def test_attribute_hints_targets_error_components():
    errors = [
        "L127:8 Property 'justifyContent' does not exist on type 'StackAttribute'",
        "L20:3 Property 'color' does not exist on type 'TextAttribute'",
    ]
    hints = attribute_hints_for_errors(errors)
    assert "Stack:" in hints and "alignContent" in hints
    assert "Text:" in hints and "fontColor" in hints


def test_attribute_hints_empty_when_no_component_errors():
    assert attribute_hints_for_errors(["L1:1 Cannot find name 'foo'"]) == ""


def test_arkts_rules_mentions_key_constraints():
    assert "any" in ARKTS_RULES
    assert "declaration merging" in ARKTS_RULES.lower()
