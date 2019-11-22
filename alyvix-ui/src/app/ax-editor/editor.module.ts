import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { EditorComponent } from './editor.component';
import { SelectorModule } from '../ax-selector/selector.module';
import { DesignerModule } from '../ax-designer/designer.module';
import { SelectorComponent } from '../ax-selector/selector.component';
import { AxSelectorComponent } from '../ax-selector/ax-selector.component';
import { AxTableComponent } from '../ax-selector/ax-table/ax-table.component';
import { CopyClipboardDirective } from '../directives/copy-clipboard.directive';
import { DesignerComponent } from '../ax-designer/designer.component';
import { AxDesignerComponent } from '../ax-designer/ax-designer.component';
import { TreeComponent } from '../ax-designer/tree/tree.component';
import { IComponent } from '../ax-designer/box-options/i/i.component';
import { RComponent } from '../ax-designer/box-options/r/r.component';
import { TComponent } from '../ax-designer/box-options/t/t.component';
import { InteractionComponent } from '../ax-designer/box-options/interaction/interaction.component';
import { BoxOptionsComponent } from '../ax-designer/box-options/box-options.component';
import { TreeNodeComponent } from '../ax-designer/tree/tree-node/tree-node.component';
import { SelectTypeComponent } from '../ax-designer/box-options/select-type/select-type.component';
import { ScreenComponent } from '../ax-designer/box-options/screen/screen.component';
import { CdkTableModule } from '@angular/cdk/table';
import { AngularResizedEventModule } from 'angular-resize-event';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { ContextMenuModule } from 'ngx-contextmenu';
import { CustomFormsModule } from 'ng2-validation';
import { HotkeyModule } from 'angular2-hotkeys';
import { AutocompleteLibModule } from 'angular-ng-autocomplete';
import { environment } from 'src/environments/environment';
import { NgxResizableModule } from '@3dgenomes/ngx-resizable';
import { AxHeaderComponent } from './ax-header/ax-header.component';
import { CentralPanelComponent } from './central-panel/central-panel.component';
import { ScriptEditorComponent } from './central-panel/script-editor/script-editor.component';
import { StepComponent } from './central-panel/script-editor/step/step.component';
import { ObjectsPanelComponent } from './objects-panel/objects-panel.component';
import { EditorDesignerGlobal } from './designer-global';
import { MonitorComponent } from './central-panel/monitor/monitor.component';



@NgModule({
  declarations: [
    EditorComponent,
    SelectorComponent,
    AxSelectorComponent,
    AxTableComponent,
    CopyClipboardDirective,
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
    AxHeaderComponent,
    CentralPanelComponent,
    ScriptEditorComponent,
    StepComponent,
    ObjectsPanelComponent,
    MonitorComponent,
  ],
  imports: [
    NgxResizableModule,
    BrowserModule,
    HttpClientModule,
    FormsModule,
    BrowserModule,
    CdkTableModule,
    AngularResizedEventModule,
    HttpClientModule,
    FormsModule,
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
  providers: [
    {provide: 'GlobalRefSelector', useClass: environment.globalTypeSelector},
    {provide: 'GlobalRefDesigner', useClass: EditorDesignerGlobal},
    {provide: 'GlobalRefEditor', useClass: environment.globalTypeEditor},
    {provide: 'subSystem', useValue: 'editor'}
  ],
  bootstrap: [EditorComponent]
})
export class EditorModule { }
