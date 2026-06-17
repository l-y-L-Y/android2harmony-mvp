from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .model import AndroidModule, AndroidProject, MigrationIssue


@dataclass
class AgentArtifact:
    path: str
    content: str


@dataclass
class MigrationPipeline:
    artifacts: list[AgentArtifact]
    routes: list[str]
    mock_endpoints: list[dict[str, str]]


def build_agent_pipeline(project: AndroidProject, issues: list[MigrationIssue]) -> MigrationPipeline:
    app_module = _select_app_module(project)
    routes = _discover_routes(app_module)
    endpoints = _discover_mock_endpoints(project)
    artifacts = [
        AgentArtifact("agent-workspace/01-understanding/project-model.json", _project_model(project, issues)),
        AgentArtifact("agent-workspace/02-planning/migration-plan.json", _migration_plan(project, issues, routes)),
        AgentArtifact("agent-workspace/02-planning/api-mapping.json", _api_mapping(project)),
        AgentArtifact("agent-workspace/03-migration/code-migration-tasks.md", _code_tasks(project)),
        AgentArtifact("agent-workspace/03-migration/resource-migration-tasks.md", _resource_tasks(project)),
        AgentArtifact("agent-workspace/04-uitest/test-dsl.json", _test_dsl(project, routes)),
        AgentArtifact(
            "agent-workspace/04-uitest/mock-plan.json",
            json.dumps(
                {
                    "agent": "mock-management-agent",
                    "endpoints": endpoints,
                    "dataMode": "generated-local-mock",
                    "switch": "entry/src/main/ets/network/HttpClient.ets: NetworkConfig.useMock",
                    "defaultMode": "mock",
                    "realBackendPreserved": True,
                },
                indent=2,
                ensure_ascii=False,
            ),
        ),
        AgentArtifact("agent-workspace/05-repair/repair-loop.json", _repair_loop(issues)),
        AgentArtifact("agent-workspace/06-report/output-checklist.md", _output_checklist()),
    ]
    return MigrationPipeline(artifacts=artifacts, routes=routes, mock_endpoints=endpoints)


def _select_app_module(project: AndroidProject) -> AndroidModule | None:
    apps = [m for m in project.modules if m.kind == "application"]
    return apps[0] if apps else (project.modules[0] if project.modules else None)


