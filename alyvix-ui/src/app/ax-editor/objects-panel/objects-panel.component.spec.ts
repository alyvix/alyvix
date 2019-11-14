import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ObjectsPanelComponent } from './objects-panel.component';

describe('ObjectsPanelComponent', () => {
  let component: ObjectsPanelComponent;
  let fixture: ComponentFixture<ObjectsPanelComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ObjectsPanelComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ObjectsPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
