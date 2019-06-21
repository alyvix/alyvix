import { TestBed } from '@angular/core/testing';

import { AlyvixApiService } from './alyvix-api.service';

describe('AlyvixApiService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: AlyvixApiService = TestBed.get(AlyvixApiService);
    expect(service).toBeTruthy();
  });
});
