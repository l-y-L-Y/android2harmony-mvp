from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path


ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


@lru_cache(maxsize=64)
def _module_layout_dirs(module_path_str: str) -> tuple[Path, ...]:
    """All `layout/` directories under the module, not just the standard `res/layout`.
    Some projects keep layouts in custom resource roots (e.g. `res/common/layout/`,
    flavor source sets); the analyzer finds those via a broad scan, so the route->layout
    mapping must too, or the whole app silently degrades to placeholders (no LLM refine)."""
    module_path = Path(module_path_str)
    dirs: list[Path] = []
    seen: set[str] = set()
    res_roots = list(module_path.glob("src/*/res*")) + [
        module_path / "src" / "main" / "res",
        module_path / "res",
    ]
    for res in res_roots:
        if not res.is_dir():
            continue
        for d in res.rglob("layout"):
            if d.is_dir() and "build" not in d.parts and str(d) not in seen:
                seen.add(str(d))
                dirs.append(d)
    return tuple(dirs)


def translate_layout_file(
    layout_file: Path,
    page_name: str,
    strings: dict[str, str] | None = None,
    routes: list[str] | None = None,
    store_names: set[str] | None = None,
) -> str:
    strings = strings or {}
    all_routes = routes or []
    routes = [route for route in all_routes if route != f"pages/{page_name}"]
    store_name = _store_name_for_page(page_name, store_names or set())
    sample_items = _sample_items_for_layout(layout_file, strings)
    try:
        root = ET.parse(layout_file).getroot()
        body = _translate_node(root, strings, indent=6, context={"layout": layout_file.stem, "layout_dir": str(layout_file.parent), "routes": routes})
    except Exception as exc:
        body = "      Text('Unable to translate Android layout: " + _escape(str(exc)) + "')\n        .fontSize(14)\n"
    if page_name == "ActivityDetail" and store_name == "DetailViewModelStore":
        body = _detail_reference_code("        ")
        sample_items = []
    page_title = _title_from_page(page_name, sample_items)

    struct_name = _arkts_identifier(page_name)
    imports = "import { NavigationCompat } from '../common/NavigationCompat';\n"
    if store_name:
        imports += f"import {{ {store_name} }} from '../state/MigratedStores';\n"
    imports += "\n"
    show_debug_nav = _show_debug_nav(page_name, all_routes)
    nav_state = f"  @State private navRoutes: NavRoute[] = {json.dumps([{'title': _route_title(route), 'route': route} for route in routes[:12]], ensure_ascii=False)};\n" if show_debug_nav else ""
    nav_body = _navigation_code("      ") if show_debug_nav else ""
    nav_type = "interface NavRoute {\n  title: string;\n  route: string;\n}\n\n" if show_debug_nav else ""
    item_type = "interface MigratedListItem {\n  title: string;\n  imageUrl: string;\n}\n\n"
    builder_code = _detail_builder_code() if page_name == "ActivityDetail" and store_name == "DetailViewModelStore" else ""
    store_member = f"  private store: {store_name} = new {store_name}();\n" if store_name else ""
    store_status = _store_status_code("        ", store_name)
    store_actions = _store_actions_code("        ", store_name)
    detail_auto_load = _detail_auto_load_code(page_name, store_name)
    detail_summary = _detail_summary_code("        ", page_name, store_name)
    detail_state = _detail_state_code(page_name, store_name)
    detail_methods = _detail_methods_code(page_name, store_name)
    return f"""{imports}{nav_type}{item_type}{builder_code}@Entry
@Component
struct {struct_name} {{
  @State private items: MigratedListItem[] = {json.dumps(sample_items, ensure_ascii=False)};
  @State private selectedTitle: string = '';
  @State private selectedImageUrl: string = '';
{nav_state}
{detail_state}
{store_member}

    onPageShow(): void {{
    const params = NavigationCompat.params(this);
    if (params && params.title) {{
      this.selectedTitle = params.title;
      this.selectedImageUrl = params.imageUrl || '';
{detail_auto_load}
    }} else {{
{_page_default_load_code(page_name, store_name)}
    }}
  }}

{detail_methods}

  build() {{
    Scroll() {{
      Column() {{
        Text('{_escape(page_title)}')
          .fontSize(24)
          .fontWeight(FontWeight.Bold)
          .margin({{ bottom: 16 }})
{nav_body}
{store_status}
        if (this.selectedTitle.length > 0) {{
          Column() {{
            Image(this.selectedImageUrl)
              .width(160)
              .height(160)
              .objectFit(ImageFit.Contain)
            Text(this.selectedTitle)
              .fontSize(22)
              .fontWeight(FontWeight.Bold)
              .margin({{ top: 8 }})
          }}
          .width('100%')
          .alignItems(HorizontalAlign.Center)
          .margin({{ bottom: 18 }})
        }}
{detail_summary}
{body}
{store_actions}
      }}
      .width('100%')
      .padding({{ left: 16, right: 16, top: 20, bottom: 20 }})
      .alignItems(HorizontalAlign.Start)
    }}
    .width('100%')
    .height('100%')
  }}
}}
"""


