


export interface Global{
    new_button(delay:number);
    cancel_button();
    edit(object_name:string, resolution:string);

    current_library_name:string;
    res_string:string;
}

export class MockGlobal implements Global{
    current_library_name = 'test_long_filename';
    res_string: string = '1920*1200@100';
    edit(object_name: string, resolution: string) {
      console.log(object_name);
      console.log(resolution);
      throw new Error("Method not implemented.");
    }
    new_button(delay:number) {
        console.log(delay);
        throw new Error("Method not implemented.");
    }
    cancel_button() {
        throw new Error("Method not implemented.");
    }



}

export interface GlobalRef{
    nativeGlobal():Global
}

export class AxEmbeddedSelectorGlobalRef implements GlobalRef {
    nativeGlobal(): Global { return window as any as Global; }
}

export class DevSelectorGlobalRef implements GlobalRef{
    nativeGlobal(): Global { return new MockGlobal }
}
