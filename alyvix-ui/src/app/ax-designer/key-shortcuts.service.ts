import { Injectable } from '@angular/core';
import { AxDesignerService, TreeNode } from './ax-designer-service';
import { Hotkey, HotkeysService } from 'angular2-hotkeys';

@Injectable({
  providedIn: 'root'
})
export class KeyShortcutsService {

  node: TreeNode;

  constructor(private axDesignerService: AxDesignerService, private _hotkeysService: HotkeysService) {
  }


  loadShortcuts() {


    this.axDesignerService.getSelectedNode().subscribe(x => {
      this.node = x
    });


    this._hotkeysService.add(new Hotkey('enter', (event: KeyboardEvent): boolean => { //#166602167
      this.save()
      return false; // Prevent bubbling
    }, undefined, 'Save and close'));

    this._hotkeysService.add(new Hotkey('esc', (event: KeyboardEvent): boolean => { //#166602167
      this.cancel()
      return false; // Prevent bubbling
    }, undefined, 'Cancel'));

    this._hotkeysService.add(new Hotkey('ctrl+x', (event: KeyboardEvent): boolean => {
      event.preventDefault();
      this.remove();
      return false; // Prevent bubbling
    }, undefined, 'Remove elements/group/component'));

    this._hotkeysService.add(new Hotkey('ctrl+d', (event: KeyboardEvent): boolean => {
      event.preventDefault();
      this.duplicate()
      return false; // Prevent bubbling
    }, undefined, 'Duplicate selected group/component'));

    this._hotkeysService.add(new Hotkey('ctrl+i', (event: KeyboardEvent): boolean => {
      event.preventDefault();
      this.setAs('I')
      return false; // Prevent bubbling
    }, undefined, 'Detect as Image'));

    this._hotkeysService.add(new Hotkey('ctrl+r', (event: KeyboardEvent): boolean => {
      event.preventDefault();
      this.setAs('R')
      return false; // Prevent bubbling
    }, undefined, 'Detect as Rectangle'));

    this._hotkeysService.add(new Hotkey('ctrl+t', (event: KeyboardEvent): boolean => {
      event.preventDefault();
      this.setAs('T')
      return false; // Prevent bubbling
    }, undefined, 'Detect as Text'));

    this._hotkeysService.add(new Hotkey('ctrl+m', (event: KeyboardEvent): boolean => {
      event.preventDefault();
      this.setAsMain()
      return false; // Prevent bubbling
    }, undefined, 'Set as main'));

    this._hotkeysService.add(new Hotkey('ctrl+n', (event: KeyboardEvent): boolean => {
      event.preventDefault();
      this.newComponent()
      return false; // Prevent bubbling
    }, undefined, 'New component'));
  }

  private save() {
    this.axDesignerService.save()
  }
  
  private cancel() {
    this.axDesignerService.cancel()
  }

  private remove() {
      if (!this.node) return false;
      if (!this.node.box) {
        this.axDesignerService.removeAll()
      } else if (this.node.box.is_main) {
        this.axDesignerService.removeGroup(this.node)
      } else {
        this.axDesignerService.removeComponent(this.node)
      }
  }

  private duplicate() {
    if (this.node && this.node.box) {
      if (this.node.box.is_main) {
        this.axDesignerService.duplicateGroup(this.node)
      } else {
        this.axDesignerService.duplicateComponent(this.node)
      }
    }
  }

  private setAsMain() {
    if (this.node && this.node.box && !this.node.box.is_main) {
      this.axDesignerService.setAsMain(this.node)
    }
  }

  private setAs(t:string) {
    if (this.node && this.node.box && (!this.node.box.is_main || t != 'T')) {
      this.axDesignerService.detectAs(t, this.node)
    }
  }

  private newComponent() {
    if (this.node)
        this.axDesignerService.newComponent(this.node)
  }

 
}