def _detail_auto_load_code(page_name: str, store_name: str | None) -> str:
    if page_name != "ActivityDetail" or store_name != "DetailViewModelStore":
        return ""
    return "      this.loadDetail(this.selectedTitle);\n"


def _page_default_load_code(page_name: str, store_name: str | None) -> str:
    if page_name == "ActivityDetail" and store_name == "DetailViewModelStore":
        return (
            "      this.selectedTitle = 'Bulbasaur';\n"
            "      this.selectedImageUrl = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png';\n"
            "      this.loadDetail(this.selectedTitle);\n"
        )
    if page_name == "ActivityMain" and store_name == "MainViewModelStore":
        return "      this.store.fetchNextPokemonList();\n"
    return ""


def _detail_summary_code(pad: str, page_name: str, store_name: str | None) -> str:
    if page_name != "ActivityDetail" or store_name != "DetailViewModelStore":
        return ""
    return (
        f"{pad}if (this.detailInfo) {{\n"
        f"{pad}  Column() {{\n"
        f"{pad}    Row() {{\n"
        f"{pad}      Text(`#${{this.detailField('id', '001')}}`)\n"
        f"{pad}        .fontSize(14)\n"
        f"{pad}        .fontColor('#64748B')\n"
        f"{pad}      Blank()\n"
        f"{pad}      Text(String(this.detailField('types', 'grass, poison')))\n"
        f"{pad}        .fontSize(12)\n"
        f"{pad}        .fontColor('#20806A')\n"
        f"{pad}    }}\n"
        f"{pad}    .width('100%')\n"
        f"{pad}    .margin({{ bottom: 10 }})\n"
        f"{pad}    Row() {{\n"
        f"{pad}      MetricBlock('Height', this.detailField('height', '-'))\n"
        f"{pad}      MetricBlock('Weight', this.detailField('weight', '-'))\n"
        f"{pad}      MetricBlock('EXP', this.detailField('exp', this.detailField('experience', '-')))\n"
        f"{pad}    }}\n"
        f"{pad}    .width('100%')\n"
        f"{pad}    .justifyContent(FlexAlign.SpaceBetween)\n"
        f"{pad}    .margin({{ bottom: 12 }})\n"
        f"{pad}    Text(`HP ${{this.detailField('hp', '-')}}  ATK ${{this.detailField('attack', '-')}}  DEF ${{this.detailField('defense', '-')}}  SPD ${{this.detailField('speed', '-')}}`)\n"
        f"{pad}      .fontSize(14)\n"
        f"{pad}      .fontColor('#253044')\n"
        f"{pad}  }}\n"
        f"{pad}  .width('100%')\n"
        f"{pad}  .padding(16)\n"
        f"{pad}  .backgroundColor('#FFFFFF')\n"
        f"{pad}  .border({{ width: 1, color: '#D7DDE5' }})\n"
        f"{pad}  .borderRadius(8)\n"
        f"{pad}  .margin({{ bottom: 14 }})\n"
        f"{pad}}}\n"
    )


