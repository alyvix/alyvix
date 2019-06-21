import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { BoxListEntity } from './ax-model/model';
import { map } from 'rxjs/operators';

export interface ScrapedText{
  regexp?: string,
  scraped_text: string
}

interface TestScrapedResponse{
  match: boolean
}

@Injectable({
  providedIn: 'root'
})
export class AlyvixApiService {

  constructor(private httpClient:HttpClient) { }

  getScrapedText(box: BoxListEntity):Observable<ScrapedText> {
    return this.httpClient.post<ScrapedText>("/get_scraped_txt",box)
  }

  testScrapedText(scraped:ScrapedText):Observable<boolean> {
    return this.httpClient.post<TestScrapedResponse>("test_txt_regexp",scraped).pipe(map(x => x.match))
  }

}
