import { Component, OnInit, Inject } from '@angular/core';
import { SelectorGlobal } from 'src/app/ax-selector/global';
import { EditorService } from '../editor.service';
import { SelectorDatastoreService } from 'src/app/ax-selector/selector-datastore.service';
import { AlyvixApiService } from 'src/app/alyvix-api.service';

@Component({
  selector: 'ax-header',
  templateUrl: './ax-header.component.html',
  styleUrls: ['./ax-header.component.scss']
})
export class AxHeaderComponent implements OnInit {

  constructor(@Inject('GlobalRefSelector') private global: SelectorGlobal,
    private editorService:EditorService,
    private api:AlyvixApiService
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
    if(confirm("Are you sure you want to exit Alyvix-IDE?")) {
      this.api.exitIde();
    }
  }

  newFile() {
    if(confirm("Are you sure you want to close the current case?")) {
      this.api.newCase();
    }
  }

  openFile() {
    if(confirm("Are you sure you want to close the current case?")) {
      this.api.openCase();
    }
  }

  run() {
    this.api.run(this.running ? 'stop' : 'run').subscribe(x => {
      this.running = !this.running;
    });
  }



}
