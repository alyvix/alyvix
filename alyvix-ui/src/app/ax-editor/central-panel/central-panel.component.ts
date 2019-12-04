import { Component, OnInit } from '@angular/core';
import { EditorService, LeftSelection } from '../editor.service';



@Component({
  selector: 'app-central-panel',
  templateUrl: './central-panel.component.html',
  styleUrls: ['./central-panel.component.scss']
})
export class CentralPanelComponent implements OnInit {

  baseTabs: LeftSelection[] = [{name: 'Monitor', type:'monitor'}];

  tabs: LeftSelection[] = this.baseTabs;

  selected: LeftSelection = this.tabs[0];


  constructor(private editorService:EditorService) {
  }

  ngOnInit() {
    this.editorService.getLeftSelection().subscribe(s => {
      if(s) {
        this.tabs = [s].concat(this.baseTabs);
        this.selected = s;
      }
    })
  }

  selectTab(tab:LeftSelection) {
    this.selected = tab;
  }

  isSelectedTab(tab:LeftSelection):boolean {
    return this.selected.name === tab.name;
  }

}
