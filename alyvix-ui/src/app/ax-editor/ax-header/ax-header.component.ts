import { Component, OnInit, Inject } from '@angular/core';
import { SelectorGlobal } from 'src/app/ax-selector/global';
import { EditorService } from '../editor.service';
import { SelectorDatastoreService } from 'src/app/ax-selector/selector-datastore.service';
import { AlyvixApiService } from 'src/app/alyvix-api.service';

@Component({
  selector: 'ax-header',
  templateUrl: './ax-header.component.html',
  styleUrls: ['./ax-header.component.scss']
})
export class AxHeaderComponent implements OnInit {

  constructor(@Inject('GlobalRefSelector') private global: SelectorGlobal,
    private editorService:EditorService,
    private api:AlyvixApiService
  ) { }

  name:string;

  ngOnInit() {
    this.name = this.global.current_library_name;
  }

  save() {
    this.editorService.save().subscribe(x => this.api.saveAll(false));
  }

}
