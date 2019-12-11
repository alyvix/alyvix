import { Injectable, EventEmitter } from '@angular/core';
import { SelectorDatastoreService, MapsVM, MapRowVM } from '../ax-selector/selector-datastore.service';
import { BehaviorSubject, Observable, from } from 'rxjs';
import { AxScriptFlow } from '../ax-model/model';
import { Step } from './central-panel/script-editor/step/step.component';


export interface LeftSelection{
  name:string;
  type:string;
  steps?:AxScriptFlow[];
  map?: MapRowVM[];
  onChangeSteps?: (step:AxScriptFlow[]) => any;
  onChangeMap?: (map:MapRowVM[]) => any;
}

@Injectable({
  providedIn: 'root'
})
export class EditorService {

  private _selection:BehaviorSubject<LeftSelection> = new BehaviorSubject<LeftSelection>(null);
  objectChanged:EventEmitter<string> = new EventEmitter()

  private objectSave:() => Observable<any>

  private beforeSavePromises:(() => Promise<any>)[] = [];


  constructor(
    private selectorDatastore:SelectorDatastoreService
  ) { }


  setObjectSave(o:() => Observable<any>) {
    this.objectSave = o;
  }

  reloadObject(objectName:string) {
    this.selectorDatastore.reload(objectName);
    this.objectChanged.emit(objectName);
  }

  setLeftSelection(s:LeftSelection) {
    this._selection.next(s);
  }

  getLeftSelection():Observable<LeftSelection> {
    return this._selection;
  }

  addBeforeSave(bs:() => Promise<any>) {
    this.beforeSavePromises.push(bs);
  }

  private beforeSave():Promise<any> {
    return Promise.all(this.beforeSavePromises.map(x => x()));
  }

  save():Observable<any> {
    let self = this;
    const promise = new Promise( function(resolve) {
      self.beforeSave().then(function() {
        self.selectorDatastore.save().subscribe(x => {
          self.objectSave().subscribe( y => resolve());
        });
      });
    });
    return from(promise);
  }






}
