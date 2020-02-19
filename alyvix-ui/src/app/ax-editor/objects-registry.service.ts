import { Injectable } from '@angular/core';
import { CdkDropList } from '@angular/cdk/drag-drop';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ObjectsRegistryService {


  private _objectsLists: BehaviorSubject<Set<string>> = new BehaviorSubject<Set<string>>(new Set());

  constructor() { }

  addObjectList(dropList: string) {
    if(dropList) {
      this._objectsLists.next(this._objectsLists.value.add(dropList));
    }
  }

  removeObjectList(dropList:string) {
    this._objectsLists.value.delete(dropList);
    this._objectsLists.next(this._objectsLists.value);
  }

  objectList(): Observable<string[]> {
    return this._objectsLists.pipe(map(x => Array.from(x)));
  }

}
