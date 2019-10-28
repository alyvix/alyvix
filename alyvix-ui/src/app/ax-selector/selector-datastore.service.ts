import { Injectable, Inject } from '@angular/core';
import { AxSelectorObjects, AxSelectorComponentGroups } from '../ax-model/model';
import { RowVM } from './ax-table/ax-table.component';
import { Utils } from '../utils';
import { AlyvixApiService } from '../alyvix-api.service';
import { GlobalRef } from './global';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';


export interface AxFile {
  id: string;
  data: RowVM[];
  name: string;
  readonly: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class SelectorDatastoreService {

  private editedRow: BehaviorSubject<RowVM> = new BehaviorSubject<RowVM>(null);
  private originalLibrary:AxSelectorObjects;

  constructor(
    private apiService: AlyvixApiService
    ) { }


  editRow():Observable<RowVM> {
    return this.editedRow;
  }

  reload(objectName) {
    console.log("reload selector")
    this.apiService.getLibrary().subscribe( library => {
      const updatedRow = this.modelToData(library).find(x => x.name === objectName);
      if (updatedRow) {
        console.log("updated row")
        console.log(updatedRow);
        this.editedRow.next(updatedRow);
      }
    });
  }

  getData():Observable<RowVM[]> {
    return this.apiService.getLibrary().pipe(map(library => {
      console.log(library);
      let data = [];
      if(library) {
        data = this.modelToData(library);
      }
      this.originalLibrary = library;

      return data;
    }));
  }

  private prepareModelForSubmission(data:RowVM[]):AxSelectorObjects {
    const model:AxSelectorObjects = this.originalLibrary;
    model.objects = {};
    data.forEach( d => {
      model.objects[d.name] = d.object;
    });
    return model;
  }

  saveData(data:RowVM[],close_selector):Observable<any> {
    return this.apiService.setLibrary({library: this.prepareModelForSubmission(data), close_selector: close_selector});
  }


  modelToData(model: AxSelectorObjects): RowVM[] {
    if(!model.objects) { return []; }
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

  private firstResolution(component: {[key:string]:AxSelectorComponentGroups}):string {
    return Object.entries(component).map(
      ([key, value]) =>  {
         return key;
      }
    )[0]
  }



}
