import { Component, OnInit, Input } from '@angular/core';
import { TreeNode, AxDesignerService } from '../../ax-designer-service';

@Component({
  selector: 'ax-interaction',
  templateUrl: './interaction.component.html',
  styleUrls: ['./interaction.component.css']
})
export class InteractionComponent implements OnInit {

  constructor(private axDesignerService:AxDesignerService) { }

  @Input()
  node: TreeNode
  
  interactionTypes = [
    {name: "None", value: "none"},
    {name: "Move", value: "move"},
    {name: "Click", value: "click"},
    {name: "Scroll", value: "scroll"},
    {name: "Hold", value: "hold"},
    {name: "Release", value: "release"}
  ]

  ngOnInit() {
    this.node.box.mouse.type
  }

  setPoint() {
    this.axDesignerService.setPoint(this.node)
  }

  setDefaults() {

    if(!this.node.box.mouse.features.delays_ms) {
      this.node.box.mouse.features.delays_ms = 100;
    }

    switch(this.node.box.mouse.type) {
      case 'click': {
        if(!this.node.box.mouse.features.button) {
          this.node.box.mouse.features.button = "left"
        }
        if(!this.node.box.mouse.features.amount) {
          this.node.box.mouse.features.amount = 1
        }
        break;
      }
      case 'scroll': {
        if(!this.node.box.mouse.features.direction) {
          this.node.box.mouse.features.direction = "down"
        }
        if(!this.node.box.mouse.features.amount) {
          this.node.box.mouse.features.amount = 1
        }
        break;
      }
      case 'release': {
        if(!this.node.box.mouse.features.direction) {
          this.node.box.mouse.features.direction = "down"
        }
        if(!this.node.box.mouse.features.pixels) {
          this.node.box.mouse.features.pixels = 100
        }
        break;
      }
    }
  }

}
