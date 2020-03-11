import { Component, OnInit, Inject } from '@angular/core';
import { SelectorGlobal } from 'src/app/ax-selector/global';
import { EditorService } from '../editor.service';
import { SelectorDatastoreService } from 'src/app/ax-selector/selector-datastore.service';
import { AlyvixApiService } from 'src/app/alyvix-api.service';
import { ModalService, Modal } from 'src/app/modal-service.service';

@Component({
  selector: 'ax-header',
  templateUrl: './ax-header.component.html',
  styleUrls: ['./ax-header.component.scss']
})
export class AxHeaderComponent implements OnInit {

  constructor(@Inject('GlobalRefSelector') private global: SelectorGlobal,
    private editorService:EditorService,
    private api:AlyvixApiService,
    private modal:ModalService
  ) { }

  name:string;
  running = false;

  ngOnInit() {
    this.name = this.global.current_library_name;
    this.editorService.runState.subscribe(state => this.running = state === 'run');
  }

  save() {
    this.editorService.save().subscribe(x => this.api.saveAll(false));
  }

  saveAs() {
    this.editorService.save().subscribe(x => this.api.saveAs());
  }

  exit() {

    this.editorService.save().subscribe(x => {
      this.api.checkModification().subscribe(modifications => {
        if(modifications.success) {
          this.modal.open({
            title: 'Exit',
            body: 'Are you sure you want to exit Alyvix Editor?',
            actions: [
              {
                title: 'Exit',
                importance: 'btn-secondary',
                callback: () => { this.api.exitIde() }
              }
            ],
            cancel: Modal.NOOP
          });
        } else {
          this.api.exitIde();
        }
      })
    })



  }

  newFile() {
    this.editorService.save().subscribe(x => {
      this.api.checkModification().subscribe(modifications => {
        if(modifications.success) {
          this.modal.open({
            title: 'New file',
            body: 'Are you sure you want to close the current test case?',
            actions: [
              {
                title: 'New',
                importance: 'btn-secondary',
                callback: () => { this.api.newCase() }
              }
            ],
            cancel: Modal.NOOP
          });
        } else {
          this.api.newCase()
        }
      });
    });

  }

  openFile() {
    this.editorService.save().subscribe(x => {
      this.api.checkModification().subscribe(modifications => {
        if(modifications.success) {
          this.modal.open({
            title: 'Open file',
            body: 'Are you sure you want to close the current test case?',
            actions: [
              {
                title: 'Open',
                importance: 'btn-secondary',
                callback: () => { this.api.openCase() }
              }
            ],
            cancel: Modal.NOOP
          });
        } else {
          this.api.openCase()
        }
      })
    })
  }

  run() {
    this.editorService.save().subscribe(x =>
      this.api.run(this.running ? 'stop' : 'run').subscribe(x => {
        this.running = !this.running;
      })
    );
  }



}
