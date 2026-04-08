import { Component, input, output } from '@angular/core';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-work-publications-step',
  imports: [ReactiveFormsModule],
  templateUrl: './work-publications-step.component.html',
  styleUrl: './work-publications-step.component.less',
})
export class WorkPublicationsStepComponent {
  formGroup = input.required<FormGroup>();

  next = output<void>();
  back = output<void>();

  onNext(): void {
    this.formGroup().markAllAsTouched();
    if (this.formGroup().valid) {
      this.next.emit();
    }
  }
}
