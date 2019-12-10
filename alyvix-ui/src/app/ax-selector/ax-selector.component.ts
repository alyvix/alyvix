import { Component, OnInit, ViewChild, Inject, Input } from '@angular/core';
import { ResizedEvent } from 'angular-resize-event';
import { AxTableComponent, RowVM } from './ax-table/ax-table.component';
import { environment } from 'src/environments/environment';
import { AlyvixApiService } from '../alyvix-api.service';
import { Utils } from '../utils';
import { AxSelectorComponentGroups, AxSelectorObjects } from '../ax-model/model';
import { empty } from 'rxjs';
import { SelectorUtils } from './selector-utils';
import { SelectorGlobal } from './global';
import { connectableObservableDescriptor } from 'rxjs/internal/observable/ConnectableObservable';
import { SelectorDatastoreService, AxFile } from './selector-datastore.service';



@Component({
  selector: 'ax-selector',
  templateUrl: './ax-selector.component.html',
  styleUrls: ['./ax-selector.component.scss']
})
export class AxSelectorComponent implements OnInit {


  constructor(
    private datastore: SelectorDatastoreService,
    @Inject('GlobalRefSelector') private global: SelectorGlobal
  ) { }


  @Input() editor:boolean = false;

  selected: AxFile = {id: '', data: [], name: '', readonly: false };
  main: AxFile = {id: '', data: [], name: '', readonly: false };
  files: AxFile[] = [];
  production: boolean = environment.production;
  debugJson:boolean = false;

  selectorHidden = false;


  toggleSelector() {
    this.datastore.setSelectorHidden(!this.selectorHidden);
  }


  ngOnInit(): void {
    console.log("editor:" + this.editor);
    this.debugJson = !environment.production && environment.workingOn === 'selector'
    this.datastore.getData().subscribe(data => {
      this.main = {id:Utils.uuidv4(), data: data, name: this.global.current_library_name, readonly: false };
      this.selected = this.main;
    });
    this.datastore.getSelectorHidden().subscribe(x => this.selectorHidden = x);
  }


  @ViewChild(AxTableComponent,{static:true}) table;
  onResized(event: ResizedEvent) {
    if (this.table)
      this.table.onResized(event);
  }


  selectTab(i: AxFile) {
    this.selected = i;
  }

  closeTab(i: AxFile) {
    this.selectTab(this.main);
    this.files = this.files.filter(f => f.id !== i.id);
  }

  @ViewChild('file',{static: true}) _file;
  loadFile() {
    this._file.nativeElement.click();
  }

  onFileAdd() {
    const self = this;
    const files: { [key: string]: File } = this._file.nativeElement.files;
    let file: File
    for (let key in files) {
      if (!isNaN(parseInt(key))) {
        file = files[key];
        const reader = new FileReader();
        reader.onload = function () {
          if (typeof reader.result == "string") {
            self.parseFile(file.name, reader.result);
          }
          self._file.nativeElement.value = ''; //reset the file input
        };
        reader.readAsText(file);
      }
    }
  }

  parseFile(filename: string, body: string) {
    const newFile: AxFile = {
      id: Utils.uuidv4(),
      data: this.datastore.modelToData(JSON.parse(body)),
      readonly: true,
      name: filename.substring(0, filename.indexOf('.alyvix'))
    }
    this.files.push(newFile);
  }

  onImport(rows: RowVM[]) {
    console.log(rows);
    SelectorUtils.duplicateRows(rows, this.main.data);
  }

}
