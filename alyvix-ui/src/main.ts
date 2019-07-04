import { enableProdMode, PlatformRef, NgModuleRef } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';
import { HotkeysService } from 'angular2-hotkeys';

if (environment.production) {
  enableProdMode();
}


var designer: void | NgModuleRef<AppModule>

function loadAlyvixDesigner() {
  platformBrowserDynamic().bootstrapModule(AppModule).catch(err => console.log(err)).then(module => designer = module)
}

function unloadAlyvixDesigner() {
  if (designer) {
    const hotkeyService = designer.injector.get(HotkeysService);
    hotkeyService.reset();
    designer.destroy();
  }
}


(window as any).loadAlyvixDesigner = loadAlyvixDesigner;
(window as any).unloadAlyvixDesigner = unloadAlyvixDesigner;

/* TO TEST
var node = document.createElement("app-root");
document.body.append(node);
loadAlyvixDesigner()
*/

if (!environment.production) {
  loadAlyvixDesigner();
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


