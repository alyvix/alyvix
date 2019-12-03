import { Component, OnInit, Inject } from '@angular/core';
import { SelectorGlobal } from 'src/app/ax-selector/global';

@Component({
  selector: 'ax-header',
  templateUrl: './ax-header.component.html',
  styleUrls: ['./ax-header.component.scss']
})
export class AxHeaderComponent implements OnInit {

  constructor(@Inject('GlobalRefSelector') private global: SelectorGlobal) { }

  name:string;

  ngOnInit() {
    this.name = this.global.current_library_name;
  }

}
