import { Component, OnInit, Input, ViewChild, OnDestroy, Output, EventEmitter } from '@angular/core';
import { CdkDragDrop, CdkDropList, CdkDrag } from '@angular/cdk/drag-drop';
import { ObjectsRegistryService } from 'src/app/ax-editor/objects-registry.service';
import { SelectorDatastoreService } from 'src/app/ax-selector/selector-datastore.service';
import { Draggable } from 'src/app/utils/draggable';

export interface Step{
  id: string;
  name: string;
  type: string;
  condition?:string;
  parameter?:string;
  parameterType?:string;
  disabled:boolean;
}
@Component({
  selector: 'script-step',
  templateUrl: './step.component.html',
  styleUrls: ['./step.component.scss']
})
export class StepComponent implements OnInit,OnDestroy {



  firstParameterId:string = 'list-' + Math.random().toString(36).substring(2);
  secondParameterId:string = 'list-' + Math.random().toString(36).substring(2);


  constructor(private objectRegistry:ObjectsRegistryService, private selectorDatastore:SelectorDatastoreService) { }

  private conditions = {
    'object': ['run', 'if true', 'if false'],
    'section': ['run'],
    'map': ['for']
  };

  condition = '';
  secondParameterEnabled = false;
  secondParameterValue = '';
  secondParameterType = 'warning';

  private _step:Step;

  @Output() stepChange: EventEmitter<Step> = new EventEmitter();

  @Input()
  set step(step: Step) {
    this._step = step;
    this.secondParameterEnabled = !(step.condition === 'run');
    this.condition = step.condition;
    this.secondParameterValue = step.parameter;
    if(this.secondParameterValue && this.secondParameterValue !== '') {
      this.secondParameterType = this.selectorDatastore.objectOrSection(this.secondParameterValue);
    }
    if (this.secondParameterEnabled) {
      setTimeout(() => this.objectRegistry.addObjectList(this.secondParameterId), 200);
    }
  }

  @Input() selected:boolean;

  get step(): Step {
    return this._step;
  }

  nextCondition() {
    const conditionsForType:string[] = this.conditions[this._step.type];
    const i = conditionsForType.indexOf(this.condition) + 1;
    const n = conditionsForType.length;
    this.condition = conditionsForType[(i % n + n) % n];
    switch(this.condition) {
      case 'run':
        this.secondParameterEnabled = false;
        break;
      default:
        this.secondParameterEnabled = true;
    }
    if (this.secondParameterEnabled) {
      setTimeout(() => this.objectRegistry.addObjectList(this.secondParameterId), 200);
    }
    this.step.condition = this.condition;
    this.stepChange.emit(this.step);
  }

  dropped(event: DragEvent) {
   const step:Step = JSON.parse(event.dataTransfer.getData(Draggable.STEP));
   if(step) {
    this._step.name = step.name;
    if(this._step.type != step.type) {
      this._step.condition = step.condition || this.conditions[this.step.type][0];
    }
    this.condition = this.step.condition;
    this.secondParameterEnabled = !(this.step.condition === 'run');
    this._step.type = step.type;
    this._step.id = step.id;
    this.stepChange.emit(this.step);
    }
    event.stopPropagation();
  }

  droppedSecond(event: DragEvent) {
    const step:Step = JSON.parse(event.dataTransfer.getData(Draggable.STEP));
    if(step && step.type !== "map") {
      this.secondParameterValue = step.name;
      this.secondParameterType = step.type;
      this.step.parameter = this.secondParameterValue;
      this.stepChange.emit(this.step);
    }
    event.stopPropagation();
  }

  ngOnInit() {
    this.objectRegistry.addObjectList(this.firstParameterId);
  }

  ngOnDestroy(): void {
    this.objectRegistry.removeObjectList(this.firstParameterId);
    this.objectRegistry.removeObjectList(this.secondParameterId);
  }

  enableDrop(event:DragEvent) {
    return  this.step.id !== Draggable.DRAGGING_ID &&
            !event.dataTransfer.types.includes(Draggable.ORDER)
  }

  dragoverPrimary(event:DragEvent) {
    if(this.enableDrop(event)) {
      event.preventDefault();
      event.stopPropagation();
    }
  }

  primaryTempName = null;

  dragenterPrimary(event:DragEvent) {
    if(this.enableDrop(event)) {
      this.primaryTempName = Draggable.TITLE.decode(event.dataTransfer.types)
      event.preventDefault();
      event.stopPropagation();
    }
  }

  dragleavePrimary(event:DragEvent) {
    console.log("dragleave");
    if(this.primaryTempName) {
      this.primaryTempName = null;
    }
  }

  secondaryTempName = null;

  dragoverSecondary(event:DragEvent) {
    if(this.enableDrop(event)) {
      event.preventDefault();
      event.stopPropagation();
    }
  }

  dragenterSecondary(event:DragEvent) {
    if(this.enableDrop(event) && Draggable.TYPE.decode(event.dataTransfer.types) != "map") {
      this.secondaryTempName = Draggable.TITLE.decode(event.dataTransfer.types)
      event.preventDefault();
      event.stopPropagation();
    }
  }

  dragleaveSecondary(event:DragEvent) {
    console.log("dragleave");
    if(this.secondaryTempName) {
      this.secondaryTempName = null;
    }
  }


  startDrag(event:DragEvent) {

    event.dataTransfer.setDragImage(Draggable.labelTitle(this.step.name), 0, 0);
    event.dataTransfer.setData(Draggable.STEP,JSON.stringify(this._step));
    event.dataTransfer.setData(Draggable.ORDER,"true");
    event.dataTransfer.setData(Draggable.ID.encode(this._step.id),"id");
  }


}
