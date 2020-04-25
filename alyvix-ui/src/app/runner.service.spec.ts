import { TestBed } from '@angular/core/testing';

import { RunnerService } from './runner.service';

describe('RunnerService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: RunnerService = TestBed.get(RunnerService);
    expect(service).toBeTruthy();
  });
});
