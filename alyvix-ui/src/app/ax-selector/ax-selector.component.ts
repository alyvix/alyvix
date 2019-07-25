import { Component, OnInit, ElementRef, ViewChild, Inject } from '@angular/core';
import { AxSelectorObject, AxSelectorObjects, AxSelectorComponentGroups } from '../ax-model/model';
import { AxModelMock } from '../ax-model/mock';
import { DomSanitizer } from '@angular/platform-browser';
import { ResizedEvent } from 'angular-resize-event';
import { GlobalRef } from './global';
import { AlyvixApiService } from '../alyvix-api.service';


interface RowVM{
  name:string
  object:AxSelectorObject
  selectedResolution:string
}

@Component({
    selector: 'ax-selector',
    templateUrl: './ax-selector.component.html',
    styleUrls: ['./ax-selector.component.scss']
  })
  export class AxSelectorComponent implements OnInit {

    constructor(private _sanitizer: DomSanitizer,@Inject('GlobalRef') private global: GlobalRef,private apiService:AlyvixApiService) {}

    model:AxSelectorObjects
    data: RowVM[];

    private firstResolution(component: {[key:string]:AxSelectorComponentGroups}):string {
      return Object.entries(component).map(
        ([key, value]) =>  {
           return key
        }
      )[0]
    }

    objectKeys = Object.keys;

    imageFor(image:string) {
      return this._sanitizer.bypassSecurityTrustResourceUrl("data:image/png;base64,"+image);
    }

    changeObjectName(oldKey: string,newKey: string) {
      delete Object.assign(this.model.objects, {[newKey]: this.model.objects[oldKey] })[oldKey];
      delete Object.assign(this.data, {[newKey]: this.data })[oldKey];
    }

    @ViewChild('tableContainer') tableContainer: ElementRef;
    onResized(event: ResizedEvent) {
      this.tableContainer.nativeElement.style.height = (event.newHeight - 44 - 40) + "px"
    }

    ok() {
      const model:AxSelectorObjects = { objects: {}};
      this.data.forEach( d => {
        model[d.name] = d.object;
      });
      this.apiService.setLibrary(model).subscribe(x => console.log(x));
    }

    cancel() {
      	this.global.nativeGlobal().cancel_button()
    }

    delay:number = 0;
    newObject() {
      this.global.nativeGlobal().new_button(this.delay);
    }

    changeTransactionGroup(row:RowVM,tg:string) {
      if(tg.length == 0) {
        row.object.measure.group = null;
      } else {
        row.object.measure.group = tg;
      }
    }



    selectorColumns = ['name','transactionGroup','dateModified','timeout','break','measure','warning','critical','resolution','screen']

    ngOnInit(): void {
        this.apiService.getLibrary().subscribe( library => {
          this.model = library;
          this.data = Object.entries(this.model.objects).map(
            ([key, value]) =>  {
               if(!value.measure) value.measure = {output: false, thresholds: {}}
               return {name:key, object:value, selectedResolution: this.firstResolution(value.components)}
            }
          );
        })
    }

  }
