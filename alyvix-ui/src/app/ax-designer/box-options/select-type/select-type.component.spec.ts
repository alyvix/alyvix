import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SelectTypeComponent } from './select-type.component';

describe('SelectTypeComponent', () => {
  let component: SelectTypeComponent;
  let fixture: ComponentFixture<SelectTypeComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SelectTypeComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SelectTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
