import { Component, input, output } from '@angular/core';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-academic-info-step',
  imports: [ReactiveFormsModule],
  templateUrl: './academic-info-step.component.html',
  styleUrl: './academic-info-step.component.less',
})
export class AcademicInfoStepComponent {
  formGroup = input.required<FormGroup>();

  next = output<void>();
  back = output<void>();

  educationLevels = [
    "Bachelor's",
    "Master's",
    'PhD',
    'Postdoc',
    'Other',
  ];

  onNext(): void {
    this.formGroup().markAllAsTouched();
    if (this.formGroup().valid) {
      this.next.emit();
    }
  }
}
