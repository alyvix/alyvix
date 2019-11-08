import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.scss']
})
export class EditorComponent implements OnInit {

  @ViewChild("container", {static: true}) container: ElementRef;

  selectorHeight = 300;
  topLeftHeight = 50;


  constructor() { }

  containerHeight():number {
    return this.container.nativeElement.clientHeight;
  }

  containerTop():number {
    return this.container.nativeElement.offsetTop;
  }

  resizing(event) {
    if(this.containerHeight() - (event.info.evt.clientY - this.containerTop()) > 300 && (event.info.evt.clientY - this.containerTop()) > 150) {
      this.topLeftHeight = event.info.evt.clientY - this.containerTop();
      this.selectorHeight = this.containerHeight() - this.topLeftHeight;
    }
  }

  ngOnInit() {
    this.topLeftHeight = this.container.nativeElement.offsetHeight - 300
  }

}
