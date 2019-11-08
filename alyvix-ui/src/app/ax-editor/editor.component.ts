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
  objectsWidth = 300;

  objectCollapsed = false;

  constructor() { }

  containerHeight():number {
    return this.container.nativeElement.clientHeight;
  }

  containerTop():number {
    return this.container.nativeElement.offsetTop;
  }

  expandObjects() {
    this.objectsWidth = 300;
    this.objectCollapsed = false;
  }

  resizing(event) {
    if(this.containerHeight() - (event.info.evt.clientY - this.containerTop()) > 300 && (event.info.evt.clientY - this.containerTop()) > 150) {
      this.topLeftHeight = event.info.evt.clientY - this.containerTop();
      this.selectorHeight = this.containerHeight() - this.topLeftHeight;
    } else if(this.containerHeight() - (event.info.evt.clientY - this.containerTop()) < 100) {
      this.topLeftHeight = this.containerHeight()-18;
      this.selectorHeight = 18;
    }
  }

  resizingVertical(event) {
    if(event.info.evt.clientX > 300) {
      this.objectsWidth = event.info.evt.clientX;
      this.objectCollapsed = false;
    } else if(event.info.evt.clientX < 18) {
      this.objectsWidth = 18;
      this.objectCollapsed = true;
    } else {
      this.objectsWidth = 300;
      this.objectCollapsed = false;
    }
  }

  ngOnInit() {
    this.topLeftHeight = this.container.nativeElement.offsetHeight - 300
  }

}
