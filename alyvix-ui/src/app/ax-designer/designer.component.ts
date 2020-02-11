import { Component } from '@angular/core';
import { AxModel } from '../ax-model/model';
import { AxModelMock } from '../ax-model/mock';
import { environment } from 'src/environments/environment';
import { GroupsFlag } from './ax-global';
import { KeyShortcutsService } from './key-shortcuts.service';

@Component({
  selector: 'app-root',
  templateUrl: './designer.component.html',
  styleUrls: ['./designer.component.scss']
})
export class DesignerComponent {
  title = 'app';

  axModel:AxModel = AxModelMock.get()
  flags: GroupsFlag = AxModelMock.flags()

  totalHeight = 590;

  production:boolean = environment.production;

  constructor(private keyShortcuts:KeyShortcutsService) {
    this.keyShortcuts.loadShortcuts()
  }

}
