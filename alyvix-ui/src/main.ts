import { enableProdMode, PlatformRef, NgModuleRef } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { DesignerModule } from './app/ax-designer/designer.module';
import { environment } from './environments/environment';
import { HotkeysService } from 'angular2-hotkeys';
import { SelectorModule } from './app/ax-selector/selector.module';

if (environment.production) {
  enableProdMode();
}


var designer: void | NgModuleRef<DesignerModule>
var selector: void | NgModuleRef<SelectorModule>

function loadAlyvixDesigner() {
  platformBrowserDynamic().bootstrapModule(DesignerModule).catch(err => console.log(err)).then(module => designer = module)
}

function loadAlyvixSelector() {
  platformBrowserDynamic().bootstrapModule(SelectorModule).catch(err => console.log(err)).then(module => selector = module)
}

function unloadAlyvixDesigner() {
  if (designer) {
    const hotkeyService = designer.injector.get(HotkeysService);
    hotkeyService.reset();
    designer.destroy();
  }
}

function unloadAlyvixSelector() {
  if (selector) {
    selector.destroy();
  }
}


(window as any).loadAlyvixDesigner = loadAlyvixDesigner;
(window as any).unloadAlyvixDesigner = unloadAlyvixDesigner;
(window as any).loadAlyvixSelector = loadAlyvixSelector;
(window as any).unloadAlyvixSelector = unloadAlyvixSelector;

/* TO TEST
var node = document.createElement("app-root");
document.body.append(node);
loadAlyvixDesigner()
*/

if (!environment.production) {
  if(environment.workingOn == "designer") {
    loadAlyvixDesigner();
  } else if(environment.workingOn == "selector") {
    loadAlyvixSelector();
  }
  
  //loadAlyvixSelector();
  // uncomment o simulate multiple close open of the designer
  // setTimeout(() => {
  //   unloadAlyvixDesigner();
  //   console.log("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
  //   var node = document.createElement("app-root");
  //   document.body.append(node);
  //   loadAlyvixDesigner();
  //   setTimeout(() => {
  //     unloadAlyvixDesigner();
  //     console.log("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
  //     var node = document.createElement("app-root");
  //     document.body.append(node);
  //     loadAlyvixDesigner();
  //   }, 5000);
  // }, 5000);

}


