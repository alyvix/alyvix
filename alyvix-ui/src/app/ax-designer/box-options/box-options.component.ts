import { Component, OnInit, Input } from '@angular/core';
import { BoxListEntity } from 'src/app/ax-model/model';
import { TreeNode } from '../ax-designer-service';

@Component({
  selector: 'ax-box-options',
  templateUrl: './box-options.component.html',
  styleUrls: ['./box-options.component.css']
})
export class BoxOptionsComponent implements OnInit {

  @Input()
  node: TreeNode

  changeType(event) {
    console.log(event.srcElement.value);
    this.node.box.type = event.srcElement.value;
  }

  constructor() { }

  ngOnInit() {
  }

}
