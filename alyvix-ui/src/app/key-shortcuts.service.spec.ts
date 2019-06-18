import { TestBed } from '@angular/core/testing';

import { KeyShortcutsService } from './key-shortcuts.service';

describe('KeyShortcutsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: KeyShortcutsService = TestBed.get(KeyShortcutsService);
    expect(service).toBeTruthy();
  });
});
