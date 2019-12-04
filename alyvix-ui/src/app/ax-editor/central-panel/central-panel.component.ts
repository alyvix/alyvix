import { Component, OnInit } from '@angular/core';
import { EditorService, LeftSelection } from '../editor.service';
import { AxScriptFlow } from 'src/app/ax-model/model';
import { MapRowVM } from 'src/app/ax-selector/selector-datastore.service';



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

  scriptChanged(flow:AxScriptFlow[]) {
    if (this.selected.onChangeSteps) {
      this.selected.onChangeSteps(flow);
    }
  }

  mapChanged(map:MapRowVM[]) {
    if(this.selected.onChangeMap) {
      this.selected.onChangeMap(map);
    }
  }

}
