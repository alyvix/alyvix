import { Component, OnInit, ViewChild, ChangeDetectorRef, ElementRef } from '@angular/core';
import { AxDesignerService } from '../../ax-designer-service';
import { AxSystemCall } from 'src/app/ax-model/model';
import { AlyvixApiService } from 'src/app/alyvix-api.service';
import { DesignerDatastoreService } from '../../designer-datastore.service';

import * as _ from 'lodash';

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


  processes: string[] = [];


  @ViewChild('selectProcess',{static: true}) selectProcess: ElementRef;

  ngOnInit() {
    if(!this.axService.axModel.call) {
      this.axService.axModel.call = {type: "run", features: {}}
    }
    this.call = this.axService.getModel().call;
    this.arguments = this.call.features.arguments;
    this.path = this.call.features.path;
    this.process = this.call.features.process;
    this.alyvixApi.getProcesses().subscribe(x => {
      this.processes = _.uniq(x.object_exists);
    });
    this.datastore.getSelectedFile().subscribe(f => {
      if (f.length > 0) {
        this.changePath(f);
        this.datastore.setSelectedFile("");
        this.changeDetecor.markForCheck();
        this.changeDetecor.detectChanges();
      }
    });
  }

  changeType(t) {
    this.call.type = t;
    if(t === 'run') {
      delete this.call.features.process;
      this.call.features.path = this.path;
      this.call.features.arguments = this.arguments;
    } else if(t === 'kill') {
      delete this.call.features.arguments;
      delete this.call.features.path;
      this.call.features.process = this.process;
    }
  }

  changeProcess(event) {
    console.log(event);
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
    this.alyvixApi.openOpenFileDialog().subscribe(x => {});
  }



}
