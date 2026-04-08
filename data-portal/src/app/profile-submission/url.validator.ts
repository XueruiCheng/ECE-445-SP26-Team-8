import { AbstractControl, ValidationErrors } from '@angular/forms';

export function optionalUrlValidator(control: AbstractControl): ValidationErrors | null {
  if (!control.value) return null;
  try {
    new URL(control.value);
    return null;
  } catch {
    return { invalidUrl: true };
  }
}
