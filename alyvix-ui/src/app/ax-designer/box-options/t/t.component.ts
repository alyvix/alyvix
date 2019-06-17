import { Component, OnInit, Input, ViewChild } from '@angular/core';
import { TreeNode } from '../../ax-designer-service';
import { FormControl } from '@angular/forms';

@Component({
  selector: 'ax-designer-t',
  templateUrl: './t.component.html',
  styleUrls: ['./t.component.css']
})
export class TComponent implements OnInit {

  constructor() { }

  @Input()
  node: TreeNode

  regex:FormControl = new FormControl('', this.checkRegex);

  checkRegex(control: FormControl) {
    console.log("check")
    let regexp = control.value;
    try {
        new RegExp(regexp);
    } catch(e) {
        return {
          regexp: {
            invalidRegexp: regexp
          }
        }
    }
    return null;
  }

  ngOnInit() {

    if(!this.node.box.features.T.type) {
      this.node.box.features.T.type = "detection";
    }
  }

}
