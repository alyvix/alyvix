import { Mock } from "protractor/built/driverProviders";
import { AxModelMock } from "../ax-model/mock";



export interface SelectorGlobal{
    current_library_name:string;
    res_string:string;
}

export class MockSelectorGlobal implements SelectorGlobal{
    current_library_name = 'test_long_filename';
    res_string: string = AxModelMock.resolution;
}

export class SelectorGlobalRef implements SelectorGlobal {
  current_library_name: string = (window as any).current_library_name;
  res_string: string = (window as any).res_string;
}
