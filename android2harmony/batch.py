from __future__ import annotations

import json
from pathlib import Path

from .analyzer import analyze_project
from .generator import generate_harmony_project
from .llm_agents import LLMRefineOptions


def discover_android_projects(root: Path) -> list[Path]:
    root = root.resolve()
    projects: list[Path] = []
    for candidate in sorted(root.iterdir()):
        if not candidate.is_dir():
            continue
        if (candidate / "settings.gradle.kts").exists() or (candidate / "settings.gradle").exists():
            projects.append(candidate)
    return projects


def batch_convert(input_root: Path, output_root: Path, force: bool, llm_options: LLMRefineOptions) -> dict:
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    for project_root in discover_android_projects(input_root):
        output_dir = output_root / f"{project_root.name}-harmony"
        try:
            project, issues = analyze_project(project_root)
            result = generate_harmony_project(project, issues, output_dir, force=force, llm_options=llm_options)
            results.append(
                {
                    "project": project_root.name,
                    "status": "generated",
                    "output": str(result.output_dir),
                    "issues": len(result.issues),
                    "generatedFiles": len(result.generated_files),
                    "copiedFiles": len(result.copied_files),
                }
            )
        except Exception as exc:
            results.append({"project": project_root.name, "status": "failed", "error": str(exc)})
    summary = {"inputRoot": str(input_root), "outputRoot": str(output_root), "projects": results}
    (output_root / "batch-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary

