import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { BoxListEntity, AxSelectorObjects } from './ax-model/model';
import { map, retry, catchError } from 'rxjs/operators';

export interface ScrapedText{
  regexp?: string,
  reg_exp?: string,
  scraped_text: string
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
