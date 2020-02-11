import { Component, OnInit, Input } from '@angular/core';
import { BoxListEntity } from 'src/app/ax-model/model';
import { TreeNode } from '../ax-designer-service';

@Component({
  selector: 'ax-box-options',
  templateUrl: './box-options.component.html',
  styleUrls: ['./box-options.component.scss']
})
export class BoxOptionsComponent implements OnInit {

  @Input()
  node: TreeNode

  constructor() { }

  ngOnInit() {
  }

}
