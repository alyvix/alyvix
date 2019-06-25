import { Component, OnInit, Input } from '@angular/core';
import { TreeNode, AxDesignerService } from '../../ax-designer-service';

@Component({
  selector: 'ax-interaction',
  templateUrl: './interaction.component.html',
  styleUrls: ['./interaction.component.scss']
})
export class InteractionComponent implements OnInit {

  constructor(private axDesignerService:AxDesignerService) { }

  @Input()
  node: TreeNode
  
  interactionTypes = [
    {name: "None", value: null},
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
    this.axDesignerService.setPoint(this.node);
  }

  isPointAlreadySelected():boolean {
    return this.node.box.mouse.features.point.dx > 0 && this.node.box.mouse.features.point.dy > 0;
  }

  removePoint() {
    this.node.box.mouse.features.point.dx = 0;
    this.node.box.mouse.features.point.dy = 0;
    this.axDesignerService.updateAx();
  }

  pixelsChange() {
    if(this.node.box.mouse.features.pixels < 1)
      this.node.box.mouse.features.pixels = 1;
  }
  
  delayChange() {
    if(this.node.box.mouse.features.delays_ms < 1)
      this.node.box.mouse.features.delays_ms = 1;
  }

  amountChange() {
    console.log("amount change")
    if(this.node.box.mouse.features.amount < 1)
      this.node.box.mouse.features.amount = 1;
  }

  interactionChange() {

    //Pivotal #166603801 - `Delays [ms]`settings for `Click` and `Scroll` are different (i.e. toggle different last values)
    this.node.box.mouse.features.delays_ms = 100;
    

    switch(this.node.box.mouse.type) {
      case 'click': {
        if(!this.node.box.mouse.features.button) {
          this.node.box.mouse.features.button = "left"
        }
        //Pivotal #166603801 - Discussion with AP always to default
        this.node.box.mouse.features.amount = 1
        
        break;
      }
      case 'scroll': {
        //Pivotal #166603801 - Discussion with AP always to default
        this.node.box.mouse.features.direction = "down"
        this.node.box.mouse.features.amount = 1
        break;
      }
      case 'release': {
        //Pivotal #166603801 - Discussion with AP always to default
        this.node.box.mouse.features.direction = "down"
        if(!this.node.box.mouse.features.pixels) {
          this.node.box.mouse.features.pixels = 100
        }
        break;
      }
    }

    this.axDesignerService.updateAx();

  }

}
