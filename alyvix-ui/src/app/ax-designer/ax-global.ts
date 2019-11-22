import { AxModel, BoxListEntity } from "../ax-model/model";
import { AxModelMock } from "../ax-model/mock";
import { Utils } from "../utils";
import { Observable } from "rxjs";
import { of } from 'rxjs';

export interface GroupsFlag{
    created:boolean[]
    count:number[]
    main:boolean[]
}

//define here methods and variables that are defined in the global scope of alyvix
export enum RectType{
    Box = "box",
    Window = "window",
    Button = "button"
}

export interface DesignerGlobal{
    axModel():Observable<AxModel>;
    background():Observable<string>;

    lastElement():BoxListEntity;

    newComponent(group:number):any
    setPoint(i:number):any

    setRectangles():any

    getGroupsFlag():GroupsFlag //can be mocked no effect on UI
    setGroupFlags(flags:GroupsFlag) //can be mocked no effect on UI

    getSelectedNode():number //can be mocked no effect on UI
    setSelectedNode(i:number) //can be mocked no effect on UI

    get_rect_type(rect:BoxListEntity):RectType
    set_rect_type(type:RectType,rect:BoxListEntity)

    setTypeNode(s:string) //can be mocked no effect on ui

    uuidv4():string
}

export class MockDesignerGlobal implements DesignerGlobal{
    uuidv4(): string {
        return Utils.uuidv4();
    }

    get_rect_type(rect: BoxListEntity): RectType {
        console.log("get_rect_type");
        return RectType.Box;
    }
    set_rect_type(type: RectType, rect: BoxListEntity) {
        console.log("set_rect_type");
    }


    lastElement(): BoxListEntity {
        return null;
    }
    setGroupFlags(flags: GroupsFlag) {

    }
    getGroupsFlag(): GroupsFlag {
        return AxModelMock.flags();
    }
    setRectangles() {

    }

    setPoint(i: number) {
        throw new Error("Method not implemented.");
    }
    newComponent(group: number) {
        throw new Error("Method not implemented.");
    }

    getSelectedNode():number {
        return null;
    }

    setSelectedNode(i:number) {

	}

	setTypeNode(s:string){

	}



    axModel(): Observable<AxModel> {
        return of(AxModelMock.get());
    }

    background():Observable<string> {
      return of("");
    }

}

export class DesignerGlobalRef implements DesignerGlobal {
  axModel(): Observable<AxModel> { return of((window as any).axModel()); }
  lastElement(): BoxListEntity { return (window as any).lastElement(); }
  newComponent(group: number) { return (window as any).newComponent(group); }
  setPoint(i: number) { return (window as any).setPoint(i); }
  setRectangles() { return (window as any).setRectangles(); }
  getGroupsFlag(): GroupsFlag { return (window as any).getGroupsFlag(); }
  setGroupFlags(flags: GroupsFlag) { return (window as any).setGroupFlags(flags); }
  getSelectedNode(): number { return (window as any).getSelectedNode(); }
  setSelectedNode(i: number) { return (window as any).setSelectedNode(i); }
  get_rect_type(rect: BoxListEntity): RectType { return (window as any).get_rect_type(rect); }
  set_rect_type(type: RectType, rect: BoxListEntity) { return (window as any).set_rect_type(type,rect); }
  setTypeNode(s: string) { return (window as any).setTypeNode(s); }
  uuidv4(): string { return (window as any).uuidv4(); }
  background():Observable<string> {
    return of("");
  }
}

