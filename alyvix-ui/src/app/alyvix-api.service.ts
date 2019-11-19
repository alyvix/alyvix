import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { BoxListEntity, AxSelectorObjects, DesignerModel } from './ax-model/model';
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

  constructor(private httpClient:HttpClient) { }

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

  selectorNew(delay: number) {
    return this.httpClient.get<any>('/selector_button_new_api?delay=' +  delay).subscribe(x => {
      console.log('new');
    });
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

  designerParameters(object_name:string,resolution:string):Observable<DesignerModel> {
    return this.httpClient.get<DesignerModel>('/ide_selector_index_changed_api?object_name=' + object_name + '&resolution=' + resolution);
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
