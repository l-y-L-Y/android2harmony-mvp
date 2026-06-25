from __future__ import annotations

import re
from pathlib import Path

from .model import AndroidApiUsage, AndroidModule, AndroidProject, MigrationIssue


SOURCE_EXTENSIONS = {".kt", ".java"}

FEATURE_PATTERNS: list[tuple[str, str]] = [
    ("compose", r"@Composable|androidx\.compose|setContent\s*\{"),
    ("room", r"androidx\.room|@Entity|@Dao|RoomDatabase"),
    ("hilt", r"dagger\.hilt|@HiltAndroidApp|@AndroidEntryPoint|@Inject"),
    ("navigation", r"androidx\.navigation|NavHost|composable\("),
    ("viewmodel", r"ViewModel|androidx\.lifecycle"),
    ("coroutines", r"kotlinx\.coroutines|suspend fun|Flow<|StateFlow<"),
    ("android_api", r"import android\.|android\.content|android\.app|android\.os"),
    ("datastore", r"androidx\.datastore"),
    ("workmanager", r"androidx\.work"),
    ("network_api", r"retrofit2|okhttp3|@GET|@POST|@PUT|@DELETE|@PATCH|Retrofit\.Builder|OkHttpClient"),
]

RISK_RULES: list[tuple[str, str, str, str]] = [
    ("compose", "Compose UI requires ArkUI rewrite", "Convert @Composable screens to ArkUI component/build() pages."),
    ("room", "Room database has no direct Harmony equivalent", "Replace with Harmony relational storage, preferences, or a repository abstraction."),
    ("hilt", "Hilt dependency injection requires replacement", "Use a handwritten service container or ArkTS service registration."),
    ("navigation", "AndroidX Navigation requires route mapping", "Generate ArkUI router pages and migrate route parameters."),
    ("android_api", "Direct Android API usage requires adaptation", "Replace with HarmonyOS APIs or isolate behind platform adapters."),
    ("workmanager", "WorkManager background tasks require replacement", "Migrate to HarmonyOS background task capabilities."),
    ("network_api", "Retrofit/OkHttp API layer requires Harmony HTTP migration", "Generate an ArkTS HTTP client and keep MockServer fixtures for tests."),
]

ANDROID_API_RULES: list[tuple[str, str, str, str]] = [
    (r"\bimport\s+android\.app\.Activity\b|\bAppCompatActivity\b|\bFragmentActivity\b|\bActivity\b", "lifecycle", "Android Activity lifecycle", "UIAbility/Page lifecycle"),
    (r"\bimport\s+androidx\.fragment\.app\.Fragment\b|\bFragment\b", "navigation", "Android Fragment", "ArkUI component/page composition"),
    (r"\bimport\s+android\.content\.Intent\b|\bIntent\s*\(", "navigation", "Intent navigation/data passing", "router.pushUrl/router.back with params"),
    (r"\bimport\s+android\.content\.Context\b|\bContext\b", "context", "Android Context", "common.Context or explicit service injection"),
    (r"\bimport\s+android\.os\.Build\b|\bBuild\.VERSION\b|\bRequiresApi\b", "platform", "Android API level/version gate", "Harmony device info and capability checks"),
    (r"\bimport\s+android\.os\.Parcelable\b|\bParcelable\b|\bParcelize\b", "serialization", "Android Parcelable model", "plain ArkTS model or JSON serialization"),
    (r"\bSharedPreferences\b|\bgetSharedPreferences\s*\(", "storage", "SharedPreferences", "preferences API"),
    (r"\bRoomDatabase\b|\b@Database\b|\b@Entity\b|\b@Dao\b|\b@Query\b|\b@Insert\b", "database", "Room persistence", "relationalStore plus DAO adapter"),
    (r"\bRecyclerView\b|\bListAdapter\b|\bPagingDataAdapter\b|\bDiffUtil\b", "ui", "RecyclerView adapter/list", "ArkUI List/Grid and state array"),
    (r"\bViewModel\b|\bLiveData\b|\bStateFlow\b|\bFlow<|\bsuspend\s+fun\b|\bviewModelScope\b", "state", "Lifecycle/ViewModel/coroutine state", "ArkUI @State/@Observed plus Promise/async"),
    (r"\bGlide\b|\bCoil\b|\bPicasso\b|\bImageView\b", "media", "Android image loading/view", "ArkUI Image with resource/media/http source"),
    (r"\bManifest\.permission\b|\brequestPermissions\b|\bcheckSelfPermission\b", "permission", "Android runtime permission", "abilityAccessCtrl permission flow"),
    (r"\bNotificationManager\b|\bNotificationCompat\b|\bPendingIntent\b", "notification", "Android notifications", "notificationManager Kit"),
    (r"\bWorkManager\b|\bWorker\b|\bCoroutineWorker\b|\bJobScheduler\b|\bAlarmManager\b", "background", "Android background task", "BackgroundTasksKit/WorkScheduler equivalent"),
    (r"\bMediaPlayer\b|\bExoPlayer\b|\bCameraX\b|\bCamera\b|\bLocationManager\b|\bFusedLocationProviderClient\b", "device", "Android media/camera/location", "Harmony media/camera/location kits"),
    (r"\bResources\b|\bR\.(string|drawable|layout|color|dimen)\b", "resources", "Android resources", "Harmony resources/base media/element/profile"),
    (r"\bBroadcastReceiver\b|\bService\b|\bContentProvider\b", "component", "Android app component", "ExtensionAbility or explicit service facade"),
    (r"\bandroidx\.benchmark\b|\bandroidx\.test\.uiautomator\b|\bUiDevice\b|\bUiObject2\b|\bBaselineProfileRule\b", "test", "Android benchmark/UIAutomator", "Harmony UITest and performance test"),
    (r"\bRetrofit\b|\bOkHttpClient\b|@GET\b|@POST\b|@PUT\b|@DELETE\b|@PATCH\b", "network", "Retrofit/OkHttp", "NetworkKit http client"),
]