def _project_model(project: AndroidProject, issues: list[MigrationIssue]) -> str:
    payload = {
        "agent": "understanding-analysis-agent",
        "project": project.name,
        "root": str(project.root),
        "modules": [
            {
                "name": module.name,
                "kind": module.kind,
                "path": str(module.path),
                "namespace": module.namespace,
                "applicationId": module.application_id,
                "manifest": str(module.manifest) if module.manifest else None,
                "sourceCount": len(module.source_files),
                "resourceCount": len(module.resource_files),
                "features": sorted(module.features),
                "androidApiUsageCount": len(module.android_api_usages),
                "androidApiUsages": [
                    {
                        "api": usage.api,
                        "category": usage.category,
                        "file": usage.file,
                        "line": usage.line,
                        "harmonyTarget": usage.harmony_target,
                        "status": usage.status,
                    }
                    for usage in module.android_api_usages[:200]
                ],
                "dependencies": module.dependencies,
            }
            for module in project.modules
        ],
        "issues": [asdict(issue) for issue in issues],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _migration_plan(project: AndroidProject, issues: list[MigrationIssue], routes: list[str]) -> str:
    steps = [
        {"agent": "migration-planning-agent", "task": "rank-modules", "output": [m.name for m in project.modules]},
        {"agent": "code-migration-agent", "task": "convert-kotlin-java-to-arkts-placeholders", "strategy": "preserve-original-source-and-generate-adapters"},
        {"agent": "engineering-build-agent", "task": "generate-deveco-hvigor-project", "strategy": "stage-model-entry-module"},
        {"agent": "adaptation-agent", "task": "inject-platform-adapters-mock-and-logs", "strategy": "create ArkTS adapter layer and mock config"},
        {"agent": "uitest-agent", "task": "generate-smoke-test-dsl", "routes": routes},
        {"agent": "repair-agent", "task": "consume-build-test-failures-and-regenerate-fixes", "input": "agent-workspace/05-repair/repair-loop.json"},
    ]
    risk = [{"category": i.category, "severity": i.severity, "file": i.file, "suggestion": i.suggestion} for i in issues]
    return json.dumps({"project": project.name, "steps": steps, "riskRegister": risk}, indent=2, ensure_ascii=False)


def _api_mapping(project: AndroidProject) -> str:
    used = {feature for module in project.modules for feature in module.features}
    usages = [usage for module in project.modules for usage in module.android_api_usages]
    mappings = {
        "android_api": {"target": "HarmonyOS Kit APIs", "status": "manual-adapter-required"},
        "compose": {"target": "ArkUI declarative components", "status": "screen-rewrite-required"},
        "room": {"target": "relationalStore or repository-backed storage", "status": "data-layer-rewrite-required"},
        "hilt": {"target": "ArkTS service registry", "status": "di-rewrite-required"},
        "navigation": {"target": "router pages", "status": "route-map-generated"},
        "coroutines": {"target": "Promise/async or task pool", "status": "logic-review-required"},
        "viewmodel": {"target": "@Observed/@State/@Provide or app-level store", "status": "state-layer-rewrite-required"},
        "datastore": {"target": "preferences", "status": "storage-adapter-required"},
        "workmanager": {"target": "background task", "status": "background-capability-required"},
        "network_api": {"target": "ArkTS HTTP client plus MockServer fixtures", "status": "api-client-generation-required"},
    }
    api_items = [
        {
            "api": usage.api,
            "category": usage.category,
            "source": f"{usage.file}:{usage.line}",
            "harmonyTarget": usage.harmony_target,
            "status": usage.status,
        }
        for usage in usages[:300]
    ]
    return json.dumps(
        {
            "usedFeatures": sorted(used),
            "mappings": {k: v for k, v in mappings.items() if k in used},
            "androidApiUsages": api_items,
        },
        indent=2,
        ensure_ascii=False,
    )


def _code_tasks(project: AndroidProject) -> str:
    lines = ["# Code Migration Tasks", ""]
    for module in project.modules:
        lines.append(f"## {module.name}")
        lines.append(f"- Generate ArkTS adapters for {len(module.source_files)} Kotlin/Java files.")
        if "compose" in module.features:
            lines.append("- Convert Compose screens to ArkUI pages/components.")
        if "android_api" in module.features:
            lines.append(f"- Replace {len(module.android_api_usages)} direct Android API usage points with HarmonyOS platform adapters.")
            for usage in module.android_api_usages[:12]:
                lines.append(f"  - `{usage.file}:{usage.line}` {usage.api} -> {usage.harmony_target} ({usage.status})")
        if "room" in module.features:
            lines.append("- Replace Room entities/DAO/database with Harmony storage adapter.")
        if "hilt" in module.features:
            lines.append("- Replace Hilt graph with ArkTS service registry.")
        lines.append("")
    return "\n".join(lines)


def _resource_tasks(project: AndroidProject) -> str:
    lines = ["# Resource Migration Tasks", ""]
    for module in project.modules:
        lines.append(f"- `{module.name}`: copy {len(module.resource_files)} Android resources, convert string resources, preserve unsupported XML under `android_original`.")
    return "\n".join(lines) + "\n"


def _test_dsl(project: AndroidProject, routes: list[str]) -> str:
    initial = _initial_route(routes)
    has_real_list_detail = "pages/ActivityMain" in routes and "pages/ActivityDetail" in routes
    cases = [
        {"name": "cold_start", "steps": [{"action": "launch"}, {"assert": "page_visible", "target": initial}]}
    ]
    if has_real_list_detail:
        cases.append(
            {
                "name": "click_pokemon_item_to_detail",
                "steps": [
                    {"action": "launch"},
                    {"assert": "text_visible", "target": "Bulbasaur"},
                    {"action": "click_text", "target": "Bulbasaur"},
                    {"assert": "page_visible", "target": "pages/ActivityDetail"},
                    {"assert": "text_visible", "target": "Bulbasaur"},
                    {"assert": "wait_text", "target": "Height", "timeoutMs": 5000},
                    {"assert": "wait_text", "target": "7", "timeoutMs": 5000},
                    {"assert": "wait_text", "target": "HP 45", "timeoutMs": 5000},
                ],
            }
        )
        cases.append(
            {
                "name": "back_from_detail_to_list",
                "steps": [
                    {"action": "launch"},
                    {"assert": "text_visible", "target": "Bulbasaur"},
                    {"action": "click_text", "target": "Bulbasaur"},
                    {"assert": "page_visible", "target": "pages/ActivityDetail"},
                    {"action": "press_back"},
                    {"assert": "page_visible", "target": "pages/ActivityMain"},
                    {"assert": "text_visible", "target": "Bulbasaur"},
                ],
            }
        )
    if has_real_list_detail:
        return json.dumps({"agent": "test-generation-agent", "framework": "official-uitest", "project": project.name, "cases": cases}, indent=2)
    for route in routes:
        if route == initial:
            continue
        cases.append(
            {
                "name": f"click_to_{route.split('/')[-1]}",
                "steps": [
                    {"action": "launch"},
                    {"action": "click_text", "target": _route_title(route)},
                    {"assert": "page_visible", "target": route},
                ],
            }
        )
    return json.dumps({"agent": "test-generation-agent", "framework": "official-uitest", "project": project.name, "cases": cases}, indent=2)


def _repair_loop(issues: list[MigrationIssue]) -> str:
    return json.dumps(
        {
            "agent": "repair-iteration-agent",
            "loop": ["diagnose-failure", "propose-fix", "apply-fix", "rebuild", "rerun-uitest", "verify"],
            "maxIterations": 5,
            "deviceValidationInput": "agent-workspace/05-repair/device-validation-result.json",
            "runner": "python -m android2harmony.cli validate-dsl <generated-project> --bundle <bundle>",
            "knownRisks": [asdict(issue) for issue in issues],
        },
        indent=2,
        ensure_ascii=False,
    )


def _output_checklist() -> str:
    return """# Output And Report Checklist

- HarmonyOS project can be opened by DevEco Studio.
- `migration-report.md` lists completion, risks, unmigrated items, and manual intervention points.
- `agent-workspace/04-uitest/test-dsl.json` contains generated smoke tests.
- `agent-workspace/05-repair/repair-loop.json` captures the repair iteration protocol.
- `python -m android2harmony.cli validate-dsl` writes `agent-workspace/05-repair/device-validation-result.json`.
- `android_original/` keeps source snapshots for traceability.
"""


def _discover_routes(module: AndroidModule | None) -> list[str]:
    if not module:
        return ["pages/Index"]
    routes = ["pages/Index"]
    seen = {route.lower() for route in routes}
    from .xml_layout_translator import page_to_layout_file, _module_layout_dirs
    claimed_layouts: set[str] = set()
    if module.manifest and module.manifest.exists():
        for page in _discover_manifest_routes(module.manifest):
            route = f"pages/{page}"
            key = route.lower()
            if key not in seen:
                routes.append(route)
                seen.add(key)
                claimed = page_to_layout_file(module.path, route)
                if claimed:
                    claimed_layouts.add(claimed.stem.lower())
    # Scan every layout dir (incl. custom resource roots like res/home/layout) so the
    # content-bearing fragments behind an Activity shell become real pages, not just the
    # ones in standard res/layout. fragment_*/activity_* layouts are screens.
    for layout_dir in _module_layout_dirs(str(module.path)):
        for layout in sorted(layout_dir.glob("*.xml")):
            # Skip reusable sub-components (list rows, headers, dialogs, includes);
            # they are not screens. Skip layouts already owned by a manifest activity.
            if _is_component_layout(layout.stem) or layout.stem.lower() in claimed_layouts:
                continue
            route = f"pages/{_page_name(layout.stem)}"
            key = route.lower()
            if key not in seen:
                routes.append(route)
                seen.add(key)
    for source in module.source_files:
        text = source.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"composable\(['\"]([^'\"]+)['\"]", text):
            route = f"pages/{_page_name(match.group(1))}"
            key = route.lower()
            if key not in seen:
                routes.append(route)
                seen.add(key)
    # Compose apps: each screen-level @Composable becomes a page (no XML layout exists).
    from .compose import discover_compose_screens
    for screen_name in discover_compose_screens(module):
        route = f"pages/{screen_name}"
        key = route.lower()
        if key not in seen:
            routes.append(route)
            seen.add(key)
    return routes


