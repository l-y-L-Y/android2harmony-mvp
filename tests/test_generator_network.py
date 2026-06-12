import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import _discover_retrofit_methods, _http_client_ets
from android2harmony.model import AndroidModule, AndroidProject


class GeneratorNetworkTest(unittest.TestCase):
    def test_discovers_retrofit_verbs_path_query_and_body_params(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
package sample

interface Api {
  @GET("users/{id}")
  suspend fun getUser(@Path("id") id: String, @Query("expand") expand: String): User

  @POST("users")
  suspend fun createUser(@Body request: UserRequest): User

  @PUT("users/{id}")
  suspend fun updateUser(@Path("id") id: String, @Body request: UserRequest): User
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])

            methods = _discover_retrofit_methods(project)

            self.assertEqual([item["verb"] for item in methods], ["GET", "POST", "PUT"])
            self.assertEqual(methods[0]["params"], "path:id,query:expand")
            self.assertEqual(methods[1]["params"], "body:request")
            self.assertEqual(methods[2]["params"], "path:id,body:request")

    def test_http_client_preserves_http_verbs_and_body_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface Api {
  @POST("users")
  suspend fun createUser(@Body request: UserRequest): User
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])

            client = _http_client_ets(project)

            self.assertIn("async createUser(params: HttpParams = new HttpParams(), body?: Object)", client)
            self.assertIn("http.RequestMethod.POST", client)
            self.assertIn("const requestOptions: http.HttpRequestOptions", client)
            self.assertIn("requestOptions.extraData = JSON.stringify(body)", client)
            self.assertIn("Content-Type", client)
            self.assertNotIn("header: body === undefined ? undefined : {", client)

    def test_patch_routes_are_generated_with_supported_harmony_request_method(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface Api {
  @PATCH("users/{id}")
  suspend fun updateUser(@Path("id") id: String, @Body request: UserRequest): User
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])

            client = _http_client_ets(project)

            self.assertIn("http.RequestMethod.PUT", client)
            self.assertNotIn("http.RequestMethod.PATCH", client)
            self.assertEqual(client.count("async updateUser("), 1)

    def _project(self, root: Path, sources: list[Path]) -> AndroidProject:
        module = AndroidModule(name="app", path=root / "app", kind="application", source_files=sources)
        return AndroidProject(root=root, name="Sample", modules=[module], settings_file=None, gradle_files=[])


if __name__ == "__main__":
    unittest.main()
