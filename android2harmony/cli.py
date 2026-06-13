from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _load_dotenv() -> None:
    """Load KEY=value lines from a local .env (cwd or repo root) into the environment,
    so the LLM token/base-url just work without the user exporting them each time.
    Existing environment variables win."""
    candidates = [Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env"]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
        break


from .analyzer import analyze_project
from .batch import batch_convert
from .build_summary import write_build_summary
from .generator import generate_harmony_project
from .device_validator import validate_dsl_on_device, validate_on_device
from .emulator import run_emulator_diagnostic
from .llm_agents import LLMRefineOptions
from .llm_provider import call_llm, load_llm_config_from_env
from .repair import write_repair_diagnosis
from .report_index import write_report_index
from .uitrans_rules import write_uitrans_rule_index
from .web_server import run as run_web_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="android2harmony", description="Generate HarmonyOS migration scaffolds from Android projects.")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze an Android project and print a summary.")
    analyze.add_argument("project", type=Path)

    convert = sub.add_parser("convert", help="Generate a HarmonyOS project scaffold.")
    convert.add_argument("project", type=Path)
    convert.add_argument("--output", "-o", type=Path, required=True)
    convert.add_argument("--force", action="store_true")
    convert.add_argument("--llm-refine-pages", action="store_true", help="Use the configured LLM to refine generated ArkUI pages.")
    convert.add_argument("--llm-all-agents", action="store_true", help="Prefer the configured LLM for every migration agent, falling back to rules when validation fails.")
    convert.add_argument("--llm-max-pages", type=int, default=0, help="Maximum number of pages to refine with LLM. 0 means no limit.")
    convert.add_argument("--uitrans-index", type=Path, default=Path("rules/uitrans-index.json"), help="Path to indexed UITrans rule summary.")

    repair_build_p = sub.add_parser("repair-build", help="Build with hvigor and LLM-repair ArkTS compile errors until it passes.")
    repair_build_p.add_argument("project", type=Path)
    repair_build_p.add_argument("--max-iters", type=int, default=3)

    llm = sub.add_parser("llm-check", help="Check the configured LLM provider without storing secrets.")
    llm.add_argument("--prompt", default="Reply with OK and your model name.")

    rules = sub.add_parser("index-uitrans", help="Index UITrans migration prompts and ArkUI reference docs.")
    rules.add_argument("uitrans", type=Path)
    rules.add_argument("--output", "-o", type=Path, required=True)

    web = sub.add_parser("web", help="Start the local upload-and-convert web UI.")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)

    validate = sub.add_parser("validate-device", help="Install and launch the generated HarmonyOS app on an hdc target.")
    validate.add_argument("project", type=Path)
    validate.add_argument("--hdc", type=Path, default=Path("D:/DevEco Studio/sdk/default/openharmony/toolchains/hdc.exe"))
    validate.add_argument("--bundle", default="com.generated.simplegallery")
    validate.add_argument("--ability", default="EntryAbility")
    validate.add_argument("--click-text", help="Optional UITest text target to click after launch.")

    validate_dsl = sub.add_parser("validate-dsl", help="Run generated UITest DSL on an hdc target and write repair input.")
    validate_dsl.add_argument("project", type=Path)
    validate_dsl.add_argument("--hdc", type=Path, default=Path("D:/DevEco Studio/sdk/default/openharmony/toolchains/hdc.exe"))
    validate_dsl.add_argument("--bundle", default="com.generated.simplegallery")
    validate_dsl.add_argument("--ability", default="EntryAbility")
    validate_dsl.add_argument("--dsl", type=Path, help="Optional path to test-dsl.json.")
    validate_dsl.add_argument("--no-emulator-diagnostics", action="store_true", help="Skip DevEco emulator diagnostics when hdc is offline.")
    validate_dsl.add_argument("--repair-diagnose", action="store_true", help="Write LLM repair diagnosis and patch plan when DSL validation fails.")

    repair = sub.add_parser("repair-diagnose", help="Use the configured LLM to diagnose build or DSL validation failures.")
    repair.add_argument("project", type=Path)
    repair.add_argument("--validation", type=Path, help="Optional device-validation-result.json path.")
    repair.add_argument("--build-log", type=Path, help="Optional Hvigor build log path.")

    build_summary = sub.add_parser("build-summary", help="Parse a DevEco/Hvigor build log and write report artifacts.")
    build_summary.add_argument("project", type=Path)
    build_summary.add_argument("--log", type=Path, required=True, help="Path to captured Hvigor build log.")

    report_index = sub.add_parser("report-index", help="Aggregate build, validation, and repair summaries into one index.")
    report_index.add_argument("project", type=Path)

    emulator = sub.add_parser("emulator-diagnose", help="Discover/start a DevEco emulator instance and wait for hdc.")
    emulator.add_argument("--emulator", type=Path, default=Path("D:/DevEco Studio/tools/emulator/Emulator.exe"))
    emulator.add_argument("--hdc", type=Path, default=Path("D:/DevEco Studio/sdk/default/openharmony/toolchains/hdc.exe"))
    emulator.add_argument("--name", help="Optional DevEco emulator instance name.")
    emulator.add_argument("--wait-seconds", type=int, default=60)
    emulator.add_argument("--hdc-port", type=int, default=15000)
    emulator.add_argument("--report", type=Path)
    emulator.add_argument("--deployed-root", type=Path, help="DevEco emulator deployed root that contains device folders.")
    emulator.add_argument("--image-root", type=Path, help="Huawei SDK image root that contains system-image/...")

    batch = sub.add_parser("batch-convert", help="Convert every Gradle Android project under a directory.")
    batch.add_argument("input_root", type=Path)
    batch.add_argument("--output-root", "-o", type=Path, required=True)
    batch.add_argument("--force", action="store_true")
    batch.add_argument("--llm-refine-pages", action="store_true")
    batch.add_argument("--llm-all-agents", action="store_true")
    batch.add_argument("--llm-max-pages", type=int, default=0)
    batch.add_argument("--uitrans-index", type=Path, default=Path("rules/uitrans-index.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    _load_dotenv()
    args = build_parser().parse_args(argv)
    try:
        if args.command == "llm-check":
            config = load_llm_config_from_env()
            print(f"Provider: {config.provider}")
            print(f"Base URL configured: {bool(config.base_url)}")
            print(f"Model: {config.model}")
            print(call_llm(args.prompt, max_tokens=256))
            return 0

        if args.command == "repair-build":
            from .build_repair import repair_build
            result = repair_build(args.project, args.max_iters, log_sink=lambda m: print(m, flush=True))
            print(json.dumps({
                "passed": result.passed,
                "iterations": result.iterations,
                "initialErrors": result.initial_error_count,
                "finalErrors": result.final_error_count,
                "repairedFiles": result.repaired_files,
            }, ensure_ascii=False, indent=2))
            return 0 if result.passed else 1

        if args.command == "index-uitrans":
            write_uitrans_rule_index(args.uitrans, args.output)
            print(f"Wrote UITrans rule index: {args.output}")
            return 0

        if args.command == "web":
            run_web_server(args.host, args.port)
            return 0

        if args.command == "validate-device":
            result = validate_on_device(args.project, args.hdc, args.bundle, args.ability, args.click_text)
            print(result.report)
            click_ok = True if not args.click_text else result.clicked
            return 0 if result.started and result.layout_dumped and result.screenshot_captured and click_ok else 1

        if args.command == "validate-dsl":
            result = validate_dsl_on_device(
                args.project,
                args.hdc,
                args.bundle,
                args.ability,
                args.dsl,
                not args.no_emulator_diagnostics,
                args.repair_diagnose,
            )
            print(result.report)
            return 0 if result.passed else 1

        if args.command == "repair-diagnose":
            output = write_repair_diagnosis(args.project, args.validation, args.build_log)
            print(f"Repair diagnosis: {output}")
            return 0

        if args.command == "build-summary":
            output = write_build_summary(args.project, args.log)
            write_report_index(args.project)
            print(f"Build summary: {output}")
            return 0

        if args.command == "report-index":
            output = write_report_index(args.project)
            print(f"Report index: {output}")
            return 0

        if args.command == "emulator-diagnose":
            result = run_emulator_diagnostic(
                args.emulator,
                args.hdc,
                args.name,
                args.wait_seconds,
                args.hdc_port,
                args.report,
                args.deployed_root or Path.home() / "AppData" / "Local" / "Huawei" / "Emulator" / "deployed",
                args.image_root or Path.home() / "AppData" / "Local" / "Huawei" / "Sdk",
            )
            print(result.summary())
            return 0 if result.online else 1

        if args.command == "batch-convert":
            llm_options = LLMRefineOptions(
                enabled=args.llm_refine_pages or args.llm_all_agents,
                all_agents=args.llm_all_agents,
                max_pages=args.llm_max_pages,
                uitrans_index=(Path.cwd() / args.uitrans_index if not args.uitrans_index.is_absolute() else args.uitrans_index),
            )
            summary = batch_convert(args.input_root, args.output_root, args.force, llm_options)
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return 0

        project, issues = analyze_project(args.project)
        if args.command == "analyze":
            print(f"Project: {project.name}")
            print(f"Root: {project.root}")
            print(f"Modules: {len(project.modules)}")
            for module in project.modules:
                print(f"- {module.name} [{module.kind}] sources={len(module.source_files)} resources={len(module.resource_files)} features={','.join(sorted(module.features)) or 'none'}")
            print(f"Issues: {len(issues)}")
            for issue in issues:
                print(f"- {issue.severity} {issue.category}: {issue.message}")
            return 0

        llm_options = LLMRefineOptions(
            enabled=args.llm_refine_pages or args.llm_all_agents,
            all_agents=args.llm_all_agents,
            max_pages=args.llm_max_pages,
            uitrans_index=(Path.cwd() / args.uitrans_index if not args.uitrans_index.is_absolute() else args.uitrans_index),
        )
        result = generate_harmony_project(project, issues, args.output, args.force, llm_options=llm_options)
        print(f"Generated: {result.output_dir}")
        print(f"Generated files: {len(result.generated_files)}")
        print(f"Copied files: {len(result.copied_files)}")
        print(f"Issues: {len(result.issues)}")
        print(f"Report: {result.output_dir / 'migration-report.md'}")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
