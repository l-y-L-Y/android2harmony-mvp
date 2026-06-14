import type router from '@ohos.router';
import type { UIContext } from '@ohos.arkui.UIContext';

interface UiContextOwner {
  getUIContext(): UIContext;
}

export class NavigationCompat {
  static params(owner: Object): Record<string, string> {
    try {
      const uiContext = (owner as UiContextOwner).getUIContext();
      const params = uiContext.getRouter().getParams() as Record<string, string>;
      return params || {};
    } catch (err) {
      return {};
    }
  }

  static push(owner: Object, options: router.RouterOptions): void {
    try {
      const uiContext = (owner as UiContextOwner).getUIContext();
      uiContext.getRouter().pushUrl(options);
    } catch (err) {
      return;
    }
  }

  static replace(owner: Object, options: router.RouterOptions): void {
    try {
      const uiContext = (owner as UiContextOwner).getUIContext();
      uiContext.getRouter().replaceUrl(options);
    } catch (err) {
      return;
    }
  }
}
