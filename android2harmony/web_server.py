from __future__ import annotations

import json
import mimetypes
import shutil
import time
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .analyzer import analyze_project
from .generator import generate_harmony_project
from .llm_agents import LLMRefineOptions


REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = REPO_ROOT / "web"
DEFAULT_WORK_ROOT = Path("D:/codex/out/web-migrations")
MAX_UPLOAD_BYTES = 1024 * 1024 * 1024


class WebMigrationError(Exception):
    pass


class MigrationWebHandler(BaseHTTPRequestHandler):
    server_version = "android2harmony-web/0.1"

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/downloads/"):
            name = unquote(parsed.path.removeprefix("/downloads/"))
            self._send_download(DEFAULT_WORK_ROOT / name, head_only=True)
            return
        target = WEB_ROOT / "index.html" if parsed.path == "/" else (WEB_ROOT / parsed.path.removeprefix("/")).resolve()
        if not _is_relative_to(target, WEB_ROOT):
            self.send_response(400)
            self.end_headers()
            return
        self._send_file(target, head_only=True)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_file(WEB_ROOT / "index.html")
            return
        if parsed.path.startswith("/downloads/"):
            name = unquote(parsed.path.removeprefix("/downloads/"))
            self._send_download(DEFAULT_WORK_ROOT / name)
            return
        target = (WEB_ROOT / parsed.path.removeprefix("/")).resolve()
        if not _is_relative_to(target, WEB_ROOT):
            self._send_json({"error": "invalid static path"}, status=400)
            return
        self._send_file(target)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/convert":
            self._send_json({"error": "not found"}, status=404)
            return
        try:
            result = self._handle_convert()
            self._send_json(result)
        except WebMigrationError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:
            self._send_json({"error": f"conversion failed: {exc}"}, status=500)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[web] {self.address_string()} - {fmt % args}")

    def _handle_convert(self) -> dict[str, object]:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            raise WebMigrationError("empty request")
        if content_length > MAX_UPLOAD_BYTES:
            raise WebMigrationError("upload is too large")

        content_type = self.headers.get("Content-Type", "")
        boundary = _multipart_boundary(content_type)
        if not boundary:
            raise WebMigrationError("expected multipart/form-data upload")
        body = self.rfile.read(content_length)
        fields, files = _parse_multipart(body, boundary)
        if "archive" not in files:
            raise WebMigrationError("missing archive file")

        filename, archive_bytes = files["archive"]
        if not filename.lower().endswith(".zip"):
            raise WebMigrationError("only .zip archives are supported")

        job_id = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        job_root = DEFAULT_WORK_ROOT / job_id
        upload_dir = job_root / "upload"
        source_dir = job_root / "source"
        output_dir = job_root / "harmony"
        upload_dir.mkdir(parents=True, exist_ok=True)
        archive_path = upload_dir / _safe_filename(filename)
        archive_path.write_bytes(archive_bytes)

        _extract_zip_safe(archive_path, source_dir)
        android_root = _find_android_project_root(source_dir)
        if android_root is None:
            raise WebMigrationError("no Gradle Android project found in uploaded archive")

        llm_all_agents = fields.get("llmAllAgents", "false") == "true"
        llm_enabled = fields.get("llmRefine", "false") == "true" or llm_all_agents
        max_pages = int(fields.get("llmMaxPages", "0") or "0")
        project, issues = analyze_project(android_root)
        llm_options = LLMRefineOptions(enabled=llm_enabled, all_agents=llm_all_agents, max_pages=max_pages, uitrans_index=REPO_ROOT / "rules" / "uitrans-index.json")
        result = generate_harmony_project(project, issues, output_dir, force=True, llm_options=llm_options)

        zip_base = DEFAULT_WORK_ROOT / f"{job_id}-harmony"
        archive_output = shutil.make_archive(str(zip_base), "zip", output_dir)
        report_md = output_dir / "migration-report.md"
        report_json = output_dir / "migration-report.json"
        report_preview = report_md.read_text(encoding="utf-8-sig", errors="ignore")[:12000] if report_md.exists() else ""
        report_md_url = ""
        report_json_url = ""
        if report_md.exists():
            report_copy = DEFAULT_WORK_ROOT / f"{job_id}-migration-report.md"
            shutil.copy2(report_md, report_copy)
            report_md_url = f"/downloads/{report_copy.name}"
        if report_json.exists():
            report_json_copy = DEFAULT_WORK_ROOT / f"{job_id}-migration-report.json"
            shutil.copy2(report_json, report_json_copy)
            report_json_url = f"/downloads/{report_json_copy.name}"

        return {
            "jobId": job_id,
            "projectName": project.name,
            "androidRoot": str(android_root),
            "outputDir": str(output_dir),
            "downloadUrl": f"/downloads/{Path(archive_output).name}",
            "reportMdUrl": report_md_url,
            "reportJsonUrl": report_json_url,
            "generatedFiles": len(result.generated_files),
            "copiedFiles": len(result.copied_files),
            "issues": len(result.issues),
            "features": result.features,
            "reportPreview": report_preview,
        }

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path, head_only: bool = False) -> None:
        if not path.exists() or not path.is_file():
            self._send_json({"error": "not found"}, status=404)
            return
        data = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if content_type == "text/html":
            content_type = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    def _send_download(self, path: Path, head_only: bool = False) -> None:
        path = path.resolve()
        if not _is_relative_to(path, DEFAULT_WORK_ROOT) or not path.exists() or path.suffix.lower() not in {".zip", ".md", ".json"}:
            self._send_json({"error": "download not found"}, status=404)
            return
        data = path.read_bytes()
        self.send_response(200)
        content_type = {
            ".zip": "application/zip",
            ".md": "text/markdown; charset=utf-8",
            ".json": "application/json; charset=utf-8",
        }.get(path.suffix.lower(), "application/octet-stream")
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if not head_only:
            self.wfile.write(data)


