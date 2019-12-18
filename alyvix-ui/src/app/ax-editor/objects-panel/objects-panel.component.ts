import { Component, OnInit, ViewChild } from '@angular/core';
import { ObjectsRegistryService } from '../objects-registry.service';
import { LeftSelection, EditorService } from '../editor.service';
import { SelectorDatastoreService, MapsVM, SectionVM, ScriptEmpty,ScriptVM } from 'src/app/ax-selector/selector-datastore.service';
import { AxScriptFlow } from 'src/app/ax-model/model';
import { Step } from '../central-panel/script-editor/step/step.component';
import { Utils } from 'src/app/utils';



@Component({
  selector: 'app-objects-panel',
  templateUrl: './objects-panel.component.html',
  styleUrls: ['./objects-panel.component.scss']
})
export class ObjectsPanelComponent implements OnInit {

  constructor(
    private objectRegistry:ObjectsRegistryService,
    private editorService:EditorService,
    private selectorDatastore:SelectorDatastoreService
    ) { }



  objectLists:string[] = [];

  maps:MapsVM[] = [];
  script:ScriptVM = ScriptEmpty;

  selected:LeftSelection = {name: 'MAIN', type:'object'};


  ngOnInit() {

    this.objectRegistry.objectList().subscribe(x => {
      setTimeout(() => {
        this.objectLists = x;
      }, 200);
    });
    this.editorService.setLeftSelection(this.selected);
    this.selectorDatastore.getMaps().subscribe(m => this.maps = m);
    this.selectorDatastore.getScripts().subscribe(s => {
      if(s) {
        this.script = s;
        if(!this.selected) {
          this.selectMain();
        }
      }
    });
    this.editorService.addBeforeSave(() => {
      let self = this;
      return new Promise(function(resolve) {
        self.selectorDatastore.setMaps(self.maps);
        self.selectorDatastore.setScripts(self.script);
        resolve();
      })
    })

  }

  selectMap(map:MapsVM) {
    this.selected = {name:map.name, type: 'map', map: map.rows, onChangeMap: rows => map.rows = rows};
    this.editorService.setLeftSelection(this.selected);
  }

  selectMain() {
    this.selected = {name:'MAIN', type: 'object', steps: this.script.main, onChangeSteps: s => this.script.main = s};
    this.editorService.setLeftSelection(this.selected);
  }

  selectFail() {
    this.selected = {name:'FAIL', type: 'object', steps: this.script.fail, onChangeSteps: s => this.script.fail = s};
    this.editorService.setLeftSelection(this.selected);
  }

  selectExit() {
    this.selected = {name:'EXIT', type: 'object', steps: this.script.exit, onChangeSteps: s => this.script.exit = s};
    this.editorService.setLeftSelection(this.selected);
  }

  selectSection(section:SectionVM) {
    this.selected = {name:section.name, type: 'object', steps: section.instructions, onChangeSteps: s => section.instructions = s};
    this.editorService.setLeftSelection(this.selected);
  }

  isSelectedMap(map:MapsVM):boolean {
    return this.selected.name === map.name && this.selected.type == 'map';
  }

  isSelected(name:string):boolean {
    return this.selected.name === name && this.selected.type == 'object';
  }

  addMap() {
    let i = 1;
    while(this.maps.find(x => x.name === 'Map'+i)) {
      i++;
    }
    this.maps.push({name: 'Map'+i, rows:[{name: 'key', value: 'value'}]});
  }

  removeMap(map:MapsVM) {
    if(confirm('Are you sure to delete map: '+ map + '?')) {
      this.maps = this.maps.filter(x => x !== map);
    }
  }

  changeMapName(map:MapsVM, name:string) {
    map.name = name;
    this.selectMap(map);
  }

  addSection() {
    let i = 1;
    while(this.script.sections.find(x => x.name === 'Section'+i)) {
      i++;
    }
    this.script.sections.push({name: 'Section'+i, instructions: []});
  }

  removeSection(section) {
    if(confirm('Are you sure to delete section: '+ section + '?')) {
      this.script.sections = this.script.sections.filter(x => x !== section);
    }
  }

  changeSectionName(section:SectionVM, name:string) {
    section.name = name;
    this.selectSection(section);
  }

  mapToStep(map: MapsVM):Step {
    return {
      id: Utils.uuidv4(),
      name: map.name,
      type: 'map',
      condition: 'for',
      disabled: false
    };
  }

  sectionToStep(section: SectionVM):Step {
    return {
      id: Utils.uuidv4(),
      name: section.name,
      type: 'section',
      condition: 'run',
      disabled: false
    }
  }


}
