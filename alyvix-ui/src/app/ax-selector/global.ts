


export interface Global{
    new_button();
    cancel_button();
    add_button();
}

export class MockGlobal implements Global{
    new_button() {
        throw new Error("Method not implemented.");
    }
    cancel_button() {
        throw new Error("Method not implemented.");
    }
    add_button() {
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