import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { DragDropModule } from '@angular/cdk/drag-drop';

import { AngularResizedEventModule } from 'angular-resize-event';
import { ContextMenuModule } from 'ngx-contextmenu';
import {HotkeyModule} from 'angular2-hotkeys';
import { CustomFormsModule } from 'ng2-validation'


import { DesignerComponent } from './designer.component';
import { AxDesignerComponent } from './ax-designer.component';
import { TreeComponent } from './tree/tree.component';
import { IComponent } from './box-options/i/i.component';
import { RComponent } from './box-options/r/r.component';
import { TComponent } from './box-options/t/t.component';
import { InteractionComponent } from './box-options/interaction/interaction.component';
import { BoxOptionsComponent } from './box-options/box-options.component';
import { environment } from 'src/environments/environment';
import { TreeNodeComponent } from './tree/tree-node/tree-node.component';
import { SelectTypeComponent } from './box-options/select-type/select-type.component';
import { ScreenComponent } from './box-options/screen/screen.component';
import {AutocompleteLibModule} from 'angular-ng-autocomplete';

@NgModule({
  declarations: [
    DesignerComponent,
    AxDesignerComponent,
    TreeComponent,
    IComponent,
    RComponent,
    TComponent,
    InteractionComponent,
    BoxOptionsComponent,
    TreeNodeComponent,
    SelectTypeComponent,
    ScreenComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    DragDropModule,
    AngularResizedEventModule,
    ContextMenuModule.forRoot(),
    HotkeyModule.forRoot({cheatSheetHotkey: "ctrl+h"}),
    CustomFormsModule,
    ReactiveFormsModule,
    AutocompleteLibModule
  ],
  providers: [{provide: 'GlobalRef', useClass: environment.globalType}],
  bootstrap: [DesignerComponent]
})
export class DesignerModule { }
