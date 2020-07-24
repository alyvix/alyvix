import { Injectable, EventEmitter } from '@angular/core';
import { CdkDropList } from '@angular/cdk/drag-drop';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Step } from './central-panel/script-editor/step/step.component';

@Injectable({
  providedIn: 'root'
})
export class ObjectsRegistryService {

  addStep:EventEmitter<Step> = new EventEmitter();

  constructor() { }


}
