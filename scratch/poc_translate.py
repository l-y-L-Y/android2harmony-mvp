"""One-off PoC: feed a real Android layout to mimo and get a faithful ArkUI page.

Proves the LLM-first page generation approach before rewiring the generator.
Usage: python scratch/poc_translate.py <layout.xml> <PageStructName> <app_label>
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from android2harmony.llm_provider import call_llm, extract_code_block  # noqa: E402

layout_path = Path(sys.argv[1])
struct_name = sys.argv[2]
app_label = sys.argv[3] if len(sys.argv) > 3 else "App"
xml = layout_path.read_text(encoding="utf-8", errors="ignore")

system = (
    "You are a senior HarmonyOS ArkUI engineer migrating an Android app to HarmonyOS (Stage model, ArkTS). "
    "You translate one Android XML layout into ONE faithful ArkUI page. "
    "Return ONLY the .ets file content, no markdown, no explanation."
)

prompt = f"""Migrate this Android XML layout into a single HarmonyOS ArkUI page.

App: {app_label}
Page struct name (must match exactly): {struct_name}

HARD REQUIREMENTS:
- Output a complete compilable ArkTS file: `@Entry @Component struct {struct_name} {{ build() {{ ... }} }}`.
- PRESERVE every visible Chinese/English text string EXACTLY as in the layout (e.g. "检查新版本", "版本：1.0.0", copyright). Do NOT translate or anglicize.
- Faithfully reproduce the visual layout: gravity/alignment, vertical/horizontal order, spacing, bold/size hints. FrameLayout with center|bottom gravity => a Stack or Column aligned to the bottom-center.
- Use real ArkUI components: Text, Button, Image, Column, Row, Stack, List, TextInput, Checkbox.
- For images/backgrounds you cannot resolve, use only `$r('app.media.foreground')` or a plain background color. Do NOT invent resource names.
- No "debug navigation", no route-button lists, no placeholder "Sample Item" data.
- Buttons may have empty onClick `(){{}}` or a TODO comment if the action is unknown.
- Keep it self-contained: no imports of project files that may not exist.

Android XML layout ({layout_path.name}):
```xml
{xml}
```
"""

resp = call_llm(prompt, system=system, max_tokens=4000)
code = extract_code_block(resp)
here = Path(__file__).resolve().parent
(here / f"raw_{struct_name}.txt").write_text(resp, encoding="utf-8")
out = here / f"out_{struct_name}.ets"
out.write_text(code, encoding="utf-8")
print(f"WROTE {out} (code={len(code)} chars, raw={len(resp)} chars)")
