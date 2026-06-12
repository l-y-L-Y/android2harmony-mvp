from pathlib import Path

from android2harmony.analyzer import analyze_project


def test_analyze_architecture_samples_when_available():
    root = Path("D:/work/Android/architecture-samples")
    if not root.exists():
        return
    project, issues = analyze_project(root)
    assert project.modules
    assert any(module.kind == "application" for module in project.modules)
    assert issues

