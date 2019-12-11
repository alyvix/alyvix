import { Component, OnInit, Input, ViewChild, OnDestroy, Output, EventEmitter } from '@angular/core';
import { CdkDragDrop, CdkDropList, CdkDrag } from '@angular/cdk/drag-drop';
import { ObjectsRegistryService } from 'src/app/ax-editor/objects-registry.service';
import { PriBaseDropList } from 'pri-ng-dragdrop/lib/entities/pri.base.drop.list';
import { PriDropEventArgs } from 'pri-ng-dragdrop';

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


  constructor(private objectRegistry:ObjectsRegistryService) { }

  private conditions = {
    'object': ['run', 'if true', 'if false'],
    'section': ['run', 'if true', 'if false'],
    'map': ['for']
  };

  condition = '';
  secondParameterEnabled = false;
  secondParameterValue = '';
  secondParameterType = 'object';

  private _step:Step;

  @Output() stepChange: EventEmitter<Step> = new EventEmitter();

  @Input()
  set step(step: Step) {
    this._step = step;
    this.secondParameterEnabled = !(step.condition === 'run');
    this.condition = step.condition;
    this.secondParameterValue = step.parameter;
    if (this.secondParameterEnabled) {
      setTimeout(() => this.objectRegistry.addObjectList(this.secondParameterId), 200);
    }
  }

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

  dropped(event: PriDropEventArgs) {
   this.step.name = event.itemData.name;
   this.stepChange.emit(this.step);
  }

  droppedSecond(event: PriDropEventArgs) {
   this.secondParameterValue = event.itemData.name;
   this.secondParameterType = evet.itemData.type;
   this.step.parameter = this.secondParameterValue;
   this.stepChange.emit(this.step);
  }

  ngOnInit() {
    this.objectRegistry.addObjectList(this.firstParameterId);
  }

  ngOnDestroy(): void {
    this.objectRegistry.removeObjectList(this.firstParameterId);
    this.objectRegistry.removeObjectList(this.secondParameterId);
  }

  readonly canDropObject = (listData: any, itemData: Step) => {
    return itemData.type === 'object' || itemData.type === 'section';
  }

}
