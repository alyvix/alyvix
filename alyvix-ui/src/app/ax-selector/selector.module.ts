import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { environment } from 'src/environments/environment';
import { SelectorComponent } from './selector.component';
import { AxSelectorComponent } from './ax-selector.component';

import {CdkTableModule} from '@angular/cdk/table'



@NgModule({
  declarations: [
    SelectorComponent,
    AxSelectorComponent
  ],
  imports: [
    BrowserModule,
    CdkTableModule
  ],
  providers: [],
  bootstrap: [SelectorComponent]
})
export class SelectorModule { }
