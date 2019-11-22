import { Component, OnInit, Inject, ViewChild, ElementRef } from '@angular/core';
import { DesignerGlobal } from 'src/app/ax-designer/ax-global';
import { EditorGlobal } from '../../editor-global';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-monitor',
  templateUrl: './monitor.component.html',
  styleUrls: ['./monitor.component.scss']
})
export class MonitorComponent implements OnInit {

  constructor(
    @Inject('GlobalRefEditor') private editorGlobal: EditorGlobal,
    @Inject('GlobalRefDesigner') private designerGlobal: DesignerGlobal,
    private _sanitizer: DomSanitizer
  ) { }

  @ViewChild("monitorCanvas", {static: true}) monitorCanvas: ElementRef;


  h:number;
  w:number;

  _background:string;

  ngOnInit() {
    console.log("monitor on init");
    this.h = this.editorGlobal.res_h;
    this.w = this.editorGlobal.res_w;
    this.designerGlobal.background().subscribe(bg => {
      if(bg) {
        console.log(bg.length);
        this._background = bg;
      }
    })
    this.monitorCanvas.nativeElement.height = this.editorGlobal.res_h;
    this.monitorCanvas.nativeElement.width = this.editorGlobal.res_w;
    this.editorGlobal.setCanvas(this.monitorCanvas.nativeElement);
    this.designerGlobal.setRectangles();
  }

  background() {
    return this._sanitizer.bypassSecurityTrustStyle("url("+this._background+")");
  }

}
