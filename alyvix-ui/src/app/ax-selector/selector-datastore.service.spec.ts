import { TestBed } from '@angular/core/testing';

import { SelectorDatastoreService } from './selector-datastore.service';

describe('SelectorDatastoreService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: SelectorDatastoreService = TestBed.get(SelectorDatastoreService);
    expect(service).toBeTruthy();
  });
});
