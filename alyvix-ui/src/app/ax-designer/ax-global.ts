import { AxModel, BoxListEntity } from "../ax-model/model";
import { AxModelMock } from "../ax-model/mock";
import { Utils } from "../utils";

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

export interface AxGlobal{
    axModel():AxModel;

    lastElement():BoxListEntity;

    newComponent(group:number):any
    setPoint(i:number):any

    setRectangles():any //can be mocked no effect on UI
    save():any //API call can be done directly by UI
    cancel():any //API call can be done directly by UI

    getGroupsFlag():GroupsFlag //can be mocked no effect on UI
    setGroupFlags(flags:GroupsFlag) //can be mocked no effect on UI

    getSelectedNode():number //can be mocked no effect on UI
    setSelectedNode(i:number) //can be mocked no effect on UI

    get_rect_type(rect:BoxListEntity):RectType //can be integrated in angular
    set_rect_type(type:RectType,rect:BoxListEntity) //can be integrated in angular

    setTypeNode(s:string) //can be mocked no effect on ui

    uuidv4():string
}

export class MockGlobal implements AxGlobal{
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
    save() {
        throw new Error("Method not implemented.");
    }
    cancel() {
        throw new Error("Method not implemented.");
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



    axModel(): AxModel {
        return AxModelMock.get();
    }
}

export interface GlobalRef{
    nativeGlobal():AxGlobal
}

export class AxEmbeddedGlobalRef implements GlobalRef {
    nativeGlobal(): AxGlobal { return window as any as AxGlobal; }
}

export class DevGlobalRef implements GlobalRef{
    nativeGlobal(): AxGlobal { return new MockGlobal }
}
