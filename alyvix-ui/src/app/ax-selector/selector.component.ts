import { Component } from '@angular/core';
import { AxModel } from '../ax-model/model';
import { AxModelMock } from '../ax-model/mock';
import { environment } from 'src/environments/environment';
import { GroupsFlag } from '../ax-model/ax-global';

@Component({
  selector: 'app-root',
  templateUrl: './selector.component.html',
  styleUrls: ['./selector.component.scss']
})
export class SelectorComponent {
  title = 'app';

  axModel:AxModel = AxModelMock.get()
  flags: GroupsFlag = AxModelMock.flags()

  totalHeight = 590;

  production:boolean = environment.production;

  constructor() {
  }

}
