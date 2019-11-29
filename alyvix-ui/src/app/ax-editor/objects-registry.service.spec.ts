import { TestBed } from '@angular/core/testing';

import { ObjectsRegistryService } from './objects-registry.service';

describe('ObjectsRegistryService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: ObjectsRegistryService = TestBed.get(ObjectsRegistryService);
    expect(service).toBeTruthy();
  });
});
