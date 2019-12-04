import { Component, OnInit, ViewChild, Input } from '@angular/core';
import { ObjectsRegistryService } from '../../objects-registry.service';
import { CdkDropList, CdkDragDrop, moveItemInArray, CdkDrag } from '@angular/cdk/drag-drop';
import { Step } from './step/step.component';
import { AxScriptFlow, AxScriptFlowObj } from 'src/app/ax-model/model';

@Component({
  selector: 'app-script-editor',
  templateUrl: './script-editor.component.html',
  styleUrls: ['./script-editor.component.scss']
})
export class ScriptEditorComponent implements OnInit {


  @ViewChild('actions', {static: true}) actions:CdkDropList;

  _steps:Step[] = []

  @Input() set steps(steps: AxScriptFlow[]) {
    if(steps) {
      steps.map(s => {
        if(typeof s === 'string') {
          this._steps.push({name: s, type: 'object', condition: 'run'});
        } else {
          if(s.if_true) {
            this._steps.push({name: s.if_true, type: 'object', condition: 'if true', parameter: s.flow});
          } else if(s.if_false) {
            this._steps.push({name: s.if_false, type: 'object', condition: 'if false', parameter: s.flow});
          } else if(s.for) {
            this._steps.push({name: s.for, type: 'map', condition: 'for', parameter: s.flow});
          }
        }
      });
    }
  }



  constructor(private objectRegistry:ObjectsRegistryService) { }

  ngOnInit() {
    this.objectRegistry.addObjectList(this.actions);
  }

  dropped(event: CdkDragDrop<any,any>) {
    console.log('actions');
    console.log(event);
    switch(event.previousContainer.data) {
      case 'actions':
        moveItemInArray(this.steps, event.previousIndex, event.currentIndex);
        break;
      case 'object':
      case 'map':
        this._steps.push({name: event.item.data, type: event.previousContainer.data});
        break;
    }
  }

  enter(event) {
    console.log("enter parent");
    console.log(event);
  }

  canDrop(drag: CdkDrag, drop: CdkDropList) {
    console.log('canDrop')
    console.log(drag);
    console.log(drop);
    return true;
  }

}
