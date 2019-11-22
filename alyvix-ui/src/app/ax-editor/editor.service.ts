import { Injectable } from '@angular/core';
import { SelectorDatastoreService } from '../ax-selector/selector-datastore.service';

@Injectable({
  providedIn: 'root'
})
export class EditorService {

  constructor(
    private selectorDatastore:SelectorDatastoreService
  ) { }

  designerFullscreen = false;

  private reloading = false;

  reloadObject(objectName:string) {
    if(!this.reloading && this.designerFullscreen) {
      this.reloading = true;
      console.log(objectName);
      this.selectorDatastore.reload(objectName);
      this.designerFullscreen = false;
      this.reloading = false;
    }
  }
}
