from android2harmony.page_metrics import classify_page, project_page_metrics
from pathlib import Path


# gank FragmentHome: a single edit icon on a colored background, no text/list -> near_empty
GANK_HOME = """@Entry
@Component
export struct FragmentHome {
  build() {
    Stack({ alignContent: Alignment.TopEnd }) {
      Image($r('app.media.ic_edit_pencil')).width(40).onClick(() => {})
    }.width('100%').height('100%').backgroundColor('#1976D2')
  }
}"""

# NovelReader reading page: explicit placeholder text
NOVEL_PLACEHOLDER = """@Entry
@Component
struct ReadPage {
  build() {
    Column() {
      Text('阅读内容区域').fontSize(20)
      Text('此处显示书籍正文内容').fontSize(14)
    }.width('100%').height('100%')
  }
}"""

# MVVMHabit TabBar tab: one label only -> near_empty (faithfully empty, still flagged)
TABBAR = """@Entry
@Component
export struct FragmentTabBar1 {
  @State textContent: string = "TabBar_1"
  build() {
    Column() { Text(this.textContent).fontSize(16) }.width('100%').height('100%')
  }
}"""

# Rich list page (article feed)
RICH_LIST = """@Entry
@Component
struct Feed {
  @State items: string[] = []
  build() {
    Column() {
      Text('玩安卓').fontSize(20)
      List() {
        ForEach(this.items, (it: string) => {
          ListItem() { Text(it) }
        })
      }
    }
  }
}"""

# Login page: inputs + button + several texts -> rich
LOGIN = """@Entry
@Component
struct Login {
  build() {
    Column() {
      Text('欢迎')
      TextInput({ placeholder: '请输入用户名' })
      TextInput({ placeholder: '请输入密码' })
      Button('登录')
      Text('忘记密码')
    }
  }
}"""


def test_near_empty_single_icon():
    assert classify_page(GANK_HOME).klass == "near_empty"


def test_placeholder_text_detected():
    assert classify_page(NOVEL_PLACEHOLDER).klass == "placeholder"


def test_tabbar_label_is_near_empty():
    assert classify_page(TABBAR).klass == "near_empty"


def test_list_page_is_rich():
    m = classify_page(RICH_LIST)
    assert m.klass == "rich" and m.lists >= 1


def test_login_is_rich():
    m = classify_page(LOGIN)
    assert m.klass == "rich" and m.inputs >= 2


def test_empty_build_is_empty():
    code = "@Entry\n@Component\nstruct E { build() { Column() {} } }"
    assert classify_page(code).klass == "empty"


# Host page that embeds another generated page component -> not blank (delegates render)
HOST_EMBED = """@Entry
@Component
export struct LoginActivity {
  build() {
    Stack() { FragmentLogin() }.width('100%').height('100%')
  }
}"""

# Content lives in @Builder methods declared BEFORE build() (SideBarContainer host)
BUILDER_CONTENT = """@Entry
@Component
export struct MainActivity {
  @Builder DrawerContent() {
    Column() {
      Text('hotBitmapGG')
      Image($r('app.media.avatar'))
      ForEach(this.menuItems, (m: object) => { Text('x') })
    }
  }
  build() {
    SideBarContainer() { this.DrawerContent() }
  }
}"""


def test_embedded_subpage_is_rich():
    # without knowing FragmentLogin is a page -> would look empty; with it -> rich
    assert classify_page(HOST_EMBED).klass == "empty"
    assert classify_page(HOST_EMBED, page_names=("FragmentLogin", "LoginActivity")).klass == "rich"


def test_builder_method_content_is_counted():
    # content is in @Builder before build(); whole-file counting must see it
    assert classify_page(BUILDER_CONTENT).klass == "rich"


def test_non_screen_pages_excluded_from_blank_ratio(tmp_path: Path):
    pages = tmp_path / "entry" / "src" / "main" / "ets" / "pages"
    pages.mkdir(parents=True)
    (pages / "AdapterPhotoSet.ets").write_text(
        "@Component\nstruct AdapterPhotoSet { build() { Image(this.url) } }", encoding="utf-8")
    (pages / "CommonEmptyView.ets").write_text(
        "@Component\nstruct CommonEmptyView { build() { Text('暂无') } }", encoding="utf-8")
    (pages / "Feed.ets").write_text(RICH_LIST, encoding="utf-8")
    report = project_page_metrics(tmp_path)
    assert report["excludedNonScreen"] == 2  # adapter + empty-view not screens
    assert report["screenPages"] == 1
    assert report["blankLikePages"] == 0  # the one real screen (Feed) is rich
    assert report["blankLikeRatio"] == 0.0


def test_project_metrics_aggregates(tmp_path: Path):
    pages = tmp_path / "entry" / "src" / "main" / "ets" / "pages"
    pages.mkdir(parents=True)
    (pages / "FragmentHome.ets").write_text(GANK_HOME, encoding="utf-8")
    (pages / "Feed.ets").write_text(RICH_LIST, encoding="utf-8")
    report = project_page_metrics(tmp_path)
    assert report["totalPages"] == 2
    assert report["byClass"]["near_empty"] == 1
    assert report["byClass"]["rich"] == 1
    assert report["blankLikePages"] == 1
    assert report["blankLikeRatio"] == 0.5
