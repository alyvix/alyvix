import { Observable, BehaviorSubject, of } from "rxjs";
import { ValidationErrors, AsyncValidatorFn, AbstractControl } from "@angular/forms";
import { switchMap, debounceTime, catchError, take } from "rxjs/operators";



//https://stackoverflow.com/questions/36919011/how-to-add-debounce-time-to-an-async-validator-in-angular-2

export class Validation {

/**
 * From a given remove validation fn, it returns the AsyncValidatorFn
 * @param remoteValidation: The remote validation fn that returns an observable of <ValidationErrors | null>
 * @param debounceMs: The debounce time
 */
static debouncedAsyncValidator<TValue>(
    remoteValidation: (v: TValue) => Observable<ValidationErrors | null>,
    remoteError: ValidationErrors = { remote: "Unhandled error occurred." },
    debounceMs = 300
  ): AsyncValidatorFn {
    const values = new BehaviorSubject<TValue>(null);
    const validity$ = values.pipe(
      debounceTime(debounceMs),
      switchMap(remoteValidation),
      catchError(() => of(remoteError)),
      take(1)
    );
  
    return (control: AbstractControl) => {
      if (!control.value) return of(null);
      values.next(control.value);
      return validity$;
    };
  }

}