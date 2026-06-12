import json, os, urllib.request
from pathlib import Path
env = Path(__file__).resolve().parent.parent / ".env"
for line in env.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())

base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/")
tok = os.environ["ANTHROPIC_AUTH_TOKEN"]
xml = Path("D:/codex/android-benchmarks/OSChinaAndroid/res/layout/about.xml").read_text(encoding="utf-8", errors="ignore")
system = ("You are a senior HarmonyOS ArkUI engineer. Translate one Android XML layout into ONE faithful, "
          "complete, compilable ArkTS page. Return ONLY the .ets file content, no markdown fences.")
prompt = f"""Migrate this Android layout into a single HarmonyOS ArkUI page named `About`.
Preserve every Chinese/English text EXACTLY. Reproduce the bottom-center stacked layout.
Use Text/Button/Image/Column/Stack. No invented resources. No debug navigation.
Output the COMPLETE file, do not stop early.

```xml
{xml}
```"""
payload = {"model": "mimo-v2.5-pro", "max_tokens": 4000, "system": system,
           "messages": [{"role": "user", "content": prompt}]}
req = urllib.request.Request(base + "/v1/messages", data=json.dumps(payload).encode(),
    headers={"content-type": "application/json", "x-api-key": tok, "anthropic-version": "2023-06-01"}, method="POST")
with urllib.request.urlopen(req, timeout=180) as r:
    data = json.loads(r.read().decode())
text = "".join(b.get("text","") for b in data.get("content",[]) if b.get("type")=="text")
here = Path(__file__).resolve().parent
(here / "about_full.ets").write_text(text, encoding="utf-8")
(here / "probe_out.json").write_text(json.dumps(
    {"stop_reason": data.get("stop_reason"), "usage": data.get("usage"), "chars": len(text)},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("done", len(text))
