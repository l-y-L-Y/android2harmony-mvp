import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import _dao_adapters_ets
from android2harmony.model import AndroidModule, AndroidProject


class GeneratorRoomTest(unittest.TestCase):
    def test_dao_memory_fallback_supports_where_order_and_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dao = root / "app" / "src" / "main" / "java" / "TaskDao.kt"
            dao.parent.mkdir(parents=True)
            dao.write_text(
                """
package sample

@Dao
interface TaskDao {
  @Insert
  suspend fun insertTasks(tasks: List<TaskEntity>)

  @Query("SELECT * FROM TaskEntity WHERE status = :status ORDER BY createdAt DESC LIMIT :limit")
  suspend fun loadRecent(status: String, limit: Int): List<TaskEntity>
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [dao])

            code = _dao_adapters_ets(project)

            self.assertIn("async loadRecent(status?: ValueType, limit?: ValueType)", code)
            self.assertIn("const args: ValueType[] = this.compactArgs([status, limit]);", code)
            self.assertIn("this.applyWhereEquals(rows, sql, args)", code)
            self.assertIn("this.applyOrderBy(rows, sql)", code)
            self.assertIn("this.applyLimit(rows, sql, args)", code)

    def _project(self, root: Path, sources: list[Path]) -> AndroidProject:
        module = AndroidModule(name="app", path=root / "app", kind="application", source_files=sources)
        return AndroidProject(root=root, name="Sample", modules=[module], settings_file=None, gradle_files=[])


if __name__ == "__main__":
    unittest.main()
