import { Component, OnInit, ViewChild, Input, OnDestroy, Output, EventEmitter } from '@angular/core';
import { ObjectsRegistryService } from '../../objects-registry.service';
import { CdkDragDrop, moveItemInArray, CdkDrag } from '@angular/cdk/drag-drop';
import { Step } from './step/step.component';
import { AxScriptFlow, AxScriptFlowObj } from 'src/app/ax-model/model';
import { PriBaseDropList } from 'pri-ng-dragdrop/lib/entities/pri.base.drop.list';
import { PriDropEventArgs } from 'pri-ng-dragdrop';
import { Utils } from 'src/app/utils';
import { SelectorDatastoreService } from 'src/app/ax-selector/selector-datastore.service';
import { RowVM } from 'src/app/ax-selector/ax-table/ax-table.component';

@Component({
  selector: 'app-script-editor',
  templateUrl: './script-editor.component.html',
  styleUrls: ['./script-editor.component.scss']
})
export class ScriptEditorComponent implements OnInit,OnDestroy {



  listId:string = "list-" + Math.random().toString(36).substring(2);
  lastListId:string = "list-" + Math.random().toString(36).substring(2);

  _steps:Step[] = []

  objects:RowVM[] = [];

  @Output() change:EventEmitter<AxScriptFlow[]> = new EventEmitter();

  @Input() set steps(steps: AxScriptFlow[]) {
    this._steps = [];
    if(steps) {
      this._steps = steps.map(s => this.toStep(s));
      console.log(this._steps);
    }
  }

  private objectOrSection(name:string):string {
    if(!name) return null;
    if(this.objects.find(x => x.name === name)) {
      return 'object';
    } else {
      return 'section';
    }
  }

  private toStep(s:AxScriptFlow):Step {
    if(typeof s === 'string') {
      return {id: Utils.uuidv4(), name: s, type: this.objectOrSection(s), condition: 'run', disabled: false};
    } else {
      if(s.if_true) {
        return {id: Utils.uuidv4(), name: s.if_true, type: this.objectOrSection(s.if_true), condition: 'if true', parameter: s.flow, parameterType: this.objectOrSection(s.flow), disabled: false};
      } else if(s.if_false) {
        return {id: Utils.uuidv4(), name: s.if_false, type: this.objectOrSection(s.if_false), condition: 'if false', parameter: s.flow, parameterType: this.objectOrSection(s.flow), disabled: false};
      } else if(s.for) {
        return {id: Utils.uuidv4(), name: s.for, type: 'map', condition: 'for', parameter: s.flow, parameterType: this.objectOrSection(s.flow), disabled: false};
      } else if(s.disable) {
        const disabled = this.toStep(s.disable);
        disabled.disabled = true;
        return disabled;
      }
    }
  }



  constructor(private objectRegistry:ObjectsRegistryService, private selectorDatastore:SelectorDatastoreService) { }

  ngOnInit() {
    this.objectRegistry.addObjectList(this.listId);
    this.objectRegistry.addObjectList(this.lastListId);
    this.selectorDatastore.getData().subscribe(d => this.objects = d);
  }

  ngOnDestroy(): void {
    this.objectRegistry.removeObjectList(this.listId);
    this.objectRegistry.removeObjectList(this.lastListId);
  }

  dropped(event: PriDropEventArgs) {
    switch(event.sourceListData) {
      case 'actions':
        const index = this._steps.findIndex(x => x.id === event.itemData.id)
        moveItemInArray(this._steps, index, event.dropIndex);
        break;
      case 'object':
      case 'section':
      case 'map':
        this._steps.splice(event.dropIndex, 0, event.itemData);
        break;
    }
    this.emitChange();
  }

  stepChange(step:Step) {
    this.emitChange();
  }

  emitChange() {
    const flow: AxScriptFlow[] = this._steps.map(s => {
      switch (s.condition) {
        case 'run':
          return s.name;
        case 'if true':
          return {
            flow: s.parameter,
            if_true: s.name
          };
        case 'if false':
          return {
            flow: s.parameter,
            if_false: s.name
          };
        case 'for':
          return {
            flow: s.parameter,
            for: s.name
          };
      }
    });
    this.change.emit(flow);
  }



  droppedEnd(event: PriDropEventArgs) {
    this._steps.push(event.itemData);
  }



}
