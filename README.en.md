# Android → HarmonyOS Transpiler

A local tool that transpiles Chinese Android client apps into HarmonyOS ArkTS / ArkUI (Stage model) projects. Pipeline: **analyze the Android project → generate a HarmonyOS project → compile and auto-repair compile errors → install on a HarmonyOS emulator to verify**. Optionally calls Mimo (mimo-v2.5-pro) to refine ArkUI pages page-by-page.

> 中文版见 [README.md](README.md)

## What It Does

- Analyzes Gradle Android projects: modules, manifests, sources, resources, dependencies, migration risks.
- Generates a HarmonyOS Stage Model project that DevEco Studio / Hvigor can open and build.
- Maps Android XML layouts into ArkUI page drafts.
- Migrates strings, images, fonts, and keeps an original Android XML/source snapshot.
- Produces migration-workspace artifacts: understanding, planning, migration tasks, UITest DSL, repair loop, reports.
- **Self-sufficient repair loop**: when the build fails it locates and fixes ArkTS errors and iterates until it passes (deterministic fixups + LLM repair + guaranteed-compile fallback), with no manual per-project patching.
- Batch conversion of multiple Android repositories.
- Device validation via `hdc` / `aa start` / `uitest` (install + screenshot).

## Supported Scope

- ✅ **Supported**: Gradle projects, legacy Android projects, XML layouts, DataBinding, Jetpack Compose, single Activity + Fragment.
- ❌ **Not supported**: game / custom-render engines (libGDX, Unity), cross-platform frameworks (React Native, Flutter).

## Worked Examples: 5 Open-Source Android Clients

End-to-end transpile + build-repair + on-device verification was run against 5 open-source Chinese clients within scope. Full report and side-by-side screenshots: **[`examples/test5-5apps/REPORT.md`](examples/test5-5apps/REPORT.md)**.

| Project | Type | Initial errors | Repair iters | Build result |
|---|---|---|---|---|
| JetpackMVVM | single Activity+Fragment / MVVM | 7 | 2 | ✅ pass |
| PlayAndroid | partial Compose + .kts | 115 | 5 | ✅ pass |
| WanAndroidGoweii | DataBinding + ViewPager | 377→147 | 5 | ✅ pass |
| YCVideoPlayer | video-player sample set | 126 | 5 | ✅ pass |
| KingTV | live-stream / video client | 46 | 5 | ✅ pass |

- **5/5 compile green into HAPs**; 4/5 passed on the first try, 1 (WanAndroidGoweii) failed and was fixed by a **root-cause fix in the transpiler** (guarantee exactly one `@Entry` per routed page + structural-error self-healing) then re-transpiled to pass — the fix lives in transpiler code, not per-project patches.
- 5/5 render real business UI on the HarmonyOS emulator (song lists / article feeds / live streams / player menus), not debug shells.

HarmonyOS emulator screenshots:

| JetpackMVVM | PlayAndroid | WanAndroidGoweii | YCVideoPlayer | KingTV |
|---|---|---|---|---|
| ![](examples/test5-5apps/screenshots/JetpackMVVM.jpeg) | ![](examples/test5-5apps/screenshots/PlayAndroid2.jpeg) | ![](examples/test5-5apps/screenshots/WanAndroidGoweii.jpeg) | ![](examples/test5-5apps/screenshots/YCVideoPlayer2.jpeg) | ![](examples/test5-5apps/screenshots/KingTV.jpeg) |

### Single-Project Deep Dive (input/output and directory layout)

Want to see exactly what the transpiler "eats and emits"? **[`examples/jetpackmvvm-deep-dive/`](examples/jetpackmvvm-deep-dive/README.md)** lays one project fully open:

- `android-original/` — the original Android source (71 Java + 34 XML).
- `harmony-output/` — the generated HarmonyOS project (101 `.ets`, build caches stripped), with a fully annotated **output directory structure**.
- Login-page **before/after code comparison** (DataBinding XML → ArkUI `@State` declarative UI).

## Requirements

- Python 3.10+ (runtime uses the standard library only).
- HarmonyOS toolchain: DevEco Studio (hvigor, node, hdc, SDK) — needed for build/install.
- (Optional) a Mimo account for page-level refinement and migration-artifact enhancement.

## Configuring Mimo (never commit the token)

The token is supplied via environment variables or a local `.env`. **`.env` is in `.gitignore` and is not committed.** Create `.env` in the repo root:

```dotenv
ANDROID2HARMONY_LLM_MODEL=mimo-v2.5-pro
# Anthropic-compatible endpoint (one of the two)
ANTHROPIC_BASE_URL=https://token-plan-sgp.xiaomimimo.com/anthropic
ANTHROPIC_AUTH_TOKEN=<your-token>
# Or OpenAI-compatible endpoint
# ANDROID2HARMONY_LLM_PROVIDER=openai-compatible
# OPENAI_BASE_URL=https://token-plan-sgp.xiaomimimo.com/v1
# OPENAI_API_KEY=<your-token>
```

The CLI auto-loads `.env` on startup. Test connectivity:

```powershell
python -m android2harmony.cli llm-check
```

## Three-Step Usage

```powershell
# 1. Transpile: analyze the Android project + LLM-generate the HarmonyOS project
python -m android2harmony.cli convert "<AndroidProjectDir>" -o "<OutputDir>" --force --llm-refine-pages

# 2. Build and auto-repair compile errors (iterate until it passes)
python -m android2harmony.cli repair-build "<OutputDir>" --max-iters 5

# 3. Install on a HarmonyOS emulator and screenshot
#    (first ensure `hdc list targets` shows a device, e.g. 127.0.0.1:5555)
python -m android2harmony.cli validate-device "<OutputDir>" --bundle <bundleName>
```

- `<bundleName>` comes from the `bundleName` field in `AppScope/app.json5` of the output dir.
- Source-only (no build): run step 1 only, then open the output dir in DevEco Studio.
- Large projects are slow by design: one model inference per page, 4-way parallel by default (`ANDROID2HARMONY_LLM_CONCURRENCY` to tune).

## Output Layout

Inside the output directory:

| Item | Location |
|---|---|
| Generated ArkUI page source | `entry/src/main/ets/pages/*.ets` |
| Migration report (API/network/DB/risks/unfinished) | `migration-report.md` |
| UI fidelity report (entry screen, per-page LLM/fallback/placeholder, known gaps) | `agent-workspace/03-migration/ui-fidelity-report.md` |
| LLM call logs | `agent-workspace/llm-calls/` |
| On-device screenshot (from step 3) | `uitest-screenshot.png` |
| Open in DevEco | open the whole output directory |

## Other Commands

```powershell
python -m android2harmony.cli analyze "<AndroidProjectDir>"        # analyze only: modules/pages/risks
python -m android2harmony.cli batch-convert "<DirWithManyApps>" -o "<OutRoot>" --force --llm-refine-pages
python -m android2harmony.cli web --host 127.0.0.1 --port 8765     # web UI: upload a zip to transpile
```

## Known Limits

This is not a full semantic compiler. Room, Hilt, Android Framework API calls, MediaStore, permissions, real data binding, and full navigation still need migration rules or LLM-assisted repair stages. These gaps are surfaced explicitly in the migration report and workspace files.

## Tests

```powershell
python -m pytest
```
