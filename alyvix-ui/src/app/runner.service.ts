import { Injectable } from '@angular/core';
import { AxScriptFlow } from './ax-model/model';
import { AlyvixApiService } from './alyvix-api.service';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RunnerService {

  private _running:BehaviorSubject<boolean> = new BehaviorSubject(false)

  constructor(
    private api:AlyvixApiService
  ) { }

  setState(state:string) {
    if(state === "RUN") this._running.next(false)
  }

  running():Observable<boolean> {
    return this._running;
  }

  runAll() {
    this.api.run('run').subscribe(_ => this._running.next(true))
  }

  stop() {
    this.api.run('stop').subscribe(_ => this._running.next(false))
  }

  runOne(name:string) {
    this.api.runOne(name).subscribe(_ => this._running.next(true))
  }

  runSelection(flow:AxScriptFlow[]) {
    this.api.runSelection(flow).subscribe(_ => this._running.next(true))
  }

}
