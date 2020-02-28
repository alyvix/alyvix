import { Component, OnInit } from '@angular/core';
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

}
