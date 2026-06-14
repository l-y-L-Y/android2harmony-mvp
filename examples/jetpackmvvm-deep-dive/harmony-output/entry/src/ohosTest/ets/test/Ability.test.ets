import { describe, it, expect } from '@ohos/hypium';

export default function abilityTest() {
  describe('JetpackMVVM migration smoke test', () => {
    it('generated_project_has_entry_page', 0, () => {
      expect('pages/Index').assertContain('Index');
    });
  });
}
