import { BoxListEntity } from "../ax-model/model";
import { NgZone, Injectable } from "@angular/core";

export interface EditorGlobal{
  res_h:number;
  res_w:number;
  scaling_factor:number;

  setCanvas(c:HTMLCanvasElement);
  setBoxes(boxes:BoxListEntity[]);

}

@Injectable({
  providedIn: 'root'
})
export class MockEditorGlobal implements EditorGlobal{
  setBoxes(boxes: BoxListEntity[]) {
    console.log(boxes);
  }
  res_h: number = 1080;
  res_w: number = 1920;
  scaling_factor: number = 100;
  setCanvas(c: HTMLCanvasElement) {
    console.log("set canvas");
    console.log(c);
  }


}

@Injectable({
  providedIn: 'root'
})
export class EditorGlobalRef implements EditorGlobal {

  constructor(private zone: NgZone) {}

  res_h: number = (window as any).res_h;
  res_w: number = (window as any).res_w;
  scaling_factor: number = (window as any).scaling_factor;
  setCanvas(c: HTMLCanvasElement) {
    this.zone.runOutsideAngular(() => (window as any).setCanvas(c));
  }
  setBoxes(c: BoxListEntity[]) {
    this.zone.runOutsideAngular(() => (window as any).setBoxes(c));
  }

}
