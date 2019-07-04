import { AxModel, BoxListEntity } from "./model";
import { AxModelMock } from "./mock";

export interface GroupsFlag{
    created:boolean[]
    count:number[]
    main:boolean[]
}

//define here methods and variables that are defined in the global scope of alyvix
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
	
	setTypeNode(s:string)
}

export class MockGlobal implements AxGlobal{
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