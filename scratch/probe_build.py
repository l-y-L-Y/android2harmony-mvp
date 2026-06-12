import os, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
for line in (root / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
sys.path.insert(0, str(root))
from android2harmony.build_repair import run_hvigor_build, parse_build_errors

proj = Path("D:/codex/out/oschina-harmony-v2")
ok, log = run_hvigor_build(proj)
(root / "scratch" / "probe_build.log").write_text(log, encoding="utf-8")
errs = parse_build_errors(log)
print("ok=", ok)
print("log_chars=", len(log))
print("parsed_files=", len(errs), "total_errors=", sum(len(v) for v in errs.values()))
print("--- tail ---")
print(log[-800:])
