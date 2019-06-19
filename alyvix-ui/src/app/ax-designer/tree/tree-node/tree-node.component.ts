import { Component, OnInit, Input, Output, EventEmitter, ViewChild, ElementRef } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { AxDesignerService, TreeNode } from '../../ax-designer-service';
import { environment } from 'src/environments/environment';

export interface GroupColors{
  main:string
  selected:string
  thumbnail:string
}

@Component({
  selector: 'ax-tree-node',
  templateUrl: './tree-node.component.html',
  styleUrls: ['./tree-node.component.scss']
})
export class TreeNodeComponent implements OnInit {

  constructor(private _sanitizer: DomSanitizer, private axDesignerService:AxDesignerService) { }

  @Input()
  node:TreeNode;

  selectedNode:TreeNode;

  thumbnailWidth:number = 0;

  @ViewChild("canvas") canvas: ElementRef;

  icon(type) {
    switch(type) {
      case 'I': return ['far','fa-image'] 
      case 'R': return ['fas','fa-expand'] 
      case 'T': return ['fas','fa-font'] 
    }
  }

  ngOnInit() {

    console.log("Init component TreeNode")
    this.axDesignerService.getSelectedNode().subscribe(n => this.selectedNode = n);
    if(this.node.box) {
      this.thumbnailWidth = this.node.box.thumbnail.image_w;
      var ctx = this.canvas.nativeElement.getContext("2d");
      var image = new Image();
      var self = this;
      image.onload = function() {

        //TODO use https://github.com/waveinch/alyvix/blob/bd2f1527aadc9a6892afd00be54546d6a5536ff4/alyvix/ide/server/templates/drawing.html#L1788
        var dpi = window.devicePixelRatio || 1;
        ctx.drawImage(image, 0, 0);
        var t = self.node.box.thumbnail;
        ctx.rect(t.x, t.y, t.w, t.h);
        ctx.strokeStyle = self.groupColor(self.node.box.group);
        ctx.translate(0.5,0.5);
        ctx.lineWidth = 1;
        ctx.stroke();


        ctx.scale(dpi, dpi);
        ctx.translate(0.5, 0.5);
        ctx.lineWidth = 1;
        ctx.strokeStyle = self.groupColor(self.node.box.group).thumbnail;
        ctx.strokeRect(t.x, t.y, t.w, t.h);

        
      };
      image.src = this.node.image;
    }
  }

  imageFor() {
    return this._sanitizer.bypassSecurityTrustResourceUrl(this.node.image);
  }



  groupColor(group:number):GroupColors {
    switch(group) {
      case 0: return {main: "#ff00ff", thumbnail: "#ff0000", selected: "#85008E"}
      case 1: return {main: "#00bc00", thumbnail: "#009500", selected: "#005000"}
      case 2: return {main: "#0072ff", thumbnail: "#0000ff", selected: "#001D8E"}
    }
  }


  isSelected():boolean {
    return this.node == this.selectedNode;
  }

  

  setBackground() {
    if(this.node.box) {
      if(this.isSelected()) {
        return {"background-color": this.groupColor(this.node.box.group).selected}
      } else {
         return {"background-color": this.groupColor(this.node.box.group).main}
      }
    }
  }

  nodeClick() {
    this.axDesignerService.setSelectedNode(this.node);
  }

  leafTypes = ['I','R','T'];
  primaryTypes = ['I','R'];
  nextType(main:boolean, t:string):string {
    var types = []
    if(main){
      types = this.primaryTypes;
    } else {
      types = this.leafTypes;
    }
    var i = (types.indexOf(t) + 1) % types.length;
    console.log(i);
    return types[i];
  }

  doubleClick() {
    if(this.node.box) {
      this.node.box.type = this.nextType(this.node.box.is_main,this.node.box.type)
    }
  }


  private _interactionIconClick():string {
    if(this.node.box.mouse.features) {
      if (this.node.box.mouse.features.amount >= 2)
        if(this.node.box.mouse.features.button == 'left')
          return "Mouse_32px4";
        else
          return "Mouse_32px4_2"      
      else
        if(this.node.box.mouse.features.button == 'left')
          return "Mouse_32px2";  
        else
          return "Mouse_32px3";
    } else {
      return null
    }
  }

  private _interactionIconScroll():string {
    if(this.node.box.mouse.features) {
      switch(this.node.box.mouse.features.direction) {
        case 'up': return "Mouse_32px6"
        case 'left': return "Mouse_32px8"
        case 'right': return "Mouse_32px9"
        case 'down': return "Mouse_32px7"
      } 
    } else {
      return null;
    }
    
  }

  private _interactionIconRelease():string {
    if(this.node.box.mouse.features) {
      switch(this.node.box.mouse.features.direction) {
        case 'up': return "Mouse_32px13"
        case 'left': return "Mouse_32px15"
        case 'right': return "Mouse_32px16"
        case 'down': return "Mouse_32px14"
        default: return "Mouse_32px12"
      }
    }
    return null;
  }

  private _interactionMouseIcon():string {
    if(this.node.box) {
      if(this.node.box.mouse) {
        switch(this.node.box.mouse.type) {
          case 'move': return "Mouse_32px"
          case 'click': return this._interactionIconClick()
          case 'scroll': return this._interactionIconScroll()
          case 'hold': return "Mouse_32px10"
          case 'release': return this._interactionIconRelease()
        }
      }
    }
    return null;
  }

  private _interactionKeyboardIcon():string {
    if(this.node.box) {
      if(this.node.box.keyboard) {
        if(this.node.box.keyboard.string.match(/\{(\d+)\}/)) {
          return "Keyboard_32px6"
        }
        if(this.node.box.keyboard.string) {
          return "Keyboard_32px"
        }
      }
    }
    return null
  }

  private _icon(icon:string):string {
    if(icon) {
      return environment.assets + "/static/img/icons/1x/190123_Alyvix_"+icon+".png"
    }
    return null;
  }

  interactionMouseIcon() {
    return this._icon(this._interactionMouseIcon());
  }

  interactionKeyboardIcon() {
    return this._icon(this._interactionKeyboardIcon());
  }


}
