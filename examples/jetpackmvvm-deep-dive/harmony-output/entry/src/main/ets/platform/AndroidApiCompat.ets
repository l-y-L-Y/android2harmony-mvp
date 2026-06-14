/*
 * Generated Android API compatibility facade.
 * This file is the central landing point for Android system API migration.
 * Generated adapters call these methods first; project-specific behavior can
 * then be completed without scattering platform code across pages.
 */

export interface AndroidApiUsage {
  api: string;
  category: string;
  file: string;
  line: number;
  harmonyTarget: string;
  status: string;
}

export interface AndroidPermissionMapping {
  androidName: string;
  harmonyName: string;
  status: string;
}

export interface AndroidResourceMapping {
  androidName: string;
  harmonyName: string;
  kind: string;
  source: string;
}

export const AndroidApiCategories: string[] = [
  'component',
  'context',
  'lifecycle',
  'media',
  'navigation',
  'network',
  'notification',
  'permission',
  'platform',
  'resources',
  'state',
  'ui',
];

export const AndroidApiUsageMap: AndroidApiUsage[] = [
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\MainActivity.java",
    "line": 68,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android image loading/view",
    "category": "media",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\bind\\CommonBindingAdapter.java",
    "line": 22,
    "harmonyTarget": "ArkUI Image with resource/media/http source",
    "status": "adapter-required"
  },
  {
    "api": "Android image loading/view",
    "category": "media",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\bind\\CommonBindingAdapter.java",
    "line": 28,
    "harmonyTarget": "ArkUI Image with resource/media/http source",
    "status": "adapter-required"
  },
  {
    "api": "Android image loading/view",
    "category": "media",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\bind\\CommonBindingAdapter.java",
    "line": 37,
    "harmonyTarget": "ArkUI Image with resource/media/http source",
    "status": "adapter-required"
  },
  {
    "api": "Android image loading/view",
    "category": "media",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\bind\\CommonBindingAdapter.java",
    "line": 38,
    "harmonyTarget": "ArkUI Image with resource/media/http source",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\bind\\WebViewBindingAdapter.java",
    "line": 4,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\bind\\WebViewBindingAdapter.java",
    "line": 28,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\DrawerFragment.java",
    "line": 70,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\LoginFragment.java",
    "line": 75,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\LoginFragment.java",
    "line": 105,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\LoginFragment.java",
    "line": 137,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\MainFragment.java",
    "line": 81,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\PlayerFragment.java",
    "line": 82,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\PlayerFragment.java",
    "line": 200,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\PlayerFragment.java",
    "line": 229,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\PlayerFragment.java",
    "line": 230,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\PlayerFragment.java",
    "line": 232,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\SearchFragment.java",
    "line": 70,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\view\\PlayPauseView.java",
    "line": 5,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\view\\PlayPauseView.java",
    "line": 37,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 23,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 24,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android app component",
    "category": "component",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 25,
    "harmonyTarget": "ExtensionAbility or explicit service facade",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 26,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 27,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 29,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 35,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android app component",
    "category": "component",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 51,
    "harmonyTarget": "ExtensionAbility or explicit service facade",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 81,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 85,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 87,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 90,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 91,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 91,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 93,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 94,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 95,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 97,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 101,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 101,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 106,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 108,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 146,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 147,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 159,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 160,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 161,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 163,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 164,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 166,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 167,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 169,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 170,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 172,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 173,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android notifications",
    "category": "notification",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 175,
    "harmonyTarget": "notificationManager Kit",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 176,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\widget\\PlayerService.java",
    "line": 190,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DiffUtils.java",
    "line": 20,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DiffUtils.java",
    "line": 30,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DiffUtils.java",
    "line": 32,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DiffUtils.java",
    "line": 43,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DiffUtils.java",
    "line": 45,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DiffUtils.java",
    "line": 60,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DiffUtils.java",
    "line": 62,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DrawerAdapter.java",
    "line": 19,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DrawerAdapter.java",
    "line": 20,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DrawerAdapter.java",
    "line": 23,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DrawerAdapter.java",
    "line": 35,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DrawerAdapter.java",
    "line": 36,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DrawerAdapter.java",
    "line": 41,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\DrawerAdapter.java",
    "line": 47,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\PlaylistAdapter.java",
    "line": 19,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\PlaylistAdapter.java",
    "line": 22,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\PlaylistAdapter.java",
    "line": 35,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\PlaylistAdapter.java",
    "line": 36,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "RecyclerView adapter/list",
    "category": "ui",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\PlaylistAdapter.java",
    "line": 40,
    "harmonyTarget": "ArkUI List/Grid and state array",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\ui\\page\\adapter\\PlaylistAdapter.java",
    "line": 44,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\message\\DrawerCoordinateManager.java",
    "line": 41,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Android app component",
    "category": "component",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\message\\PlayerReceiver.java",
    "line": 19,
    "harmonyTarget": "ExtensionAbility or explicit service facade",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\message\\PlayerReceiver.java",
    "line": 20,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\message\\PlayerReceiver.java",
    "line": 21,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android app component",
    "category": "component",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\message\\PlayerReceiver.java",
    "line": 29,
    "harmonyTarget": "ExtensionAbility or explicit service facade",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\message\\PlayerReceiver.java",
    "line": 32,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\message\\SharedViewModel.java",
    "line": 19,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\message\\SharedViewModel.java",
    "line": 31,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\proxy\\PlayerManager.java",
    "line": 19,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\proxy\\PlayerManager.java",
    "line": 20,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\proxy\\PlayerManager.java",
    "line": 22,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\proxy\\PlayerManager.java",
    "line": 57,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\proxy\\PlayerManager.java",
    "line": 65,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\proxy\\PlayerManager.java",
    "line": 66,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\proxy\\PlayerManager.java",
    "line": 77,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\proxy\\PlayerManager.java",
    "line": 167,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\request\\AccountRequester.java",
    "line": 49,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\request\\DownloadRequester.java",
    "line": 26,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\request\\InfoRequester.java",
    "line": 42,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\request\\InfoRequester.java",
    "line": 57,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\request\\MusicRequester.java",
    "line": 40,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\request\\MusicRequester.java",
    "line": 55,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\domain\\usecase\\CanBeStoppedUseCase.java",
    "line": 32,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Retrofit/OkHttp",
    "category": "network",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\api\\AccountService.java",
    "line": 13,
    "harmonyTarget": "NetworkKit http client",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\config\\Const.java",
    "line": 12,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\config\\Const.java",
    "line": 13,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Retrofit/OkHttp",
    "category": "network",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\repository\\DataRepository.java",
    "line": 43,
    "harmonyTarget": "NetworkKit http client",
    "status": "partially-generated"
  },
  {
    "api": "Retrofit/OkHttp",
    "category": "network",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\repository\\DataRepository.java",
    "line": 47,
    "harmonyTarget": "NetworkKit http client",
    "status": "partially-generated"
  },
  {
    "api": "Retrofit/OkHttp",
    "category": "network",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\repository\\DataRepository.java",
    "line": 64,
    "harmonyTarget": "NetworkKit http client",
    "status": "partially-generated"
  },
  {
    "api": "Retrofit/OkHttp",
    "category": "network",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\repository\\DataRepository.java",
    "line": 69,
    "harmonyTarget": "NetworkKit http client",
    "status": "partially-generated"
  },
  {
    "api": "Retrofit/OkHttp",
    "category": "network",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\repository\\DataRepository.java",
    "line": 75,
    "harmonyTarget": "NetworkKit http client",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\repository\\DataRepository.java",
    "line": 90,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\puremusic\\data\\repository\\DataRepository.java",
    "line": 100,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\androidTest\\java\\com\\kunminx\\puremusic\\ExampleInstrumentedTest.java",
    "line": 5,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\androidTest\\java\\com\\kunminx\\puremusic\\ExampleInstrumentedTest.java",
    "line": 23,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 3,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 23,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 25,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 33,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 35,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 46,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 79,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 87,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\AdaptScreenUtils.java",
    "line": 94,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android runtime permission",
    "category": "permission",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 3,
    "harmonyTarget": "abilityAccessCtrl permission flow",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 6,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 8,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 11,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 23,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 25,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 58,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 69,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 99,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 110,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 123,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 143,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 154,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 223,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 236,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 251,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 269,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 315,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 332,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 351,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 373,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 383,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 387,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 459,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 474,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 515,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 556,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 557,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 567,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 578,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 579,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android API level/version gate",
    "category": "platform",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 589,
    "harmonyTarget": "Harmony device info and capability checks",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 600,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 612,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 613,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 615,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 616,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 620,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\BarUtils.java",
    "line": 620,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android runtime permission",
    "category": "permission",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\NetworkUtils.java",
    "line": 3,
    "harmonyTarget": "abilityAccessCtrl permission flow",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\NetworkUtils.java",
    "line": 5,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\NetworkUtils.java",
    "line": 36,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android runtime permission",
    "category": "permission",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 3,
    "harmonyTarget": "abilityAccessCtrl permission flow",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 7,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 10,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 22,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 44,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 56,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 68,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 77,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 85,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 94,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 103,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 121,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 141,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 160,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 171,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 190,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 201,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 213,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\ScreenUtils.java",
    "line": 237,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 4,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 7,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 63,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 132,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 141,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 143,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 149,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 154,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 181,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 186,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 198,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 207,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 212,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 225,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 228,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 234,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 236,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 241,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 248,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 271,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 278,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 312,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 313,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 316,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 327,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\utils\\Utils.java",
    "line": 345,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\bind\\DrawablesBindingAdapter.java",
    "line": 6,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\bind\\DrawablesBindingAdapter.java",
    "line": 919,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 19,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 20,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 21,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 29,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 69,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 73,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 78,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 87,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseActivity.java",
    "line": 93,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 19,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 20,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 21,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 26,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 53,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 57,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 61,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 70,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 76,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\BaseFragment.java",
    "line": 80,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\StateHolder.java",
    "line": 3,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\ui\\page\\StateHolder.java",
    "line": 8,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\domain\\request\\Requester.java",
    "line": 3,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\domain\\request\\Requester.java",
    "line": 6,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\domain\\request\\Requester.java",
    "line": 17,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Android Activity lifecycle",
    "category": "lifecycle",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\domain\\request\\Requester.java",
    "line": 35,
    "harmonyTarget": "UIAbility/Page lifecycle",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\domain\\request\\Requester.java",
    "line": 48,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Lifecycle/ViewModel/coroutine state",
    "category": "state",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\data\\response\\DataResult.java",
    "line": 22,
    "harmonyTarget": "ArkUI @State/@Observed plus Promise/async",
    "status": "adapter-required"
  },
  {
    "api": "Android app component",
    "category": "component",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\data\\response\\manager\\NetworkStateReceive.java",
    "line": 19,
    "harmonyTarget": "ExtensionAbility or explicit service facade",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\data\\response\\manager\\NetworkStateReceive.java",
    "line": 20,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Intent navigation/data passing",
    "category": "navigation",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\data\\response\\manager\\NetworkStateReceive.java",
    "line": 21,
    "harmonyTarget": "router.pushUrl/router.back with params",
    "status": "adapter-required"
  },
  {
    "api": "Android app component",
    "category": "component",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\data\\response\\manager\\NetworkStateReceive.java",
    "line": 33,
    "harmonyTarget": "ExtensionAbility or explicit service facade",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\data\\response\\manager\\NetworkStateReceive.java",
    "line": 36,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android resources",
    "category": "resources",
    "file": "src\\main\\java\\com\\kunminx\\architecture\\data\\response\\manager\\NetworkStateReceive.java",
    "line": 39,
    "harmonyTarget": "Harmony resources/base media/element/profile",
    "status": "partially-generated"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\androidTest\\java\\com\\kunminx\\architecture\\ExampleInstrumentedTest.java",
    "line": 21,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  },
  {
    "api": "Android Context",
    "category": "context",
    "file": "src\\androidTest\\java\\com\\kunminx\\architecture\\ExampleInstrumentedTest.java",
    "line": 39,
    "harmonyTarget": "common.Context or explicit service injection",
    "status": "adapter-required"
  }
];
export const AndroidPermissionMappings: AndroidPermissionMapping[] = [
  {
    "androidName": "android.permission.INTERNET",
    "harmonyName": "ohos.permission.INTERNET",
    "status": "generated"
  },
  {
    "androidName": "android.permission.ACCESS_NETWORK_STATE",
    "harmonyName": "ohos.permission.GET_NETWORK_INFO",
    "status": "generated"
  },
  {
    "androidName": "android.permission.FOREGROUND_SERVICE",
    "harmonyName": "ohos.permission.FOREGROUND_SERVICE",
    "status": "adapter-required"
  }
];
export const AndroidResourceMappings: AndroidResourceMapping[] = [
  {
    "androidName": "anim.h_fragment_enter",
    "harmonyName": "anim.h_fragment_enter",
    "kind": "anim",
    "source": "app/src/main/res/anim/h_fragment_enter.xml"
  },
  {
    "androidName": "anim.h_fragment_exit",
    "harmonyName": "anim.h_fragment_exit",
    "kind": "anim",
    "source": "app/src/main/res/anim/h_fragment_exit.xml"
  },
  {
    "androidName": "anim.h_fragment_pop_enter",
    "harmonyName": "anim.h_fragment_pop_enter",
    "kind": "anim",
    "source": "app/src/main/res/anim/h_fragment_pop_enter.xml"
  },
  {
    "androidName": "anim.h_fragment_pop_exit",
    "harmonyName": "anim.h_fragment_pop_exit",
    "kind": "anim",
    "source": "app/src/main/res/anim/h_fragment_pop_exit.xml"
  },
  {
    "androidName": "drawable.bar_selector_white",
    "harmonyName": "media.bar_selector_white",
    "kind": "media",
    "source": "app/src/main/res/drawable/bar_selector_white.xml"
  },
  {
    "androidName": "drawable.bg_home",
    "harmonyName": "media.bg_home",
    "kind": "media",
    "source": "app/src/main/res/drawable/bg_home.png"
  },
  {
    "androidName": "drawable.ic_menu_black_48dp",
    "harmonyName": "media.ic_menu_black_48dp",
    "kind": "media",
    "source": "app/src/main/res/drawable/ic_menu_black_48dp.xml"
  },
  {
    "androidName": "drawable.ic_music_note_black_48dp",
    "harmonyName": "media.ic_music_note_black_48dp",
    "kind": "media",
    "source": "app/src/main/res/drawable/ic_music_note_black_48dp.xml"
  },
  {
    "androidName": "drawable.ic_search_black_48dp",
    "harmonyName": "media.ic_search_black_48dp",
    "kind": "media",
    "source": "app/src/main/res/drawable/ic_search_black_48dp.xml"
  },
  {
    "androidName": "drawable.loading_animation",
    "harmonyName": "media.loading_animation",
    "kind": "media",
    "source": "app/src/main/res/drawable/loading_animation.xml"
  },
  {
    "androidName": "drawable.progressbar_color",
    "harmonyName": "media.progressbar_color",
    "kind": "media",
    "source": "app/src/main/res/drawable/progressbar_color.xml"
  },
  {
    "androidName": "drawable.bg_album_default",
    "harmonyName": "media.bg_album_default",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/bg_album_default.png"
  },
  {
    "androidName": "drawable.ic_action_pause",
    "harmonyName": "media.ic_action_pause",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/ic_action_pause.png"
  },
  {
    "androidName": "drawable.ic_action_play",
    "harmonyName": "media.ic_action_play",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/ic_action_play.png"
  },
  {
    "androidName": "drawable.ic_close_white",
    "harmonyName": "media.ic_close_white",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/ic_close_white.png"
  },
  {
    "androidName": "drawable.ic_launcher",
    "harmonyName": "media.ic_launcher",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/ic_launcher.png"
  },
  {
    "androidName": "drawable.ic_next_dark",
    "harmonyName": "media.ic_next_dark",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/ic_next_dark.png"
  },
  {
    "androidName": "drawable.ic_player",
    "harmonyName": "media.ic_player",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/ic_player.png"
  },
  {
    "androidName": "drawable.ic_previous_dark",
    "harmonyName": "media.ic_previous_dark",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/ic_previous_dark.png"
  },
  {
    "androidName": "drawable.ic_progress",
    "harmonyName": "media.ic_progress",
    "kind": "media",
    "source": "app/src/main/res/drawable-xxhdpi/ic_progress.png"
  },
  {
    "androidName": "layout.activity_main",
    "harmonyName": "layout.activity_main",
    "kind": "layout",
    "source": "app/src/main/res/layout/activity_main.xml"
  },
  {
    "androidName": "layout.adapter_library",
    "harmonyName": "layout.adapter_library",
    "kind": "layout",
    "source": "app/src/main/res/layout/adapter_library.xml"
  },
  {
    "androidName": "layout.adapter_play_item",
    "harmonyName": "layout.adapter_play_item",
    "kind": "layout",
    "source": "app/src/main/res/layout/adapter_play_item.xml"
  },
  {
    "androidName": "layout.fragment_drawer",
    "harmonyName": "layout.fragment_drawer",
    "kind": "layout",
    "source": "app/src/main/res/layout/fragment_drawer.xml"
  },
  {
    "androidName": "layout.fragment_login",
    "harmonyName": "layout.fragment_login",
    "kind": "layout",
    "source": "app/src/main/res/layout/fragment_login.xml"
  },
  {
    "androidName": "layout.fragment_main",
    "harmonyName": "layout.fragment_main",
    "kind": "layout",
    "source": "app/src/main/res/layout/fragment_main.xml"
  },
  {
    "androidName": "layout.fragment_player",
    "harmonyName": "layout.fragment_player",
    "kind": "layout",
    "source": "app/src/main/res/layout/fragment_player.xml"
  },
  {
    "androidName": "layout.fragment_search",
    "harmonyName": "layout.fragment_search",
    "kind": "layout",
    "source": "app/src/main/res/layout/fragment_search.xml"
  },
  {
    "androidName": "layout.notify_player_big",
    "harmonyName": "layout.notify_player_big",
    "kind": "layout",
    "source": "app/src/main/res/layout/notify_player_big.xml"
  },
  {
    "androidName": "layout.notify_player_small",
    "harmonyName": "layout.notify_player_small",
    "kind": "layout",
    "source": "app/src/main/res/layout/notify_player_small.xml"
  },
  {
    "androidName": "navigation.nav_drawer",
    "harmonyName": "navigation.nav_drawer",
    "kind": "navigation",
    "source": "app/src/main/res/navigation/nav_drawer.xml"
  },
  {
    "androidName": "navigation.nav_main",
    "harmonyName": "navigation.nav_main",
    "kind": "navigation",
    "source": "app/src/main/res/navigation/nav_main.xml"
  },
  {
    "androidName": "navigation.nav_slide",
    "harmonyName": "navigation.nav_slide",
    "kind": "navigation",
    "source": "app/src/main/res/navigation/nav_slide.xml"
  },
  {
    "androidName": "declare-styleable.PlayPauseView",
    "harmonyName": "declare-styleable.PlayPauseView",
    "kind": "declare-styleable",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/attrs.xml"
  },
  {
    "androidName": "color.colorPrimary",
    "harmonyName": "element.colorPrimary",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/colors.xml"
  },
  {
    "androidName": "color.colorPrimaryDark",
    "harmonyName": "element.colorPrimaryDark",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/colors.xml"
  },
  {
    "androidName": "color.colorAccent",
    "harmonyName": "element.colorAccent",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/colors.xml"
  },
  {
    "androidName": "color.white",
    "harmonyName": "element.white",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/colors.xml"
  },
  {
    "androidName": "color.black",
    "harmonyName": "element.black",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/colors.xml"
  },
  {
    "androidName": "color.gray",
    "harmonyName": "element.gray",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/colors.xml"
  },
  {
    "androidName": "color.light_gray",
    "harmonyName": "element.light_gray",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/colors.xml"
  },
  {
    "androidName": "color.transparent",
    "harmonyName": "element.transparent",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/colors.xml"
  },
  {
    "androidName": "dimen.sliding_up_header",
    "harmonyName": "element.sliding_up_header",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/dimen.xml"
  },
  {
    "androidName": "dimen.sliding_up_header_land",
    "harmonyName": "element.sliding_up_header_land",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/dimen.xml"
  },
  {
    "androidName": "string.app_name",
    "harmonyName": "element.app_name",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.app_name_debug",
    "harmonyName": "element.app_name_debug",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.welcome_back",
    "harmonyName": "element.welcome_back",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.free_music_json",
    "harmonyName": "element.free_music_json",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.library_json",
    "harmonyName": "element.library_json",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.play",
    "harmonyName": "element.play",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.notify_of_play",
    "harmonyName": "element.notify_of_play",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.network_unconnected",
    "harmonyName": "element.network_unconnected",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.play_repeat",
    "harmonyName": "element.play_repeat",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.play_repeat_once",
    "harmonyName": "element.play_repeat_once",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.play_shuffle",
    "harmonyName": "element.play_shuffle",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.unfinished",
    "harmonyName": "element.unfinished",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.recently",
    "harmonyName": "element.recently",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.best_practice",
    "harmonyName": "element.best_practice",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.app_summary",
    "harmonyName": "element.app_summary",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.project_title",
    "harmonyName": "element.project_title",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.Copyright",
    "harmonyName": "element.Copyright",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.search_page_tip",
    "harmonyName": "element.search_page_tip",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.test_download",
    "harmonyName": "element.test_download",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.test_lifecycle_download",
    "harmonyName": "element.test_lifecycle_download",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.search_back",
    "harmonyName": "element.search_back",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.relearn_android",
    "harmonyName": "element.relearn_android",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.learn_more_friends",
    "harmonyName": "element.learn_more_friends",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.learn_more",
    "harmonyName": "element.learn_more",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.login_title",
    "harmonyName": "element.login_title",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.login_content",
    "harmonyName": "element.login_content",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.user_name",
    "harmonyName": "element.user_name",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.user_password",
    "harmonyName": "element.user_password",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.login",
    "harmonyName": "element.login",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.username_or_pwd_incomplete",
    "harmonyName": "element.username_or_pwd_incomplete",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.network_state_retry",
    "harmonyName": "element.network_state_retry",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.article_navigation",
    "harmonyName": "element.article_navigation",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "string.github_project",
    "harmonyName": "element.github_project",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/strings.xml"
  },
  {
    "androidName": "style.AppTheme",
    "harmonyName": "style.AppTheme",
    "kind": "style",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/app/src/main/res/values/styles.xml"
  },
  {
    "androidName": "xml.network_security_config",
    "harmonyName": "xml.network_security_config",
    "kind": "xml",
    "source": "app/src/main/res/xml/network_security_config.xml"
  },
  {
    "androidName": "string.network_not_good",
    "harmonyName": "element.network_not_good",
    "kind": "element",
    "source": "D:/codex/android-benchmarks/test5/JetpackMVVM/architecture/src/main/res/values/strings.xml"
  },
  {
    "androidName": "xml.file_paths",
    "harmonyName": "xml.file_paths",
    "kind": "xml",
    "source": "architecture/src/main/res/xml/file_paths.xml"
  }
];

