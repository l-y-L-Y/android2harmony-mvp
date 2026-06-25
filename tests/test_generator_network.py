import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from android2harmony.generator import (
    _body_type_from_params,
    _discover_retrofit_base_url,
    _discover_retrofit_methods,
    _dto_fields,
    _effective_base_url,
    _http_client_ets,
    _http_method_summary,
    _uses_bearer_auth,
)
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

    def test_discovers_non_suspend_retrofit_methods(self):
        # Retrofit interfaces that return Call<>/Single<> instead of `suspend fun` must still
        # be discovered, otherwise the client falls back to MockServer.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface Api {
  @GET("posts")
  fun getPosts(): Call<List<Post>>
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])
            methods = _discover_retrofit_methods(project)
            self.assertEqual([m["name"] for m in methods], ["getPosts"])
            self.assertEqual(methods[0]["path"], "posts")

    def test_http_client_tolerates_empty_and_non_json_responses(self):
        # Register/POST often returns an empty 200 body (success) and endpoints sometimes return
        # a plain status string ('not found'). JSON.parse would throw on both; the client must not.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface Api {
  @POST("api/data/")
  suspend fun register(@Body data: User): User
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])
            client = _http_client_ets(project)
            self.assertIn("if (text.length === 0)", client)
            self.assertIn("return {} as Object;", client)
            # parse failure returns the raw text instead of throwing.
            self.assertIn("return text as Object;", client)
            self.assertNotIn("HTTP response parse failed", client)

    def test_build_url_joins_base_and_path_with_single_slash(self):
        # A baseUrl ending in '/' + an endpoint path starting with '/' must not produce '//path'
        # (strict backends 404 on the double slash). The client normalizes to one slash.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface Api {
  @GET("/api/posts/")
  suspend fun getPosts(): Response<List<Post>>
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])
            client = _http_client_ets(project)
            # normalization present, naive concatenation gone.
            self.assertIn("this.baseUrl.replace(/\\/+$/, '')", client)
            self.assertIn("resolved.replace(/^\\/+/, '')", client)
            self.assertNotIn("`${this.baseUrl}${resolved}", client)

    def test_discovers_java_retrofit_methods_with_space_and_value_path(self):
        # Java Retrofit interface: `@GET ("path")` (space before paren), `public Call<T> name()`
        # (no `fun`), and `@Path(value = "X", encoded = true)` / `@Body T x`. All previously missed.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "API.java"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
public interface API {
    @GET ("api/data/")
    public Call<ArrayList<Data>> getAllData();

    @GET ("api/data/{Email}/{Password}/")
    public Call<Data> getyourProfile(@Path(value = "Email" , encoded = true) String email,
        @Path(value = "Password" , encoded = true) String password);

    @POST ("api/data/")
    public Call<ResponseBody> postAllData(@Body Data data);
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])
            methods = _discover_retrofit_methods(project)
            by_name = {m["name"]: m for m in methods}
            self.assertEqual(set(by_name), {"getAllData", "getyourProfile", "postAllData"})
            self.assertEqual(by_name["getAllData"]["verb"], "GET")
            self.assertEqual(by_name["getAllData"]["path"], "api/data/")
            self.assertEqual(by_name["getyourProfile"]["params"], "path:Email,path:Password")
            self.assertEqual(by_name["postAllData"]["verb"], "POST")
            self.assertEqual(by_name["postAllData"]["params"], "body:data")

    def test_base_url_resolved_from_companion_constant_reference(self):
        # Foodium's pattern: `.baseUrl(FoodiumService.FOODIUM_API_URL)` with the literal living
        # in a `const val` elsewhere. Previously missed -> useMock stayed true.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
interface FoodiumService {
  companion object {
    const val FOODIUM_API_URL = "https://patilshreyas.github.io/"
  }
}
""",
                encoding="utf-8",
            )
            module = root / "app" / "src" / "main" / "java" / "ApiModule.kt"
            module.write_text(
                """
val retrofit = Retrofit.Builder()
  .baseUrl(FoodiumService.FOODIUM_API_URL)
  .build()
