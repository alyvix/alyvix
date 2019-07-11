import { Component, OnInit, Input, Injectable, Inject  } from '@angular/core';
import { TreeNode } from '../../ax-designer-service';
import { I } from 'src/app/ax-model/model';
import { GlobalRef, GroupsFlag } from "src/app/ax-model/ax-global";

import * as fastDeepEqual from 'fast-deep-equal';



@Component({
  selector: 'ax-designer-i',
  templateUrl: './i.component.html',
  styleUrls: ['./i.component.css']
})
export class IComponent implements OnInit {

  constructor(@Inject('GlobalRef') private global: GlobalRef,) { }

  _node:TreeNode

  @Input()
  set node(node: TreeNode) {
    this._node = node;
    this.onNodeChange();
  }

  get node():TreeNode {
    return this._node;
  }


  mode:I

  
  match:I = {'colors': true, 'likelihood': 0.9}
  color:I = {'colors': true, 'likelihood': 0.7}
  shape:I = {'colors': false, 'likelihood': 0.7}
  modes:I[] = [this.match,this.color,this.shape]

  updateMode(event) {
    this.mode = event;
    this.node.box.features.I = event;
  }

  ngOnInit() {}

  onNodeChange() {
    this.mode = this.modes.find(x => fastDeepEqual(x,this.node.box.features.I))
    if(!this.mode) {
      this.mode = this.match;
      this.node.box.features.I = this.match;
    }
    this.global.nativeGlobal().setTypeNode("I");
    console.log(this.mode)
  }

}
