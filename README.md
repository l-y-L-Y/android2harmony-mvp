# Android → 鸿蒙(HarmonyOS)转译器

把中文 Android 客户端 App 转译成鸿蒙 ArkTS / ArkUI(Stage 模型)工程的本地工具。流程为:**分析 Android 工程 → 生成鸿蒙工程 → 编译并自动修复编译错误 → 装到鸿蒙模拟器验证**。可选调用 Mimo(mimo-v2.5-pro)逐页精修 ArkUI 页面。

> English version: see [README.en.md](README.en.md)

## 它能做什么

- 分析 Gradle Android 工程:模块、清单、源码、资源、依赖、迁移风险。
- 生成 DevEco Studio / Hvigor 可直接打开并编译的鸿蒙 Stage 模型工程。
- 把 Android XML 布局按规则映射成 ArkUI 页面草稿。
- 迁移字符串、图片、字体,并保留原始 Android XML/源码快照。
- 生成迁移工作区产物:理解、规划、迁移任务、UITest DSL、修复循环、报告。
- **自给自足的编译修复循环**:编译失败时自动定位并修复 ArkTS 错误,迭代到通过(确定性修复 + LLM 修复 + 兜底保编译),无需手工逐项目打补丁。
- 支持批量转译多个 Android 仓库。
- 支持通过 `hdc` / `aa start` / `uitest` 做实机安装与截图验证。

## 支持范围

- ✅ **支持**:Gradle 工程、老式 Android 工程、XML 布局、DataBinding、Jetpack Compose、单 Activity + Fragment。
- ❌ **不支持**:游戏/自绘引擎(libGDX、Unity)、跨平台框架(React Native、Flutter)。

## 实测案例:5 个开源 Android 客户端

对 5 个符合转译范围的开源中文客户端做了端到端转译 + 编译修复 + 鸿蒙模拟器实机验证,完整报告与对照截图见 **[`examples/test5-5apps/REPORT.md`](examples/test5-5apps/REPORT.md)**。

| 项目 | 类型 | 首次编译错误 | 修复迭代 | 编译结果 |
|---|---|---|---|---|
| JetpackMVVM | 单 Activity+Fragment / MVVM | 7 | 2 | ✅ 通过 |
| PlayAndroid | 部分 Compose + .kts | 115 | 5 | ✅ 通过 |
| WanAndroidGoweii | DataBinding + ViewPager | 377→147 | 5 | ✅ 通过 |
| YCVideoPlayer | 视频播放器示例集 | 126 | 5 | ✅ 通过 |
| KingTV | 直播/视频客户端 | 46 | 5 | ✅ 通过 |

- **5/5 全部编译通过出 HAP**;首测 4/5 一次过,1 个(WanAndroidGoweii)失败经**转译器根因修复**(保证每个路由页恰好一个 `@Entry` + 结构错误自愈)后再转通过——修复落在转译器代码而非逐项目打补丁。
- 5/5 在鸿蒙模拟器渲染真实业务界面(歌单/文章流/直播/播放器菜单),非调试壳。

下面是鸿蒙模拟器实机截图:

| JetpackMVVM | PlayAndroid | WanAndroidGoweii | YCVideoPlayer | KingTV |
|---|---|---|---|---|
| ![](examples/test5-5apps/screenshots/JetpackMVVM.jpeg) | ![](examples/test5-5apps/screenshots/PlayAndroid2.jpeg) | ![](examples/test5-5apps/screenshots/WanAndroidGoweii.jpeg) | ![](examples/test5-5apps/screenshots/YCVideoPlayer2.jpeg) | ![](examples/test5-5apps/screenshots/KingTV.jpeg) |

### 单项目深度拆解(看清输入/输出与目录结构)

想看转译器具体「吃进什么、吐出什么」?**[`examples/jetpackmvvm-deep-dive/`](examples/jetpackmvvm-deep-dive/README.md)** 把 JetpackMVVM 一个项目完整摊开:

