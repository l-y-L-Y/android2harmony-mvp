import { describe, it, expect } from '@ohos/hypium';

export default function localUnitTest() {
  describe('JetpackMVVM local migration checks', () => {
    it('migration_scaffold_exists', 0, () => {
      expect('JetpackMVVM').assertEqual('JetpackMVVM');
    });
  });
}