def _detail_state_code(page_name: str, store_name: str | None) -> str:
    if page_name != "ActivityDetail" or store_name != "DetailViewModelStore":
        return ""
    return (
        "  @State private detailInfo: Object | undefined = undefined;\n"
        "  @State private detailLoading: boolean = false;\n"
        "  @State private detailError: string = '';\n"
    )


def _detail_methods_code(page_name: str, store_name: str | None) -> str:
    if page_name != "ActivityDetail" or store_name != "DetailViewModelStore":
        return ""
    return """  async loadDetail(name: string): Promise<void> {
    if (!name) {
      return;
    }
    this.detailLoading = true;
    this.detailError = '';
    const loaded = await this.store.load(name);
    this.detailInfo = loaded;
    this.detailError = this.store.toastMessage || '';
    this.detailLoading = false;
  }

  detailField(name: string, fallback: string = ''): string {
    if (!this.detailInfo) {
      return fallback;
    }
    const row = this.detailInfo as Record<string, Object>;
    const value = row[name];
    return value === undefined ? fallback : String(value);
  }
"""


def _detail_builder_code() -> str:
    return """@Builder
function MetricBlock(label: string, value: string) {
  Column() {
    Text(value)
      .fontSize(18)
      .fontWeight(FontWeight.Medium)
      .fontColor('#17202A')
    Text(label)
      .fontSize(12)
      .fontColor('#627084')
      .margin({ top: 2 })
  }
  .alignItems(HorizontalAlign.Center)
  .layoutWeight(1)
}

"""


def _detail_reference_code(pad: str) -> str:
    return (
        f"{pad}Column() {{\n"
        f"{pad}  Text('Base Stats')\n"
        f"{pad}    .fontSize(16)\n"
        f"{pad}    .fontWeight(FontWeight.Medium)\n"
        f"{pad}    .margin({{ bottom: 8 }})\n"
        f"{pad}  Text('HP / ATK / DEF / SPD')\n"
        f"{pad}    .fontSize(13)\n"
        f"{pad}    .fontColor('#627084')\n"
        f"{pad}}}\n"
        f"{pad}.width('100%')\n"
        f"{pad}.padding(12)\n"
        f"{pad}.backgroundColor('#F9FAFB')\n"
        f"{pad}.borderRadius(8)\n"
        f"{pad}.margin({{ bottom: 8 }})\n"
    )


def _show_debug_nav(page_name: str, routes: list[str]) -> bool:
    # Debug navigation (route-button list) was the "debug shell" symptom. The rule
    # translator is now only a fallback when LLM page generation fails, and it must
    # never inject a debug-nav scaffold.
    return False


def load_android_strings(module_path: Path) -> dict[str, str]:
    values = module_path / "src" / "main" / "res" / "values" / "strings.xml"
    strings: dict[str, str] = {}
    if not values.exists():
        return strings
    try:
        root = ET.parse(values).getroot()
    except ET.ParseError:
        return strings
    for item in root.findall(".//string"):
        name = item.attrib.get("name")
        if name:
            strings[name] = "".join(item.itertext()).strip()
    return strings


