import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Modal, ModalService, ModalVM, ModalAction } from 'src/app/modal-service.service';

/**
 * Using https://biig-io.github.io/ngx-smart-modal
 */

@Component({
  selector: 'ax-modal',
  templateUrl: './ax-modal.component.html',
  styleUrls: ['./ax-modal.component.scss']
})
export class AxModalComponent implements OnInit {

  constructor(
    private modalService:ModalService
  ) { }

  id = Modal.ID

  vm:ModalVM

  @ViewChild("actions",{static:true}) actions:ElementRef;

  ngOnInit() {
    this.modalService.data().subscribe(d => this.vm = d);
  }

  do(a:ModalAction) {
    console.log('Action: ' + a.title);
    a.callback();
    this.modalService.close();
  }

  allActions():ModalAction[] {
    return this.vm.actions.concat([this.vm.cancel]);
  }

  get actionEl():HTMLDivElement {
    return this.actions.nativeElement as HTMLDivElement
  }

  focusFirst() {

    if(this.actions.nativeElement as HTMLDivElement) {
      this.actionEl.querySelector("button").focus();
    }
  }

  keyupButton(action:ModalAction, event:KeyboardEvent) {
    // if(event.keyCode == 9) {
    //   event.stopPropagation();
    //   event.preventDefault();
    //   const i = this.allActions().findIndex(x => x.title === action.title);
    //   if(i >= 0) {
    //     this.actionEl.querySelectorAll("button").item((i + 1) % this.allActions().length).focus();
    //   }

    // }
  }

}
