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

  _node:TreeNode

  @Input()
  set node(node: TreeNode) {
    this._node = node;
    this.onNodeChange();
  }

  get node():TreeNode {
    return this._node;
  }


  regexpValidation = Validation.debouncedAsyncValidator<string>(v => {
    return this.alyvixApi.testScrapedText({ regexp: v, scraped_text: this.scraped }).pipe(map(res => {
      this.regExWarning = res.match == 'yellow'
      return res.match != 'red' ? null : { regexp: { invalidRegexp: v } }
    }))

  })

  regex: FormControl = new FormControl('', null, this.regexpValidation);



  isScraper(): boolean {
    return this.node.box.features.T.type == 'scraper'
  }

  scraped: string = ""

  regExWarning:boolean = false

  onNodeChange() {
    if (!this.node.box.features.T.type) {
      this.node.box.features.T.type = "detection";
    }
    if (this.node && this.node.box) {
      this.alyvixApi.getScrapedText(this.node.box).subscribe(x => {
        this.scraped = x.scraped_text;
        if (!this.node.box.features.T.regexp) {
          this.node.box.features.T.regexp = x.reg_exp
        }
      })
    }

    this.global.nativeGlobal().setTypeNode("T");
  }
  
  ngOnInit() { 
    
  }

}