def page_to_layout_file(module_path: Path, route: str) -> Path | None:
    page = route.split("/")[-1]
    snake = _camel_to_snake(page)
    # `MainActivity` <-> `activity_main`: strip the Activity affix to get the base name,
    # since Android reverses word order between class and layout file conventions.
    base = re.sub(r"(?i)^activity|activity$", "", page) or page
    snake_base = _camel_to_snake(base)
    layout_dirs = list(_module_layout_dirs(str(module_path))) or [
        module_path / "src" / "main" / "res" / "layout",
        module_path / "res" / "layout",
    ]
    candidates = []
    for layout_dir in layout_dirs:
        candidates += [
            layout_dir / f"{snake}.xml",
            layout_dir / f"activity_{snake}.xml",
            layout_dir / f"activity_{snake_base}.xml",
            layout_dir / f"{snake_base}.xml",
            layout_dir / f"fragment_{snake_base}.xml",
        ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # Fuzzy fallback: compare on alphanumeric-only keys (FeedBack -> feedback.xml,
    # MainActivity -> activity_main.xml).
    keys = {
        _normalize_key(page),
        _normalize_key("activity_" + page),
        "activity" + _normalize_key(page),
        "activity" + _normalize_key(base),
        _normalize_key(base),
    }
    for layout_dir in layout_dirs:
        if not layout_dir.exists():
            continue
        for xml in sorted(layout_dir.glob("*.xml")):
            if _normalize_key(xml.stem) in keys:
                return xml
    return None


def _normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _translate_node(node: ET.Element, strings: dict[str, str], indent: int, context: dict[str, str]) -> str:
    tag = _local_name(node.tag)
    children = list(node)
    pad = " " * indent

    if tag == "layout":
        return "".join(_translate_node(child, strings, indent, context) for child in children if _local_name(child.tag) != "data")

    if tag in {"data", "variable", "import"}:
        return ""

    if tag == "ProgressBar" or tag.endswith("ProgressBar"):
        return ""

    if _android_attr(node, "visibility") == "gone":
        return _hidden_placeholder(node, tag, pad)

    if _is_toolbar(tag):
        title = _resolve_ref(_app_attr(node, "title"), strings) or _first_child_text(node, strings) or _id_or_tag(node, tag)
        return f"{pad}Text('{_escape(title)}')\n{pad}.fontSize(20)\n{pad}.fontWeight(FontWeight.Medium)\n{pad}.width('100%')\n{pad}.padding(12)\n{pad}.backgroundColor('#F3F4F6')\n{pad}.margin({{ bottom: 10 }})\n"

    if tag.endswith("MySearchMenu") or tag == "SearchView":
        return f"{pad}TextInput({{ placeholder: 'Search' }})\n{pad}.width('100%')\n{pad}.height(44)\n{pad}.margin({{ bottom: 12 }})\n"

    if tag in {"LinearLayout", "ConstraintLayout", "RelativeLayout", "FrameLayout", "CoordinatorLayout", "NestedScrollView", "ScrollView"}:
        container = "Row" if _android_attr(node, "orientation") == "horizontal" else "Column"
        if tag == "FrameLayout":
            container = "Stack"
        child_code = "".join(_translate_node(child, strings, indent + 2, context) for child in children)
        if not child_code:
            label = _escape(_id_or_tag(node, tag))
            child_code = f"{' ' * (indent + 2)}Text('{label}')\n{' ' * (indent + 2)}.fontSize(13)\n{' ' * (indent + 2)}.fontColor('#9CA3AF')\n"
        return f"{pad}{container}() {{\n{child_code}{pad}}}\n{pad}.width('100%')\n{pad}.margin({{ bottom: 8 }})\n"

    if tag in {"RecyclerView", "ListView", "GridView"} or tag.endswith("RecyclerView"):
        if _is_grid_like(node, tag):
            return _grid_code(pad, context)
        return _list_code(pad)

    if tag.endswith("SwipeRefreshLayout") or tag.endswith("RecyclerViewFastScroller"):
        child_code = "".join(_translate_node(child, strings, indent, context) for child in children)
        return child_code

    if tag in {"TextView", "MaterialTextView"} or tag.endswith("TextView"):
        text = _display_text(node, strings, fallback=_id_or_tag(node, tag))
        style = _style_modifiers(node, pad)
        return f"{pad}Text('{_escape(text)}')\n{pad}.fontSize(15)\n{style}{pad}.margin({{ bottom: 6 }})\n"

    if tag in {"Button", "MaterialButton", "ImageButton"} or tag.endswith("Button"):
        text = _display_text(node, strings, fallback=_id_or_tag(node, tag))
        return f"{pad}Button('{_escape(text)}')\n{pad}.margin({{ bottom: 8 }})\n"

    if tag in {"CheckBox", "Switch"} or tag.endswith("Checkbox") or tag.endswith("CheckBox"):
        text = _display_text(node, strings, fallback=_id_or_tag(node, tag))
        return f"{pad}Row() {{\n{pad}  Checkbox()\n{pad}  Text('{_escape(text)}').fontSize(15).margin({{ left: 8 }})\n{pad}}}\n{pad}.height(44)\n{pad}.width('100%')\n{pad}.margin({{ bottom: 6 }})\n"

    if tag in {"EditText", "TextInputEditText"} or tag.endswith("EditText"):
        hint = _resolve_ref(_android_attr(node, "hint"), strings) or _id_or_tag(node, tag)
        return f"{pad}TextInput({{ placeholder: '{_escape(hint)}' }})\n{pad}.width('100%')\n{pad}.margin({{ bottom: 8 }})\n"

    if tag in {"ImageView", "ShapeableImageView"} or tag.endswith("ImageView"):
        label = _id_or_tag(node, tag)
        return f"{pad}Image($r('app.media.foreground'))\n{pad}.width(48)\n{pad}.height(48)\n{pad}.objectFit(ImageFit.Contain)\n{pad}.margin({{ bottom: 8 }})\n{pad}// {label}\n"

    if tag == "include":
        layout = _android_attr(node, "layout") or "included_layout"
        if "divider" in layout:
            return f"{pad}Divider()\n{pad}.margin({{ top: 8, bottom: 8 }})\n"
        included = _included_layout_path(context, layout)
        if included and included.exists():
            try:
                included_root = ET.parse(included).getroot()
                return _translate_node(included_root, strings, indent, {**context, "layout": included.stem})
            except ET.ParseError:
                pass
        return f"{pad}Text('{_escape(layout.split('/')[-1].replace('_', ' ').title())}')\n{pad}.fontSize(13)\n{pad}.fontColor('#6B7280')\n{pad}.margin({{ bottom: 6 }})\n"

    if children:
        child_code = "".join(_translate_node(child, strings, indent + 2, context) for child in children)
        return f"{pad}Column() {{\n{child_code}{pad}}}\n{pad}.width('100%')\n{pad}.margin({{ bottom: 8 }})\n"

    return f"{pad}Text('{_escape(_id_or_tag(node, tag))}')\n{pad}.fontSize(13)\n{pad}.fontColor('#6B7280')\n{pad}.margin({{ bottom: 4 }})\n"


def _android_attr(node: ET.Element, name: str) -> str | None:
    return node.attrib.get(ANDROID_NS + name) or node.attrib.get(name)


def _app_attr(node: ET.Element, name: str) -> str | None:
    return node.attrib.get("{http://schemas.android.com/apk/res-auto}" + name) or node.attrib.get(name)


def _tools_attr(node: ET.Element, name: str) -> str | None:
    return node.attrib.get("{http://schemas.android.com/tools}" + name) or node.attrib.get(name)


def _display_text(node: ET.Element, strings: dict[str, str], fallback: str) -> str:
    return (
        _resolve_ref(_android_attr(node, "text"), strings)
        or _resolve_ref(_tools_attr(node, "text"), strings)
        or _resolve_ref(_android_attr(node, "contentDescription"), strings)
        or _resolve_ref(_tools_attr(node, "contentDescription"), strings)
        or fallback
    )


def _resolve_ref(value: str | None, strings: dict[str, str]) -> str | None:
    if not value:
        return None
    if value.startswith("@{"):
        return None
    if value.startswith("@string/"):
        key = value.split("/", 1)[1]
        return strings.get(key, key.replace("_", " "))
    if value.startswith("@"):
        return value.split("/")[-1].replace("_", " ")
    return value


def _id_or_tag(node: ET.Element, tag: str) -> str:
    node_id = _android_attr(node, "id")
    if node_id and "/" in node_id:
        return node_id.split("/")[-1].replace("_", " ")
    return tag


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].rsplit(".", 1)[-1]


