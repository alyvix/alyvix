import { Injectable, Inject, EventEmitter } from '@angular/core';
import { AxSelectorObjects, AxSelectorComponentGroups, AxScript, AxMaps, AxScriptFlow,AxScriptFlowObj, AxMap, AxSelectorComponent, T } from '../ax-model/model';
import { RowVM } from './ax-table/ax-table.component';
import { Utils } from '../utils';
import { AlyvixApiService } from '../alyvix-api.service';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { isArray } from 'util';
import * as _ from 'lodash';
import { identifierModuleUrl } from '@angular/compiler';


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

export interface MapRename{
  oldName:string
  newName:string
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
  renameMap:EventEmitter<MapRename> = new EventEmitter();
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
    console.log('data')
    console.log(data)
    this.data = data;
  }



  getData():Observable<RowVM[]> {
    return this.apiService.getLibrary().pipe(map(library => {
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

    console.log(name)
    console.log(this.data)

    if(this.data.find(x => x.name === name)) {
      return 'object';
    } else {
      return 'section';
    }
  }

  public static toAxMaps(ms:MapsVM[]):AxMaps {
      let maps = {}
      ms.forEach(m => {
        maps[m.name] = SelectorDatastoreService.toAxMap(m.rows);
      })
      return maps;
  }

  public static toAxMap(m:MapRowVM[]):AxMap  {
        let obj = {};
        m.forEach(r => {
          obj[r.name] = r.value || r.values;
        })
        return obj;
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
    model.maps = SelectorDatastoreService.toAxMaps(this.maps.value);
    return model;
  }

  saveData(data:RowVM[],close_selector:boolean):Observable<any> {
    return this.apiService.setLibrary({library: this.prepareModelForSubmission(data), close_selector: close_selector});
  }

  save():Observable<RowVM[]> {
    return this.apiService.setLibrary({library: this.prepareModelForSubmission(this.data), close_selector: false}).pipe(map(x => this.data))
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



  private checkInObject(mapName:string):string[] {
    return _.flatMap(this.data,d => {
      return _.flatMap(Object.keys(d.object.components),k => {
        const textComponents:AxSelectorComponent[] = _.flatMap(d.object.components[k].groups,g => g.subs)
                                                      .filter(c => (c as any).detection && (c as any).detection.type === 'text' )
                                                      .map(c => c as AxSelectorComponent)
        if(textComponents.some(c => (c.detection.features as T).type === 'map' && (c.detection.features as T).map === mapName)) {
          return ["Used in object " + d.name + " at "+k]
        } else {
          return []
        }
      })
    })
  }



  private checkInScript(objectName:string, label:string, firstPlace:boolean, objTest:((o:AxScriptFlowObj) => boolean)):string[] {
    const inFlow:((name:string,flow:AxScriptFlow[]) => string[]) = (name,flow) => {
      let contains = flow.some(f => {
        if(typeof f === "string") {
          return objectName === f && firstPlace;
        } else {
          return  objTest(f)
        }
      });
      return contains ? [label + " used in script: " + name] : []
    }

    const script = this.script.getValue();
    console.log(script)
    if(script) {
      let sections = script.sections ? _.flatMap(script.sections,s => inFlow(s.name,s.instructions)) : []
      return [
        ...inFlow('main',script.main),
        ...inFlow('fail',script.fail),
        ...inFlow('exit',script.exit),
        ...sections
      ]
    } else {
      return []
    }
  }

  unsafeData():RowVM[] {
    return this.data
  }

  objectUsage(objectName:string):string[] {
    return this.checkInScript(objectName,"Object",true,f =>
      (f.flow && f.flow === objectName) ||
      (f.if_true && f.if_true === objectName) ||
      (f.if_false && f.if_true === objectName)
    )
  }

  sectionUsage(objectName:string):string[] {
    return this.checkInScript(objectName,"Section",true,f => f.flow && f.flow === objectName)
  }

  mapUsage(mapName:string):string[] {
    let scripts =  this.checkInScript(mapName,"Map",false,f => f.for && f.for === mapName)
    let objects = this.checkInObject(mapName);
    return scripts.concat(objects);
  }


  private refactorInObject(oldName:string,newName:string):void {
    this.renameMap.emit({oldName: oldName, newName:newName})
    this.data.forEach(d => {
      Object.keys(d.object.components).forEach(k => {
        const textComponents:AxSelectorComponent[] = _.flatMap(d.object.components[k].groups,g => g.subs)
                                                      .filter(c => (c as any).detection && (c as any).detection.type === 'text' )
                                                      .map(c => c as AxSelectorComponent)
        textComponents.forEach(c => {
          if((c.detection.features as T).type === 'map' && (c.detection.features as T).map === oldName) {
            (c.detection.features as T).map = newName
          }
        })
      })
    })
  }

  private refactorInScript(oldName:string, newName:string, firstPlace:boolean, objRename:((o:AxScriptFlowObj) => void)):void {
    const renameFlow:((flow:AxScriptFlow[]) => void) = (flow) => {
      flow.forEach((f,i) => {
        if(typeof f === "string") {
          if(oldName === f && firstPlace) {
            flow[i] = newName
          }
        } else {
          objRename(f)
        }
      });
    }

    const script = this.script.getValue();
    if(script) {
      renameFlow(script.main)
      renameFlow(script.fail)
      renameFlow(script.exit)
      if(script.sections) {
        script.sections.forEach(s => renameFlow(s.instructions))
      }
    }
    this.setScripts(script);
  }

  refactorObject(oldName:string,newName:string) {

    this.data.filter(x => x.name === oldName).forEach(x => {
      console.log('rename on this data')
      x.name = newName
    })

    this.refactorInScript(oldName,newName,true,flow => {
      if(flow.flow && flow.flow === oldName) {
        flow.flow = newName
      }
      if(flow.if_false && flow.if_false === oldName) {
        flow.if_false = newName
      }
      if(flow.if_true && flow.if_true === oldName) {
        flow.if_true = newName
      }
    })
  }

  refactorSection(oldName:string,newName:string) {
    this.refactorInScript(oldName,newName,true,flow => {
      if(flow.flow && flow.flow === oldName) {
        flow.flow = newName
      }
    })
  }

  refactorMap(oldName:string,newName:string) {
    this.refactorInScript(oldName,newName,false,flow => {
      if(flow.for && flow.for === oldName) {
        flow.for = newName
      }
    })

    this.refactorInObject(oldName,newName)
  }

  nameCheck(name:string):boolean {
    return name === "main" ||
    name === "fail" ||
    name === "exit" ||
    this.data.some(x => name === x.name) ||
    this.script.value.sections.some(x => name === x.name) ||
    this.maps.value.some(x => name === x.name)
  }

  nameValidation(input:HTMLInputElement, old:string):string {
      const valid = input.validity.valid && input.value.length > 0;

      const duplicate = input.value === old ? false : this.nameCheck(input.value);

      const isCli = input.value === "cli"

      let result = null

      if(!valid) result = "Only alphanumeric characters and - _ ` ` (space) are allowed"
      if(duplicate) result =  'Object name already in use'
      if(isCli) result = '`cli` is not a valid name'
      return result
  }





}
