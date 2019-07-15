import { Component, OnInit } from '@angular/core';

@Component({
    selector: 'ax-selector',
    templateUrl: './ax-selector.component.html',
    styleUrls: ['./ax-selector.component.scss']
  })
  export class AxSelectorComponent implements OnInit {
    
    data: any[] = [
      {name:'aaa',title:'bbb'},
      {name:'aaa',title:'bbb'},
      {name:'aaa',title:'bbb'},
      {name:'aaa',title:'bbb'},
      {name:'aaa',title:'bbb'},
    ]

    selectorColumns = ['name','transactionGroup','dateModified','timeout','break','measure','warning','critical','resolution','screen'] 

    ngOnInit(): void {
    }

  }