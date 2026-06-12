from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


DEFAULT_EMULATOR = Path("D:/DevEco Studio/tools/emulator/Emulator.exe")
DEFAULT_HDC = Path("D:/DevEco Studio/sdk/default/openharmony/toolchains/hdc.exe")
DEFAULT_DEPLOYED = Path.home() / "AppData" / "Local" / "Huawei" / "Emulator" / "deployed"
DEFAULT_IMAGE_ROOT = Path.home() / "AppData" / "Local" / "Huawei" / "Sdk"


@dataclass
class EmulatorDevice:
    name: str
    path: Path
    image_root: Path | None
    api_version: str
    model: str


@dataclass
class EmulatorDiagnostic:
    devices: list[EmulatorDevice]
    selected: EmulatorDevice | None
    command: list[str]
    process_started: bool
    process_exit_code: int | None
    process_output: str
    hdc_targets: list[str]
    log_summaries: list[dict[str, str]]
    report_file: Path | None = None

    @property
    def online(self) -> bool:
        return any(target and target != "[Empty]" for target in self.hdc_targets)

    def to_dict(self) -> dict[str, object]:
        return {
            "devices": [
                {
                    "name": item.name,
                    "path": str(item.path),
                    "imageRoot": str(item.image_root) if item.image_root else "",
                    "apiVersion": item.api_version,
                    "model": item.model,
                }
                for item in self.devices
            ],
            "selected": self.selected.name if self.selected else "",
            "command": self.command,
            "processStarted": self.process_started,
            "processExitCode": self.process_exit_code,
            "processOutput": self.process_output,
            "hdcTargets": self.hdc_targets,
            "logSummaries": self.log_summaries,
            "online": self.online,
            "reportFile": str(self.report_file) if self.report_file else "",
        }

    def summary(self) -> str:
        lines = [
            "Emulator diagnostic:",
            f"- discovered devices: {len(self.devices)}",
            f"- selected: {self.selected.name if self.selected else 'none'}",
            f"- process started: {self.process_started}",
            f"- process exit code: {self.process_exit_code if self.process_exit_code is not None else 'running/unknown'}",
            f"- hdc targets: {', '.join(self.hdc_targets) if self.hdc_targets else '[Empty]'}",
        ]
        if self.command:
            lines.append(f"- command: {' '.join(self.command)}")
        if self.process_output:
            lines.append(f"- process output: {self.process_output.strip()}")
        for item in self.log_summaries[:3]:
            lines.append(f"- log {item.get('file', '')}: {item.get('matched', '') or item.get('tail', '')[:240]}")
        if self.report_file:
            lines.append(f"- report: {self.report_file}")
        return "\n".join(lines)


def discover_deveco_emulators(deployed_root: Path = DEFAULT_DEPLOYED, image_root: Path = DEFAULT_IMAGE_ROOT) -> list[EmulatorDevice]:
    list_file = deployed_root / "lists.json"
    devices: list[EmulatorDevice] = []
    if list_file.exists():
        try:
            raw = json.loads(list_file.read_text(encoding="utf-8", errors="ignore"))
        except json.JSONDecodeError:
            raw = []
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "")).strip()
                path = Path(str(item.get("path", "")))
                image_dir = str(item.get("imageDir", "")).strip().replace("/", "\\")
                full_image_root = image_root / image_dir if image_dir else None
                if name and path:
                    devices.append(
                        EmulatorDevice(
                            name=name,
                            path=path,
                            image_root=full_image_root,
                            api_version=str(item.get("apiVersion", "")),
                            model=str(item.get("model", "")),
                        )
                    )
    if not devices:
        for ini in deployed_root.glob("*.ini"):
            name = ini.stem
            path = _read_ini_value(ini, "path")
            config = Path(path) / "config.ini" if path else deployed_root / name / "config.ini"
            image_sub_path = _read_ini_value(config, "imageSubPath")
            devices.append(
                EmulatorDevice(
                    name=name,
                    path=Path(path) if path else deployed_root / name,
                    image_root=(image_root / image_sub_path.replace("/", "\\")) if image_sub_path else None,
                    api_version=_read_ini_value(config, "os.apiVersion"),
                    model=_read_ini_value(config, "productModel") or name,
                )
            )
    if not devices:
        for directory in deployed_root.iterdir() if deployed_root.exists() else []:
            if not directory.is_dir():
                continue
            config = directory / "config.ini"
            if not config.exists():
                continue
            image_sub_path = _read_ini_value(config, "imageSubPath")
            devices.append(
                EmulatorDevice(
                    name=_read_ini_value(config, "name") or directory.name,
                    path=directory,
                    image_root=(image_root / image_sub_path.replace("/", "\\")) if image_sub_path else None,
                    api_version=_read_ini_value(config, "os.apiVersion"),
                    model=_read_ini_value(config, "productModel") or directory.name,
                )
            )
    return devices


