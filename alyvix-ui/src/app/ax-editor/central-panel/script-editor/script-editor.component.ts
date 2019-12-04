import { Component, OnInit, ViewChild, Input, OnDestroy, Output, EventEmitter } from '@angular/core';
import { ObjectsRegistryService } from '../../objects-registry.service';
import { CdkDragDrop, moveItemInArray, CdkDrag } from '@angular/cdk/drag-drop';
import { Step } from './step/step.component';
import { AxScriptFlow, AxScriptFlowObj } from 'src/app/ax-model/model';
import { PriBaseDropList } from 'pri-ng-dragdrop/lib/entities/pri.base.drop.list';
import { PriDropEventArgs } from 'pri-ng-dragdrop';
import { Utils } from 'src/app/utils';

@Component({
  selector: 'app-script-editor',
  templateUrl: './script-editor.component.html',
  styleUrls: ['./script-editor.component.scss']
})
export class ScriptEditorComponent implements OnInit,OnDestroy {



  listId:string = "list-" + Math.random().toString(36).substring(2);
  lastListId:string = "list-" + Math.random().toString(36).substring(2);

  _steps:Step[] = []

  @Output() change:EventEmitter<AxScriptFlow[]> = new EventEmitter();

  @Input() set steps(steps: AxScriptFlow[]) {
    this._steps = [];
    if(steps) {
      steps.map(s => {
        if(typeof s === 'string') {
          this._steps.push({id: Utils.uuidv4(), name: s, type: 'object', condition: 'run'});
        } else {
          if(s.if_true) {
            this._steps.push({id: Utils.uuidv4(), name: s.if_true, type: 'object', condition: 'if true', parameter: s.flow});
          } else if(s.if_false) {
            this._steps.push({id: Utils.uuidv4(), name: s.if_false, type: 'object', condition: 'if false', parameter: s.flow});
          } else if(s.for) {
            this._steps.push({id: Utils.uuidv4(), name: s.for, type: 'map', condition: 'for', parameter: s.flow});
          }
        }
      });
      console.log(this._steps);
    }
  }



  constructor(private objectRegistry:ObjectsRegistryService) { }

  ngOnInit() {
    this.objectRegistry.addObjectList(this.listId);
    this.objectRegistry.addObjectList(this.lastListId);
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
