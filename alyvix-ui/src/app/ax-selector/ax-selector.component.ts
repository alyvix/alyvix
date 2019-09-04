import { Component, OnInit, ViewChild} from '@angular/core';
import { ResizedEvent } from 'angular-resize-event';
import { AxTableComponent } from './ax-table/ax-table.component';
import { environment } from 'src/environments/environment';

@Component({
    selector: 'ax-selector',
    templateUrl: './ax-selector.component.html',
    styleUrls: ['./ax-selector.component.scss']
  })
  export class AxSelectorComponent implements OnInit {


    selectedTab = 1;

    ngOnInit(): void {

    }

    production:boolean = environment.production;


    @ViewChild(AxTableComponent) table;
    onResized(event: ResizedEvent) {
      this.table.onResized(event);
    }

    selectTab(i) {
      this.selectedTab = i;
    }

  }
