import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RComponent } from './r.component';

describe('RComponent', () => {
  let component: RComponent;
  let fixture: ComponentFixture<RComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
