/* Generated from Room @Dao interfaces. */
import { relationalStore } from '@kit.ArkData';
import { RelationalStoreAdapter } from './RelationalStoreAdapter';

type ValueType = relationalStore.ValueType;

function resultSetToRows(resultSet: relationalStore.ResultSet): Object[] {
  const rows: Object[] = [];
  try {
    const names = resultSet.columnNames;
    while (resultSet.goToNextRow()) {
      const row: Record<string, Object> = {};
      names.forEach((name: string, index: number) => {
        try {
          row[name] = resultSet.getString(index);
        } catch (err) {
          row[name] = '';
        }
      });
      rows.push(row);
    }
  } catch (err) {
    return rows;
  }
  try {
    resultSet.close();
  } catch (err) {
    return rows;
  }
  return rows;
}

export class MigratedDaoAdapter {
  async queryAll(): Promise<Object[]> {
    return [];
  }
}
