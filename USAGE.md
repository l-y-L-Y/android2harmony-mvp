# 使用指南：Android → 鸿蒙 转译器

## 0. 这些东西都在哪

| 项 | 路径 |
|---|---|
| **转译器源码（git 仓库）** | `D:\claudecli\android2harmony-mvp` |
| **token 配置** | `D:\claudecli\android2harmony-mvp\.env`（已 gitignore，CLI 自动加载） |
| **现成 Android 样本** | `D:\codex\android-benchmarks\`（OSChina/Tusky/AntennaPod/Nextcloud…）、`D:\work\Android\`（Pokedex…） |
| **转译输出** | 你用 `-o` 指定，惯例放 `D:\codex\out\<名字>` |

> 这是个**本地 git 仓库**（无远程）。`git log` 看提交历史。

## 1. 要测一个新样本：样本放哪？

**放哪都行**——转译器吃的是「目录路径」，你把 Android 工程（含 `build.gradle`/`settings.gradle` 或老式 `AndroidManifest.xml` 的目录）放任意位置，把路径传给 `convert` 即可。建议放 `D:\codex\android-benchmarks\<你的项目>` 跟其它样本一起。

支持：Gradle 工程、老式 Android 工程、XML 布局、DataBinding、Jetpack Compose、单 Activity+Fragment。
不支持：游戏/自绘（libGDX/Unity）、跨平台（RN/Flutter）。

## 2. 怎么用（三步）

在 `D:\claudecli\android2harmony-mvp` 目录下运行（token 会自动从 .env 加载，**不用手动设环境变量**）：

```powershell
# 第 1 步：转译（分析 + LLM 生成鸿蒙工程）
python -m android2harmony.cli convert "D:\path\to\AndroidProject" -o "D:\codex\out\myapp-harmony" --force --llm-refine-pages

# 第 2 步：编译并自动修复编译错误（迭代到通过）
python -m android2harmony.cli repair-build "D:\codex\out\myapp-harmony" --max-iters 5

# 第 3 步：装到鸿蒙模拟器并截图（先确保模拟器在线：hdc list targets 显示 127.0.0.1:5555）
python -m android2harmony.cli validate-device "D:\codex\out\myapp-harmony" --bundle <bundleName>
```

- `<bundleName>` 从 `D:\codex\out\myapp-harmony\AppScope\app.json5` 里的 `bundleName` 字段拿（通常是 `com.xxx` 或 `com.generated.xxx`）。
- 大项目慢是正常的：每页一次 mimo 推理调用，已 4 路并行（`ANDROID2HARMONY_LLM_CONCURRENCY` 可调）。
- 只想要源码、不编译：只跑第 1 步即可，用 DevEco Studio 打开 `-o` 那个目录。

## 3. 怎么看结果

转译输出目录 `D:\codex\out\myapp-harmony\` 里：

| 看什么 | 在哪 |
|---|---|
| **生成的页面（ArkUI 源码）** | `entry\src\main\ets\pages\*.ets` |
| **实机截图** | `uitest-screenshot.png`（第 3 步生成） |
| **迁移报告** | `migration-report.md`（API/网络/数据库/风险/没做完的点） |
| **UI 保真报告** | `agent-workspace\03-migration\ui-fidelity-report.md`（入口屏、哪些页 LLM 生成/兜底/占位、已知限制） |
| **LLM 调用记录** | `agent-workspace\llm-calls\` |
| **能否编译** | 第 2 步输出 `passed: true/false` |
| **DevEco 打开** | 直接用 DevEco Studio 打开整个 `myapp-harmony` 目录 |

## 4. 常用其它命令

```powershell
python -m android2harmony.cli analyze "D:\path\to\AndroidProject"   # 只分析,看模块/页面/风险
python -m android2harmony.cli llm-check                              # 测 mimo 连通
python -m android2harmony.cli batch-convert "D:\dir\with\many\apps" -o "D:\codex\out\batch" --force --llm-refine-pages
```
