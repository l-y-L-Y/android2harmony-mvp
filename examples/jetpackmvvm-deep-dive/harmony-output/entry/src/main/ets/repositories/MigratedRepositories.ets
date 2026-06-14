import { ServiceRegistry } from '../common/ServiceRegistry';
import { HttpParams, MigratedHttpClient } from '../network/HttpClient';

export class MigratedRepository {
  private readonly http: MigratedHttpClient = ServiceRegistry.require<MigratedHttpClient>('MigratedHttpClient', new MigratedHttpClient());

  async fetchAll(): Promise<Object[]> {
    return [];
  }

}
