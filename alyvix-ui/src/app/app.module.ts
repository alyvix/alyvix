import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DragDropModule } from '@angular/cdk/drag-drop';

import { AngularResizedEventModule } from 'angular-resize-event';
import { ContextMenuModule } from 'ngx-contextmenu';
import {HotkeyModule} from 'angular2-hotkeys';
import { CustomFormsModule } from 'ng2-validation'


import { AppComponent } from './app.component';
import { AxDesignerComponent } from './ax-designer/ax-designer.component';
import { TreeComponent } from './ax-designer/tree/tree.component';
import { IComponent } from './ax-designer/box-options/i/i.component';
import { RComponent } from './ax-designer/box-options/r/r.component';
import { TComponent } from './ax-designer/box-options/t/t.component';
import { InteractionComponent } from './ax-designer/box-options/interaction/interaction.component';
import { BoxOptionsComponent } from './ax-designer/box-options/box-options.component';
import { environment } from 'src/environments/environment';
import { TreeNodeComponent } from './ax-designer/tree/tree-node/tree-node.component';
import { SelectTypeComponent } from './ax-designer/box-options/select-type/select-type.component';

@NgModule({
  declarations: [
    AppComponent,
    AxDesignerComponent,
    TreeComponent,
    IComponent,
    RComponent,
    TComponent,
    InteractionComponent,
    BoxOptionsComponent,
    TreeNodeComponent,
    SelectTypeComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    DragDropModule,
    AngularResizedEventModule,
    ContextMenuModule.forRoot(),
    HotkeyModule.forRoot(),
    CustomFormsModule,
    ReactiveFormsModule
  ],
  providers: [{provide: 'GlobalRef', useClass: environment.globalType}],
  bootstrap: [AppComponent]
})
export class AppModule { }
