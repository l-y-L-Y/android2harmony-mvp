import { hilog } from '@kit.PerformanceAnalysisKit';

const DOMAIN = 0x0000;

export class Logger {
  static info(message: string): void {
    hilog.info(DOMAIN, 'android2harmony', '%{public}s', message);
  }

  static error(message: string): void {
    hilog.error(DOMAIN, 'android2harmony', '%{public}s', message);
  }
}
