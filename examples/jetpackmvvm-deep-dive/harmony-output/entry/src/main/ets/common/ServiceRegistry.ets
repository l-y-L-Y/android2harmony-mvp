export class ServiceRegistry {
  private static services: Map<string, Object> = new Map<string, Object>();

  static register(name: string, service: Object): void {
    ServiceRegistry.services.set(name, service);
  }

  static resolve<T extends Object>(name: string): T | undefined {
    return ServiceRegistry.services.get(name) as T | undefined;
  }

  static require<T extends Object>(name: string, fallback: T): T {
    const existing = ServiceRegistry.resolve<T>(name);
    if (existing) {
      return existing;
    }
    ServiceRegistry.register(name, fallback);
    return fallback;
  }

  static has(name: string): boolean {
    return ServiceRegistry.services.has(name);
  }
}
