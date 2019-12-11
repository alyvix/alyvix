import { Mock } from "protractor/built/driverProviders";
import { AxModelMock } from "../ax-model/mock";
import { Injectable } from "@angular/core";



export interface SelectorGlobal{
    current_library_name:string;
    res_string:string;
}

@Injectable({
  providedIn: 'root'
})
export class MockSelectorGlobal implements SelectorGlobal{
    current_library_name = 'test_long_filename';
    res_string: string = AxModelMock.resolution;
}

@Injectable({
  providedIn: 'root'
})
export class SelectorGlobalRef implements SelectorGlobal {
  current_library_name: string = (window as any).current_library_name;
  res_string: string = (window as any).res_string;
}
