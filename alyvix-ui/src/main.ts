import { enableProdMode, PlatformRef, NgModuleRef } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';

if (environment.production) {
  enableProdMode();
}


var designer:void | NgModuleRef<AppModule>

function loadAlyvixDesigner() {
  platformBrowserDynamic().bootstrapModule(AppModule).catch(err => console.log(err)).then(module => designer = module)
}

function unloadAlyvixDesigner() {
  if(designer) {
    designer.destroy();
  }
}


(window as any).loadAlyvixDesigner = loadAlyvixDesigner;
(window as any).unloadAlyvixDesigner = unloadAlyvixDesigner;

if(!environment.production) {
  loadAlyvixDesigner();
}


