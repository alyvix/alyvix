import { Component, OnInit, Input, ViewChild, OnDestroy, Output, EventEmitter } from '@angular/core';
import { CdkDragDrop, CdkDropList, CdkDrag } from '@angular/cdk/drag-drop';
import { ObjectsRegistryService } from 'src/app/ax-editor/objects-registry.service';
import { SelectorDatastoreService, MapsVM, SectionVM } from 'src/app/ax-selector/selector-datastore.service';
import { Draggable } from 'src/app/utils/draggable';
import { EditorService } from 'src/app/ax-editor/editor.service';
import { RowVM } from 'src/app/ax-selector/ax-table/ax-table.component';

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
export class StepComponent implements OnInit {




  constructor(
    private selectorDatastore:SelectorDatastoreService,
    private editorService:EditorService
    ) { }

  private conditions = {
    'object': ['run', 'if true', 'if false'],
    'section': ['run'],
    'map': ['for']
  };

  condition = '';
  secondParameterEnabled = false;
  secondParameterValue = '';
  secondParameterType = 'warning';
  droppingSecond = false;
  droppingPrimary = false;

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

  }

  get missing(): boolean {
    if(this.selectorDatastore.unsafeData() && this.selectorDatastore.unsafeData().some(x => this.step.name == x.name)) {
      return false
    }
    if(this.sections && this.sections.some(x => this.step.name == x.name)) {
      return false
    }
    if(this.maps && this.maps.some(x => this.step.name == x.name)) {
      return false
    }
    return true
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
    this.step.condition = this.condition;
    this.stepChange.emit(this.step);
  }

  dropped(event: DragEvent) {
    this.droppingPrimary = false;
    if(this.enableDropArea(event)) {
      if(this.enableDropPrimary(event)) {
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
      }
      event.stopPropagation();
    }
  }


  droppedSecond(event: DragEvent) {
    this.droppingSecond = false;
    if(this.enableDropArea(event)) {
      if(this.enableDropSecondary(event)) {
        const step:Step = JSON.parse(event.dataTransfer.getData(Draggable.STEP));
        if(step) {
          this.secondParameterValue = step.name;
          this.secondParameterType = step.type;
          this.step.parameter = this.secondParameterValue;
          this.stepChange.emit(this.step);
        }
      }
      event.stopPropagation();
    }
  }

  maps:MapsVM[] = []
  sections:SectionVM[] = []

  ngOnInit() {
    this.selectorDatastore.getMaps().subscribe(m => this.maps = m)
    this.selectorDatastore.getScripts().subscribe(s => this.sections = s.sections)
  }


  enableDropArea(event:DragEvent):boolean {
    return  this.step.id !== Draggable.DRAGGING_ID &&
            !event.dataTransfer.types.includes(Draggable.ORDER)
  }

  enableDropPrimary(event:DragEvent):boolean {
    switch(Draggable.TYPE.decode(event.dataTransfer.types)) {
      case 'object': return this.step.type === "object" && this.step.condition !== "run";
      case 'section': return false;
      case 'map': return this.step.type === "map"
    }
  }

  enableDropSecondary(event:DragEvent):boolean {
    switch(Draggable.TYPE.decode(event.dataTransfer.types)) {
      case 'object': return true;
      case 'section': return true;
      case 'map': return false;
    }
  }

  dragoverPrimary(event:DragEvent) {
    if(this.enableDropArea(event)) {
      if(this.enableDropPrimary(event)) {
        this.droppingPrimary = true;
      }
      event.preventDefault();
      event.stopPropagation();
    }
  }

  primaryTempName = null;

  // dragenterPrimary(event:DragEvent) {
  //   if(this.enableDrop(event)) {
  //     this.primaryTempName = Draggable.TITLE.decode(event.dataTransfer.types)
  //     event.preventDefault();
  //     event.stopPropagation();
  //   }
  // }

  disableDrop(event:DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    return false;
  }

  dragleavePrimary(event:DragEvent) {
    this.droppingPrimary = false;
    if(this.primaryTempName) {
      this.primaryTempName = null;
    }
  }

  secondaryTempName = null;

  dragoverSecondary(event:DragEvent) {
    if(this.enableDropArea(event)) {
      if(this.enableDropSecondary(event)) {
        this.droppingSecond = true;
      }
      event.preventDefault();
      event.stopPropagation();
    }
  }

  // dragenterSecondary(event:DragEvent) {
  //   if(this.enableDrop(event) && Draggable.TYPE.decode(event.dataTransfer.types) != "map") {
  //     this.secondaryTempName = Draggable.TITLE.decode(event.dataTransfer.types)
  //     event.preventDefault();
  //     event.stopPropagation();
  //   }
  // }

  dragleaveSecondary(event:DragEvent) {
    this.droppingSecond = false;
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

  openSection(section:string) {
    this.editorService.setSection.emit(section);
  }


}
