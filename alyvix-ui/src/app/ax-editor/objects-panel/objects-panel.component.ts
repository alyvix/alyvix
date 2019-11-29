import { Component, OnInit, ViewChild } from '@angular/core';
import { CdkDropList } from '@angular/cdk/drag-drop';
import { ObjectsRegistryService } from '../objects-registry.service';

@Component({
  selector: 'app-objects-panel',
  templateUrl: './objects-panel.component.html',
  styleUrls: ['./objects-panel.component.scss']
})
export class ObjectsPanelComponent implements OnInit {

  constructor(private objectRegistry:ObjectsRegistryService) { }



  objectLists:CdkDropList[] = [];


  ngOnInit() {

    this.objectRegistry.objectList().subscribe(x => {
      setTimeout(() => {
        this.objectLists = x;
      }, 200);
    });
  }

  dropped(event) {
    console.log(event);
  }

}
