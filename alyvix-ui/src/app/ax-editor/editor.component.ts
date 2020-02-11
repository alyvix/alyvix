import { Component, OnInit, ViewChild, ElementRef, Inject, ChangeDetectorRef } from '@angular/core';
import { DesignerGlobal } from '../ax-designer/ax-global';
import { SelectorDatastoreService } from '../ax-selector/selector-datastore.service';
import { NgProgressComponent } from '@ngx-progressbar/core';
import { AlyvixApiService } from '../alyvix-api.service';
import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';

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
  designerWidth = 420;
  leftWidth:number;

  objectCollapsed = false;
  designerCollapsed = false;

  @ViewChild(NgProgressComponent, {static: true}) progressBar: NgProgressComponent;

  constructor(
    @Inject('GlobalRefDesigner') private global: DesignerGlobal,
    private selectorDatastore:SelectorDatastoreService,
    private changeDetector: ChangeDetectorRef,
    private apiService:AlyvixApiService
    ) { }

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
      this.lastSelectorHeight = this.selectorHeight;
      this.selectorDatastore.setSelectorHidden(false);
    } else if(this.containerHeight() - (event.info.evt.clientY - this.containerTop()) < 100) {
      this.selectorDatastore.setSelectorHidden(true);
    }
  }

  lastSelectorHeight = 300;
  setSelectorShow(hidden:boolean) {
    if(hidden) {
      this.lastSelectorHeight = this.selectorHeight;
      this.topLeftHeight = this.containerHeight()-18;
      this.selectorHeight = 18;
    } else if (this.selectorHeight == 18) {
      const newHeight = Math.max(300,this.lastSelectorHeight);
      this.topLeftHeight = this.containerHeight()-newHeight;
      this.selectorHeight = newHeight;
    }
  }



  resizingVertical(event) {
    if(event.info.evt.clientX > 300) {
      this.objectsWidth = event.info.evt.clientX;
      this.objectCollapsed = false;
    } else if(event.info.evt.clientX < 18) {
      this.objectsWidth = 0;
      this.objectCollapsed = true;
    } else {
      this.objectsWidth = 300;
      this.objectCollapsed = false;
    }
  }

  toggleDesigner() {
    this.designerCollapsed = !this.designerCollapsed;
    if(this.designerCollapsed) {
      this.leftWidth = this.container.nativeElement.offsetWidth
    } else {
      this.leftWidth = this.container.nativeElement.offsetWidth  - this.designerWidth
    }
  }

  savedWidthObjects = 300;
  toggleObjects() {
    this.objectCollapsed = !this.objectCollapsed;
    if(this.objectCollapsed) {
      this.savedWidthObjects = this.objectsWidth;
      this.objectsWidth = 0;
    } else {
      this.objectsWidth = this.savedWidthObjects;
    }
  }

  hasDesigner = false;

  ngOnInit() {

    this.global.axModel().subscribe(model => {
      this.hasDesigner = model ? true : false;
      this.changeDetector.markForCheck();
    });
    this.resize();

    this.apiService.startLoading.subscribe( x => this.progressBar.start())
    this.apiService.endLoading.subscribe(x => this.progressBar.complete())

  }

  private resize() {
    this.topLeftHeight = this.container.nativeElement.offsetHeight - 300;
    if(this.designerCollapsed) {
      this.leftWidth = this.container.nativeElement.offsetWidth
    } else {
      this.leftWidth = this.container.nativeElement.offsetWidth  - this.designerWidth
    }
    this.selectorDatastore.getSelectorHidden().subscribe(hidden => this.setSelectorShow(hidden));
  }

  onResized(event) {
    this.resize();
  }

}
