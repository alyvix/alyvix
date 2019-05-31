import { Component, OnInit, ViewChild, ElementRef, Inject } from '@angular/core';
import { AxModel, BoxListEntity } from '../ax-model/model';
import { AxDesignerService, TreeNode } from './ax-designer-service';
import { GlobalRef } from '../ax-model/ax-global';
import { ResizedEvent } from 'angular-resize-event';
import { TouchSequence } from 'selenium-webdriver';

@Component({
  selector: 'ax-designer',
  templateUrl: './ax-designer.component.html',
  styleUrls: ['./ax-designer.component.css']
})
export class AxDesignerComponent implements OnInit {

  constructor(private axDesignerService:AxDesignerService) { }

  axModel:AxModel;

  @ViewChild('pullDown') pullDown: ElementRef;
  @ViewChild('treeContainer') treeContainer: ElementRef;

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
    console.log(event)
    var i = this.axDesignerService.indexSelectedNode(this.selectedNode);
    if(i*this.treeElementHeight > (event.newHeight + this.treeContainer.nativeElement.scrollTop)) {
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
  }


  showAdd():boolean {


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

}
