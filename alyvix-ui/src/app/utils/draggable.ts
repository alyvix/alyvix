import { Step } from "../ax-editor/central-panel/script-editor/step/step.component";

export interface EncoderDecoder{
  encode(d:string)
  decode(data:ReadonlyArray<string>)
}

export namespace Draggable {
  export const STEP = "alyvix/action-step";
  export const ORDER = "alyvix/action-order";
  export const TITLE = trasform("alyvix/action-title-");
  export const ID = trasform("alyvix/action-id-");
  export const TYPE = trasform("alyvix/action-type-");

  export const DRAGGING_ID = "dragged";


  export function labelTitle(name:string):HTMLDivElement {
    const old = document.getElementById("dragLabel");
    if(old) {
      old.remove();
    }
    const title = document.createElement("div");
    title.id = "dragLabel";
    title.innerHTML = name;
    title.style.position = "absolute";
    title.style.left = "-100%";
    document.body.append(title);
    return title;
  }

  export function startDrag(event:DragEvent,type:string,step:Step) {

    event.dataTransfer.setDragImage(labelTitle(step.name), 0, 0);
    event.dataTransfer.setData(Draggable.TYPE.encode(type),type);
    event.dataTransfer.setData(Draggable.TITLE.encode(step.name),"name");
    event.dataTransfer.setData(Draggable.STEP,JSON.stringify(step));
  }


  function extract(constant:string):((data:ReadonlyArray<string>) => string) { return data => {
    const t = data.find(x => x.startsWith(constant));
    if(t) {
      return t.substr(constant.length);
    }
    return null;
  }}

  function encode(constant:string):((s:string) => string) { return t =>
    constant + t
  }

  //WORKAROUND since for security reason the browser doesen't allow to access the data during drag, I enode the data as data types
  function trasform(constant:string):EncoderDecoder {
    return {
      encode: encode(constant),
      decode: extract(constant)
    }
  }
}
