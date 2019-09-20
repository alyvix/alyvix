import { Injectable, Inject } from '@angular/core';
import { AxSelectorObjects, AxSelectorComponentGroups } from '../ax-model/model';
import { RowVM } from './ax-table/ax-table.component';
import { Utils } from '../utils';
import { AlyvixApiService } from '../alyvix-api.service';
import { GlobalRef } from './global';
import { BehaviorSubject, Observable } from 'rxjs';


export interface AxFile {
  data: RowVM[];
  name: string;
  readonly: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class SelectorDatastoreService {

  private workingCase: BehaviorSubject<AxFile> = new BehaviorSubject<AxFile>(null);
  private editedRow: BehaviorSubject<RowVM> = new BehaviorSubject<RowVM>(null);

  constructor(
    private apiService: AlyvixApiService,
    @Inject('GlobalRef') private global: GlobalRef
    ) { }


  load() {
    this.apiService.getLibrary().subscribe( library => {
      this.workingCase.next({data: this.modelToData(library), name: this.global.nativeGlobal().current_library_name, readonly: false});
    });
  }

  getWorkingCase(): Observable<AxFile> {
    return this.workingCase;
  }

  editRow():Observable<RowVM> {
    return this.editedRow;
  }

  reload(objectName) {
    console.log("reload selector")
    this.apiService.getLibrary().subscribe( library => {
      const updatedRow = this.modelToData(library).find(x => x.name === objectName);
      if (updatedRow) {
        this.editedRow.next(updatedRow);
      }
    });
  }


  modelToData(model: AxSelectorObjects): RowVM[] {
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
