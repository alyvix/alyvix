import { Injectable } from '@angular/core';
import { NgxSmartModalService } from 'ngx-smart-modal';
import { BehaviorSubject, Observable } from 'rxjs';

/**
 * Using https://biig-io.github.io/ngx-smart-modal
 */

export interface ModalVM {
  title:string;
  body:string;
  list?:string[];
  actions: ModalAction[];
  cancel: ModalAction;
}

export interface ModalAction{
  title:string;
  importance:string;
  callback: () => any
}

export namespace Modal {
  export const ID = 'axModal'
  export const NOOP:ModalAction = {
    title: "Cancel",
    importance: '',
    callback: () => { console.log('NOOP') }
  }
}

@Injectable({
  providedIn: 'root'
})
export class ModalService {

  private emptyModal:ModalVM = {title: '', body: '', actions:[], cancel:Modal.NOOP}
  private _data:BehaviorSubject<ModalVM> = new BehaviorSubject(this.emptyModal);

  constructor(
    private ngxSmartModalService: NgxSmartModalService
  ) { }

  open(modal: ModalVM) {
    this._data.next(modal);
    this.ngxSmartModalService.getModal(Modal.ID).open()
  }

  close() {
    this.ngxSmartModalService.close(Modal.ID)
  }

  data():Observable<ModalVM> {
    return this._data;
  }

}
