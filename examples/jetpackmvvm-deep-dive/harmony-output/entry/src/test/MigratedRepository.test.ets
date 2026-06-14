import { describe, it, expect } from '@ohos/hypium';
import { PokemonDaoAdapter, PokemonInfoDaoAdapter } from '../main/ets/database/DaoAdapters';

export default function migratedRepositoryTest() {
  describe('JetpackMVVM migrated DAO adapter checks', () => {
    it('filters_pokemon_by_page', 0, async () => {
      const dao = new PokemonDaoAdapter();
      await dao.insertPokemonList([
        { page: 0, name: 'bulbasaur', url: 'pokemon/1' },
        { page: 1, name: 'ivysaur', url: 'pokemon/2' },
      ]);
      const pageZero = await dao.getPokemonList(0);
      expect(pageZero.length).assertEqual(1);
      const throughPageOne = await dao.getAllPokemonList(1);
      expect(throughPageOne.length).assertEqual(2);
    });

    it('filters_pokemon_info_by_name', 0, async () => {
      const dao = new PokemonInfoDaoAdapter();
      await dao.insertPokemonInfo({ id: 1, name: 'bulbasaur', height: 7, weight: 69, experience: 64, types: '[]', hp: 45, attack: 49, defense: 49, speed: 45, exp: 64 });
      const found = await dao.getPokemonInfo('bulbasaur');
      expect(found.length).assertEqual(1);
    });
  });
}