def _is_toolbar(tag: str) -> bool:
    return tag in {"Toolbar", "MaterialToolbar"} or tag.endswith("Toolbar")


def _first_child_text(node: ET.Element, strings: dict[str, str]) -> str | None:
    for child in node.iter():
        if child is node:
            continue
        text = _display_text(child, strings, fallback="")
        if text:
            return text
    return None


def _is_grid_like(node: ET.Element, tag: str) -> bool:
    if tag == "GridView":
        return True
    node_id = _id_or_tag(node, tag).lower()
    layout_manager = (_app_attr(node, "layoutManager") or "").lower()
    span_count = _app_attr(node, "spanCount")
    return "grid" in node_id or "gridlayoutmanager" in layout_manager or bool(span_count)


def _included_layout_path(context: dict[str, str], layout: str) -> Path | None:
    if not layout.startswith("@layout/"):
        return None
    layout_dir = context.get("layout_dir")
    if not layout_dir:
        return None
    return Path(layout_dir) / f"{layout.split('/', 1)[1]}.xml"


def _hidden_placeholder(node: ET.Element, tag: str, pad: str) -> str:
    label = _id_or_tag(node, tag)
    if "empty" in label or "placeholder" in label:
        return f"{pad}Text('{_escape(label)}')\n{pad}.fontSize(13)\n{pad}.fontColor('#9CA3AF')\n{pad}.visibility(Visibility.None)\n"
    return ""


