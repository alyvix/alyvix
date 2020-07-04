import { Component, OnInit, ViewChild, ChangeDetectorRef, ElementRef } from '@angular/core';
import { AxDesignerService } from '../../ax-designer-service';
import { AxSystemCall, AxModel } from 'src/app/ax-model/model';
import { AlyvixApiService } from 'src/app/alyvix-api.service';
import { DesignerDatastoreService } from '../../designer-datastore.service';

import * as _ from 'lodash';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'ax-designer-screen',
  templateUrl: './screen.component.html',
  styleUrls: ['./screen.component.scss']
})
export class ScreenComponent implements OnInit {

  constructor(
    private axService:AxDesignerService,
    private alyvixApi:AlyvixApiService,
    private datastore:DesignerDatastoreService,
    private changeDetecor: ChangeDetectorRef) { }

  call:AxSystemCall


    // TO REPRODUCE
    // 1. Create new object
    // 2. Define a call using the select
    // 3. Save
    // 4. reopen the object

  processes: string[] = [];


  @ViewChild('selectProcess',{static: true}) selectProcess: ElementRef;


  private CALLER_PATH = 'path'
  private CALLER_ARG = 'arg'

  ngOnInit() {
    this.axService.getModelAsync().subscribe(ax => {
      if(this.axService.axModel) {
        if(!this.axService.axModel.call) {
          this.axService.axModel.call = {type: "run", features: {}}
        }
        this.call = this.axService.getModel().call;
        if(this.call.features) {
          this.arguments = this.call.features.arguments;
          this.path = this.call.features.path;
          this.process = this.call.features.process;
        }
      }
    });
    this.alyvixApi.getProcesses().subscribe(x => {
      this.processes = _.uniq(x.object_exists);
    });
    this.datastore.getSelectedFile().subscribe(o => {
      if (o) {
        if(o.caller === this.CALLER_PATH) {
          this.changePath(o.file);
        } else if(o.caller === this.CALLER_ARG) {
          this.changeArguments(o.file);
        }
        this.datastore.resetFile();
        this.changeDetecor.markForCheck();
        this.changeDetecor.detectChanges();
      }
    });
  }

  changeType(t) {
    if(t === 'run') {
      if(this.call.features) {
        delete this.call.features.process;
      } else {
        this.call.features = {};
      }
      this.call.features.path = this.path;
      this.call.features.arguments = this.arguments;
    } else if(t === 'kill') {
      if(this.call.features) {
        delete this.call.features.arguments;
        delete this.call.features.path;
      } else {
        this.call.features = {};
      }
      this.call.features.process = this.process;
    } else if(t === 'none') {
      delete this.call.features;
    }
    this.call.type = t;
  }

  changeProcess(event) {
    this.axService.axModel.call.features.process = event;
    this.process = event;
  }
  process:string = "";
  arguments:string = "";
  path:string = "";

  changePath(p) {
    this.call.features.path = p;
    this.path = p;
  }

  changeArguments(a) {
    this.arguments = a;
    this.call.features.arguments = a;
  }


  selectFile() {
    this.alyvixApi.openOpenFileDialog(this.CALLER_PATH).subscribe(x => {});
  }

  selectArgument() {
    this.alyvixApi.openOpenFileDialog(this.CALLER_ARG).subscribe(x => {});
  }



}
