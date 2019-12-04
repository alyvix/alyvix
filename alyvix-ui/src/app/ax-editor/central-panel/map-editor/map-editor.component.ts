import { Component, OnInit, Input,ChangeDetectorRef, Output,EventEmitter } from '@angular/core';
import { MapRowVM } from 'src/app/ax-selector/selector-datastore.service';
import { Utils } from 'src/app/utils';




@Component({
  selector: 'app-map-editor',
  templateUrl: './map-editor.component.html',
  styleUrls: ['./map-editor.component.scss']
})
export class MapEditorComponent implements OnInit {

  displayedColumns: string[] = [];
  valuesColumns: string[] = [];
  dataSource = [];

  @Output() mapChange: EventEmitter<MapRowVM[]> = new EventEmitter();

  @Input() set rows(rows:MapRowVM[]) {

    if(rows) {
      this.valuesColumns = [];
      this.dataSource = [];
      this.valuesColumns = [];
      let lenghts:number[] = rows.map(r => r.values ? r.values.length : 1);
      this.displayedColumns.push("key");
      for(let i = 1; i<=Math.max(...lenghts);i++) {
        this.valuesColumns.push('value'+i);
      }
      this.dataSource = rows.map((r,i) => {
        let res = {id: Utils.uuidv4(), key: r.name}
        if(r.value) {
          res['value1'] = r.value;
        } else if(r.values) {
          r.values.forEach((x,i) => res['value'+(i+1)] = x);
        }
        return res;
      });
      this.displayedColumns = ['key'].concat(this.valuesColumns);

    }
  }

  tableChanged(values:string[], current:string,column:string) {
    values[column] = current;
    this.emitChange();
  }

  addRow() {
    this.dataSource.push({id: Utils.uuidv4(), key: "new"});
    this.displayedColumns = ['key'];
    this.changeDetector.markForCheck();
    this.changeDetector.detectChanges();
    this.displayedColumns = ['key'].concat(this.valuesColumns);
    this.emitChange();
  }

  addColumn() {
    const newColumn = 'value'+(this.valuesColumns.length+1);
    this.valuesColumns.push(newColumn);
    this.displayedColumns.push(newColumn);
    this.emitChange();
  }

  emitChange() {
    let result:MapRowVM[] = this.dataSource.map(row => {
      let res = {
        name: row.key
      }
      let values = [];
      this.valuesColumns.forEach(c => {
        if(row[c] && row[c] !== '') {
          values.push(row[c]);
        }
      });
      if(values.length == 1) {
        res['value'] = values[0];
      } else if(values.length > 1) {
        res['values'] = values;
      }
      return res;
    })
    this.mapChange.emit(result);
  }

  constructor(
    private changeDetector:ChangeDetectorRef
  ) { }

  ngOnInit() {
  }

}