export class PermissionResult {
  name: string;
  harmonyName: string;
  granted: boolean;
  status: string;

  constructor(name: string, harmonyName: string, granted: boolean, status: string) {
    this.name = name;
    this.harmonyName = harmonyName;
    this.granted = granted;
    this.status = status;
  }
}

export class AndroidResourceRef {
  name: string;
  value: string;
  kind: string;

  constructor(name: string, value: string, kind: string) {
    this.name = name;
    this.value = value;
    this.kind = kind;
  }
}

export class AndroidContextService {
  name: string;
  status: string;

  constructor(name: string, status: string) {
    this.name = name;
    this.status = status;
  }
}

export class AndroidPreferences {
  private values: Map<string, string> = new Map<string, string>();

  getString(key: string, fallback: string = ''): string {
    const value = this.values.get(key);
    return value === undefined ? fallback : value;
  }

  putString(key: string, value: string): void {
    this.values.set(key, value);
  }

  getBoolean(key: string, fallback: boolean = false): boolean {
    const value = this.values.get(key);
    if (value === undefined) {
      return fallback;
    }
    return value === 'true';
  }

  putBoolean(key: string, value: boolean): void {
    this.values.set(key, value ? 'true' : 'false');
  }

  getNumber(key: string, fallback: number = 0): number {
    const value = this.values.get(key);
    if (value === undefined) {
      return fallback;
    }
    return Number(value);
  }

