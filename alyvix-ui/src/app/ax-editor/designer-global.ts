import { AlyvixApiService } from "../alyvix-api.service";
import { environment } from "src/environments/environment";
import { SelectorDatastoreService, AxFile } from "../ax-selector/selector-datastore.service";
import { Injectable, Inject, NgZone } from "@angular/core";
import { EditorModule } from "./editor.module";
import { AxModel, BoxListEntity, AxMaps } from "../ax-model/model";
import { RowVM } from "../ax-selector/ax-table/ax-table.component";
import { SelectorGlobal } from "../ax-selector/global";
import { of, Observable, BehaviorSubject } from 'rxjs';
import { AxDesignerService } from "../ax-designer/ax-designer-service";
import { EditorService } from "./editor.service";
import * as _ from 'lodash';
import { first,map } from 'rxjs/operators'
import { loadavg } from "os";

@Injectable({
  providedIn: 'root',
})
export class EditorDesignerGlobal extends environment.globalTypeDesigner {

  private _model:BehaviorSubject<AxModel> = new BehaviorSubject<AxModel>(null);
  private _background:BehaviorSubject<string> = new BehaviorSubject<string>(null);
  private selectedRows:RowVM[];
  private tabSelected:AxFile;
  private _maps:BehaviorSubject<AxMaps> = new BehaviorSubject<AxMaps>(null);

  constructor(
    private api:AlyvixApiService,
    private selectorDatastore:SelectorDatastoreService,
    private editorService:EditorService,
    zone: NgZone,
    @Inject('GlobalRefSelector') private global: SelectorGlobal,) {
    super(zone);
    this.selectorDatastore.tabSelected().subscribe(main => { //change tab
      this.tabSelected = main;
      if(this._model.value) {
        this.editorService.save().subscribe( y => { // I need to save the library to avoid having an unknown name saving the single object
            this._model.next(null);
            this.selectorDatastore.changeTab.emit(main);
        });
      } else {
        this.selectorDatastore.changeTab.emit(main);
      }
    });
    this.selectorDatastore.changedNameRow.subscribe(name => {
      this._model.value.object_name = name
      this.editorService.save().subscribe( y => { // I need to save the library to avoid having an unknown name saving the single object
        console.log('saved after name change');
      });
    });
    this.selectorDatastore.changedBreak.subscribe(b => this._model.value.detection.break = b );
    this.selectorDatastore.changedTimeout.subscribe(to => this._model.value.detection.timeout_s = to );
    this.selectorDatastore.getMaps().subscribe(maps => {
      this._maps.next(SelectorDatastoreService.toAxMaps(maps));
    });
    this.editorService.objectChanged.subscribe(object => {
      this.loadNext(this.selectedRows);
    });
    this.editorService.setObjectSave((objects:string[]) => { // check if the current object needs to be saved
      if(this._model.value && objects.includes(this._model.value.object_name)) {
        return this.api.saveObject(this._model.value)
      } else {
        return of('')
      }
    })
    this.selectorDatastore.changedSelection.subscribe(rows => { // change selection trigger save
      if(this.checkIfChangedRows(rows)) {
        if(this._model.value) {
          this.editorService.save().subscribe( y => { // I need to save the library to avoid having an unknown name saving the single object
              this.loadNext(rows);
          });
        } else {
          this.loadNext(rows);
        }
      }
      this.selectedRows = rows;
    });
  }

  private checkIfChangedRows(rows:RowVM[]):boolean {
    let result = true;
    if(this.selectedRows) {
      result = rows.length !== this.selectedRows.length || rows.some(x => this.selectedRows.map(y => y.name).findIndex(y => y !== x.name) >= 0)
    }
    return result;
  }

  private loadNext(rows:RowVM[]) {
    if(rows && rows.length === 1 && rows[0].selectedResolution === this.global.res_string && this.tabSelected && this.tabSelected.main) {
      this.reloadDesignerModel(rows[0]);
    } else {
      this._model.next(null);
    }
  }



  axModel(): Observable<AxModel> {
    return this._model;
  }

  axMaps(): Observable<AxMaps> {
    return this._maps;
  }

  background(): Observable<string> {
    return this._background;
  }



  newComponent(group:number) {
    if(this._model.value) {
      this.editorService.save().subscribe( y => {
        this.api.editObjectFullScreen(this._model.value.object_name,this.global.res_string,"newComponent",group).subscribe(x => {
          this._model.next(null);
        });
      });
    }
  }

  setPoint(i:number) {
    if(this._model.value) {
      this.editorService.save().subscribe( y => {
        this.api.editObjectFullScreen(this._model.value.object_name,this.global.res_string,"setPoint",i).subscribe(x => {
          this._model.next(null);
        });
      });
    }
  }

  private reloadDesignerModel(row:RowVM) {
    return this.api.designerParameters(row.name,this.global.res_string).subscribe(x => {
      const model:AxModel = {
        box_list: x.file_dict.boxes.map((box, i) => {
          box.thumbnail = x.thumbnails.thumbnails[i];
          return box;
        }),
        object_name: x.file_dict.object_name,
        background: 'data:image/png;base64,' + x.background,
        detection: x.file_dict.detection,
        call: x.file_dict.call
      };

      this._background.next('data:image/png;base64,'+ x.background);
      this.setBoxes(model.box_list);
      this._model.next(model);
    })
  }

  setBoxes(boxes: BoxListEntity[]) {
    if(boxes) {
      super.setBoxes(boxes);
    } else if(this._model.value) {
      console.log('default boxes')
      super.setBoxes(this._model.value.box_list)
    }
  }

  lastElement(): BoxListEntity {
    return null; //TODO
  }

}
