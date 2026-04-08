import { Component, input, output } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'app-review-step',
  templateUrl: './review-step.component.html',
  styleUrl: './review-step.component.less',
})
export class ReviewStepComponent {
  formGroup = input.required<FormGroup>();
  headshotPreviewUrl = input<string | null>(null);

  editStep = output<number>();
  submit = output<void>();
  back = output<void>();

  get personal() {
    return this.formGroup().get('personal')?.value;
  }

  get academic() {
    return this.formGroup().get('academic')?.value;
  }

  get work() {
    return this.formGroup().get('work')?.value;
  }
}
