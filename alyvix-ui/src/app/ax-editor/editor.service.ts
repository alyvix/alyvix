import { Injectable, EventEmitter } from '@angular/core';
import { SelectorDatastoreService, MapsVM, MapRowVM, AxFile } from '../ax-selector/selector-datastore.service';
import { BehaviorSubject, Observable, from, timer } from 'rxjs';
import { AxScriptFlow } from '../ax-model/model';
import { Step } from './central-panel/script-editor/step/step.component';
import { debounce } from 'rxjs/operators';
import { RunnerService } from '../runner.service';
import { CentralPanelComponent } from './central-panel/central-panel.component';


export interface LeftSelection{
  name:string;
  type:string;
  steps?:() => AxScriptFlow[];
  map?:() => MapRowVM[];
  onChangeSteps?: (step:AxScriptFlow[]) => any;
  onChangeMap?: (map:MapRowVM[]) => any;
}

export interface ConsoleElement{
  line?:string;
  image?:string;
}

@Injectable({
  providedIn: 'root'
})
export class EditorService {

  private _selection:BehaviorSubject<LeftSelection> = new BehaviorSubject<LeftSelection>(null);
  objectChanged:EventEmitter<string> = new EventEmitter()
  setSection:EventEmitter<string> = new EventEmitter()
  private tab:AxFile

  private console:BehaviorSubject<ConsoleElement[]> = new BehaviorSubject<ConsoleElement[]>([])

  private objectSave:(objects:string[]) => Observable<any>

  private beforeSavePromises:(() => Promise<any>)[] = [];

  private throttledChange:EventEmitter<any> = new EventEmitter();


  private running = false;

  constructor(
    private selectorDatastore:SelectorDatastoreService,
    private runnerService:RunnerService
  ) {
    this.selectorDatastore.tabSelected().subscribe(tab => this.tab = tab);
    this.throttledChange.pipe(debounce(() => timer(500))).subscribe(x =>{
      this.save().subscribe(x => {});
    });
    this.runnerService.running().subscribe(x => {
      if(this.running && !x) { // end run
        this.setLeftSelection(CentralPanelComponent.consoleTab)
      }
      this.running = x;
    })
  }


  setObjectSave(o:(objects:string[]) => Observable<any>) {
    this.objectSave = o;
  }

  reloadObject(objectName:string) {
    console.log('EditorService::reloadObject('+objectName+")")
    if(this.tab && this.tab.main) { // do only when the working case tab is open
     this.selectorDatastore.reload(objectName);
    }
    this.objectChanged.emit(objectName);
  }

  setLeftSelection(s:LeftSelection) {
    this._selection.next(s);
  }

  getLeftSelection():Observable<LeftSelection> {
    return this._selection;
  }

  addBeforeSave(bs:() => Promise<any>) {
    this.beforeSavePromises.push(bs);
  }

  private beforeSave():Promise<any> {
    return Promise.all(this.beforeSavePromises.map(x => x()));
  }


  saveThrottled() {
    this.throttledChange.emit(true);
  }

  save():Observable<any> {
    let self = this;
    const promise = new Promise( function(resolve) {
      self.beforeSave().then(function() {
        self.selectorDatastore.save().subscribe(x => {
          self.objectSave(x.map(x => x.name)).subscribe( y => resolve());
        });
      });
    });
    return from(promise);
  }

  consoleClear() {
    this.console.next([]);
  }

  consoleAppendLine(line:string) {
    this.console.next(this.console.value.concat([{line: line}]))
  }

  consoleAppendImage(image:string) {
    this.console.next(this.console.value.concat([{image: image}]))
  }

  consoleElements():Observable<ConsoleElement[]> {
    return this.console
  }






}
