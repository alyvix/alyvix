import { enableProdMode, PlatformRef, NgModuleRef, NgZone } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { DesignerModule } from './app/ax-designer/designer.module';
import { environment } from './environments/environment';
import { HotkeysService } from 'angular2-hotkeys';
import { SelectorModule } from './app/ax-selector/selector.module';
import { SelectorDatastoreService } from './app/ax-selector/selector-datastore.service';
import { DesignerDatastoreService } from './app/ax-designer/designer-datastore.service';
import { EditorModule } from './app/ax-editor/editor.module';
import { AxModelMock } from './app/ax-model/mock';
import { EditorService } from './app/ax-editor/editor.service';
import { RunnerService } from './app/runner.service';


if (environment.production) {
  enableProdMode();
}


let designer: void | NgModuleRef<DesignerModule>
let selector: void | NgModuleRef<SelectorModule>
let editor: void | NgModuleRef<EditorModule>

function ngZone():NgZone {
  if(editor) {
    return editor.injector.get(NgZone);
  } else if(selector) {
    return selector.injector.get(NgZone);
  } else if(designer) {
    return designer.injector.get(NgZone);
  }
  return null;
}

function loadAlyvixDesigner() {
  console.log('loadAlyvixDesigner');
  platformBrowserDynamic().bootstrapModule(DesignerModule).catch(err => console.log(err)).then(module => designer = module)
}

function loadAlyvixSelector() {
  console.log('loadAlyvixSelector');
  platformBrowserDynamic().bootstrapModule(SelectorModule).catch(err => console.log(err)).then(module => selector = module)
}

function loadAlyvixEditor() {
  console.log('loadAlyvixEditor');
  platformBrowserDynamic().bootstrapModule(EditorModule).catch(err => console.log(err)).then(module => editor = module)
}



function unloadAlyvixDesigner() {
  console.log('unloadAlyvixDesigner');
  if (designer) {
    const hotkeyService = designer.injector.get(HotkeysService);
    hotkeyService.reset();
    designer.destroy();
  }
}

function unloadAlyvixSelector() {
  console.log('unloadAlyvixSelector');
  if (selector) {
    selector.destroy();
  }
}

function setExePath(path,caller) {
  console.log("Calling setExePath("+ path + "," + caller +")")
  const zone = ngZone();
  if(zone) {
    zone.run(() => {
      if(designer) {
        const datastore = designer.injector.get(DesignerDatastoreService);
        datastore.setSelectedFile(path,caller);
      } else if(editor) {
        const datastore = editor.injector.get(DesignerDatastoreService);
        datastore.setSelectedFile(path,caller);
      }
    });
  }
}

function changeResolution(resolution) {
  console.log(resolution)
}

function reloadAlyvixIde(objectName: string) {
  const zone = ngZone();
  if(zone) {
    zone.run(() => {
      console.log('reload editor ' + objectName);
      if(editor) {
        const service = editor.injector.get(EditorService);
        service.reloadObject(objectName);
      }
    });
  }
}

function reloadAlyvixSelector(objectName: string) {
  const zone = ngZone();
  if(zone) {
    zone.run(() => {
      console.log('reload selector ' + objectName);
      if (selector) {
        const selectorDatastore = selector.injector.get(SelectorDatastoreService);
        selectorDatastore.reload(objectName);
      }
    });
  }
}

function setRunState(state:string) {

  const zone = ngZone();
  if(zone) {
    zone.run(() => {
      console.log('set run state ' + state);
      if (editor) {
        const runnerService = editor.injector.get(RunnerService);
        runnerService.setState(state);
      }
    });
  }
}

function consoleAppendLine(line:string) {

  const zone = ngZone();
  if(zone) {
    zone.run(() => {
      console.log('consoleAppendLine ' + line);
      if (editor) {
        const service = editor.injector.get(EditorService);
        service.consoleAppendLine(line);
      }
    });
  }
}

function consoleAppendImage(image:string) {

  const zone = ngZone();
  if(zone) {
    zone.run(() => {
      console.log('consoleAppendImage ');
      if (editor) {
        const service = editor.injector.get(EditorService);
        service.consoleAppendImage(image);
      }
    });
  }
}

function consoleClear() {

  const zone = ngZone();
  if(zone) {
    zone.run(() => {
      console.log('consoleClear ' );
      if (editor) {
        const service = editor.injector.get(EditorService);
        service.consoleClear();
      }
    });
  }
}


(window as any).loadAlyvixEditor = loadAlyvixEditor;
(window as any).loadAlyvixDesigner = loadAlyvixDesigner;
(window as any).unloadAlyvixDesigner = unloadAlyvixDesigner;
(window as any).loadAlyvixSelector = loadAlyvixSelector;
(window as any).reloadAlyvixSelector = reloadAlyvixSelector;
(window as any).unloadAlyvixSelector = unloadAlyvixSelector;
(window as any).setExePath = setExePath;
(window as any).changeResolution = changeResolution;
(window as any).reloadAlyvixIde = reloadAlyvixIde;
(window as any).setRunState = setRunState;

(window as any).consoleAppendLine = consoleAppendLine;
(window as any).consoleAppendImage = consoleAppendImage;
(window as any).consoleClear = consoleClear;

(window as any).axModelMock =  function() {
  return AxModelMock.get();
};

(window as any).flagsMock =  function() {
  return AxModelMock.flags();
};


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
  } else if(environment.workingOn == "editor") {
    loadAlyvixEditor();
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


