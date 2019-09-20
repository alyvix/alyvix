import { RowVM } from "./ax-table/ax-table.component";

import * as _ from 'lodash';
import { Utils } from "../utils";

export class SelectorUtils {

  static isDuplicatedName(name: string, data: RowVM[]):boolean {
    return data.filter(x => name === x.name).length > 1;
  }

  static duplicateRows(rows: RowVM[], data:RowVM[]):RowVM[] {
    const result: RowVM[] = [];
    rows.forEach(row => {
      const newRow = _.cloneDeep(row);
      newRow.id = Utils.uuidv4();
      newRow.name = row.name + '_copy';
      data.push(newRow);
      let count = 0;
      while (this.isDuplicatedName(newRow.name, data)) {
        count++;
        newRow.name = row.name + '_copy_' + count;
      }
      result.push(newRow);
    });
    return result;
  }
}
