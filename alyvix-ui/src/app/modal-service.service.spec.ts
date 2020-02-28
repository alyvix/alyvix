import { TestBed } from '@angular/core/testing';

import { ModalServiceService } from './modal-service.service';

describe('ModalServiceService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: ModalServiceService = TestBed.get(ModalServiceService);
    expect(service).toBeTruthy();
  });
});
