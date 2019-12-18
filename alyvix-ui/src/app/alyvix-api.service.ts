import { Injectable, Inject } from '@angular/core';
import { Observable, throwError, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { BoxListEntity, AxSelectorObjects, DesignerModel, AxModel } from './ax-model/model';
import { map, retry, catchError } from 'rxjs/operators';

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

  constructor(private httpClient:HttpClient, @Inject("subSystem") private subSystem:string) { }

  getScrapedText(box: BoxListEntity):Observable<ScrapedText> {
    return this.httpClient.post<ScrapedText>("/get_scraped_txt",box)
  }

  testScrapedText(scraped:ScrapedText):Observable<TestScrapedResponse> {
    return this.httpClient.post<TestScrapedResponse>("/test_txt_regexp",scraped)
  }

  getLibrary():Observable<AxSelectorObjects> {
    return this.httpClient.get<AxSelectorObjects>("/get_library_api").pipe(
      retry(1),
      catchError(this.handleError)
    );
  }

  setLibrary(library: SetLibraryRequest):Observable<DefaultResponse> {
    return this.httpClient.post<any>("/set_library_api",library);
  }

  checkObjectName(name: string): Observable<any> {
    return this.httpClient.get<any>("/check_if_object_exists_api?object_name="+name)
  }

  getProcesses():Observable<any> {
    return this.httpClient.get<any>("/get_user_process_api");
  }

  openOpenFileDialog():Observable<any> {
    return this.httpClient.get<any>("/designer_open_file_api");
  }

  checkTextDate(request:ScrapedValidation):Observable<ValidationResult> {
    return this.httpClient.post<ValidationResult>("/check_date_api",request);
  }

  checkTextNumber(request:ScrapedValidation):Observable<ValidationResult> {
    return this.httpClient.post<ValidationResult>("/check_number_api",request);
  }

  newObject(delay: number):Observable<any> {

    let baseUrl = '/selector_button_new_api';
    if (this.subSystem === 'editor') {
      baseUrl = '/ide_button_new_api';
    }

    return this.httpClient.get<any>(baseUrl + '?delay=' +  delay);
  }

  selectorCancel() {
    return this.httpClient.get<any>('/selector_shutdown_and_close_api').subscribe(x => {
      console.log('cancel');
    });
  }

  selectorEdit(object_name:string, resolution:string) {
    return this.httpClient.get<any>('/selector_button_edit_api?object_name=' + object_name + '&resolution=' + resolution).subscribe(x => {
      console.log('cancel');
    });
  }

  editObjectFullScreen(object_name:string, resolution:string, action:string, value:number):Observable<any> {
    return this.httpClient.get<any>('/ide_button_edit_api?ide=true&object_name=' + object_name + '&resolution=' + resolution + '&action=' + action + '&value=' + value);
  }

  designerParameters(object_name:string,resolution:string):Observable<DesignerModel> {
    return this.httpClient.get<DesignerModel>('/ide_selector_index_changed_api?object_name=' + object_name + '&resolution=' + resolution);
  }

  saveObject(model:AxModel):Observable<any> {
    if(model) {
      model.designerFromEditor = (this.subSystem === 'editor');
      return this.httpClient.post<any>('/save_json',model);
    } else {
      return of('')
    }
  }

  closeDesiger() {
    return this.httpClient.get<any>('/cancel_event').subscribe(x => {
      console.log("designer closed");
    })
  }

  saveAll(close:boolean) {
    return this.httpClient.get<any>('/save_all?close_editor='+close).subscribe(x => {
      console.log("save all");
    })
  }

  newCase() {
    return this.httpClient.get<any>('/ide_new_api').subscribe(x => {});
  }

  openCase() {
    return this.httpClient.get<any>('/ide_open_file_api').subscribe(x => {});
  }

  exitIde() {
    return this.httpClient.get<any>('/ide_exit_api').subscribe(x => {})
  }

  saveAs() {
    return this.httpClient.get<any>('/ide_save_as_api').subscribe(x => {})
  }

  run(action:string) {
    return this.httpClient.get<any>('/ide_run_api?action='+action)
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
