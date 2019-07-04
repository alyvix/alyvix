import { Component, OnInit, Input, ChangeDetectorRef } from '@angular/core';
import { TreeNode, AxDesignerService } from '../../ax-designer-service';
import { Mouse, Point } from 'src/app/ax-model/model';
import * as _ from 'lodash';

@Component({
  selector: 'ax-interaction',
  templateUrl: './interaction.component.html',
  styleUrls: ['./interaction.component.scss']
})
export class InteractionComponent implements OnInit {

  constructor(private axDesignerService:AxDesignerService, private cdRef:ChangeDetectorRef) { }

  private _node:TreeNode


  @Input()
  set node(node: TreeNode) {
    Promise.resolve(null).then(() => { // enqueque after change detection loop to avoid ExpressionChangedAfterItHasBeenCheckedError
      console.log("interaction init")
    
      if(!node.box.mouse_keep_options) {
        node.box.mouse_keep_options = [];
      }
      if(!node.box.mouse) {
        node.box.mouse = {
          features: {
            point: {
              dx: 0, dy:0
            }
          }
        }
      }

      this.addToKeepOptions(node)

      this._node = node;
    });
    
    
    
  }

  
  interactionTypes = [
    {name: "None", value: null},
    {name: "Move", value: "move"},
    {name: "Click", value: "click"},
    {name: "Scroll", value: "scroll"},
    {name: "Hold", value: "hold"},
    {name: "Release", value: "release"}
  ]

  ngOnInit() {
  }
   

  setPoint() {
    this.axDesignerService.setPoint(this._node);
  }

  isPointAlreadySelected():boolean {
    return this._node.box.mouse.features.point.dx > 0 && this._node.box.mouse.features.point.dy > 0;
  }

  removePoint() {
    this._node.box.mouse.features.point.dx = 0;
    this._node.box.mouse.features.point.dy = 0;
    this.axDesignerService.updateAx();
  }

  pixelsChange() {
    if(this._node.box.mouse.features.pixels < 1)
      this._node.box.mouse.features.pixels = 1;
  }
  
  delayChange() {
    if(this._node.box.mouse.features.delays_ms < 1)
      this._node.box.mouse.features.delays_ms = 1;
  }

  amountChange() {
    console.log("amount change")
    if(this._node.box.mouse.features.amount < 1)
      this._node.box.mouse.features.amount = 1;
  }

  private addToKeepOptions(node:TreeNode) {
    node.box.mouse_keep_options = node.box.mouse_keep_options.filter(x => x.type != node.box.mouse.type)
    node.box.mouse_keep_options.push(_.cloneDeep(node.box.mouse))
  }

  interactionChange(type:string) {
    this.addToKeepOptions(this._node)
    var mouse = this._node.box.mouse_keep_options.find(x => x.type == type)
    if(!mouse) {
      mouse = this.defaults(type)
    }
    this._node.box.mouse = mouse;
    this.axDesignerService.updateAx();
  }

  defaults(type:string):Mouse {

    var mouse:Mouse = {
      type: type,
      features: {
        point: {dx: 0, dy:0}
      }
    }
    //Pivotal #166603801 - `Delays [ms]`settings for `Click` and `Scroll` are different (i.e. toggle different last values)
    mouse.features.delays_ms = 100;
    

    switch(type) {
      case 'click': {
        if(!mouse.features.button) {
          mouse.features.button = "left"
        }
        //Pivotal #166603801 - Discussion with AP always to default
        mouse.features.amount = 1
        
        break;
      }
      case 'scroll': {
        //Pivotal #166603801 - Discussion with AP always to default
        mouse.features.direction = "down"
        mouse.features.amount = 1
        break;
      }
      case 'release': {
        //Pivotal #166603801 - Discussion with AP always to default
        mouse.features.direction = "none"
        if(!this._node.box.mouse.features.pixels) {
          mouse.features.pixels = 100
        }
        break;
      }
    }

    return mouse;

  }

}
