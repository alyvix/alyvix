import { Component, OnInit, Input, ViewChildren, QueryList, ElementRef, ViewChild, AfterViewInit, DoCheck } from '@angular/core';
import { TreeNode } from '../../ax-designer-service';

@Component({
  selector: 'app-select-type',
  templateUrl: './select-type.component.html',
  styleUrls: ['./select-type.component.scss']
})
export class SelectTypeComponent implements OnInit,AfterViewInit {




  _node:TreeNode

  @Input()
  set node(node: TreeNode) {
    this.loading = true;
    this._node = node;
    this.ngAfterViewInit();
  }

  get node():TreeNode {
    return this._node;
  }

  loading:boolean = true;

  @ViewChild("iElement",{static:true}) iElement: ElementRef;
  @ViewChild("rElement",{static:true}) rElement: ElementRef;
  @ViewChild("tElement",{static:true}) tElement: ElementRef;

  changeType(event) {
    console.log(event.srcElement.value);
    this.node.box.type = event.srcElement.value;
  }


  constructor() { }




  ngOnInit() { }

  ngAfterViewInit() {

    switch(this.node.box.type) {
      case 'I': if(this.iElement) { this.iElement.nativeElement.focus(); } break;
      case 'R': if(this.rElement) { this.rElement.nativeElement.focus(); } break;
      case 'T': if(this.tElement) { this.tElement.nativeElement.focus(); } break;
    }
    this.loading = false;
  }

}
