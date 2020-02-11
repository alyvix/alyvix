import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DesignerDatastoreService {

  private _selectedFile:BehaviorSubject<string> = new BehaviorSubject<string>("");


  constructor() { }

  setSelectedFile(f:string) {
    this._selectedFile.next(f);
  }

  getSelectedFile():Observable<string> {
    return this._selectedFile;
  }

}
