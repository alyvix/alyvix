import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AxModalComponent } from './ax-modal.component';

describe('AxModalComponent', () => {
  let component: AxModalComponent;
  let fixture: ComponentFixture<AxModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AxModalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AxModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
