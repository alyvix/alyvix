import { Injectable, Inject, EventEmitter } from '@angular/core';
import { Observable, throwError, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { BoxListEntity, AxSelectorObjects, DesignerModel, AxModel, AxMap, AxScriptFlow } from './ax-model/model';
import { map, retry, catchError } from 'rxjs/operators';
import { ToastrService } from 'ngx-toastr';
import { environment } from 'src/environments/environment';

export interface ScrapedText{
  regexp?: string,
  reg_exp?: string,
  scraped_text: string
}

export interface ScrapedValidation{
  scraped_text: string;
  logic: string;
}

export interface ValidationResult{
  result: boolean;
}

interface TestScrapedResponse{
  match: string
}

interface DefaultResponse{
  success: boolean
}

export interface SetLibraryRequest{
  library:AxSelectorObjects,
  close_selector: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AlyvixApiService {

  home: string = "http://localhost:4997";

  constructor(
    private httpClient:HttpClient,
    @Inject("subSystem") private subSystem:string,
    private toastr: ToastrService,
    ) { }

  startLoading:EventEmitter<boolean> = new EventEmitter();
  endLoading:EventEmitter<boolean> = new EventEmitter();

  getScrapedText(component_index:number, object_name: string, boxes: BoxListEntity[]):Observable<ScrapedText> {
    return this.httpClient.post<ScrapedText>(this.home + "/get_scraped_txt?object_name="+object_name+"&idx="+component_index,boxes)
  }

  testScrapedText(scraped:ScrapedText):Observable<TestScrapedResponse> {
    return this.httpClient.post<TestScrapedResponse>(this.home + "/test_txt_regexp",scraped)
  }

  getLibrary():Observable<AxSelectorObjects> {
    return this.httpClient.get<AxSelectorObjects>(this.home + "/get_library_api").pipe(
      retry(1),
      catchError(this.handleError)
    );
  }

  setLibrary(library: SetLibraryRequest):Observable<DefaultResponse> {
    return this.httpClient.post<any>(this.home + "/set_library_api",library);
  }

  renameObject(oldName:string,newName:string):Observable<any> {
    return this.httpClient.get<any>(this.home + "/rename_object?old_name="+oldName+"&new_name=" + newName);
  }

  checkObjectName(name: string): Observable<any> {
    return this.httpClient.get<any>(this.home + "/check_if_object_exists_api?object_name="+name)
  }

  getProcesses():Observable<any> {
    return this.httpClient.get<any>(this.home + "/get_user_process_api");
  }

  openOpenFileDialog(caller:string):Observable<any> {
    return this.httpClient.get<any>(this.home + "/designer_open_file_api?caller="+caller);
  }

  checkTextDate(request:ScrapedValidation):Observable<ValidationResult> {
    return this.httpClient.post<ValidationResult>(this.home + "/check_date_api",request);
  }

  checkTextNumber(request:ScrapedValidation):Observable<ValidationResult> {
    return this.httpClient.post<ValidationResult>(this.home + "/check_number_api",request);
  }

  newObject(delay: number):Observable<any> {

    let baseUrl = this.home + '/selector_button_new_api';
    if (this.subSystem === 'editor') {
      baseUrl = this.home + '/ide_button_new_api';
    }

    return this.httpClient.get<any>(baseUrl + '?delay=' +  delay);
  }

  grab(delay: number,name:string):Observable<any> {

    let subSystem = 'selector';
    if (this.subSystem === 'editor') {
      subSystem = 'ide';
    }

    return this.httpClient.get<any>(this.home + '/button_grab_api?name='+name+'&delay='+delay+'&caller='+subSystem);
  }

  selectorCancel() {
    return this.httpClient.get<any>(this.home + '/selector_shutdown_and_close_api').subscribe(x => {
      console.log('cancel');
    });
  }

  selectorEdit(object_name:string, resolution:string) {
    return this.httpClient.get<any>(this.home + '/selector_button_edit_api?object_name=' + object_name + '&resolution=' + resolution).subscribe(x => {
      console.log('cancel');
    });
  }

  editObjectFullScreen(object_name:string, resolution:string, action:string, value:number):Observable<any> {
    return this.httpClient.get<any>(this.home + '/ide_button_edit_api?ide=true&object_name=' + object_name + '&resolution=' + resolution + '&action=' + action + '&value=' + value);
  }

  designerParameters(object_name:string,resolution:string):Observable<DesignerModel> {
    return this.httpClient.get<DesignerModel>(this.home + '/ide_selector_index_changed_api?object_name=' + object_name + '&resolution=' + resolution);
  }

  saveObject(model:AxModel):Observable<any> {
    if(model) {
      model.designerFromEditor = (this.subSystem === 'editor');
      return this.httpClient.post<any>(this.home + '/save_json',model).pipe(map(x => {
        if(!environment.production) {
          setTimeout(() => {
            if(this.subSystem === 'editor' && (window as any).reloadAlyvixIde) {
              (window as any).reloadAlyvixIde(model.object_name);
            }
          }, 100);
        }
        return x;
      }));
    } else {
      return of('')
    }
  }

  saveMap(name:string,map:AxMap):Observable<any> {
    let obj = {name: name, dict: map}
    return this.httpClient.post<any>(this.home + '/set_map_api',obj);
  }

  closeDesiger() {
    return this.httpClient.get<any>(this.home + '/cancel_event').subscribe(x => {
      console.log("designer closed");
    })
  }

  saveAll(close:boolean) {
    this.startLoading.emit(true);
    return this.httpClient.get<any>(this.home + '/save_all?close_editor='+close).subscribe(x => {
      console.log("save all");
      this.endLoading.emit(true);
      this.toastr.success("Test Case Saved");
    })
  }

  newCase() {
    return this.httpClient.get<any>(this.home + '/ide_new_api').subscribe(x => {});
  }

  openCase() {
    return this.httpClient.get<any>(this.home + '/ide_open_file_api').subscribe(x => {});
  }

  exitIde() {
    return this.httpClient.get<any>(this.home + '/ide_exit_api').subscribe(x => {})
  }

  checkModification():Observable<DefaultResponse> {
    return this.httpClient.get<DefaultResponse>(this.home + '/is_lib_changed_api')
  }

  saveAs() {
    this.startLoading.emit(true);
    return this.httpClient.get<any>(this.home + '/ide_save_as_api').subscribe(x => {
      this.endLoading.emit(true);
      this.toastr.success("Test Case Saved");
    })
  }

  run(action:string):Observable<any> {
    return this.httpClient.get<any>(this.home + '/ide_run_api?action='+action)
  }

  runOne(name:string):Observable<any> {
    return this.httpClient.get<any>(this.home + '/selector_run_api?action=run&name=' + name);
  }

  runSelection(flow:AxScriptFlow[]):Observable<any> {
    return this.httpClient.post(this.home + '/central_panel_run_api?action=run',flow)
  }





  private handleError(error) {
    let errorMessage = '';
    if (error.error instanceof ErrorEvent) {
      // client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // server-side error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    window.alert(errorMessage);
    return throwError(errorMessage);
  }

}