def analyze_project(root: Path) -> tuple[AndroidProject, list[MigrationIssue]]:
    root = root.resolve()
    settings = _first_existing(root, ["settings.gradle.kts", "settings.gradle"])
    module_names = _parse_modules(settings) if settings else []
    modules: list[AndroidModule] = []
    issues: list[MigrationIssue] = []

    if not module_names:
        module_names = _discover_modules(root)
    if not module_names and _is_root_gradle_module(root):
        # Single-module Gradle project where the module IS the repo root (root build.gradle
        # + src/main/...), with no `app/` subdir and the manifest under src/main rather than
        # at the root. `_discover_modules` skips the root gradle and `_looks_like_legacy_project`
        # only checks for a root manifest, so such projects otherwise resolved to 0 modules.
        module_names = [""]
    if not module_names and _looks_like_legacy_project(root):
        module_names = [""]

    for module_name in module_names:
        module_path = root / module_name.replace(":", "").replace("/", "\\")
        if not module_path.exists():
            module_path = root / module_name.strip(":").replace(":", "\\")
        gradle_file = _first_existing(module_path, ["build.gradle.kts", "build.gradle"])
        if not gradle_file:
            if module_path == root and _looks_like_legacy_project(root):
                module = _build_legacy_module(root)
                _detect_features(module)
                _detect_android_api_usage(module)
                _add_risk_issues(module, issues)
                modules.append(module)
            continue
        text = _read_text(gradle_file)
        kind = "application" if _looks_like_application_module(text) else "library"
        module = AndroidModule(
            name=module_name.strip(":") or module_path.name,
            path=module_path,
            kind=kind,
            namespace=_extract_assignment(text, "namespace"),
            application_id=_extract_assignment(text, "applicationId"),
            min_sdk=_extract_assignment(text, "minSdk"),
            target_sdk=_extract_assignment(text, "targetSdk"),
            compile_sdk=_extract_assignment(text, "compileSdk"),
            manifest=_first_existing(module_path, ["src/main/AndroidManifest.xml"]),
            dependencies=_extract_dependencies(text),
        )
        module.source_files = _list_source_files(module_path)
        module.resource_files = _list_resource_files(module_path)
        _detect_features(module)
        _detect_android_api_usage(module)
        _add_risk_issues(module, issues)
        modules.append(module)

    gradle_files = list(root.glob("*.gradle*")) + list((root / "gradle").glob("**/*")) if (root / "gradle").exists() else list(root.glob("*.gradle*"))
    return AndroidProject(root=root, name=root.name, modules=modules, settings_file=settings, gradle_files=gradle_files), issues


def _first_existing(root: Path, names: list[str]) -> Path | None:
    for name in names:
        path = root / name
        if path.exists():
            return path
    return None


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _parse_modules(settings: Path) -> list[str]:
    text = _read_text(settings)
    modules: list[str] = []
    for match in re.finditer(r"include\(([^)]+)\)", text):
        body = match.group(1)
        modules.extend(re.findall(r'["\'](:[^"\']+)["\']', body))
    return modules


def _discover_modules(root: Path) -> list[str]:
    modules = []
    for gradle in root.rglob("build.gradle*"):
        if ".gradle" in gradle.parts or "build" in gradle.parts:
            continue
        if gradle.parent == root:
            continue
        rel = gradle.parent.relative_to(root)
        modules.append(":" + ":".join(rel.parts))
    return sorted(dict.fromkeys(modules))


