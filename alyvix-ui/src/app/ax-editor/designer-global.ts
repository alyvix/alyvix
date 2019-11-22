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
    this.selectorDatastore.getSelected().subscribe(rows => {
      if(rows && rows.length === 1 && rows[0].selectedResolution === this.global.res_string) {
        this.reloadDesignerModel(rows[0]);
      }
    })
  }


  axModel(): Observable<AxModel> {
    return this._model;
  }

  background(): Observable<string> {
    return this._background;
  }

  reloadDesignerModel(row:RowVM) {
    return this.api.designerParameters(row.name,this.global.res_string).subscribe(x => {
      const model:AxModel = {
        box_list: x.file_dict.boxes.map((box, i) => {
          box.thumbnail = x.thumbnails.thumbnails[i];
          return box;
        }),
        object_name: x.file_dict.object_name,
        background: 'data:image/png;base64,' + x.file_dict.screen,
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