""",
                encoding="utf-8",
            )
            project = self._project(root, [api, module])
            self.assertEqual(_discover_retrofit_base_url(project), "https://patilshreyas.github.io/")
            # a real base was found -> the generated client defaults to live HTTP, not mock.
            self.assertIn("static useMock: boolean = false;", _http_client_ets(project))

    def test_base_url_falls_back_to_named_url_constant(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
object ApiConfig {
  const val BASE_URL = "https://api.example.org/v2/"
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])
            self.assertEqual(_discover_retrofit_base_url(project), "https://api.example.org/v2/")

    def test_effective_base_url_env_override_wins(self):
        # `--api-base-url` (-> A2H_API_BASE_URL) repoints the client at a self-hosted backend.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
val retrofit = Retrofit.Builder().baseUrl("https://prod.example.com/").build()
""",
                encoding="utf-8",
            )
            project = self._project(root, [api])
            self.assertEqual(_discover_retrofit_base_url(project), "https://prod.example.com/")
            with mock.patch.dict(os.environ, {"A2H_API_BASE_URL": "http://10.0.2.2:3000/"}):
                self.assertEqual(_effective_base_url(project), "http://10.0.2.2:3000/")
                self.assertIn("http://10.0.2.2:3000/", _http_client_ets(project))

    def test_post_body_dto_field_names_feed_the_method_summary(self):
        # Regression (RetrofitApp Sign_up): the screen builds `new Data(Name, Email, ...)` with
        # LOCAL var names, but the server keys are the Data CLASS fields (UserName/UserMail/...).
        # The method summary must surface the real DTO field names so the POST body uses them.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "API.java"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
public interface API {
    @POST ("api/data/")
    public Call<ResponseBody> postAllData(@Body Data data);
}
""",
                encoding="utf-8",
            )
            dto = root / "app" / "src" / "main" / "java" / "Data.java"
            dto.write_text(
                """
public class Data {
    String UserName, UserMail, Password, NumberTel;
    public String getUserName() { return UserName; }
    public String getUserMail() { return UserMail; }
    public String getPassword() { return Password; }
    public String getNumberTel() { return NumberTel; }
}
""",
                encoding="utf-8",
            )
            project = self._project_at(root, [api, dto])
            self.assertEqual(_body_type_from_params("@Body Data data"), "Data")
            self.assertEqual(_dto_fields(project, "Data"), ["UserName", "UserMail", "Password", "NumberTel"])
            summary = _http_method_summary(project)
            self.assertIn("body fields: UserName,UserMail,Password,NumberTel", summary)

    def test_dto_fields_handles_kotlin_data_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "app" / "src" / "main" / "java" / "User.kt"
            src.parent.mkdir(parents=True)
            src.write_text(
                "data class User(val userName: String, val email: String, val age: Int)",
                encoding="utf-8",
            )
            project = self._project_at(root, [src])
            self.assertEqual(_dto_fields(project, "User"), ["userName", "email", "age"])
            self.assertEqual(_body_type_from_params("@Body request: User"), "User")

    def test_bearer_auth_interceptor_replicated_in_client(self):
        # An app with an OkHttp interceptor that adds `Authorization: Bearer <token>` must have
        # that replicated: a static token store + the header on every request, or token-protected
        # endpoints (cart/order) 401 after login.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "ApiService.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                """
fun createApi(): ApiService {
  val client = OkHttpClient.Builder().addInterceptor {
    val req = it.request().newBuilder()
    if (Tokens.token != null) req.addHeader("Authorization", "Bearer ${Tokens.token}")
    return@addInterceptor it.proceed(req.build())
  }.build()
}
interface ApiService {
  @GET("cart/list") fun getCart(): Single<CartResponse>
}
""",
                encoding="utf-8",
            )
            project = self._project_at(root, [api])
            self.assertTrue(_uses_bearer_auth(project))
            client = _http_client_ets(project)
            self.assertIn("static authToken: string = ''", client)
            self.assertIn("static setAuthToken(token: string)", client)
            self.assertIn("headers['Authorization'] = `Bearer ${MigratedHttpClient.authToken}`", client)

    def test_no_auth_app_has_no_bearer_plumbing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "app" / "src" / "main" / "java" / "Api.kt"
            api.parent.mkdir(parents=True)
            api.write_text(
                "interface Api {\n  @GET(\"posts\")\n  suspend fun getPosts(): List<Post>\n}\n",
                encoding="utf-8",
            )
            project = self._project_at(root, [api])
            self.assertFalse(_uses_bearer_auth(project))
            client = _http_client_ets(project)
            self.assertNotIn("authToken", client)
            self.assertNotIn("Authorization", client)

    def _project_at(self, root: Path, sources: list[Path]) -> AndroidProject:
        module = AndroidModule(name="app", path=root / "app", kind="application", source_files=sources)
        return AndroidProject(root=root, name="Sample", modules=[module], settings_file=None, gradle_files=[])

    def _project(self, root: Path, sources: list[Path]) -> AndroidProject:
        module = AndroidModule(name="app", path=root / "app", kind="application", source_files=sources)
        return AndroidProject(root=root, name="Sample", modules=[module], settings_file=None, gradle_files=[])


if __name__ == "__main__":
    unittest.main()
