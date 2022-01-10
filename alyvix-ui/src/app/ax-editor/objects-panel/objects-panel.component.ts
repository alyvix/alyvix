import { Component, OnInit, ViewChild } from '@angular/core';
import { ObjectsRegistryService } from '../objects-registry.service';
import { LeftSelection, EditorService } from '../editor.service';
import { SelectorDatastoreService, MapsVM, SectionVM, ScriptEmpty,ScriptVM } from 'src/app/ax-selector/selector-datastore.service';
import { AxScriptFlow } from 'src/app/ax-model/model';
import { Step } from '../central-panel/script-editor/step/step.component';
import { Utils } from 'src/app/utils';
import { AlyvixApiService } from 'src/app/alyvix-api.service';
import { Draggable } from 'src/app/utils/draggable';
import { ModalService, Modal } from 'src/app/modal-service.service';
import { RunnerService } from 'src/app/runner.service';
import { AxDesignerService } from 'src/app/ax-designer/ax-designer-service';



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
    private alyvixApi:AlyvixApiService,
    private runner:RunnerService,
    private modal: ModalService,
    private axDesignerService:AxDesignerService
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
        } else {
          if(this.selected.type == 'object') {
            switch(this.selected.name) {
              case 'MAIN': this.selectMain(); break;
              case 'FAIL': this.selectFail(); break;
              case 'EXIT': this.selectExit(); break;
              default: {
                const section = this.script.sections.find(x => x.name === this.selected.name)
                if(section) {
                  this.selectSection(section)
                } else {
                  this.selectMain()
                }
              }
            }
          }
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
    console.log('selectMain')
    setTimeout(() => {
      this.selected = {name:'MAIN', type: 'object', steps: () => this.script.main, onChangeSteps: s => {
        this.script.main = s;
        this.selectorDatastore.setScripts(this.script);
        this.editorService.save().subscribe(x => {});
      }};
      console.log('select Main')
      this.editorService.setLeftSelection(this.selected);
    }, 0);
    
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

      const usageCurrent = this.checkUsageMapForObject(map.name)

      let usages = this.selectorDatastore.mapUsage(map.name)
      if(usageCurrent) {
        usages.push(usageCurrent)
      }

      this.modal.open({
        title: 'Delete map',
        body: 'Are you sure you want to delete ' + map.name + '?',
        list: usages,
        actions: [
          {
            title: 'Delete',
            importance: 'btn-danger',
            callback: () => {
              this.maps = this.maps.filter(x => x !== map);
              this.editorService.save().subscribe(saved => {})
              if(this.selected.name == map.name) {
                this.selectMain();
              }
            }
          }
        ],
        cancel: Modal.NOOP
      });
    

  }

  hasFocus(input:HTMLInputElement):boolean {
    return document.activeElement === input;
  }


  private checkUsageMapForObject(mapName:string):string {
    const model = this.axDesignerService.getModel()
    //console.log(model)
    if(!model) return null
    return model.box_list.every(x => {
      if(x.features && x.features.T && x.features.T.map) {
        return x.features.T.map != mapName
      } else {
        return true
      }
    }) ?
    null :
    "Used in object " + model.object_name
  }

  private refactorMapForObject(oldName:string, newName:string) {
    const model = this.axDesignerService.getModel()
    //console.log(model)
    if(!model) return null
    model.box_list.forEach(x => {
      if(x.features && x.features.T && x.features.T.map && x.features.T.map == oldName) {
        x.features.T.map = newName
      } 
    })
  }


  changeMapName(map:MapsVM, event:Event) {
      console.log('changeMapName')
      const target = (event.target as HTMLInputElement)
      let usages = this.selectorDatastore.mapUsage(map.name);
      const usageCurrent = this.checkUsageMapForObject(map.name)

      if(usageCurrent) {
        usages.push(usageCurrent)
      }

      const rename = () => {
        //console.log(target.value)

        map.name = target.value;
        this.selectMap(map);
        
        this.editorService.save().subscribe(x => '');
      }

      if(usages.length > 0) {
        this.modal.open({
          title: 'Rename map',
          body: 'Are you sure you want to rename ' + map.name + ' to ' + target.value + '?',
          list: usages,
          actions: [
            // {
            //   title: 'Rename All',
            //   importance: 'btn-primary',
            //   callback: () => {
            //     this.selectorDatastore.refactorMap(map.name,target.value)
            //     this.refactorMapForObject(map.name,target.value)
            //     rename();
            //   }
            // },
            {
              title: 'Rename',
              importance: 'btn-danger',
              callback: rename
            }
          ],
          cancel: Modal.cancel(() => { target.value = map.name })
        });
      } else {
        rename();
      }


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

    this.modal.open({
      title: 'Delete section',
      body: 'Are you sure you want to delete ' + section.name + '?',
      list: this.selectorDatastore.sectionUsage(section.name),
      actions: [
        {
          title: 'Delete',
          importance: 'btn-danger',
          callback: () => {
            this.script.sections = this.script.sections.filter(x => x !== section);
            this.editorService.save().subscribe(saved => {})
            if(this.selected.name === section.name) {
              this.selectMain();
            }
          }
        }
      ],
      cancel: Modal.NOOP
    });

  }

  onChangeSectionName(section:SectionVM,name: string, nameInput: HTMLInputElement) {
    if(this.selectorDatastore.nameValidation(nameInput, section.name) == null) {
      section.name = name;
    }

  }

  changeSectionName(section:SectionVM, event:Event) {

    const target = (event.target as HTMLInputElement)
    const usages = this.selectorDatastore.sectionUsage(section.name);

    const rename = () => {
      section.name = target.value;
      this.selectSection(section);
      this.editorService.save();
    }

    if(usages.length > 0) {
      this.modal.open({
        title: 'Rename map',
        body: 'Are you sure you want to rename ' + section.name + ' to ' + target.value + '?',
        list: usages,
        actions: [
          {
            title: 'Rename All',
            importance: 'btn-primary',
            callback: () => {
              this.selectorDatastore.refactorSection(section.name,target.value)
              rename()
            }
          },
          {
            title: 'Rename',
            importance: 'btn-danger',
            callback: rename
          }
        ],
        cancel: Modal.cancel(() => { target.value = section.name })
      });
    } else {
      rename();
    }

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

  runSection(section:SectionVM) {
    this.runner.runOne(section.name)
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
