import { AxModel, BoxListEntity } from "../ax-model/model";
import { AxModelMock } from "../ax-model/mock";
import { Utils } from "../utils";
import { Observable } from "rxjs";
import { of } from 'rxjs';
import { NgZone, Injectable } from "@angular/core";

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

export abstract class DesignerGlobal{

    constructor(protected zone:NgZone) {

    }

    abstract axModel():Observable<AxModel>;
    abstract background():Observable<string>;

    abstract lastElement():BoxListEntity;

    abstract newComponent(group:number):any
    abstract setPoint(i:number):any

    abstract setRectangles():any

    abstract getGroupsFlag():GroupsFlag //can be mocked no effect on UI
    abstract setGroupFlags(flags:GroupsFlag) //can be mocked no effect on UI

    abstract getSelectedNode():number //can be mocked no effect on UI
    abstract setSelectedNode(i:number) //can be mocked no effect on UI

    abstract get_rect_type(rect:BoxListEntity):RectType
    abstract set_rect_type(type:RectType,rect:BoxListEntity)

    abstract setTypeNode(s:string) //can be mocked no effect on ui

    abstract uuidv4():string
}

@Injectable({
  providedIn: 'root'
})
export class MockDesignerGlobal extends DesignerGlobal{

    constructor(zone: NgZone) {
      super(zone);
    }

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
      return of(AxModelMock._model.box_list[0].thumbnail.image);
    }

}

@Injectable({
  providedIn: 'root'
})
export class DesignerGlobalRef extends DesignerGlobal {

  constructor(zone: NgZone) {
    super(zone);
  }

  axModel(): Observable<AxModel> { return this.zone.runOutsideAngular(() => of((window as any).axModel())) }
  lastElement(): BoxListEntity { return this.zone.runOutsideAngular(() =>(window as any).lastElement()) }
  newComponent(group: number) { return this.zone.runOutsideAngular(() =>(window as any).newComponent(group)) }
  setPoint(i: number) { return this.zone.runOutsideAngular(() =>(window as any).setPoint(i)) }
  setRectangles() { return this.zone.runOutsideAngular(() =>(window as any).setRectangles()) }
  getGroupsFlag(): GroupsFlag { return this.zone.runOutsideAngular(() =>(window as any).getGroupsFlag()) }
  setGroupFlags(flags: GroupsFlag) { return this.zone.runOutsideAngular(() =>(window as any).setGroupFlags(flags)) }
  getSelectedNode(): number { return this.zone.runOutsideAngular(() =>(window as any).getSelectedNode()) }
  setSelectedNode(i: number) { return this.zone.runOutsideAngular(() =>(window as any).setSelectedNode(i)) }
  get_rect_type(rect: BoxListEntity): RectType { return this.zone.runOutsideAngular(() =>(window as any).get_rect_type(rect)) }
  set_rect_type(type: RectType, rect: BoxListEntity) { return this.zone.runOutsideAngular(() =>(window as any).set_rect_type(type,rect)) }
  setTypeNode(s: string) { return this.zone.runOutsideAngular(() =>(window as any).setTypeNode(s)) }
  uuidv4(): string { return this.zone.runOutsideAngular(() =>(window as any).uuidv4()) }
  background():Observable<string> {
    return of("");
  }
}

