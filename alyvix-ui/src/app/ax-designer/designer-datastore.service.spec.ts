import { TestBed } from '@angular/core/testing';

import { DesignerDatastoreService } from './designer-datastore.service';

describe('DesignerDatastoreService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: DesignerDatastoreService = TestBed.get(DesignerDatastoreService);
    expect(service).toBeTruthy();
  });
});
