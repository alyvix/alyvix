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
import { CopyClipboardDirective } from '../directives/copy-clipboard.directive';



@NgModule({
  declarations: [
    SelectorComponent,
    AxSelectorComponent,
    AxTableComponent,
    CopyClipboardDirective
  ],
  imports: [
    BrowserModule,
    CdkTableModule,
    AngularResizedEventModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [{provide: 'GlobalRefSelector', useClass: environment.globalTypeSelector}],
  bootstrap: [SelectorComponent]
})
export class SelectorModule { }
