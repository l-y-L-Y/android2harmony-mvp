import os, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
env = root / ".env"
for line in env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
sys.path.insert(0, str(root))
from android2harmony.llm_page_agent import generate_arkui_page, validate_page

layout = Path("D:/codex/android-benchmarks/OSChinaAndroid/res/layout/login_dialog.xml")
xml = layout.read_text(encoding="utf-8", errors="ignore")
# available media stems from OSChina drawables (lowercased, sanitized roughly)
media = {p.stem.lower() for p in Path("D:/codex/android-benchmarks/OSChinaAndroid/res/drawable").glob("*.png")}
code = generate_arkui_page("LoginDialog", xml, "开源中国", available_media=media, max_tokens=12000)
ok, reason = validate_page(code, "LoginDialog")
out = root / "scratch" / "e2e_LoginDialog.ets"
out.write_text(code, encoding="utf-8")
print(f"valid={ok} reason='{reason}' chars={len(code)} -> {out}")
