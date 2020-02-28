import { Component, OnInit, ViewChild } from '@angular/core';
import { ObjectsRegistryService } from '../objects-registry.service';
import { LeftSelection, EditorService } from '../editor.service';
import { SelectorDatastoreService, MapsVM, SectionVM, ScriptEmpty,ScriptVM } from 'src/app/ax-selector/selector-datastore.service';
import { AxScriptFlow } from 'src/app/ax-model/model';
import { Step } from '../central-panel/script-editor/step/step.component';
import { Utils } from 'src/app/utils';
import { AlyvixApiService } from 'src/app/alyvix-api.service';
import { Draggable } from 'src/app/utils/draggable';



@Component({
  selector: 'app-objects-panel',
  templateUrl: './objects-panel.component.html',
  styleUrls: ['./objects-panel.component.scss']
})
export class ObjectsPanelComponent implements OnInit {

  constructor(
    private objectRegistry:ObjectsRegistryService,
    private editorService:EditorService,
    private selectorDatastore:SelectorDatastoreService,
    private alyvixApi:AlyvixApiService
    ) { }




  maps:MapsVM[] = [];
  script:ScriptVM = ScriptEmpty;


  selected:LeftSelection;


  ngOnInit() {
    this.editorService.setSection.subscribe(x => {
      this.script.sections.filter(s => s.name === x).forEach(s => this.selectSection(s));
    })
    this.selectorDatastore.getMaps().subscribe(m => this.maps = m);
    this.selectorDatastore.getScripts().subscribe(s => {
      if(s) {
        this.script = s;
        if(!this.selected) {
          this.selectMain();
        }
      }
    });
    this.editorService.addBeforeSave(() => new Promise( (resolve,r) => {
        this.selectorDatastore.setMaps(this.maps);
        resolve();
      }
    ));


  }




  selectMap(map:MapsVM) {
    this.selected = {name:map.name, type: 'map', map: () => map.rows, onChangeMap: rows => {
      map.rows = rows
      this.selectorDatastore.setMaps(this.maps);
      this.alyvixApi.saveMap(map.name,SelectorDatastoreService.toAxMap(rows)).subscribe(x => {})
    }};
    this.editorService.setLeftSelection(this.selected);
  }

  selectMain() {
    this.selected = {name:'MAIN', type: 'object', steps: () => this.script.main, onChangeSteps: s => {
      this.script.main = s;
      this.selectorDatastore.setScripts(this.script);
      this.editorService.save().subscribe(x => {});
    }};
    this.editorService.setLeftSelection(this.selected);
  }

  selectFail() {
    this.selected = {name:'FAIL', type: 'object', steps: () => this.script.fail, onChangeSteps: s => {
      this.script.fail = s;
      this.selectorDatastore.setScripts(this.script);
      this.editorService.save().subscribe(x => {});
    }};
    this.editorService.setLeftSelection(this.selected);
  }

  selectExit() {
    this.selected = {name:'EXIT', type: 'object', steps: () => this.script.exit, onChangeSteps: s => {
      this.script.exit = s;
      this.selectorDatastore.setScripts(this.script);
      this.editorService.save().subscribe(x => {});
    }};
    this.editorService.setLeftSelection(this.selected);
  }

  selectSection(section:SectionVM) {
    this.selected = {name:section.name, type: 'object', steps: () => section.instructions, onChangeSteps: s => {
      section.instructions = s;
      this.selectorDatastore.setScripts(this.script);
      this.editorService.save().subscribe(x => {});
    }};
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
    this.editorService.save().subscribe(saved => {})
  }

  removeMap(map:MapsVM) {
    if(confirm('Are you sure you want to delete that map?')) {
      this.maps = this.maps.filter(x => x !== map);
      this.editorService.save().subscribe(saved => {})
      if(this.selected.name == map.name) {
        this.selectMain();
      }
    }
  }

  changeMapName(map:MapsVM, name) {
    map.name = name.target.value;
    this.selectMap(map);
    this.editorService.saveThrottled();
  }

  addSection() {
    let i = 1;
    while(this.script.sections.find(x => x.name === 'Section'+i)) {
      i++;
    }
    this.script.sections.push({name: 'Section'+i, instructions: []});
    this.editorService.save().subscribe(saved => {})
  }

  removeSection(section:SectionVM) {
    if(confirm('Are you sure you want to delete that section?')) {
      this.script.sections = this.script.sections.filter(x => x !== section);
      this.editorService.save().subscribe(saved => {})
      if(this.selected.name == section.name) {
        this.selectMain();
      }
    }
  }

  changeSectionName(section:SectionVM, name) {
    section.name = name.target.value;
    this.selectSection(section);
    this.editorService.saveThrottled();
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


  mapDrag(event:DragEvent,map:MapsVM) {
    Draggable.startDrag(event,"map",this.mapToStep(map));
  }

  sectionDrag(event:DragEvent,section: SectionVM) {
    Draggable.startDrag(event,"section",this.sectionToStep(section));
  }

  addSectionToScript(section:SectionVM,event:MouseEvent) {
    event.stopPropagation();
    this.objectRegistry.addStep.emit(this.sectionToStep(section));
  }

  addMapToScript(map:MapsVM,event:MouseEvent) {
    event.stopPropagation();
    this.objectRegistry.addStep.emit(this.mapToStep(map));
  }




}