  putNumber(key: string, value: number): void {
    this.values.set(key, String(value));
  }
}

export class AndroidApiCompat {
  private static preferences: AndroidPreferences = new AndroidPreferences();
  private static lifecycleEvents: string[] = [];

  static describe(): string {
    return `Android API compat facade: ${AndroidApiUsageMap.length} usage points, ${AndroidApiCategories.length} categories`;
  }

  static route(url: string, params: Record<string, Object> = {}): Record<string, Object> {
    return { url, params };
  }

  static contextService(name: string): AndroidContextService {
    return new AndroidContextService(name, 'adapter-required');
  }

  static permission(name: string): PermissionResult {
    for (const item of AndroidPermissionMappings) {
      if (item.androidName === name || item.harmonyName === name) {
        return new PermissionResult(name, item.harmonyName, item.status === 'generated', item.status);
      }
    }
    const granted = name === 'ohos.permission.INTERNET' || name === 'android.permission.INTERNET';
    const harmonyName = name.startsWith('ohos.permission.') ? name : name.replace('android.permission.', 'ohos.permission.');
    return new PermissionResult(name, harmonyName, granted, granted ? 'generated' : 'adapter-required');
  }

  static resource(name: string, kind: string = 'unknown'): AndroidResourceRef {
    const normalized = name.replace('R.', '').replace('@', '').replace('/', '.');
    for (const item of AndroidResourceMappings) {
      if (item.androidName === name || item.androidName === normalized || item.harmonyName === normalized) {
        return new AndroidResourceRef(name, item.harmonyName, item.kind);
      }
    }
    return new AndroidResourceRef(name, normalized, kind);
  }

  static sharedPreferences(name: string = 'migrated'): AndroidPreferences {
    return AndroidApiCompat.preferences;
  }

  static lifecycle(event: string): void {
    AndroidApiCompat.lifecycleEvents.push(event);
  }

  static lifecycleTrace(): string[] {
    return AndroidApiCompat.lifecycleEvents;
  }

  static async runBackgroundTask(name: string, task: () => Promise<void>): Promise<void> {
    AndroidApiCompat.lifecycle(`background:${name}`);
    await task();
  }
}
