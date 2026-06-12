from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AndroidApiUsage:
    api: str
    category: str
    file: str
    line: int
    snippet: str
    harmony_target: str
    status: str


@dataclass
class AndroidModule:
    name: str
    path: Path
    kind: str
    namespace: str | None = None
    application_id: str | None = None
    min_sdk: str | None = None
    target_sdk: str | None = None
    compile_sdk: str | None = None
    manifest: Path | None = None
    source_files: list[Path] = field(default_factory=list)
    resource_files: list[Path] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    features: set[str] = field(default_factory=set)
    android_api_usages: list[AndroidApiUsage] = field(default_factory=list)


@dataclass
class AndroidProject:
    root: Path
    name: str
    modules: list[AndroidModule]
    settings_file: Path | None
    gradle_files: list[Path]


@dataclass
class MigrationIssue:
    severity: str
    category: str
    file: str
    message: str
    suggestion: str


@dataclass
class MigrationResult:
    project_name: str
    output_dir: Path
    generated_files: list[Path]
    copied_files: list[Path]
    issues: list[MigrationIssue]
    features: dict[str, int]
