import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CentralPanelComponent } from './central-panel.component';

describe('CentralPanelComponent', () => {
  let component: CentralPanelComponent;
  let fixture: ComponentFixture<CentralPanelComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CentralPanelComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CentralPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
