import { Component, OnInit, ViewChild, ChangeDetectorRef } from '@angular/core';
import { AxDesignerService } from '../../ax-designer-service';
import { AxSystemCall } from 'src/app/ax-model/model';
import { AlyvixApiService } from 'src/app/alyvix-api.service';
import { DesignerDatastoreService } from '../../designer-datastore.service';

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

  ngOnInit() {
    if(!this.axService.axModel.call) {
      this.axService.axModel.call = {type: "run", features: {}}
    }
    this.call = this.axService.getModel().call;
    this.alyvixApi.getProcesses().subscribe(x => {
      this.processes = x.object_exists;
    });
    this.datastore.getSelectedFile().subscribe(f => {
      if (f.length > 0) {
        this.call.features.path = f;
        this.datastore.setSelectedFile("");
        this.changeDetecor.markForCheck();
        this.changeDetecor.detectChanges();
      }
    });
  }

  selectFile() {
    this.alyvixApi.openOpenFileDialog().subscribe(x => {});
  }



}
