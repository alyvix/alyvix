import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AxDesignerComponent } from './ax-designer.component';

describe('AxDesignerComponent', () => {
  let component: AxDesignerComponent;
  let fixture: ComponentFixture<AxDesignerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AxDesignerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AxDesignerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
