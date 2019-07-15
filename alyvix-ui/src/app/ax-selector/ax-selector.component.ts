import { Component, OnInit, ElementRef, ViewChild, Inject } from '@angular/core';
import { AxSelectorObject, AxSelectorObjects, AxSelectorComponentGroups } from '../ax-model/model';
import { AxModelMock } from '../ax-model/mock';
import { DomSanitizer } from '@angular/platform-browser';
import { ResizedEvent } from 'angular-resize-event';
import { GlobalRef } from './global';

@Component({
    selector: 'ax-selector',
    templateUrl: './ax-selector.component.html',
    styleUrls: ['./ax-selector.component.scss']
  })
  export class AxSelectorComponent implements OnInit {
    
    constructor(private _sanitizer: DomSanitizer,@Inject('GlobalRef') private global: GlobalRef) {}

    model:AxSelectorObjects = AxModelMock.getSelector();

    
    data: {name:string, object:AxSelectorObject}[] = Object.entries(this.model.objects).map(
      ([key, value]) =>  {
         return {name:key, object:value}
      }
    );

    firstResolution(component: {[key:string]:AxSelectorComponentGroups}):{name:string,component:AxSelectorComponentGroups} {
      return Object.entries(component).map(
        ([key, value]) =>  {
           return {name:key, component:value}
        }
      )[0]
    }

    imageFor(image:string) {
      return this._sanitizer.bypassSecurityTrustResourceUrl("data:image/png;base64,"+image);
    }

    @ViewChild('tableContainer') tableContainer: ElementRef;
    onResized(event: ResizedEvent) {
      this.tableContainer.nativeElement.style.height = (event.newHeight - 44 - 40) + "px"
    }

    add() {
      this.global.nativeGlobal().add_button()
    }

    cancel() {
      	this.global.nativeGlobal().cancel_button()
    }

    newObject() {
      this.global.nativeGlobal().new_button()
    }

   

    selectorColumns = ['name','transactionGroup','dateModified','timeout','break','measure','warning','critical','resolution','screen'] 

    ngOnInit(): void {
    }

  }