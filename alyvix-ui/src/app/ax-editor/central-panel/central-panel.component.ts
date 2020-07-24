import { Component, OnInit, Inject, EventEmitter } from '@angular/core';
import { EditorService, LeftSelection } from '../editor.service';
import { AxScriptFlow } from 'src/app/ax-model/model';
import { MapRowVM, SelectorDatastoreService, MapsVM } from 'src/app/ax-selector/selector-datastore.service';
import { EditorGlobal } from '../editor-global';
import { DesignerGlobal } from 'src/app/ax-designer/ax-global';
import { SelectorGlobal } from 'src/app/ax-selector/global';

import { debounce } from 'rxjs/operators';
import { timer } from 'rxjs';
import { MapWithName } from './map-editor/map-editor.component';
import { Step } from './script-editor/step/step.component';



@Component({
  selector: 'app-central-panel',
  templateUrl: './central-panel.component.html',
  styleUrls: ['./central-panel.component.scss']
})
export class CentralPanelComponent implements OnInit {

  static consoleTab:LeftSelection = {name: 'Console', type:'console'};

  private throttledChange:EventEmitter<[LeftSelection,MapRowVM[]]> = new EventEmitter();

  monitorTab:LeftSelection = {name: 'Monitor', type:'monitor'};


  baseTabs: LeftSelection[] = [this.monitorTab,CentralPanelComponent.consoleTab];

  tabs: LeftSelection[] = [];
  steps:AxScriptFlow[] = [];

  selected: LeftSelection = this.tabs[0];

  mapSelected:MapWithName = null;

  oldCurrentResolution:string = '';


  constructor(
      private editorService:EditorService,
      private selectorDatastore: SelectorDatastoreService,
      @Inject('GlobalRefSelector') private global:SelectorGlobal
    ) {
  }

  ngOnInit() {

    this.selectorDatastore.getSelected().subscribe(s => {
      if(!s || s.length == 0 ||  s.every(x => this.oldCurrentResolution != x.selectedResolution)) {
        if(s && s.length >0) {
          this.oldCurrentResolution = s[0].selectedResolution
        } else {
          this.oldCurrentResolution = '';
        }

        let isCurrentResolution = s && s.length > 0 && s.every(x => x.selectedResolution === this.global.res_string)
        if(isCurrentResolution) {
          this.baseTabs = [this.monitorTab,CentralPanelComponent.consoleTab];
          if(!this.tabs.includes(this.monitorTab)) {
            this.tabs = this.tabs.filter(x => x.name !== CentralPanelComponent.consoleTab.name)
            this.tabs = this.tabs.concat(this.baseTabs);
          }
        } else {
          this.baseTabs = [CentralPanelComponent.consoleTab];
          if(this.tabs.includes(this.monitorTab)) {
            this.tabs = this.tabs.filter(x => x.name !== this.monitorTab.name)
            if(this.selected.name === this.monitorTab.name && this.tabs[0]) {
              this.selected = this.tabs[0]
            }
          }
        }
      }
    })

    this.editorService.getLeftSelection().subscribe(s => {
      if(s) {
        if(s.name === CentralPanelComponent.consoleTab.name) {
          this.selectTab(s)
        } else {
          this.tabs = [s].concat(this.baseTabs);
          this.selected = s;
          if(this.selected.map) {
            this.mapSelected = this.mapName(this.selected.map());
          }
          if(this.selected.steps) {
            this.steps = Array.from(this.selected.steps()); // need to do a copy for the script editor to catch the change
          }
        }
      }
    })

    this.throttledChange.pipe(debounce(() => timer(500))).subscribe(x =>{
      if(x[0].onChangeMap) {
        x[0].onChangeMap(x[1]);
      }
    });


  }


  selectTab(tab:LeftSelection) {
    if(tab.type == 'map') {
      this.mapSelected = this.mapName(tab.map());
      // this.selectorDatastore.getData().subscribe(x => {
      //   this.selectorDatastore.getMaps().subscribe(y => {
      //     this.mapSelected = y.map(z => { return {name: z.name, rows: z.rows}}).find(x => x.name == tab.name)
      //     this.selected = tab
      //   })
      // })
    } 
    this.selected = tab
    
    
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
    this.selected.onChangeMap(map);
  }

  mapName(map:MapRowVM[]):MapWithName {
    return {
      rows: map,
      name: this.selected.name
    }
  }

}
