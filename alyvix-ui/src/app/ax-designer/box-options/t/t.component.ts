import { Component, OnInit, Input } from '@angular/core';
import { TreeNode } from '../../ax-designer-service';

@Component({
  selector: 'ax-designer-t',
  templateUrl: './t.component.html',
  styleUrls: ['./t.component.css']
})
export class TComponent implements OnInit {

  constructor() { }

  @Input()
  node: TreeNode

  ngOnInit() {
    if(!this.node.box.features.T.type) {
      this.node.box.features.T.type = "detection";
    }
  }

}