def run_emulator_diagnostic(
    emulator: Path = DEFAULT_EMULATOR,
    hdc: Path = DEFAULT_HDC,
    name: str | None = None,
    wait_seconds: int = 60,
    hdc_port: int = 15000,
    report_file: Path | None = None,
    deployed_root: Path = DEFAULT_DEPLOYED,
    image_root: Path = DEFAULT_IMAGE_ROOT,
) -> EmulatorDiagnostic:
    devices = discover_deveco_emulators(deployed_root, image_root)
    selected = _select_device(devices, name)
    command: list[str] = []
    process_started = False
    process_exit_code: int | None = None
    process_output = ""
    hdc_targets: list[str] = []
    if selected and emulator.exists():
        command = [
            str(emulator),
            "-hvd",
            selected.name,
            "-path",
            str(selected.path.parent),
        ]
        if selected.image_root:
            command.extend(["-imageRoot", str(selected.image_root)])
        command.extend(["-hdcport", str(hdc_port)])
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process_started = True
        deadline = time.time() + max(wait_seconds, 1)
        while time.time() <= deadline:
            target = _list_hdc_targets(hdc)
            hdc_targets.append(target)
            if target and target != "[Empty]":
                break
            if process.poll() is not None:
                process_exit_code = process.returncode
                stdout, stderr = process.communicate(timeout=5)
                process_output = (stdout or "") + (stderr or "")
                break
            time.sleep(5)
        if process_exit_code is None and process.poll() is not None:
            process_exit_code = process.returncode
            stdout, stderr = process.communicate(timeout=5)
            process_output = (stdout or "") + (stderr or "")
        if not hdc_targets:
            hdc_targets.append(_list_hdc_targets(hdc))
    else:
        hdc_targets.append(_list_hdc_targets(hdc))
        if not emulator.exists():
            process_output = f"Emulator executable not found: {emulator}"
        elif not selected:
            process_output = "No DevEco emulator instance found."
    diagnostic = EmulatorDiagnostic(
        devices=devices,
        selected=selected,
        command=command,
        process_started=process_started,
        process_exit_code=process_exit_code,
        process_output=process_output.strip(),
        hdc_targets=hdc_targets,
        log_summaries=_collect_log_summaries(selected),
        report_file=report_file,
    )
    if report_file:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(diagnostic.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return diagnostic


def _select_device(devices: list[EmulatorDevice], name: str | None) -> EmulatorDevice | None:
    if not devices:
        return None
    if name:
        for item in devices:
            if item.name == name:
                return item
    return devices[0]


def _list_hdc_targets(hdc: Path) -> str:
    if not hdc.exists():
        return f"hdc not found: {hdc}"
    result = subprocess.run([str(hdc), "list", "targets"], capture_output=True, text=True, timeout=30)
    output = ((result.stdout or "") + (result.stderr or "")).strip()
    return output or "[Empty]"


def _read_ini_value(path: Path, key: str) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    return ""


def _collect_log_summaries(device: EmulatorDevice | None) -> list[dict[str, str]]:
    if not device:
        return []
    log_dir = device.path / "Log"
    if not log_dir.exists():
        return []
    summaries: list[dict[str, str]] = []
    patterns = [
        "EMULATOR_START_ERROR",
        "NO_ENOUGH_BASEDISK_SPACE_ERR",
        "No enough space",
        "can not read sn",
        "Unable to start",
        "hdc is not connected",
    ]
    files = sorted([item for item in log_dir.rglob("*") if item.is_file()], key=lambda item: item.stat().st_mtime, reverse=True)
    for item in files[:6]:
        text = _read_tail(item, 120)
        matched = ""
        for line in text.splitlines():
            if any(pattern in line for pattern in patterns):
                matched = line.strip()
        summaries.append({"file": str(item), "matched": matched, "tail": text[-1200:]})
    return summaries


def _read_tail(path: Path, max_lines: int) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[-max_lines:])
