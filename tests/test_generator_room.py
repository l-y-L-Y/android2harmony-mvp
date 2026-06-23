import tempfile
import unittest
from pathlib import Path

from android2harmony.generator import (
    _dao_adapter_names,
    _dao_adapters_ets,
    _room_schema_ets,
)
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

    def test_persistence_chain_matches_real_room_table(self):
        # MyNotes-shaped: non-suspend Flow @Query, @Entity(tableName=...), and a multi-line
        # comment between fields. All three used to break persistence.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "app" / "src" / "main" / "java"
            base.mkdir(parents=True)
            (base / "TaskEntity.kt").write_text(
                """
package m
@Entity(tableName = "tasks")
data class TaskEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Int? = 0,
    val title: String,
    val description: String,
    // added in db v2, hence while migrating,
    // a default value is provided
    @ColumnInfo(defaultValue = "0")
    val deadLine: String
)
""",
                encoding="utf-8",
            )
            (base / "TasksDao.kt").write_text(
                """
package m
@Dao
interface TasksDao {
  @Insert(onConflict = REPLACE)
  suspend fun saveTask(task: TaskEntity)
  @Delete
  suspend fun deleteTask(task: TaskEntity)
  @Query("SELECT * from tasks")
  fun getTasks(): Flow<List<TaskEntity>>
}
""",
                encoding="utf-8",
            )
            project = self._project(root, [base / "TaskEntity.kt", base / "TasksDao.kt"])

            schema = _room_schema_ets(project)
            dao = _dao_adapters_ets(project)

            # real Room table name (not the class name) and all 4 columns incl. the one
            # after the comment
            self.assertIn("CREATE TABLE IF NOT EXISTS tasks (", schema)
            self.assertNotIn("TaskEntity (", schema)
            self.assertIn("deadLine TEXT", schema)
            # DAO binds to that exact table even though the query is non-suspend
            self.assertIn("private tableName: string = 'tasks';", dao)
            self.assertIn("export class TasksDaoAdapter {", dao)
            # exact adapter name is what the page prompt will tell the LLM to import
            self.assertEqual(_dao_adapter_names(project), ["TasksDaoAdapter"])

    def _project(self, root: Path, sources: list[Path]) -> AndroidProject:
        module = AndroidModule(name="app", path=root / "app", kind="application", source_files=sources)
        return AndroidProject(root=root, name="Sample", modules=[module], settings_file=None, gradle_files=[])


if __name__ == "__main__":
    unittest.main()
