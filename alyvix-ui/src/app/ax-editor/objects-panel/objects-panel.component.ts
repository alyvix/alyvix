import { Component, OnInit, ViewChild } from '@angular/core';
import { CdkDropList } from '@angular/cdk/drag-drop';
import { ObjectsRegistryService } from '../objects-registry.service';
import { LeftSelection, EditorService } from '../editor.service';
import { SelectorDatastoreService, MapsVM, SectionVM, ScriptEmpty,ScriptVM } from 'src/app/ax-selector/selector-datastore.service';
import { AxScriptFlow } from 'src/app/ax-model/model';


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



  objectLists:CdkDropList[] = [];

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
    this.selectorDatastore.getScripts().subscribe(s => this.script = s);
  }

  selectMap(map:MapsVM) {
    this.selected = {name:map.name, type: 'map', map: map.rows};
    this.editorService.setLeftSelection(this.selected);
  }

  select(name:string, steps: AxScriptFlow[]) {
    this.selected = {name:name, type: 'object', steps: steps};
    this.editorService.setLeftSelection(this.selected);
  }

  selectSection(section:SectionVM) {
    this.selected = {name:section.name, type: 'object', steps: section.instructions};
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
    this.maps.push({name: 'Map'+i, rows:[]});
  }

  removeMap(map:MapsVM) {
    if(confirm('Are you sure to delete map: '+ map + '?')) {
      this.maps = this.maps.filter(x => x !== map);
    }
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


}
