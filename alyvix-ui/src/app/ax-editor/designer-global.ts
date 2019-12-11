import { AlyvixApiService } from "../alyvix-api.service";
import { environment } from "src/environments/environment";
import { SelectorDatastoreService } from "../ax-selector/selector-datastore.service";
import { Injectable, Inject } from "@angular/core";
import { EditorModule } from "./editor.module";
import { AxModel, BoxListEntity } from "../ax-model/model";
import { RowVM } from "../ax-selector/ax-table/ax-table.component";
import { SelectorGlobal } from "../ax-selector/global";
import { of, Observable, BehaviorSubject } from 'rxjs';
import { EditorGlobal } from "./editor-global";
import { AxDesignerService } from "../ax-designer/ax-designer-service";
import { EditorService } from "./editor.service";
import * as _ from 'lodash';

@Injectable({
  providedIn: 'root',
})
export class EditorDesignerGlobal extends environment.globalTypeDesigner {

  private _model:BehaviorSubject<AxModel> = new BehaviorSubject<AxModel>(null);
  private _background:BehaviorSubject<string> = new BehaviorSubject<string>(null);
  private row:RowVM;

  constructor(
    private api:AlyvixApiService,
    private selectorDatastore:SelectorDatastoreService,
    private editorService:EditorService,
    @Inject('GlobalRefSelector') private global: SelectorGlobal,
    @Inject('GlobalRefEditor') private editorGlobal: EditorGlobal,) {
    super();
    this.selectorDatastore.getSelected().subscribe(rows => {
      if(this._model.value && !this.editorService.designerFullscreen) {
          const model = this.modelWithDetection();
          this.editorService.save().subscribe( y => { // I need to save the library to avoid having an unknown name saving the single object
            this.api.saveObject(model).subscribe(x => {
              this.loadNext(rows);
            });
          });
      } else {
        this.loadNext(rows);
      }

    })
  }

  private loadNext(rows:RowVM[]) {
    if(rows && rows.length === 1 && rows[0].selectedResolution === this.global.res_string) {
      this.reloadDesignerModel(rows[0]);
    } else {
      this.row = null;
      this._model.next(null);
    }
  }



  axModel(): Observable<AxModel> {
    return this._model;
  }

  background(): Observable<string> {
    return this._background;
  }

  private modelWithDetection():AxModel {
    const model = this._model.value;
    if (model && this.row) {
      model.object_name = this.row.name;
      model.detection.break = this.row.object.detection.break;
      model.detection.timeout_s = this.row.object.detection.timeout_s;
    }
    return _.cloneDeep(model) ;
  }

  newComponent(group:number) {
    console.log("new Component")
    const model = this.modelWithDetection();
    if(model) {
      this.editorService.save().subscribe( y => {
        this.api.saveObject(model).subscribe(x => {
          this.api.editObjectFullScreen(this._model.value.object_name,this.global.res_string,"newComponent",group).subscribe(x => {
            this.editorService.designerFullscreen = true;
            this._model.next(null);
          });
        });
      });
    }
  }

  setPoint(i:number) {
    const model = this.modelWithDetection();
    if(model) {
      this.editorService.save().subscribe( y => {
        this.api.saveObject(model).subscribe(x => {
          this.api.editObjectFullScreen(this._model.value.object_name,this.global.res_string,"setPoint",i).subscribe(x => {
            this.editorService.designerFullscreen = true;
            this._model.next(null);
          });
        });
      });
    }
  }

  reloadDesignerModel(row:RowVM) {
    this.row = row;
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
      this.editorGlobal.setBoxes(model.box_list);
      this._model.next(model);
    })
  }

  lastElement(): BoxListEntity {
    return null; //TODO
  }

}
