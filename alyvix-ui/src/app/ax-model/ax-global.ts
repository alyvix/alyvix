import { AxModel } from "./model";
import { AxModelMock } from "./mock";

export interface GroupsFlag{
    created:boolean[]
    count:number[]
}

//define here methods and variables that are defined in the global scope of alyvix
export interface AxGlobal{
    axModel():AxModel;

    newComponent(group:number):any 
    setPoint(i:number):any

    setRectangles():any
    save():any
    cancel():any

    getGroupsFlag():GroupsFlag

    getSelectedNode():number
    setSelectedNode(i:number)
}

export class MockGlobal implements AxGlobal{
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