import { Component, OnInit, ViewChild, ElementRef, Inject } from '@angular/core';
import { AxModel, BoxListEntity } from '../ax-model/model';
import { AxDesignerService, TreeNode } from './ax-designer-service';
import { GlobalRef } from './ax-global';
import { ResizedEvent } from 'angular-resize-event';
import { TouchSequence } from 'selenium-webdriver';
import { KeyShortcutsService } from './key-shortcuts.service';
import { FormControl, Validators } from '@angular/forms';

@Component({
  selector: 'ax-designer',
  templateUrl: './ax-designer.component.html',
  styleUrls: ['./ax-designer.component.scss']
})
export class AxDesignerComponent implements OnInit {

  constructor(private axDesignerService:AxDesignerService, private keyShortcuts:KeyShortcutsService) { }

  axModel:AxModel;

  @ViewChild('pullDown') pullDown: ElementRef;
  @ViewChild('treeContainer') treeContainer: ElementRef;

  @ViewChild("first") first: ElementRef;
  // object_name: FormControl = new FormControl('', [
  //   Validators.required
  //   Validators.
  // ]);

  bottomWithoutOptions = 72;
  totalHeight = 590;
  treeElementHeight = 43;

  treeHeight() {

    var topHeight = 106;
    
    var bottomHeight = this.bottomWithoutOptions; 
    if(!this.selectedNode || this.selectedNode.box && !this.hideOptionsOnDrag()) {
      bottomHeight = this.pullDown.nativeElement.offsetHeight;
    }
    var height = this.totalHeight - topHeight - bottomHeight;

    return {"height.px": height, "overflow-y": "auto", "overflow-x": "hidden" }
  }

  onResized(event: ResizedEvent) {
    this.totalHeight = event.newHeight;
  }


  treeResize(event:ResizedEvent) {
    this.scrollToNode()
  }

  scrollToNode() {
    var i = this.axDesignerService.indexSelectedNode(this.selectedNode);

    var visibleUntil = this.treeContainer.nativeElement.offsetHeight  + this.treeContainer.nativeElement.scrollTop

    if(i*this.treeElementHeight > visibleUntil) {
      this.treeContainer.nativeElement.scrollTop = i*this.treeElementHeight + 50;
    }
  }

  hideOptionsOnDrag():boolean {
    return this.dragging && (this.selectedNode.box && this.selectedNode.box.is_main)
  }

  selectedNode:TreeNode
  dragging:boolean = false;

  selectNode(n:TreeNode) {
    this.selectedNode = n;
  }

  ngOnInit() {
    this.axDesignerService.getSelectedNode().subscribe(n => this.selectNode(n));
    this.axDesignerService.getDragging().subscribe(d => this.dragging = d);
    this.axModel = this.axDesignerService.getModel();
    this.first.nativeElement.focus();
    this.scrollToNode();
  }
  


  showAdd():boolean {

    //#166602599
    //`Add` button enable when screen component is selected (and disabled if the 3 groups already exist)
    if(!this.selectedNode.box) { //screen
      return this.selectedNode.children && this.selectedNode.children.length < 3;
    }

    if(this.selectedNode && this.selectedNode.box) {
      return !this.axDesignerService.isGroupFull(this.selectedNode.box.group)
    } else {
      if(this.selectedNode && this.selectedNode.children) {
        return !this.selectedNode.children.every(n => this.axDesignerService.isGroupFull(n.box.group))
      }
    }

    return false;
  }

  add() {
    this.axDesignerService.newComponent(this.selectedNode)
  }

  save() {
    this.axDesignerService.save();
  }

  cancel() {
    this.axDesignerService.cancel()
  }

  onContextMenu() { //#166602599
    return false;
  }

  changeTimeout() {
    if(this.axModel.detection.timeout_s < 1) {
      this.axModel.detection.timeout_s = 1
    }
  }

}
