import { AxModel, BoxListEntity } from "./model";
import { AxModelMock } from "./mock";

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

    setRectangles():any
    save():any
    cancel():any

    getGroupsFlag():GroupsFlag
    setGroupFlags(flags:GroupsFlag)

    getSelectedNode():number
    setSelectedNode(i:number)
    
    get_rect_type(rect:BoxListEntity):RectType
    set_rect_type(type:RectType,rect:BoxListEntity)
    
    setTypeNode(s:string)
    
    uuidv4():string 
}

export class MockGlobal implements AxGlobal{
    uuidv4(): string {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
          });
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