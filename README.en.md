# Android to HarmonyOS Migration MVP

This repository contains a local Android-to-HarmonyOS migration tool. It generates DevEco/Hvigor projects, preserves Android source snapshots, creates migration reports, and can optionally use Mimo to refine generated ArkUI pages and agent artifacts.

## What It Does

- Analyzes Gradle Android projects, modules, manifests, source files, resources, dependencies, and migration risks.
- Generates a HarmonyOS Stage Model project that DevEco Studio and Hvigor can open and build.
- Converts Android XML layouts into ArkUI page drafts with rule-based mappings.
- Copies strings, images, fonts, and original Android XML/source snapshots.
- Generates Agent workspace artifacts: understanding, planning, migration tasks, UITest DSL, repair loop, and reports.
- Optionally calls Mimo for page-level ArkUI refinement and all-agent migration artifact enhancement after rule generation.
- Supports batch conversion for multiple Android repositories.
- Supports device validation through `hdc`, `aa start`, `uitest dumpLayout`, and `uitest screenCap`.

## Rule-Only Conversion

```powershell
python -m android2harmony.cli convert <android-project> --output <out-dir> --force
```

## Batch Conversion

```powershell
python -m android2harmony.cli batch-convert <android-dir> --output-root <out-root> --force
```

## Web Upload UI

```powershell
python -m android2harmony.cli web --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`, upload a zipped Android project, and download the generated HarmonyOS project zip after conversion.

## Mimo Agent Enhancement

Do not commit tokens. Set them in the shell only:

```powershell
$env:ANDROID2HARMONY_LLM_PROVIDER = "openai-compatible"
$env:OPENAI_BASE_URL = "https://token-plan-sgp.xiaomimimo.com/v1"
$env:ANDROID2HARMONY_LLM_MODEL = "mimo-v2.5-pro"
$env:OPENAI_API_KEY = "<token>"

python -m android2harmony.cli llm-check
python -m android2harmony.cli convert <android-project> --output <out-dir> --force --llm-all-agents --llm-max-pages 3
```

## Current Limits

This is not a complete semantic compiler. Room, Hilt, Android Framework API calls, media store behavior, permissions, real data binding, and full navigation still require migration rules or LLM-assisted repair stages. The current design keeps those gaps explicit in reports and Agent workspace files.
