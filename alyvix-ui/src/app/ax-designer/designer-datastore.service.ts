import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';


export interface SelectPath{
  file: string,
  caller:string
}

@Injectable({
  providedIn: 'root'
})
export class DesignerDatastoreService {

  private _selectedFile:BehaviorSubject<SelectPath> = new BehaviorSubject<SelectPath>(null);


  constructor() { }

  setSelectedFile(f:string,caller:string) {
    this._selectedFile.next({file:f, caller:caller});
  }

  resetFile() {
    this._selectedFile.next(null);
  }

  getSelectedFile():Observable<SelectPath> {
    return this._selectedFile;
  }

}
