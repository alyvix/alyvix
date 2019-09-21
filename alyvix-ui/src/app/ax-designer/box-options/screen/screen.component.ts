import { Component, OnInit, ViewChild } from '@angular/core';
import { AxDesignerService } from '../../ax-designer-service';
import { AxSystemCall } from 'src/app/ax-model/model';
import { AlyvixApiService } from 'src/app/alyvix-api.service';

@Component({
  selector: 'ax-designer-screen',
  templateUrl: './screen.component.html',
  styleUrls: ['./screen.component.scss']
})
export class ScreenComponent implements OnInit {

  constructor(private axService:AxDesignerService, private alyvixApi:AlyvixApiService) { }

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
  }

  @ViewChild('file') _file;
  selectFile() {
    this._file.nativeElement.click();
  }

  onFileSelected() {
    const self = this;
    const files: { [key: string]: File } = this._file.nativeElement.files;
    let file: File
    for (let key in files) {
      if (!isNaN(parseInt(key))) {
        file = files[key];
        console.log(file);
      }
    }
  }

}
