import { Component } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-root',
  templateUrl: './selector.component.html',
  styleUrls: ['./selector.component.scss']
})
export class SelectorComponent {
  title = 'app';

  totalHeight = 590;

  production:boolean = environment.production;

  constructor() {
  }

}
