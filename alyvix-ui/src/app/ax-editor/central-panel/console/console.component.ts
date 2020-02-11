import { Component, OnInit } from '@angular/core';
import { ConsoleElement, EditorService } from '../../editor.service';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-console',
  templateUrl: './console.component.html',
  styleUrls: ['./console.component.scss']
})
export class ConsoleComponent implements OnInit {

  consoleItems:ConsoleElement[]

  constructor(private editorService:EditorService,
    private _sanitizer: DomSanitizer,) { }

  imageFor(image) {
    return this._sanitizer.bypassSecurityTrustResourceUrl("data:image/png;base64," + image);
  }

  ngOnInit() {
    this.editorService.consoleElements().subscribe(i => this.consoleItems = i);
  }

}