def _looks_like_legacy_project(root: Path) -> bool:
    return (root / "AndroidManifest.xml").exists() and ((root / "src").exists() or (root / "res").exists())


def _is_root_gradle_module(root: Path) -> bool:
    """A single-module Gradle project whose module is the repo root: a build.gradle at the
    root plus the conventional src/main source set (manifest typically under src/main)."""
    has_gradle = _first_existing(root, ["build.gradle.kts", "build.gradle"]) is not None
    return has_gradle and (root / "src" / "main").exists()


def _build_legacy_module(root: Path) -> AndroidModule:
    manifest = _first_existing(root, ["AndroidManifest.xml"])
    manifest_text = _read_text(manifest) if manifest else ""
    package_name = _extract_manifest_package(manifest_text)
    module = AndroidModule(
        name=root.name,
        path=root,
        kind="application",
        namespace=package_name,
        application_id=package_name,
        min_sdk=_extract_manifest_sdk(manifest_text, "minSdkVersion"),
        target_sdk=None,
        compile_sdk=None,
        manifest=manifest,
        dependencies=_legacy_dependencies(root),
    )
    module.source_files = _list_source_files(root)
    module.resource_files = _list_resource_files(root)
    return module


def _extract_assignment(text: str, key: str) -> str | None:
    patterns = [
        rf"{re.escape(key)}\s*=\s*[\"']([^\"']+)[\"']",
        rf"{re.escape(key)}\s+([0-9]+)",
        rf"{re.escape(key)}\s*=\s*([0-9]+)",
        rf"{re.escape(key)}\s*=\s*libs\.versions\.([A-Za-z0-9_.-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _extract_dependencies(text: str) -> list[str]:
    dependencies: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"(implementation|api|ksp|compileOnly|runtimeOnly|debugImplementation|testImplementation|androidTestImplementation)\(", stripped):
            dependencies.append(stripped.rstrip(","))
    return dependencies


def _extract_manifest_package(text: str) -> str | None:
    match = re.search(r'package\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else None


def _extract_manifest_sdk(text: str, attr: str) -> str | None:
    match = re.search(rf'android:{re.escape(attr)}\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else None


def _legacy_dependencies(root: Path) -> list[str]:
    libs = root / "libs"
    if not libs.exists():
        return []
    return [f"files('{path.name}')" for path in sorted(libs.glob("*.jar"))]


def _looks_like_application_module(text: str) -> bool:
    application_markers = [
        "com.android.application",
        "android.application",
        "libs.plugins.android.application",
        "applicationId",
    ]
    return any(marker in text for marker in application_markers)


def _list_source_files(module_path: Path) -> list[Path]:
    roots = [module_path / "src" / "main", module_path / "src"]
    files: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in SOURCE_EXTENSIONS and path not in seen:
                seen.add(path)
                files.append(path)
    return files


def _list_resource_files(module_path: Path) -> list[Path]:
    roots = [module_path / "src" / "main" / "res", module_path / "res"]
    files: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path not in seen:
                seen.add(path)
                files.append(path)
    return files


def _detect_features(module: AndroidModule) -> None:
    combined = "\n".join(_read_text(path) for path in module.source_files)
    dep_text = "\n".join(module.dependencies)
    for name, pattern in FEATURE_PATTERNS:
        if re.search(pattern, combined) or re.search(pattern, dep_text):
            module.features.add(name)


def _detect_android_api_usage(module: AndroidModule) -> None:
    seen: set[tuple[str, str, int]] = set()
    for path in module.source_files:
        text = _read_text(path)
        rel = str(path.relative_to(module.path)) if path.is_relative_to(module.path) else str(path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            for pattern, category, api, target in ANDROID_API_RULES:
                if not re.search(pattern, stripped):
                    continue
                key = (api, rel, line_number)
                if key in seen:
                    continue
                seen.add(key)
                module.android_api_usages.append(
                    AndroidApiUsage(
                        api=api,
                        category=category,
                        file=rel,
                        line=line_number,
                        snippet=stripped[:220],
                        harmony_target=target,
                        status=_api_status(category),
                    )
                )
                if category in {"network"}:
                    module.features.add("network_api")
                elif category in {"database"}:
                    module.features.add("room")
                else:
                    module.features.add("android_api")


def _api_status(category: str) -> str:
    if category in {"network", "database", "resources", "ui"}:
        return "partially-generated"
    return "adapter-required"


def _add_risk_issues(module: AndroidModule, issues: list[MigrationIssue]) -> None:
    for feature, message, suggestion in RISK_RULES:
        if feature in module.features:
            issues.append(
                MigrationIssue(
                    severity="high" if feature in {"compose", "android_api"} else "medium",
                    category=feature,
                    file=str(module.path),
                    message=f"{module.name}: {message}",
                    suggestion=suggestion,
                )
            )