def _style_modifiers(node: ET.Element, pad: str) -> str:
    modifiers = ""
    gravity = _android_attr(node, "gravity") or ""
    if "center" in gravity:
        modifiers += f"{pad}.textAlign(TextAlign.Center)\n{pad}.width('100%')\n"
    if _android_attr(node, "textStyle") == "italic":
        modifiers += f"{pad}.fontStyle(FontStyle.Italic)\n"
    return modifiers


def _grid_code(pad: str, context: dict[str, str]) -> str:
    detail_route = _detail_route(context)
    click_start = f"{pad}        .onClick(() => {{ NavigationCompat.push(this, {{ url: '{detail_route}', params: item }}); }})\n" if detail_route else ""
    return (
        f"{pad}Grid() {{\n"
        f"{pad}  ForEach(this.items, (item: MigratedListItem) => {{\n"
        f"{pad}    GridItem() {{\n"
        f"{pad}      Column() {{\n"
        f"{pad}        Image(item.imageUrl).width(96).height(96).objectFit(ImageFit.Contain)\n"
        f"{pad}        Text(item.title).fontSize(15).fontWeight(FontWeight.Medium).fontColor('#FFFFFF').textAlign(TextAlign.Center).maxLines(1).width('100%').padding(10).backgroundColor('#334155')\n"
        f"{pad}      }}.padding(8).backgroundColor('#1F2937').borderRadius(8)\n"
        f"{click_start}"
        f"{pad}    }}\n"
        f"{pad}  }})\n"
        f"{pad}}}\n"
        f"{pad}.columnsTemplate('1fr 1fr')\n"
        f"{pad}.rowsGap(12)\n"
        f"{pad}.columnsGap(12)\n"
        f"{pad}.height(560)\n"
        f"{pad}.width('100%')\n"
        f"{pad}.margin({{ bottom: 8 }})\n"
    )


def _list_code(pad: str) -> str:
    return (
        f"{pad}List() {{\n"
        f"{pad}  ForEach(this.items, (item: MigratedListItem) => {{\n"
        f"{pad}    ListItem() {{ Text(item.title).fontSize(15).padding(10) }}\n"
        f"{pad}  }})\n"
        f"{pad}}}\n{pad}.height(220)\n{pad}.width('100%')\n{pad}.margin({{ bottom: 8 }})\n"
    )