def _multipart_boundary(content_type: str) -> bytes | None:
    for item in content_type.split(";"):
        item = item.strip()
        if item.startswith("boundary="):
            value = item.split("=", 1)[1].strip('"')
            return value.encode("utf-8")
    return None


def _parse_multipart(body: bytes, boundary: bytes) -> tuple[dict[str, str], dict[str, tuple[str, bytes]]]:
    fields: dict[str, str] = {}
    files: dict[str, tuple[str, bytes]] = {}
    marker = b"--" + boundary
    for part in body.split(marker):
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        if part.endswith(b"--"):
            part = part[:-2].rstrip(b"\r\n")
        header_blob, sep, data = part.partition(b"\r\n\r\n")
        if not sep:
            continue
        headers = header_blob.decode("utf-8", errors="ignore").split("\r\n")
        disposition = next((h for h in headers if h.lower().startswith("content-disposition:")), "")
        attrs = _header_attrs(disposition)
        name = attrs.get("name")
        if not name:
            continue
        if "filename" in attrs:
            files[name] = (attrs["filename"], data.rstrip(b"\r\n"))
        else:
            fields[name] = data.decode("utf-8", errors="ignore").strip()
    return fields, files


def _header_attrs(value: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for item in value.split(";"):
        item = item.strip()
        if "=" not in item:
            continue
        key, raw = item.split("=", 1)
        attrs[key.strip()] = raw.strip().strip('"')
    return attrs


def _safe_filename(value: str) -> str:
    name = Path(value).name.replace("\\", "_").replace("/", "_")
    return name or "android-project.zip"


def _extract_zip_safe(archive: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            dest = (target / info.filename).resolve()
            if not _is_relative_to(dest, target.resolve()):
                raise WebMigrationError(f"unsafe zip entry: {info.filename}")
        zf.extractall(target)


def _find_android_project_root(root: Path) -> Path | None:
    candidates: list[Path] = []
    for path in [root, *root.rglob("*")]:
        if not path.is_dir():
            continue
        has_settings = any((path / name).exists() for name in ["settings.gradle", "settings.gradle.kts"])
        has_build = any((path / name).exists() for name in ["build.gradle", "build.gradle.kts"])
        has_manifest = bool(list(path.glob("*/src/main/AndroidManifest.xml"))) or (path / "src/main/AndroidManifest.xml").exists()
        if has_settings and has_build:
            candidates.append(path)
        elif has_build and has_manifest:
            candidates.append(path)
    if not candidates:
        return None
    candidates.sort(key=lambda item: (len(item.relative_to(root).parts), str(item)))
    return candidates[0]


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def run(host: str = "127.0.0.1", port: int = 8765) -> None:
    DEFAULT_WORK_ROOT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), MigrationWebHandler)
    print(f"android2harmony web UI: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
