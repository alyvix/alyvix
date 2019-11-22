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

@Injectable({
  providedIn: 'root',
})
export class EditorDesignerGlobal extends environment.globalTypeDesigner {

  private _model:BehaviorSubject<AxModel> = new BehaviorSubject<AxModel>(null);
  private _background:BehaviorSubject<string> = new BehaviorSubject<string>(null);

  constructor(
    private api:AlyvixApiService,
    private selectorDatastore:SelectorDatastoreService,
    @Inject('GlobalRefSelector') private global: SelectorGlobal,
    @Inject('GlobalRefEditor') private editorGlobal: EditorGlobal,) {
    super();
    console.log("new instance of EditorDesignerGlobal")
    this.selectorDatastore.getSelected().subscribe(rows => {

      if(this._model.value) {
        this.api.saveObject(this._model.value).subscribe(x => {
          console.log("object saved");
        });
      }
      if(rows && rows.length === 1 && rows[0].selectedResolution === this.global.res_string) {
        this.reloadDesignerModel(rows[0]);
      } else {
        this._model.next(null);
      }
    })
  }


  axModel(): Observable<AxModel> {
    return this._model;
  }

  background(): Observable<string> {
    return this._background;
  }

  newComponent(group:number) {
    if(this._model.value) {
      this.api.saveObject(this._model.value).subscribe(x => {
        this.api.editObjectFullScreen(this._model.value.object_name,this.global.res_string,"newComponent",group);
      });
    }
  }

  setPoint(i:number) {
    if(this._model.value) {
      this.api.saveObject(this._model.value).subscribe(x => {
        this.api.editObjectFullScreen(this._model.value.object_name,this.global.res_string,"setPoint",i);
      });
    }
  }

  reloadDesignerModel(row:RowVM) {
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
