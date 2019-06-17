import { Component, OnInit, Input } from '@angular/core';
import { TreeNode } from '../../ax-designer-service';

@Component({
  selector: 'app-select-type',
  templateUrl: './select-type.component.html',
  styleUrls: ['./select-type.component.scss']
})
export class SelectTypeComponent implements OnInit {

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
