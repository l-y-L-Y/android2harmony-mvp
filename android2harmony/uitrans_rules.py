from __future__ import annotations

import json
from pathlib import Path


def extract_uitrans_rule_index(uitrans_root: Path) -> dict:
    harmony_prompt_root = uitrans_root / "core" / "prompt" / "prompts" / "harmony"
    template_root = uitrans_root / "template" / "harmony_empty_ability_v5"
    component_doc_root = uitrans_root / "script" / "auto_harmony_document"

    prompts = _collect_files(harmony_prompt_root, ".prompt")
    docs = _collect_dirs(component_doc_root)
    return {
        "source": str(uitrans_root),
        "harmonyPromptRoot": str(harmony_prompt_root),
        "templateRoot": str(template_root),
        "promptFiles": prompts,
        "componentDocumentCount": len(docs),
        "componentDocumentSamples": docs[:80],
        "recommendedUse": [
            "Use harmony/rules/*.prompt as migration policy.",
            "Use harmony/examples/*.prompt as few-shot examples.",
            "Use script/auto_harmony_document directories as ArkUI component reference index.",
            "Use template/harmony_empty_ability_v5 as a DevEco-compatible project template.",
        ],
    }


def write_uitrans_rule_index(uitrans_root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(extract_uitrans_rule_index(uitrans_root), indent=2, ensure_ascii=False), encoding="utf-8")


def _collect_files(root: Path, suffix: str) -> list[str]:
    if not root.exists():
        return []
    return [str(path.relative_to(root)) for path in sorted(root.rglob(f"*{suffix}"))]


def _collect_dirs(root: Path) -> list[str]:
    if not root.exists():
        return []
    return [path.name for path in sorted(root.iterdir()) if path.is_dir()]

