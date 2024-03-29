import { Component, OnInit, Inject, ViewChild, ElementRef } from '@angular/core';
import { DesignerGlobal } from 'src/app/ax-designer/ax-global';
import { EditorGlobal } from '../../editor-global';
import { DomSanitizer } from '@angular/platform-browser';
import { BoxListEntity } from 'src/app/ax-model/model';

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

  private fixDpi(n:number):number {
    return Math.floor(n / this.editorGlobal.scaling_factor * 100);
  }

  ngOnInit() {
    this.h = this.fixDpi(this.editorGlobal.res_h);
    this.w =this.fixDpi(this.editorGlobal.res_w);
    this.designerGlobal.background().subscribe(bg => {
      if(bg) {
        this._background = bg;
      }
    })
    this.editorGlobal.setCanvas(this.monitorCanvas.nativeElement);
    this.monitorCanvas.nativeElement.height = this.h;
    this.monitorCanvas.nativeElement.width = this.w;
    this.designerGlobal.axModel().subscribe(m => {
      const boxes = m ? m.box_list : null;
      this.designerGlobal.setRectangles(boxes);
    })


  }

  background() {
    return this._sanitizer.bypassSecurityTrustStyle("url("+this._background+")");
  }

}