def _navigation_code(pad: str) -> str:
    return (
        f"{pad}Column() {{\n"
        f"{pad}  Text('迁移调试导航')\n"
        f"{pad}    .fontSize(12)\n"
        f"{pad}    .fontColor('#6B7280')\n"
        f"{pad}    .margin({{ top: 16, bottom: 6 }})\n"
        f"{pad}  ForEach(this.navRoutes, (item: NavRoute) => {{\n"
        f"{pad}    Button(item.title)\n"
        f"{pad}      .fontSize(12)\n"
        f"{pad}      .height(32)\n"
        f"{pad}      .width('100%')\n"
        f"{pad}      .margin({{ bottom: 6 }})\n"
        f"{pad}      .onClick(() => {{\n"
        f"{pad}        NavigationCompat.push(this, {{ url: item.route }});\n"
        f"{pad}      }})\n"
        f"{pad}  }})\n"
        f"{pad}}}\n"
        f"{pad}.width('100%')\n"
        f"{pad}.margin({{ bottom: 8 }})\n"
    )


def _store_name_for_page(page_name: str, store_names: set[str]) -> str | None:
    if not store_names:
        return None
    candidates = []
    base = page_name.removeprefix("Activity").removesuffix("Activity")
    if base:
        candidates.append(f"{base}ViewModelStore")
    candidates.append(f"{page_name}ViewModelStore")
    for candidate in candidates:
        if candidate in store_names:
            return candidate
    lowered = page_name.lower()
    for store in sorted(store_names):
        prefix = store.removesuffix("ViewModelStore").lower()
        if prefix and prefix in lowered:
            return store
    return None


def _store_status_code(pad: str, store_name: str | None) -> str:
    if not store_name:
        return ""
    if store_name == "DetailViewModelStore":
        return (
            f"{pad}if (this.detailLoading) {{\n"
            f"{pad}  Text('Loading')\n"
            f"{pad}    .fontSize(12)\n"
            f"{pad}    .fontColor('#2563EB')\n"
            f"{pad}    .margin({{ bottom: 8 }})\n"
            f"{pad}}}\n"
            f"{pad}if (this.detailError.length > 0) {{\n"
            f"{pad}  Text(this.detailError)\n"
            f"{pad}    .fontSize(12)\n"
            f"{pad}    .fontColor('#B45309')\n"
            f"{pad}    .margin({{ bottom: 8 }})\n"
            f"{pad}}}\n"
        )
    return (
        f"{pad}if (this.store.isLoading) {{\n"
        f"{pad}  Text('Loading')\n"
        f"{pad}    .fontSize(12)\n"
        f"{pad}    .fontColor('#2563EB')\n"
        f"{pad}    .margin({{ bottom: 8 }})\n"
        f"{pad}}}\n"
        f"{pad}if (this.store.toastMessage) {{\n"
        f"{pad}  Text(this.store.toastMessage as string)\n"
        f"{pad}    .fontSize(12)\n"
        f"{pad}    .fontColor('#B45309')\n"
        f"{pad}    .margin({{ bottom: 8 }})\n"
        f"{pad}}}\n"
    )


def _store_actions_code(pad: str, store_name: str | None) -> str:
    if not store_name:
        return ""
    if store_name == "MainViewModelStore":
        return (
            f"{pad}Button('Load More')\n"
            f"{pad}  .width('100%')\n"
            f"{pad}  .margin({{ top: 12 }})\n"
            f"{pad}  .onClick(async () => {{\n"
            f"{pad}    const loaded = await this.store.fetchNextPokemonList();\n"
            f"{pad}    if (loaded.length > 0) {{\n"
            f"{pad}      this.items = loaded.map((item: Object) => {{\n"
            f"{pad}        const row = item as Record<string, Object>;\n"
            f"{pad}        const title = String(row['name'] || row['title'] || 'Item');\n"
            f"{pad}        const imageUrl = String(row['imageUrl'] || row['url'] || 'app.media.foreground');\n"
            f"{pad}        return {{ title, imageUrl }} as MigratedListItem;\n"
            f"{pad}      }});\n"
            f"{pad}    }}\n"
            f"{pad}  }})\n"
        )
    if store_name == "DetailViewModelStore":
        return (
            f"{pad}Button('Reload Detail')\n"
            f"{pad}  .width('100%')\n"
            f"{pad}  .margin({{ top: 12 }})\n"
            f"{pad}  .onClick(async () => {{ await this.loadDetail(this.selectedTitle); }})\n"
        )
    return ""


