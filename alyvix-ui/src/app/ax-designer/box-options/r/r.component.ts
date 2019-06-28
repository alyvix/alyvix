import { Component, OnInit, Input, Injectable, Inject  } from '@angular/core';
import { TreeNode } from '../../ax-designer-service';
import { R, WidthOrHeight, BoxListEntity } from 'src/app/ax-model/model';
import { GlobalRef, GroupsFlag } from "src/app/ax-model/ax-global";

import * as _ from 'lodash';


@Component({
  selector: 'ax-designer-r',
  templateUrl: './r.component.html',
  styleUrls: ['./r.component.css']
})
export class RComponent implements OnInit {

  constructor(@Inject('GlobalRef') private global: GlobalRef,) { }

  @Input()
  node: TreeNode


  box:R
  window:R
  button:R
  

  mode:R
  modes:R[]

  ngOnInit() {
    var widths = this.widths(this.node.box.w)
    var heights = this.heights(this.node.box.w,this.node.box.h)
    this.box = {width: widths[0], height: heights[0]}
    this.window = {width: widths[1], height: heights[1]}
    this.button = {width: widths[2], height: heights[2]}
    var modes = [this.box,this.window,this.button]
    this.mode = modes.find(x => _.isEqual(x,this.node.box.features.R))
    if(!this.mode) {
      var m = this.default(this.node.box)
      this.mode = m;
      this.node.box.features.R = m;
	}
	
	this.global.nativeGlobal().setTypeNode("R");
  }

  updateMode(event:R) {
    this.mode = event;
	this.node.box.features.R = event;
	this.global.nativeGlobal().setTypeNode("R");
  }

  default(rect:BoxListEntity):R {
    if(rect.w >= rect.h * 8 && rect.h >= 15 && rect.h <= 50) {
      return this.box
    } else if (rect.w >= 120 && rect.h >= 120) {
      return this.window
    } else {
      return this.button
    }
  }




  //BOX,WINDOW,BUTTON
  widths(w:number):WidthOrHeight[] {

    var min_w = w - 10;
    if (min_w < 4) min_w = 4;

    if(w >= 1200) {
      return [
        {"min":w - 800, "max":w + 900},
        {"min":w - 700, "max":w + 900},
        {"min":min_w, "max": w + 10}
      ]

    } else if(w >= 700) {
      return [
        {"min":w - 350, "max":w + 800},
        {"min":w - 400, "max":w + 850},
        {"min":min_w, "max": w + 10}
      ]
    } else if(w >= 300) {
      return [
        {"min":w - 140, "max":w + 500},
        {"min":w - 350, "max":w + 800},
        {"min":min_w, "max": w + 10}
      ]
    } else {
      return [
        {"min":w - 10, "max":w + 150},
        {"min":w - 80, "max":w + 300},
        {"min":min_w, "max":w + 10}
      ]
    }
  }

  //BOX,WINDOW,BUTTON
  heights(w:number,h:number):WidthOrHeight[] {

    var box:WidthOrHeight
    if (w >= 1200)
        box = {"min":h - 8, "max":h + 8};
    else if (w >= 700)
        box = {"min":h - 8, "max":h + 8};
    else if (w >= 300)
        box = {"min":h - 8, "max":h + 8};
    else
        box = {"min":h - 8, "max":h + 8};
  

    var window:WidthOrHeight
    if (h >= 1200)
        window = {"min":h - 700, "max": h + 900};
    else if (h >= 700)
        window = {"min":h - 400, "max": h + 850};
    else if (h >= 300)
        window = {"min":h - 350, "max": h + 800};
    else
        window = {"min":h - 80, "max": h + 300};

    var min_h = h - 10;            
    if (min_h < 4) min_h = 4;
    var button:WidthOrHeight =  {"min":min_h, "max":h + 10}

    return [box,window,button]

  }

}
