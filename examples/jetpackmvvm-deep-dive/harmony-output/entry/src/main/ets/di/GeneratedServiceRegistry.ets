import { ServiceRegistry } from '../common/ServiceRegistry';
import { MigratedHttpClient } from '../network/HttpClient';
import { PokemonDaoAdapter, PokemonInfoDaoAdapter } from '../database/DaoAdapters';
import { MigratedRepository } from '../repositories/MigratedRepositories';

export class HiltBinding {
  kind: string;
  name: string;
  target: string;
  source: string;
  params: string;

  constructor(kind: string, name: string, target: string, source: string, params: string = '') {
    this.kind = kind;
    this.name = name;
    this.target = target;
    this.source = source;
    this.params = params;
  }
}

export const HILT_BINDINGS: HiltBinding[] = [

];

export class GeneratedServiceRegistry {
  static configure(): void {
    ServiceRegistry.require<MigratedHttpClient>('MigratedHttpClient', new MigratedHttpClient());
    ServiceRegistry.require<PokemonDaoAdapter>('PokemonDaoAdapter', new PokemonDaoAdapter());
    ServiceRegistry.require<PokemonInfoDaoAdapter>('PokemonInfoDaoAdapter', new PokemonInfoDaoAdapter());
    ServiceRegistry.require<MigratedRepository>('MigratedRepository', new MigratedRepository());
  }

  static bindingCount(): number {
    return HILT_BINDINGS.length;
  }
}
