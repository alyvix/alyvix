import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { environment } from 'src/environments/environment';
import { SelectorComponent } from './selector.component';
import { AxSelectorComponent } from './ax-selector.component';

import {CdkTableModule} from '@angular/cdk/table'
import { AngularResizedEventModule } from 'angular-resize-event';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AxTableComponent } from './ax-table/ax-table.component';



@NgModule({
  declarations: [
    SelectorComponent,
    AxSelectorComponent,
    AxTableComponent
  ],
  imports: [
    BrowserModule,
    CdkTableModule,
    AngularResizedEventModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [{provide: 'GlobalRef', useClass: environment.globalTypeSelector}],
  bootstrap: [SelectorComponent]
})
export class SelectorModule { }
