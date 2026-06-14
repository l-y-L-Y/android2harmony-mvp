import { common } from '@kit.AbilityKit';
import { relationalStore } from '@kit.ArkData';
import { RoomSchemaSql } from './RoomSchema';

export class RelationalStoreAdapter {
  private store?: relationalStore.RdbStore;
  private lastError: string = '';

  async open(context: common.Context, name: string = 'migrated_room.db'): Promise<void> {
    const config: relationalStore.StoreConfig = {
      name,
      securityLevel: relationalStore.SecurityLevel.S1,
    };
    try {
      this.store = await relationalStore.getRdbStore(context, config);
      for (const sql of RoomSchemaSql) {
        await this.executeSql(sql);
      }
      this.lastError = '';
    } catch (err) {
      this.store = undefined;
      this.lastError = JSON.stringify(err);
    }
  }

  async executeSql(sql: string, bindArgs: relationalStore.ValueType[] = []): Promise<void> {
    if (!this.store) {
      return;
    }
    try {
      await this.store.executeSql(sql, bindArgs);
      this.lastError = '';
    } catch (err) {
      this.lastError = JSON.stringify(err);
    }
  }

  async querySql(sql: string, bindArgs: relationalStore.ValueType[] = []): Promise<relationalStore.ResultSet | undefined> {
    if (!this.store) {
      return undefined;
    }
    try {
      const resultSet = await this.store.querySql(sql, bindArgs);
      this.lastError = '';
      return resultSet;
    } catch (err) {
      this.lastError = JSON.stringify(err);
      return undefined;
    }
  }

  diagnostics(): string {
    return this.lastError;
  }
}
