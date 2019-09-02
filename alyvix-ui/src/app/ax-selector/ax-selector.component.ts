import { Component, OnInit, ViewChild} from '@angular/core';
import { ResizedEvent } from 'angular-resize-event';
import { AxTableComponent } from './ax-table/ax-table.component';

@Component({
    selector: 'ax-selector',
    templateUrl: './ax-selector.component.html',
    styleUrls: ['./ax-selector.component.scss']
  })
  export class AxSelectorComponent implements OnInit {


    selectedTab = 1;

    ngOnInit(): void {

    }

    @ViewChild(AxTableComponent) table;
    onResized(event: ResizedEvent) {
      this.table.onResized(event);
    }

    selectTab(i) {
      this.selectedTab = i;
    }

  }
