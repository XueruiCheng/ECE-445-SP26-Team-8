import { Component, input, output } from '@angular/core';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-personal-info-step',
  imports: [ReactiveFormsModule],
  templateUrl: './personal-info-step.component.html',
  styleUrl: './personal-info-step.component.less',
})
export class PersonalInfoStepComponent {
  formGroup = input.required<FormGroup>();
  headshotPreviewUrl = input<string | null>(null);
  videoPreviewUrl = input<string | null>(null);

  headshotSelected = output<File>();
  videoSelected = output<File>();
  next = output<void>();

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.headshotSelected.emit(file);
    }
  }

  onVideoSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.videoSelected.emit(file);
    }
  }

  get bioLength(): number {
    return this.formGroup().get('bio')?.value?.length ?? 0;
  }

  onNext(): void {
    this.formGroup().markAllAsTouched();
    if (this.formGroup().valid) {
      this.next.emit();
    }
  }
}