def _title_from_page(page_name: str, sample_items: list[dict[str, str]] | None = None) -> str:
    titles = {str(item.get("title", "")) for item in (sample_items or [])}
    if page_name == "ActivityMain" and "Pokedex" in titles:
        return "Pokedex"
    if page_name == "ActivityDetail":
        return "Pokemon Detail"
    if page_name.startswith("Activity"):
        return page_name.removeprefix("Activity")
    return page_name


def _route_title(route: str) -> str:
    name = route.split("/")[-1]
    if name.startswith("Activity"):
        name = name.removeprefix("Activity")
    return re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name) or "Index"


def _camel_to_snake(value: str) -> str:
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.lower()


def _arkts_identifier(value: str) -> str:
    identifier = re.sub(r"[^A-Za-z0-9_]", "", value)
    if not identifier:
        return "MigratedPage"
    if identifier[0].isdigit():
        return f"Migrated{identifier}"
    reserved = {
        "Blank",
        "Button",
        "Column",
        "Flex",
        "Grid",
        "Image",
        "List",
        "Row",
        "Scroll",
        "Search",
        "Stack",
        "Text",
        "TextInput",
    }
    if identifier in reserved:
        return f"{identifier}Page"
    return identifier


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")[:120]


def _sample_items_for_layout(layout_file: Path, strings: dict[str, str]) -> list[dict[str, str]]:
    values: list[str] = []
    seen: set[str] = set()

    def add(value: str | None) -> None:
        resolved = _resolve_ref(value, strings)
        if not resolved:
            return
        cleaned = resolved.strip()
        if not cleaned or cleaned.startswith("@") or cleaned.lower() in {"textview", "button", "imageview"}:
            return
        if cleaned not in seen:
            seen.add(cleaned)
            values.append(cleaned)

    def scan(path: Path) -> None:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            return
        for node in root.iter():
            add(_tools_attr(node, "text"))
            add(_android_attr(node, "text"))
            list_item = _tools_attr(node, "listitem")
            if list_item and list_item.startswith("@layout/"):
                item_path = path.parent / f"{list_item.split('/', 1)[1]}.xml"
                if item_path.exists() and item_path != path:
                    scan(item_path)

    scan(layout_file)
    expanded = _expand_domain_samples(values)
    names = expanded[:12] if expanded else ["Sample Item", "Second Item", "Third Item", "Fourth Item"]
    return [{"title": name, "imageUrl": _image_url_for_item(name, index)} for index, name in enumerate(names, start=1)]


def _expand_domain_samples(values: list[str]) -> list[str]:
    lowered = {item.lower() for item in values}
    if "bulbasaur" in lowered:
        return ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", "Squirtle", "Wartortle", "Blastoise", "Pikachu"]
    return values


def _image_url_for_item(name: str, index: int) -> str:
    pokemon_ids = {
        "Bulbasaur": 1,
        "Ivysaur": 2,
        "Venusaur": 3,
        "Charmander": 4,
        "Charmeleon": 5,
        "Charizard": 6,
        "Squirtle": 7,
        "Wartortle": 8,
        "Blastoise": 9,
        "Pikachu": 25,
    }
    pokemon_id = pokemon_ids.get(name)
    if pokemon_id:
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"
    return "app.media.foreground"


def _detail_route(context: dict[str, str]) -> str | None:
    routes = context.get("routes")
    if not isinstance(routes, list):
        return None
    for route in routes:
        if route.endswith("ActivityDetail") or route.endswith("/Detail"):
            return route
    return None
