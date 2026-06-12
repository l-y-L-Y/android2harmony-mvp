import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import _repositories_ets
from android2harmony.model import AndroidModule, AndroidProject


class GeneratorRepositoryTest(unittest.TestCase):
    def test_pokedex_repository_helper_uses_arkts_safe_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "PokemonApi.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface PokemonApi {
  @GET("pokemon")
  suspend fun fetchPokemonList(): PokemonResponse

  @GET("pokemon/{name}")
  suspend fun fetchPokemonInfo(@Path("name") name: String): PokemonInfo
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])

            code = _repositories_ets(project)

            self.assertIn("private pokemonImageUrl(apiUrl: string, name: string): string {", code)
            self.assertIn("${match[1]}", code)
            self.assertIn("this.fallbackPokemonId(name)", code)
            self.assertNotIn("{{", code)
            self.assertNotIn("'bulbasaur':", code)

    def test_generic_repository_uses_discovered_retrofit_methods_without_pokedex_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "UserApi.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface UserApi {
  @GET("users/{id}")
  suspend fun getUser(@Path("id") id: String): User

  @POST("users")
  suspend fun createUser(@Body request: UserRequest): User
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])

            code = _repositories_ets(project)

            self.assertIn("async getUser(params: HttpParams = new HttpParams()): Promise<Object>", code)
            self.assertIn("return this.http.getUser(params);", code)
            self.assertIn("async createUser(params: HttpParams = new HttpParams(), body?: Object): Promise<Object>", code)
            self.assertIn("return this.http.createUser(params, body);", code)
            self.assertNotIn("PokemonDaoAdapter", code)
            self.assertNotIn("PokemonInfo", code)

    def test_repository_methods_are_deduplicated_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api1 = root / "app" / "src" / "main" / "java" / "UserApi.kt"
            api2 = root / "feature" / "src" / "main" / "java" / "UserApi.kt"
            api1.parent.mkdir(parents=True)
            api2.parent.mkdir(parents=True)
            api1.write_text(
                """
interface UserApi {
  @GET("users")
  suspend fun getUsers(): List<User>
}
""",
                encoding="utf-8",
            )
            api2.write_text(
                """
interface UserApi2 {
  @GET("users")
  suspend fun getUsers(): List<User>
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api1, api2])

            code = _repositories_ets(project)

            self.assertEqual(code.count("async getUsers("), 1)
            self.assertEqual(code.count("return this.http.getUsers(params);"), 1)

    def _project(self, root: Path, sources: list[Path]) -> AndroidProject:
        module = AndroidModule(name="app", path=root / "app", kind="application", source_files=sources)
        return AndroidProject(root=root, name="Sample", modules=[module], settings_file=None, gradle_files=[])


if __name__ == "__main__":
    unittest.main()
