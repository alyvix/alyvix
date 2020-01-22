import { Component, OnInit, Input, ViewChild, Injectable, Inject } from '@angular/core';
import { TreeNode, AxDesignerService } from '../../ax-designer-service';
import { FormControl, AsyncValidatorFn, AbstractControl } from '@angular/forms';
import { AlyvixApiService } from 'src/app/alyvix-api.service';
import { map, first } from 'rxjs/operators';
import { Validation } from 'src/app/utils/validators';
import { DesignerGlobal, GroupsFlag } from "src/app/ax-designer/ax-global";

@Component({
  selector: 'ax-designer-t',
  templateUrl: './t.component.html',
  styleUrls: ['./t.component.scss']
})
export class TComponent implements OnInit {

  constructor(private alyvixApi: AlyvixApiService, @Inject('GlobalRefDesigner') private global: DesignerGlobal, private axDesigerService:AxDesignerService) { }

  _node:TreeNode
  loading:boolean

  @Input()
  set node(node: TreeNode) {
    this._node = node;
    this.loading = true;
    this.onNodeChange();
  }

  get node():TreeNode {
    return this._node;
  }


  regexpValidation = Validation.debouncedAsyncValidator<string>(v => {
    return this.alyvixApi.testScrapedText({ regexp: v, scraped_text: this.scraped }).pipe(map(res => {
      this.regExWarning = res.match == 'yellow'
      this.loading = false;
      return res.match != 'red' ? null : { regexp: { invalidRegexp: v } }
    }))

  })

  regex: FormControl = new FormControl('', null, this.regexpValidation);



  isMap(): boolean {
    return this.node.box.features.T.type == 'map'
  }

  scraped: string = ""

  regExWarning:boolean = false;

  maps:string[] = []


  onRegexChange() {
    this.node.box.features.T.regexp = this.regex.value;
  }

  numberLogicValidation = Validation.debouncedAsyncValidator<string>(v => {
    return this.alyvixApi.checkTextNumber({ logic: v, scraped_text: this.scraped }).pipe(map(res => {
      return res.result ? null : { number: { invalidNumber: v } }
    }))
  })
  numberLogic: FormControl = new FormControl('', null, this.numberLogicValidation);

  onNumberLogicChange() {
    this.node.box.features.T.logic = this.numberLogic.value;
  }

  dateLogicValidation = Validation.debouncedAsyncValidator<string>(v => {
    return this.alyvixApi.checkTextDate({ logic: v, scraped_text: this.scraped }).pipe(map(res => {
      return res.result ? null : { number: { invalidNumber: v } }
    }))
  })
  dateLogic: FormControl = new FormControl('', null, this.dateLogicValidation);
  onDateLogicChange() {
    this.node.box.features.T.logic = this.dateLogic.value;
  }

  onNodeChange() {
    if (!this.node.box.features.T.type) {
      this.node.box.features.T.type = "detect";
    }
    if (!this.node.box.features.T.detection && this.node.box.features.T.type === 'detect') {
      this.node.box.features.T.detection = "regex";
    }
    if (!this.node.box.features.T.map && this.node.box.features.T.type === 'map') {
      this.node.box.features.T.map = "None";
    }
    if (this.node && this.node.box) {
      let object_name = ''
      this.global.axModel().pipe(first()).subscribe(axModel => object_name = axModel.object_name)
      this.alyvixApi.getScrapedText(this.axDesigerService.indexSelectedNode(this.node),object_name,this.node.box).subscribe(x => {
        this.scraped = x.scraped_text;
        if (!this.node.box.features.T.regexp) {
          if(this.node.box.features.T.detection === "regex") {
            this.node.box.features.T.regexp = x.reg_exp
          }
          this.regex.setValue(x.reg_exp);
        } else {
          this.regex.setValue(this.node.box.features.T.regexp);
        }
        if(this.node.box.features.T.logic && this.node.box.features.T.detection === 'number') {
          this.numberLogic.setValue(this.node.box.features.T.logic);
        }
        if(this.node.box.features.T.logic && this.node.box.features.T.detection === 'date') {
          this.dateLogic.setValue(this.node.box.features.T.logic);
        }
      })
    }

    this.global.setTypeNode("T");
  }

  changeScrapMode(mode) {
    this.node.box.features.T.detection = mode;
    if(mode === 'number') {
      this.numberLogic.setValue('more_than_zero');
      this.node.box.features.T.logic = this.numberLogic.value;
      delete this.node.box.features.T.regexp;
    } else if(mode === 'date') {
      this.dateLogic.setValue('last_hour');
      this.node.box.features.T.logic = this.dateLogic.value;
      delete this.node.box.features.T.regexp;
    } else {
      delete this.node.box.features.T.logic;
      this.node.box.features.T.regexp = this.regex.value;
    }
  }

  changeType(type) {
    this.node.box.features.T.type = type;
    if(type === 'detect') {
      this.node.box.features.T.detection = "regex";
      this.node.box.features.T.regexp = this.regex.value;
      delete this.node.box.features.T.map;
    } else {
      this.node.box.features.T.map = "None";
      delete this.node.box.features.T.logic;
      delete this.node.box.features.T.regexp;
      delete this.node.box.features.T.detection;
    }
  }

  ngOnInit() {
    this.global.axMaps().subscribe(maps => {
      if(maps) {
        this.maps = Object.keys(maps);
      }
    });
  }

}
