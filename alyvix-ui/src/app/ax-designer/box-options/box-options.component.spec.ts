import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BoxOptionsComponent } from './box-options.component';

describe('BoxOptionsComponent', () => {
  let component: BoxOptionsComponent;
  let fixture: ComponentFixture<BoxOptionsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BoxOptionsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BoxOptionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
