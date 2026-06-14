# 单项目深度案例:JetpackMVVM(输入 → 输出全貌)

[上一级的 5 项目案例](../test5-5apps/REPORT.md) 从「面」上证明了 5/5 可转译;本目录从「点」上拆开 **一个项目的完整输入与输出**,让你看清转译器到底吃进什么、吐出什么、目录结构长什么样。

- **原始 Android 工程(输入)**:`android-original/`
- **生成的鸿蒙工程(输出)**:`harmony-output/`(已剔除 `build/`、`.hvigor/`、`oh_modules/` 等可重生成的编译缓存)
- 实机截图:鸿蒙 [`JetpackMVVM.jpeg`](../test5-5apps/screenshots/JetpackMVVM.jpeg) ｜ 安卓原版 [`jetpack_orig2.png`](../test5-5apps/screenshots/jetpack_orig2.png)

## 1. 这个项目是什么

[KunMinX/Jetpack-MVVM-Best-Practice](https://github.com/KunMinX/Jetpack-MVVM-Best-Practice) 的 PureMusic 示例:单 Activity + 多 Fragment、MVVM、**DataBinding**、Java 实现。输入快照含 **71 个 Java 类 + 34 个 XML**(其中 10 个布局对应 10 个界面)。属转译器受支持类型。

## 2. 转译过程与结果

```powershell
python -m android2harmony.cli convert "<JetpackMVVM>" -o "<out>\JetpackMVVM" --force --llm-refine-pages
python -m android2harmony.cli repair-build "<out>\JetpackMVVM" --max-iters 5
python -m android2harmony.cli validate-device "<out>\JetpackMVVM" --bundle com.generated.jetpackmvvm
```

| 首次编译错误 | 修复迭代 | 最终错误 | 结果 | 降级占位页 |
|---|---|---|---|---|
| 7 | 2 | 0 | ✅ 编译通过出 HAP | 0 |

**一次过、无降级**,所有页面均为模型真实翻译。

## 3. 输出目录结构详解

```
harmony-output/
├─ AppScope/                          # 应用级配置
│  ├─ app.json5                       #   bundleName=com.generated.jetpackmvvm / 版本 / 应用名
│  └─ resources/base/media/           #   应用图标
├─ entry/                             # 主 HAP 模块
│  └─ src/main/
│     ├─ module.json5                 # 模块配置 + abilities 声明
│     ├─ ets/
│     │  ├─ entryability/             # UIAbility 入口(对应 Android 启动 Activity/Application)
│     │  ├─ pages/   (10 .ets)        # 页面 ArkUI —— 与 10 个 Android 布局 1:1
│     │  │                            #   MainActivity / FragmentMain / FragmentLogin /
│     │  │                            #   FragmentPlayer / FragmentSearch / FragmentDrawer /
│     │  │                            #   AdapterLibrary / NotifyPlayerBig/Small / Index
│     │  ├─ routes/  (1)              # 路由表(对应 Fragment 导航)
│     │  ├─ state/   (1)              # 状态层(对应 ViewModel / *States)
│     │  ├─ repositories/ (1)         # 仓库层(MVVM Repository)
│     │  ├─ network/ (1)              # 网络层
│     │  ├─ models/  (1)              # 数据模型
│     │  ├─ database/ (4)             # 本地存储(对应 Room / 持久化)
│     │  ├─ di/      (1)              # 依赖注入(对应 Hilt)
│     │  ├─ platform/ (1)             # 平台适配封装
│     │  ├─ common/  (4)              # 公共工具
│     │  └─ migrated/ (71 .ets)       # 原 71 个 Java 类的逐类迁移(app/ + architecture/)
│     └─ resources/base/
│        ├─ element/                  # 字符串 / 颜色
│        ├─ media/                    # 图片 / 字体
│        └─ profile/main_pages.json   # 页面路由注册表(每条路由 = 一个 @Entry 页)
├─ build-profile.json5                # 工程构建配置
├─ oh-package.json5                   # 依赖清单
├─ hvigorfile.ts                      # 构建脚本
├─ migration-report.md                # 迁移报告:API/网络/数据库/风险/未完成项逐项列出
└─ test-plan.md                       # 测试计划
```

> 共 **101 个 `.ets`**:10 个页面 + 71 个逐类迁移 + 20 个支撑层(路由/状态/仓库/网络/存储/DI/工具)。
> 设计原则:界面走 `pages/`,业务逻辑按 MVVM 分层落到对应目录,缺口(Room/Hilt/Framework API 等)在 `migration-report.md` 显式标注,不静默吞掉。

## 4. Before / After 代码对照(以登录页为例)

**输入** `android-original/app/res/layout/fragment_login.xml`(DataBinding + ConstraintLayout):

```xml
<layout ...>
  <data>
    <variable name="vm"    type="...LoginFragment.LoginStates" />
    <variable name="click" type="...LoginFragment.ClickProxy" />
  </data>
  <androidx.constraintlayout.widget.ConstraintLayout ...>
    <net.steamcrafted.materialiconlib.MaterialIconView
        android:id="@+id/btn_back"
        android:onClick="@{()->click.back()}"
        app:materialIcon="arrow_left" ... />
    <TextView android:id="@+id/tv_title" ... />
    ...
  </androidx.constraintlayout.widget.ConstraintLayout>
</layout>
```

**输出** `harmony-output/entry/src/main/ets/pages/FragmentLogin.ets`(ArkUI 声明式 + `@State`):

```typescript
import { router } from '@kit.ArkUI'

@Entry @Component
export struct FragmentLogin {
  @State name: string = ''
  @State password: string = ''
  @State loadingVisible: boolean = false

  build() {
    Column() {
      // Back button —— 对应 MaterialIconView + onClick="@{()->click.back()}"
      Row() {
        Image($r('app.media.ic_previous_dark'))
          .width(24).height(24).objectFit(ImageFit.Contain)
          .onClick(() => { router.back() })
        Blank()
      }.width('100%').height(24).padding({ left: 16 }).margin({ top: 48 })

      // Title —— 对应 tv_title
      Text('欢迎来到 Jetpack MVVM 的世界')
        .fontSize(20).fontColor('#000000').textAlign(TextAlign.Center)
        .width('100%').margin({ top: 120 })

      // 用户名输入
      TextInput({ text: this.name, placeholder: '请输入用户名' })
        .type(InputType.Normal)
      ...
    }
  }
}
```

要点:ConstraintLayout → `Column`/`Row` 声明式布局;DataBinding 的 `onClick` 事件 → ArkUI `.onClick()`;`@{...}` 绑定变量 → `@State`;`MaterialIconView` 第三方图标控件 → `Image($r('app.media.*'))`。

## 5. 实机对照

| 安卓原版 | 鸿蒙转译 |
|---|---|
| ![](../test5-5apps/screenshots/jetpack_orig2.png) | ![](../test5-5apps/screenshots/JetpackMVVM.jpeg) |

同一雪山 Hero 图 + "PureMusic" 标题 + 相同的「最近播放 / 最佳实践」Tab + 相同歌单列表结构(原版 BenSound 英文曲目,转译用中文 mock 曲目)。**近乎一致。**
