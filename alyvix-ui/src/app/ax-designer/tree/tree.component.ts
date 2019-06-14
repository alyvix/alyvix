import { Component, OnInit, Input, ViewChild } from '@angular/core';
import { BoxListEntity } from 'src/app/ax-model/model';
import { CdkDragDrop, moveItemInArray, CdkDrag, CdkDragStart, DropListRef } from '@angular/cdk/drag-drop';
import { AxDesignerService, TreeNode } from '../ax-designer-service';
import { ContextMenuComponent } from 'ngx-contextmenu';



@Component({
  selector: 'ax-designer-tree',
  templateUrl: './tree.component.html',
  styleUrls: ['./tree.component.css']
})
export class TreeComponent implements OnInit {

  constructor(public axDesignerService:AxDesignerService) { }


  root:TreeNode
  options = {};

  



  

  ngOnInit() {

    this.axDesignerService.getRoot().subscribe(r => {
      this.root = r
      console.log("new root")
      console.log(r);
    });

  }

  dropPrimary(list:TreeNode[],event: CdkDragDrop<TreeNode>) {
    this.drop(list,event);
    list.forEach((node,group) => {
      if(node.box) {
        node.box.group = group;
      }
      if(node.children) {
        node.children.forEach(subnodes => {
          if(subnodes.box) {
            subnodes.box.group = group;
          }
        })
      }
    })
    this.axDesignerService.updateAx()
  }


  drop(list:TreeNode[],event: CdkDragDrop<TreeNode>) {
    console.log(event);
    moveItemInArray(list, event.previousIndex, event.currentIndex);
    list.forEach(x => x.last = false);
    list[list.length - 1].last = true;
    this.axDesignerService.setDragging(false);
    this.axDesignerService.updateAx()
  }

  startDrag(list:TreeNode[],node:TreeNode,event:CdkDragStart) {
    var others = list.filter(x => x != node)
    console.log(others)
    others.forEach(x => x.last = false);
    var last = others.slice(-1)[0];
    if(last) last.last = true;
    this.axDesignerService.setSelectedNode(node);
    this.axDesignerService.setDragging(true);
  }

  enableNewGroupComponent(axDesignerService){ return function(item) {
    if(item) {
      return !axDesignerService.isGroupFull(item.box.group)
    }
    return false;
  }}

  onContextMenu($event: MouseEvent, item: TreeNode): void {
    this.axDesignerService.setSelectedNode(item);
  }


  @ViewChild("mainContextMenu") public mainContextMenu: ContextMenuComponent;

  @ViewChild("childContextMenu") public childContextMenu: ContextMenuComponent;

}
