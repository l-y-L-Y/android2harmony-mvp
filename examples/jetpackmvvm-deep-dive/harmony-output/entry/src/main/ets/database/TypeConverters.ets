/* Generated from Room @TypeConverter classes. */

export class RoomTypeConverter {
  className: string;
  methodName: string;
  sourcePath: string;

  constructor(className: string, methodName: string, sourcePath: string) {
    this.className = className;
    this.methodName = methodName;
    this.sourcePath = sourcePath;
  }
}

export const RoomTypeConverters: RoomTypeConverter[] = [

];

export class JsonTypeConverter {
  static fromString(value: string): Object | Object[] | undefined {
    if (!value) {
      return undefined;
    }
    return JSON.parse(value) as Object;
  }

  static toString(value: Object | Object[] | undefined): string {
    if (value === undefined) {
      return '';
    }
    return JSON.stringify(value);
  }
}
