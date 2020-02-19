import { Component, OnInit, ViewChild, Input, OnDestroy, Output, EventEmitter, ElementRef } from '@angular/core';
import { ObjectsRegistryService } from '../../objects-registry.service';
import { CdkDragDrop, moveItemInArray, CdkDrag } from '@angular/cdk/drag-drop';
import { Step, StepComponent } from './step/step.component';
import { AxScriptFlow, AxScriptFlowObj } from 'src/app/ax-model/model';
import { Utils } from 'src/app/utils';
import { SelectorDatastoreService } from 'src/app/ax-selector/selector-datastore.service';
import { RowVM } from 'src/app/ax-selector/ax-table/ax-table.component';
import * as _ from 'lodash';
import { Draggable } from 'src/app/utils/draggable';

@Component({
  selector: 'app-script-editor',
  templateUrl: './script-editor.component.html',
  styleUrls: ['./script-editor.component.scss']
})
export class ScriptEditorComponent implements OnInit,OnDestroy {



  listId:string = "list-" + Math.random().toString(36).substring(2);
  lastListId:string = "list-" + Math.random().toString(36).substring(2);

  selectedSteps:Step[] = []

  _steps:Step[] = []

  objects:RowVM[] = [];

  @ViewChild('actionList',{static: true}) actionList:ElementRef;

  @Output() change:EventEmitter<AxScriptFlow[]> = new EventEmitter();

  @Input() set steps(steps: AxScriptFlow[]) {
    this._steps = [];
    if(steps) {
      this._steps = steps.map(s => this.toStep(s));
    }
  }



  private toStep(s:AxScriptFlow):Step {
    if(typeof s === 'string') {
      return {id: Utils.uuidv4(), name: s, type: this.selectorDatastore.objectOrSection(s), condition: 'run', disabled: false};
    } else {
      if(s.if_true) {
        return {id: Utils.uuidv4(), name: s.if_true, type: this.selectorDatastore.objectOrSection(s.if_true), condition: 'if true', parameter: s.flow, parameterType: this.selectorDatastore.objectOrSection(s.flow), disabled: false};
      } else if(s.if_false) {
        return {id: Utils.uuidv4(), name: s.if_false, type: this.selectorDatastore.objectOrSection(s.if_false), condition: 'if false', parameter: s.flow, parameterType: this.selectorDatastore.objectOrSection(s.flow), disabled: false};
      } else if(s.for) {
        return {id: Utils.uuidv4(), name: s.for, type: 'map', condition: 'for', parameter: s.flow, parameterType: this.selectorDatastore.objectOrSection(s.flow), disabled: false};
      } else if(s.disable) {
        const disabled = this.toStep(s.disable);
        disabled.disabled = true;
        return disabled;
      }
    }
  }


  private fromStep(s:Step):AxScriptFlow {
    if(s.disabled) {
      const tempStep:Step = _.cloneDeep(s);
      tempStep.disabled = false;
      return {disable: this.fromStep(tempStep)};
    } else {
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



  stepChange(step:Step) {
    this.emitChange();
  }

  selectStep(step:Step,event:MouseEvent) {
    if(event.shiftKey) {
      let leftIndex = -1;
      let rightIndex = -1;
      const rowIndex = this._steps.indexOf(step);
      this._steps.forEach((s,i) => {
        if(this.isSelected(s) && i < rowIndex ) {
          leftIndex = i;
        }
        if(this.isSelected(s) && i > rowIndex) {
          rightIndex = i;
        }
      });
      if(leftIndex >= 0) { // found on the right
        for(let i = leftIndex+1; i <= rowIndex; i++) {
          this.selectedSteps.push(this._steps[i]);
        }
      } else if(rightIndex > 0) {
        for(let i = rowIndex; i < rightIndex; i++) {
          this.selectedSteps.push(this._steps[i]);
        }
      } else {
        this.selectedSteps = [step];
      }
    } else if(event.ctrlKey) {
      const i = this.selectedSteps.findIndex(x => x.id === step.id)
      if(i >= 0) {
        this.selectedSteps.splice(i,1);
      } else {
        this.selectedSteps.push(step);
      }
    } else {
      this.selectedSteps = [step]
    }
  }

  isSelected(step:Step):boolean {
    return this.selectedSteps.findIndex(x => x.id === step.id) >= 0;
  }

  disableEnableSelected() {
    this.selectedSteps.forEach(s => s.disabled = !s.disabled);
    this.emitChange();
  }

  deleteSelected() {
    if(confirm("Are you sure you want to delete this step?")) {
      this._steps = this._steps.filter(s => !this.selectedSteps.map(ss => ss.id).includes(s.id));
      this.selectedSteps = [];
      this.emitChange();
    }
  }


  emitChange() {
    const flow: AxScriptFlow[] = this._steps.map(s => this.fromStep(s));
    this.change.emit(flow);
  }




  dragover(event:DragEvent) {
    if(!this.dragStep) {
      if(!event.dataTransfer.types.includes(Draggable.ORDER)) {
        const type = Draggable.TYPE.decode(event.dataTransfer.types);
        this.dragStep = {
          id:Draggable.DRAGGING_ID,
          type: type,
          name: Draggable.TITLE.decode(event.dataTransfer.types),
          disabled: false,
          condition: type === "map" ? "for" : "run"
        };
        this._steps.push(this.dragStep);
      } else if(event.dataTransfer.types.includes(Draggable.ORDER)) {
        const id = Draggable.ID.decode(event.dataTransfer.types);
        this.dragStep = this._steps.find(s => s.id === id);
      }
    }

    if(this.dragStep) {
      const position = this.dragPosition(event);
      const currentPosition = this._steps.findIndex(s => s.id === this.dragStep.id);

      if(position != currentPosition) {
        const temp = this._steps[position];
        this._steps[position] = this._steps[currentPosition];
        this._steps[currentPosition] = temp;
      }
    }



    event.preventDefault();
  }

  dragStep:Step


  dragleave(event:DragEvent) {
    if(this.dragStep && this.dragStep.id === Draggable.DRAGGING_ID) {
      this._steps = this._steps.filter(s => s.id !== this.dragStep.id);
    }
    this.dragStep = null;
    event.preventDefault();
  }

  drop(event:DragEvent) {
    console.log("drop");
    if(this.dragStep && this.dragStep.id === Draggable.DRAGGING_ID) {
      this._steps = this._steps.filter(s => s.id !== this.dragStep.id);
      const step:Step = JSON.parse(event.dataTransfer.getData(Draggable.STEP));
      if(step) {
        this._steps.splice(this.dragPosition(event),0,step);
      }
    }
    this.dragStep = null;
    event.stopPropagation();
    this.emitChange();
  }

  isDragging(step:Step) {
    return step.id === Draggable.DRAGGING_ID;
  }

  dragPosition(event:DragEvent):number {
    return Math.min(
      Math.max(
        0,
        Math.floor((event.clientY - this.actionList.nativeElement.offsetTop + 30)/60) - 1
      ),
      this._steps.length-1
    );
  }



}
