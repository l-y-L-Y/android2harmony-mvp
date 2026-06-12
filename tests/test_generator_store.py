import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import _state_stores_ets
from android2harmony.model import AndroidModule, AndroidProject


class GeneratorStoreTest(unittest.TestCase):
    def test_viewmodel_action_calls_matching_repository_method_and_updates_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "UserApi.kt"
            viewmodel = root / "app" / "src" / "main" / "java" / "UserViewModel.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface UserApi {
  @GET("users")
  suspend fun getUsers(): List<User>
}
""",
                encoding="utf-8",
            )
            viewmodel.write_text(
                """
class UserViewModel : ViewModel() {
  private val users: MutableStateFlow<List<User>> = MutableStateFlow(emptyList())

  fun getUsers() {
  }
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api, viewmodel])

            code = _state_stores_ets(project)

            self.assertIn("export class UserViewModelStore", code)
            self.assertIn("users: Object[] = [];", code)
            self.assertIn("isLoading: boolean = false;", code)
            self.assertIn("toastMessage: string | undefined = undefined;", code)
            self.assertIn("async getUsers(): Promise<Object[]>", code)
            self.assertIn("const result = await repository.getUsers();", code)
            self.assertIn("this.users = result as Object[];", code)

    def test_viewmodel_actions_are_deduplicated_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            viewmodel = root / "app" / "src" / "main" / "java" / "ComposeViewModel.kt"
            viewmodel.parent.mkdir(parents=True)
            viewmodel.write_text(
                """
class ComposeViewModel : ViewModel() {
  fun pickMedia() {
  }

  fun pickMedia(value: String) {
  }
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [viewmodel])

            code = _state_stores_ets(project)

            self.assertEqual(code.count("async pickMedia("), 1)

    def _project(self, root: Path, sources: list[Path]) -> AndroidProject:
        module = AndroidModule(name="app", path=root / "app", kind="application", source_files=sources)
        return AndroidProject(root=root, name="Sample", modules=[module], settings_file=None, gradle_files=[])


if __name__ == "__main__":
    unittest.main()
