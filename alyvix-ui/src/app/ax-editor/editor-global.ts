import { BoxListEntity } from "../ax-model/model";

export interface EditorGlobal{
  res_h:number;
  res_w:number;

  setCanvas(c:HTMLCanvasElement);
  setBoxes(boxes:BoxListEntity[]);

}

export class MockEditorGlobal implements EditorGlobal{
  setBoxes(boxes: BoxListEntity[]) {
    console.log(boxes);
  }
  res_h: number = 1200;
  res_w: number = 1920;
  setCanvas(c: HTMLCanvasElement) {
    console.log("set canvas");
    console.log(c);
  }


}

export class EditorGlobalRef implements EditorGlobal {
  res_h: number = (window as any).res_h;
  res_w: number = (window as any).res_w;
  setCanvas(c: HTMLCanvasElement) {
    (window as any).setCanvas(c);
  }
  setBoxes(c: BoxListEntity[]) {
    (window as any).setBoxes(c);
  }

}
