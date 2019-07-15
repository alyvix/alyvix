import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { environment } from 'src/environments/environment';
import { SelectorComponent } from './selector.component';
import { AxSelectorComponent } from './ax-selector.component';

import {CdkTableModule} from '@angular/cdk/table'
import { AngularResizedEventModule } from 'angular-resize-event';



@NgModule({
  declarations: [
    SelectorComponent,
    AxSelectorComponent
  ],
  imports: [
    BrowserModule,
    CdkTableModule,
    AngularResizedEventModule
  ],
  providers: [{provide: 'GlobalRef', useClass: environment.globalTypeSelector}],
  bootstrap: [SelectorComponent]
})
export class SelectorModule { }
