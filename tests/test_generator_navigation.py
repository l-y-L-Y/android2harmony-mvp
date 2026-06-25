from pathlib import Path

from android2harmony.generator import (
    _repair_navigation_targets,
    _inline_sibling_stub_structs,
    _replace_local_httpclient_stub,
)


def _pages(tmp_path: Path) -> Path:
    d = tmp_path / "pages"
    d.mkdir()
    return d


def test_share_adapter_used_as_route_is_rewritten(tmp_path: Path):
    # Regression (NewPipe FragmentPlaylist): a Share button rendered as a page navigation
    # to the ShareCompat adapter -> router 'page does not exist'. Must become a real call.
    pages = _pages(tmp_path)
    (pages / "FragmentPlaylist.ets").write_text(
        "import { router } from '@kit.ArkUI';\n"
        "@Entry @Component struct FragmentPlaylist {\n"
        "  build() {\n"
        "    Text('Share').onClick(() => {\n"
        "      router.pushUrl({ url: 'pages/ShareCompat', params: { title: 'Playlist', text: this.playlist.url } });\n"
        "    })\n"
        "  }\n}\n",
        encoding="utf-8",
    )
    n = _repair_navigation_targets(pages)
    out = (pages / "FragmentPlaylist.ets").read_text(encoding="utf-8")
    assert n == 1
    assert "router.pushUrl" not in out
    assert "ShareCompat.shareText(getContext(this) as common.UIAbilityContext, this.playlist.url)" in out
    assert "from '../platform/ShareCompat'" in out
    assert "from '@kit.AbilityKit'" in out


def test_nav_to_missing_page_is_neutralized(tmp_path: Path):
    pages = _pages(tmp_path)
    (pages / "A.ets").write_text(
        "import { router } from '@kit.ArkUI';\n"
        "@Entry @Component struct A {\n"
        "  build() { Text('go').onClick(() => { router.pushUrl({ url: 'pages/GhostPage' }); }) }\n}\n",
        encoding="utf-8",
    )
    n = _repair_navigation_targets(pages)
    out = (pages / "A.ets").read_text(encoding="utf-8")
    assert n == 1
    assert "pages/GhostPage" in out  # kept inside a comment for traceability
    assert "router.pushUrl({ url: 'pages/GhostPage' })" not in out
    assert "removed nav to missing page" in out


def test_local_fragment_stub_replaced_with_real_import(tmp_path: Path):
    # Regression (Minimal-Todo): MainActivity defined a local `struct FragmentMain` stub
    # ('Main Content') AND embedded FragmentMain() -> the stub shadowed the real page so the
    # host rendered empty. The stub must be excised and the real sibling imported.
    pages = _pages(tmp_path)
    (pages / "FragmentMain.ets").write_text(
        "@Entry @Component export struct FragmentMain { build() { List() {} } }\n", encoding="utf-8")
    (pages / "MainActivity.ets").write_text(
        "import { router } from '@kit.ArkUI'\n"
        "@Component\nstruct FragmentMain {\n  build() { Column() { Text('Main Content') } }\n}\n"
        "@Entry\n@Component\nexport struct MainActivity {\n"
        "  build() { Column() { FragmentMain().layoutWeight(1) } }\n}\n",
        encoding="utf-8",
    )
    n = _inline_sibling_stub_structs(pages)
    out = (pages / "MainActivity.ets").read_text(encoding="utf-8")
    assert n == 1
    assert "Main Content" not in out          # local stub gone
    assert out.count("struct FragmentMain") == 0  # no local FragmentMain definition left
    assert "import { FragmentMain } from './FragmentMain'" in out
    assert "FragmentMain()" in out            # still embedded (now the real one)
    # the real page file is untouched
    assert "List()" in (pages / "FragmentMain.ets").read_text(encoding="utf-8")


def test_inline_stub_ignores_non_sibling_local_struct(tmp_path: Path):
    # a local helper component whose name is NOT a sibling page must be left alone
    pages = _pages(tmp_path)
    (pages / "Home.ets").write_text(
        "@Component\nstruct RowCard { build() { Text('x') } }\n"
        "@Entry @Component struct Home { build() { Column() { RowCard() } } }\n",
        encoding="utf-8",
    )
    n = _inline_sibling_stub_structs(pages)
    assert n == 0
    assert "struct RowCard" in (pages / "Home.ets").read_text(encoding="utf-8")


def test_valid_navigation_is_untouched(tmp_path: Path):
    pages = _pages(tmp_path)
    (pages / "Index.ets").write_text("@Entry @Component struct Index { build() {} }\n", encoding="utf-8")
    src = (
        "import { router } from '@kit.ArkUI';\n"
        "@Entry @Component struct Home {\n"
        "  build() { Text('x').onClick(() => { router.pushUrl({ url: 'pages/Index' }); }) }\n}\n"
    )
    (pages / "Home.ets").write_text(src, encoding="utf-8")
    n = _repair_navigation_targets(pages)
    assert n == 0
    assert (pages / "Home.ets").read_text(encoding="utf-8") == src  # unchanged


def test_local_httpclient_stub_replaced_with_real_import(tmp_path: Path):
    # Regression (NikeShop FragmentHome): the page redefined a LOCAL `class MigratedHttpClient`
    # whose methods returned [] -> the screen made no request and showed no products. The local
    # stub must be excised and the real shared client imported.
    pages = _pages(tmp_path)
    src = (
        "import router from '@ohos.router'\n\n"
        "class MigratedHttpClient {\n"
        "  async getProducts(params: HttpParams): Promise<Object[]> {\n"
        "    return [] as Object[]\n"
        "  }\n"
        "}\n\n"
        "class HttpParams {\n"
        "  set(key: string, value: string): void {}\n"
        "}\n\n"
        "@Entry\n@Component\nstruct FragmentHome {\n"
        "  private http: MigratedHttpClient = new MigratedHttpClient()\n"
        "  build() { Column() {} }\n"
        "}\n"
    )
    (pages / "FragmentHome.ets").write_text(src, encoding="utf-8")
    n = _replace_local_httpclient_stub(pages)
    assert n == 1
    out = (pages / "FragmentHome.ets").read_text(encoding="utf-8")
    assert "class MigratedHttpClient {" not in out
    assert "class HttpParams {" not in out
    # the real client is imported (only names still referenced after the stub is removed)
    assert "import { MigratedHttpClient" in out
    assert "from '../network/HttpClient';" in out
    assert "new MigratedHttpClient()" in out  # usage preserved


def test_page_without_local_httpclient_stub_is_untouched(tmp_path: Path):
    pages = _pages(tmp_path)
    src = (
        "import { MigratedHttpClient, HttpParams } from '../network/HttpClient';\n\n"
        "@Entry\n@Component\nstruct P {\n"
        "  private http: MigratedHttpClient = new MigratedHttpClient()\n"
        "  build() { Column() {} }\n"
        "}\n"
    )
    (pages / "P.ets").write_text(src, encoding="utf-8")
    n = _replace_local_httpclient_stub(pages)
    assert n == 0
    assert (pages / "P.ets").read_text(encoding="utf-8") == src
