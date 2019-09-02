import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { BoxListEntity, AxSelectorObjects } from './ax-model/model';
import { map } from 'rxjs/operators';

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
    return this.httpClient.get<AxSelectorObjects>("/get_library_api");
  }

  setLibrary(library:AxSelectorObjects):Observable<DefaultResponse> {
    return this.httpClient.post<any>("/set_library_api",library);
  }

}
