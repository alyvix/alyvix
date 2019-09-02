import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AxTableComponent } from './ax-table.component';

describe('AxTableComponent', () => {
  let component: AxTableComponent;
  let fixture: ComponentFixture<AxTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AxTableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AxTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
