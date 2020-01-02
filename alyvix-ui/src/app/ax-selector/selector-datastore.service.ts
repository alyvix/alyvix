import { Injectable, Inject, EventEmitter } from '@angular/core';
import { AxSelectorObjects, AxSelectorComponentGroups, AxScript, AxMaps, AxScriptFlow } from '../ax-model/model';
import { RowVM } from './ax-table/ax-table.component';
import { Utils } from '../utils';
import { AlyvixApiService } from '../alyvix-api.service';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { isArray } from 'util';


export interface AxFile {
  id: string;
  data: RowVM[];
  name: string;
  readonly: boolean;
  main:boolean;
}

export interface MapsVM{
  name:string;
  rows: MapRowVM[];
}

export interface MapRowVM{
  name: string;
  value?: string;
  values?: string[];
}

export interface ScriptVM{
  main: AxScriptFlow[];
  exit: AxScriptFlow[];
  fail: AxScriptFlow[];
  sections: SectionVM[];
}

export const ScriptEmpty:ScriptVM = {main:[],exit:[],fail:[],sections:[]};

export interface SectionVM{
  name: string;
  instructions: AxScriptFlow[];
}

@Injectable({
  providedIn: 'root'
})
export class SelectorDatastoreService {

  private data: RowVM[] = null;
  private selectedRows: BehaviorSubject<RowVM[]> = new BehaviorSubject<RowVM[]>(null);
  private editedRow: BehaviorSubject<RowVM> = new BehaviorSubject<RowVM>(null);
  private script: BehaviorSubject<ScriptVM> = new BehaviorSubject<ScriptVM>(null);
  private maps: BehaviorSubject<MapsVM[]> = new BehaviorSubject<MapsVM[]>([]);
  private _selectorHidden: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  private originalLibrary:AxSelectorObjects;
  changedSelection:EventEmitter<RowVM[]> = new EventEmitter();
  changedNameRow:EventEmitter<string> = new EventEmitter();
  changedBreak:EventEmitter<boolean> = new EventEmitter();
  changedTimeout:EventEmitter<number> = new EventEmitter();
  changeTab:EventEmitter<AxFile> = new EventEmitter();
  private _tabSelected: BehaviorSubject<AxFile> = new BehaviorSubject<AxFile>(null);

  static modelToData(model: AxSelectorObjects): RowVM[] {
    if(!model.objects) { return []; }
    return Object.entries(model.objects).map(
      ([key, value]) =>  {
         if (!value.measure) {
           value.measure = {output: false, thresholds: {}}
         } else  {
            if (!value.measure.thresholds) { value.measure.thresholds = {}; }
            if (typeof value.measure.output === 'undefined') { value.measure.output = false; }
         }
         return {name: key, object: value, selectedResolution: SelectorDatastoreService.firstResolution(value.components), id: Utils.uuidv4()};
      }
    );
  }

  private static firstResolution(component: {[key:string]:AxSelectorComponentGroups}):string {
    return Object.entries(component).map(
      ([key, value]) =>  {
         return key;
      }
    )[0]
  }



  constructor(
    private apiService: AlyvixApiService
    ) { }


  setSelected(rows:RowVM[]) {
    this.selectedRows.next(rows);
  }

  getSelected():Observable<RowVM[]> {
    return this.selectedRows;
  }

  getMaps():Observable<MapsVM[]> {
    return this.maps;
  }

  getScripts():Observable<ScriptVM> {
    return this.script;
  }

  setScripts(s:ScriptVM) {
    this.script.next(s);
  }

  setMaps(m:MapsVM[]) {
    this.maps.next(m);
  }

  editRow():Observable<RowVM> {
    return this.editedRow;
  }

  setSelectorHidden(h:boolean) {
    this._selectorHidden.next(h);
  }

  getSelectorHidden():Observable<boolean> {
    return this._selectorHidden;
  }

  setTabSelected(ta: AxFile) {
    this._tabSelected.next(ta);
  }

  tabSelected():Observable<AxFile> {
    return this._tabSelected
  }

  reload(objectName) {
    this.apiService.getLibrary().subscribe( library => {
      const updatedRow = SelectorDatastoreService.modelToData(library).find(x => x.name === objectName);
      if (updatedRow) {
        this.editedRow.next(updatedRow);
      }
    });
  }

  setData(data:RowVM[]) {
    this.data = data;
  }



  getData():Observable<RowVM[]> {
    return this.apiService.getLibrary().pipe(map(library => {
      console.log(library);
      let data = [];
      if(library) {
        data = SelectorDatastoreService.modelToData(library);
      }
      this.originalLibrary = library;
      this.script.next(this.scriptModelToVm(library.script));
      this.maps.next(this.mapModelToVm(library.maps));
      this.data = data;
      return data;
    }));
  }

  objectOrSection(name:string):string {
    if(!name) return null;

    if(this.data.find(x => x.name === name)) {
      return 'object';
    } else {
      return 'section';
    }
  }

  private prepareModelForSubmission(data:RowVM[]):AxSelectorObjects {
    const model:AxSelectorObjects = this.originalLibrary;
    model.objects = {};
    data.forEach( d => {
      model.objects[d.name] = d.object;
    });
    model.script = {
      case: this.script.value.main,
      sections: {
        exit: this.script.value.exit,
        fail: this.script.value.fail,
      }
    };
    this.script.value.sections.forEach(s => {
      model.script.sections[s.name] = s.instructions;
    });
    model.maps = {};
    this.maps.value.forEach(m => {
      model.maps[m.name] = {};
      m.rows.forEach(r => {
        model.maps[m.name][r.name] = r.value || r.values;
      })
    });
    return model;
  }

  saveData(data:RowVM[],close_selector:boolean):Observable<any> {
    return this.apiService.setLibrary({library: this.prepareModelForSubmission(data), close_selector: close_selector});
  }

  save():Observable<any> {
    console.log({library: this.prepareModelForSubmission(this.data), close_selector: true})
    return this.apiService.setLibrary({library: this.prepareModelForSubmission(this.data), close_selector: false})
  }




  private mapModelToVm(maps:AxMaps):MapsVM[] {
    if(!maps) return [];
    return Object.entries(maps).map( ([key, value]) => {
      return {
        name: key,
        rows: Object.entries(value).map(([key,value]) => {
          let base = {
            name: key
          };
          if(isArray(value)) base['values'] = value;
          else base['value'] = value;
          return base;
        })
      };
    });
  }

  private scriptModelToVm(script:AxScript):ScriptVM {
    if(!script) return ScriptEmpty;

    return {
      main: script.case,
      exit: (script.sections ? script.sections['exit'] : [] || []),
      fail: (script.sections ? script.sections['fail'] : [] || []),
      sections: ( script.sections ?
        Object.entries(script.sections)
          .filter(([key,value]) => key !== 'exit' && key !== 'fail')
          .map(([key,value]) => {
            return {
              name: key,
              instructions: value
            }
        }) : []
      )
    };

  }





}
