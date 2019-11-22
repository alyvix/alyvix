import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-central-panel',
  templateUrl: './central-panel.component.html',
  styleUrls: ['./central-panel.component.scss']
})
export class CentralPanelComponent implements OnInit {

  tabs = ['Script','Monitor'];

  selected = this.tabs[0];

  constructor() { }

  ngOnInit() {
  }

  selectTab(tab) {
    this.selected = tab;
  }

}
