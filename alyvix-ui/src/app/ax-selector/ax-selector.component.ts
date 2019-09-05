import { Component, OnInit, ViewChild} from '@angular/core';
import { ResizedEvent } from 'angular-resize-event';
import { AxTableComponent, RowVM } from './ax-table/ax-table.component';
import { environment } from 'src/environments/environment';
import { AlyvixApiService } from '../alyvix-api.service';
import { Utils } from '../utils';
import { AxSelectorComponentGroups, AxSelectorObjects } from '../ax-model/model';
import { empty } from 'rxjs';
import { SelectorUtils } from './selector-utils';


interface AxFile {
  data: RowVM[];
  name: string;
  readonly: boolean;
}
@Component({
    selector: 'ax-selector',
    templateUrl: './ax-selector.component.html',
    styleUrls: ['./ax-selector.component.scss']
  })
  export class AxSelectorComponent implements OnInit {


    constructor(private apiService:AlyvixApiService) {}

    selected: AxFile = {data: [], name: '', readonly: false};
    main: AxFile = {data: [], name: '', readonly: false};
    files: AxFile[] = [];
    production: boolean = environment.production;

    private firstResolution(component: {[key:string]:AxSelectorComponentGroups}):string {
      return Object.entries(component).map(
        ([key, value]) =>  {
           return key;
        }
      )[0]
    }

    private modelToData(model: AxSelectorObjects): RowVM[] {
      return Object.entries(model.objects).map(
        ([key, value]) =>  {
           if (!value.measure) {
             value.measure = {output: false, thresholds: {}}
           } else  {
              if (!value.measure.thresholds) { value.measure.thresholds = {}; }
              if (typeof value.measure.output === 'undefined') { value.measure.output = false; }
           }
           return {name: key, object: value, selectedResolution: this.firstResolution(value.components), id: Utils.uuidv4()};
        }
      );
    }

    ngOnInit(): void {
      this.apiService.getLibrary().subscribe( library => {
        this.main = {data: this.modelToData(library), name: 'main', readonly: false};
        this.selected = this.main;
      });
    }


    @ViewChild(AxTableComponent) table;
    onResized(event: ResizedEvent) {
      if (this.table) {
        this.table.onResized(event);
      }
    }

    selectTab(i: AxFile) {
      this.selected = i;
    }

    @ViewChild('file') _file;
    loadFile() {
      this._file.nativeElement.click();
    }

    onFileAdd() {
      const self = this;
      const files: { [key: string]: File } = this._file.nativeElement.files;
      let file:File
      for (let key in files) {
        if (!isNaN(parseInt(key))) {
          file = files[key];
          const reader = new FileReader();
          reader.onload = function() {
            if (typeof reader.result == "string") {
              self.parseFile(file.name, reader.result);
            }
          };
          reader.readAsText(file);
        }
      }
    }

    parseFile(filename: string, body: string) {
      const newFile:AxFile = {
        data: this.modelToData(JSON.parse(body)),
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
