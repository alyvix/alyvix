import { Component, OnInit, Inject } from '@angular/core';
import { EditorService, LeftSelection } from '../editor.service';
import { AxScriptFlow } from 'src/app/ax-model/model';
import { MapRowVM, SelectorDatastoreService } from 'src/app/ax-selector/selector-datastore.service';
import { EditorGlobal } from '../editor-global';
import { DesignerGlobal } from 'src/app/ax-designer/ax-global';
import { SelectorGlobal } from 'src/app/ax-selector/global';



@Component({
  selector: 'app-central-panel',
  templateUrl: './central-panel.component.html',
  styleUrls: ['./central-panel.component.scss']
})
export class CentralPanelComponent implements OnInit {

  monitorTab:LeftSelection = {name: 'Monitor', type:'monitor'};

  baseTabs: LeftSelection[] = [this.monitorTab];

  tabs: LeftSelection[] = this.baseTabs;

  selected: LeftSelection = this.tabs[0];



  constructor(
      private editorService:EditorService,
      private selectorDatastore: SelectorDatastoreService,
      @Inject('GlobalRefSelector') private global:SelectorGlobal
    ) {
  }

  ngOnInit() {
    this.editorService.getLeftSelection().subscribe(s => {
      if(s) {
        this.tabs = [s].concat(this.baseTabs);
        this.selected = s;
      }
    })

    this.selectorDatastore.getSelected().subscribe(s => {
      let isCurrentResolution = s && s.length > 0 && s.every(x => x.selectedResolution === this.global.res_string)
      console.log(s)
      console.log(isCurrentResolution)
      if(isCurrentResolution) {
        this.baseTabs = [this.monitorTab];
        if(!this.tabs.includes(this.monitorTab)) {
          this.tabs = this.tabs.concat(this.baseTabs);
        }
      } else {
        this.baseTabs = [];
        if(this.tabs.includes(this.monitorTab)) {
          this.tabs = this.tabs.filter(x => x.name !== this.monitorTab.name)
          if(this.selected.name === this.monitorTab.name && this.tabs[0]) {
            this.selected = this.tabs[0]
          }
        }
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