- `android-original/` —— 原始 Android 源码(71 个 Java + 34 个 XML)。
- `harmony-output/` —— 生成的鸿蒙工程(101 个 `.ets`,已剔除编译缓存),含带注释的**完整输出目录结构**说明。
- 登录页 **Before/After 代码对照**(DataBinding XML → ArkUI `@State` 声明式)。
- **[`针对项目 JetpackMVVM转译后直接生成的报告（无美化）`](examples/jetpackmvvm-deep-dive/harmony-output/migration-report.md)** 

## 环境要求

- Python 3.10+(运行时仅用标准库)。
- 鸿蒙工具链:DevEco Studio(含 hvigor、node、hdc、SDK),编译/装机时需要。
- (可选)Mimo 大模型账号,用于逐页精修与迁移产物增强。

## 配置 Mimo(不要把 token 写进仓库)

token 通过环境变量或本地 `.env` 提供。**`.env` 已在 `.gitignore` 中,不会被提交**。在仓库根目录新建 `.env`:

```dotenv
ANDROID2HARMONY_LLM_MODEL=mimo-v2.5-pro
# Anthropic 兼容端点(二选一)
ANTHROPIC_BASE_URL=https://token-plan-sgp.xiaomimimo.com/anthropic
ANTHROPIC_AUTH_TOKEN=<你的-token>
# 或 OpenAI 兼容端点
# ANDROID2HARMONY_LLM_PROVIDER=openai-compatible
# OPENAI_BASE_URL=https://token-plan-sgp.xiaomimimo.com/v1
# OPENAI_API_KEY=<你的-token>
```

CLI 启动时会自动加载 `.env`。测试连通性:

```powershell
python -m android2harmony.cli llm-check
```

## 三步用法

```powershell
# 1. 转译:分析 Android 工程 + LLM 生成鸿蒙工程
python -m android2harmony.cli convert "<Android工程目录>" -o "<输出目录>" --force --llm-refine-pages

# 2. 编译并自动修复编译错误(迭代到通过)
python -m android2harmony.cli repair-build "<输出目录>" --max-iters 5

# 3. 装到鸿蒙模拟器并截图(先确保 hdc list targets 能看到设备,如 127.0.0.1:5555)
python -m android2harmony.cli validate-device "<输出目录>" --bundle <bundleName>
```

- `<bundleName>` 取自输出目录 `AppScope/app.json5` 的 `bundleName` 字段。
- 只想要源码不编译:只跑第 1 步,然后用 DevEco Studio 打开输出目录。
- 大项目较慢属正常:每页一次模型推理,默认 4 路并行(可用 `ANDROID2HARMONY_LLM_CONCURRENCY` 调整)。

## 输出结构

转译输出目录里:

| 内容 | 位置 |
|---|---|
| 生成的 ArkUI 页面源码 | `entry/src/main/ets/pages/*.ets` |
| 迁移报告(API/网络/数据库/风险/未完成项) | `migration-report.md` |
| UI 保真报告(入口屏、各页是 LLM 生成/兜底/占位、已知限制) | `agent-workspace/03-migration/ui-fidelity-report.md` |
| LLM 调用记录 | `agent-workspace/llm-calls/` |
| 实机截图(第 3 步生成) | `uitest-screenshot.png` |
| 用 DevEco 打开 | 直接打开整个输出目录 |

## 其它命令

```powershell
python -m android2harmony.cli analyze "<Android工程目录>"     # 只分析:模块/页面/风险
python -m android2harmony.cli batch-convert "<含多个App的目录>" -o "<输出根目录>" --force --llm-refine-pages
python -m android2harmony.cli web --host 127.0.0.1 --port 8765 # 网页上传 zip 转译
```

## 已知限制

这不是完整的语义编译器。Room、Hilt、Android Framework API 调用、MediaStore、权限、真实数据绑定、完整导航等仍需迁移规则或 LLM 辅助修复阶段补齐。这些缺口会在迁移报告与工作区文件里显式标注。

## 测试

```powershell
python -m pytest
```
