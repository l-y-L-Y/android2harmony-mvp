# Runtime Setup

## Mimo API

The migration tool reads OpenAI-compatible or Anthropic-compatible API settings from environment variables. Prefer the OpenAI-compatible Mimo endpoint for `mimo-v2.5-pro`.
Do not commit real tokens to this repository.

```powershell
$env:ANDROID2HARMONY_LLM_PROVIDER = "openai-compatible"
$env:OPENAI_BASE_URL = "https://token-plan-sgp.xiaomimimo.com/v1"
$env:ANDROID2HARMONY_LLM_MODEL = "mimo-v2.5-pro"
$env:OPENAI_API_KEY = "<your-token>"

python -m android2harmony.cli llm-check
```

The Anthropic-compatible mode is still available for proxies that support it:

```powershell
$env:ANDROID2HARMONY_LLM_PROVIDER = "anthropic-compatible"
$env:ANTHROPIC_BASE_URL = "https://token-plan-sgp.xiaomimimo.com/anthropic"
$env:ANTHROPIC_MODEL = "mimo-v2.5-pro"
$env:ANTHROPIC_AUTH_TOKEN = "<your-token>"
```

## DevEco Tools

Detected local tools:

```text
D:\DevEco Studio\tools\hvigor\bin\hvigorw.bat
D:\DevEco Studio\tools\ohpm\bin\ohpm.bat
D:\DevEco Studio\tools\node\node.exe
D:\DevEco Studio\tools\emulator\Emulator.exe
D:\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe
```

Use this SDK variable when running Hvigor from a shell:

```powershell
$env:DEVECO_SDK_HOME = "D:\DevEco Studio\sdk"
```

## Emulator

Detected emulator instance:

```text
Name: Enjoy 90 Pro Max
Path: C:\Users\28273\AppData\Local\Huawei\Emulator\deployed\Enjoy 90 Pro Max
Image: C:\Users\28273\AppData\Local\Huawei\Sdk\system-image\HarmonyOS-6.0.2\phone_all_x86
API: 22
```

Current blocker from emulator log:

```text
HYPER_V_ERROR / Hyper-V not enabled
```

Enable Windows virtualization features, reboot, then check:

```powershell
& "D:\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe" list targets
```

After a device appears, the tool can install and run generated packages with `hdc`.
