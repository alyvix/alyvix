import { Component, OnInit, Input, Injectable, Inject  } from '@angular/core';
import { TreeNode } from '../../ax-designer-service';
import { R, WidthOrHeight, BoxListEntity } from 'src/app/ax-model/model';
import { DesignerGlobal, GroupsFlag, RectType } from "src/app/ax-designer/ax-global";

import * as _ from 'lodash';


@Component({
  selector: 'ax-designer-r',
  templateUrl: './r.component.html',
  styleUrls: ['./r.component.css']
})
export class RComponent implements OnInit {

  constructor(@Inject('GlobalRefDesigner') private global: DesignerGlobal,) { }

  _node:TreeNode

  @Input()
  set node(node: TreeNode) {
    this._node = node;
    this.onNodeChange();
  }

  get node():TreeNode {
    return this._node;
  }

  mode:RectType


  ngOnInit() {

  }

  onNodeChange() {
    this.mode = this.global.get_rect_type(this.node.box);
	  //this.global.setTypeNode("R");
  }

  updateMode(event:RectType) {
    //this.global.setTypeNode("R");
    this.global.set_rect_type(event,this.node.box);
    this.mode = event;
  }



}
