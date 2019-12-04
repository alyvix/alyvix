import { Injectable } from '@angular/core';
import { SelectorDatastoreService, MapsVM, MapRowVM } from '../ax-selector/selector-datastore.service';
import { BehaviorSubject, Observable } from 'rxjs';
import { AxScriptFlow } from '../ax-model/model';


export interface LeftSelection{
  name:string;
  type:string;
  steps?:AxScriptFlow[];
  map?: MapRowVM[];
}

@Injectable({
  providedIn: 'root'
})
export class EditorService {

  private _selection:BehaviorSubject<LeftSelection> = new BehaviorSubject<LeftSelection>(null);


  constructor(
    private selectorDatastore:SelectorDatastoreService
  ) { }

  designerFullscreen = false;

  private reloading = false;

  reloadObject(objectName:string) {
    if(!this.reloading && this.designerFullscreen) {
      this.reloading = true;
      console.log(objectName);
      this.selectorDatastore.reload(objectName);
      this.designerFullscreen = false;
      this.reloading = false;
    }
  }

  setLeftSelection(s:LeftSelection) {
    this._selection.next(s);
  }

  getLeftSelection():Observable<LeftSelection> {
    return this._selection;
  }




}
