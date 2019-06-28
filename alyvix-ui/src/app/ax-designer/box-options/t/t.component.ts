import { Component, OnInit, Input, ViewChild, Injectable, Inject } from '@angular/core';
import { TreeNode } from '../../ax-designer-service';
import { FormControl, AsyncValidatorFn, AbstractControl } from '@angular/forms';
import { AlyvixApiService } from 'src/app/alyvix-api.service';
import { map, switchMap, mapTo, catchError, debounce } from 'rxjs/operators';
import { Validation } from 'src/app/utils/validators';
import { timer, of, Observable } from 'rxjs';
import { GlobalRef, GroupsFlag } from "src/app/ax-model/ax-global";

@Component({
  selector: 'ax-designer-t',
  templateUrl: './t.component.html',
  styleUrls: ['./t.component.scss']
})
export class TComponent implements OnInit {

  constructor(private alyvixApi: AlyvixApiService, @Inject('GlobalRef') private global: GlobalRef, ) { }

  @Input()
  node: TreeNode


  regexpValidation = Validation.debouncedAsyncValidator<string>(v => {
    return this.alyvixApi.testScrapedText({ regexp: v, scraped_text: this.scraped }).pipe(map(res => {
      return res ? null : { regexp: { invalidRegexp: v } }
    }))
  })

  regex: FormControl = new FormControl('', null, this.regexpValidation);



  isScraper(): boolean {
    return this.node.box.features.T.type == 'scraper'
  }

  scraped: string = ""

  ngOnInit() {

    if (!this.node.box.features.T.type) {
      this.node.box.features.T.type = "detection";
    }
    if (this.node && this.node.box) {
      this.alyvixApi.getScrapedText(this.node.box).subscribe(x => {
        this.scraped = x.scraped_text;
        if (!this.node.box.features.T.regexp) {
          this.node.box.features.T.regexp = x.scraped_text


        }

        this.regexpValidation = Validation.debouncedAsyncValidator<string>(v => {
          return this.alyvixApi.testScrapedText({ regexp: v, scraped_text: this.scraped }).pipe(map(res => {
            return res ? null : { regexp: { invalidRegexp: v } }
          }))
        })

        this.regex = new FormControl(this.node.box.features.T.regexp, null, this.regexpValidation);
      })
    }

    this.global.nativeGlobal().setTypeNode("T");
  }

}