def _discover_manifest_routes(manifest: Path) -> list[str]:
    text = manifest.read_text(encoding="utf-8", errors="ignore")
    routes: list[str] = []
    for match in re.finditer(r'<activity[^>]+android:name="([^"]+)"', text):
        route = _page_name(_manifest_activity_to_page(match.group(1)))
        routes.append(route)
    return routes


def _manifest_activity_to_page(name: str) -> str:
    cleaned = name.strip()
    if cleaned.startswith("."):
        cleaned = cleaned[1:]
    return cleaned.split(".")[-1]


def _initial_route(routes: list[str]) -> str:
    for route in ["pages/ActivityMain", "pages/MainActivity", "pages/Main", "pages/AppStart", "pages/Index"]:
        if route in routes:
            return route
    return routes[0] if routes else "pages/Index"


def _route_title(route: str) -> str:
    name = route.split("/")[-1]
    name = re.sub(r"^Activity", "", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    return name or "Index"


def _discover_mock_endpoints(project: AndroidProject) -> list[dict[str, str]]:
    endpoints: list[dict[str, str]] = []
    for module in project.modules:
        for source in module.source_files:
            text = source.read_text(encoding="utf-8", errors="ignore")
            for match in re.finditer(r"@(?:GET|POST|PUT|DELETE|PATCH)\(['\"]([^'\"]+)['\"]", text):
                endpoints.append({"module": module.name, "path": match.group(1), "source": str(source)})
    return endpoints


def _page_name(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    name = "".join(part[:1].upper() + part[1:] for part in parts if part)
    return name or "MigratedPage"


_COMPONENT_MARKERS = (
    "_item", "item_", "listitem", "_header", "_footer", "_row", "_cell", "_chip",
    "_entry", "dialog", "_section", "nav_", "toolbar_", "floating_", "_menu_item",
)


def _is_component_layout(stem: str) -> bool:
    """A reusable sub-component layout (list row, header, dialog, nav item) - not a screen.
    Screens (activity_*/fragment_*/*_fragment) are always kept."""
    s = stem.lower()
    if s.startswith("include_"):  # <include> targets are reusable fragments of a screen
        return True
    if s.startswith("activity_") or s.startswith("fragment_") or s.endswith("_fragment"):
        return False
    return any(marker in s for marker in _COMPONENT_MARKERS)
