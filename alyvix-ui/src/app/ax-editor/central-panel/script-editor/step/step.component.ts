import { Component, OnInit, Input, ViewChild, OnDestroy } from '@angular/core';
import { CdkDragDrop, CdkDropList } from '@angular/cdk/drag-drop';
import { ObjectsRegistryService } from 'src/app/ax-editor/objects-registry.service';


export interface Step{
  name: string;
  type: string;
}
@Component({
  selector: 'script-step',
  templateUrl: './step.component.html',
  styleUrls: ['./step.component.scss']
})
export class StepComponent implements OnInit,OnDestroy {


  @ViewChild('firstParameter', {static: true}) firstParameter:CdkDropList;
  @ViewChild('secondParameter', {static: true}) secondParameter:CdkDropList;



  constructor(private objectRegistry:ObjectsRegistryService) { }

  private conditions = {
    'object': ['run', 'if true', 'if false'],
    'map': ['for']
  };

  condition = '';
  secondParameterEnabled = false;
  secondParameterValue = '';

  private _step:Step;

  @Input()
  set step(step: Step) {
    this._step = step;
    this.secondParameterEnabled = (step.type === 'map');
    this.condition = this.conditions[step.type][0];
    if (this.secondParameterEnabled) {
      setTimeout(() => this.objectRegistry.addObjectList(this.secondParameter), 200);
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
      setTimeout(() => this.objectRegistry.addObjectList(this.secondParameter), 200);
    }
  }

  dropped(event: CdkDragDrop<any,any>) {
   this.step = {name: event.item.data, type: event.previousContainer.data};
  }

  droppedSecond(event: CdkDragDrop<any,any>) {
    console.log('second');
    console.log(event);
   this.secondParameterValue = event.item.data;
  }

  ngOnInit() {
    this.objectRegistry.addObjectList(this.firstParameter);
  }

  ngOnDestroy(): void {
    this.objectRegistry.removeObjectList(this.firstParameter);
    this.objectRegistry.removeObjectList(this.secondParameter);
  }

  enter(event) {
    console.log("enter child");
    console.log(event);
  }

}
