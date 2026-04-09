import { Component, OnDestroy, signal, inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { optionalUrlValidator } from './url.validator';
import { QuantumHeaderComponent } from './quantum-header/quantum-header.component';
import { StepIndicatorComponent } from './step-indicator/step-indicator.component';
import { PersonalInfoStepComponent } from './personal-info-step/personal-info-step.component';
import { AcademicInfoStepComponent } from './academic-info-step/academic-info-step.component';
import { WorkPublicationsStepComponent } from './work-publications-step/work-publications-step.component';
import { ReviewStepComponent } from './review-step/review-step.component';
import { SupabaseService } from '../supabase.service'; 

@Component({
  selector: 'app-profile-submission',
  imports: [
    QuantumHeaderComponent,
    StepIndicatorComponent,
    PersonalInfoStepComponent,
    AcademicInfoStepComponent,
    WorkPublicationsStepComponent,
    ReviewStepComponent,
  ],
  templateUrl: './profile-submission.component.html',
  styleUrl: './profile-submission.component.less',
})
export class ProfileSubmissionComponent implements OnDestroy {
  currentStep = signal(1);
  submitted = signal(false);
  headshotPreviewUrl = signal<string | null>(null);
  videoPreviewUrl = signal<string | null>(null);

  private supabase = inject(SupabaseService);

  profileForm = new FormGroup({
    personal: new FormGroup({
      name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
      headshot: new FormControl<File | null>(null, { validators: [Validators.required] }),
      bio: new FormControl('', {
        nonNullable: true,
        validators: [Validators.required, Validators.maxLength(300)],
      }),
      website: new FormControl('', { nonNullable: true, validators: [optionalUrlValidator] }),
      video: new FormControl<File | null>(null, { validators: [Validators.required] }),
    }),
    academic: new FormGroup({
      educationLevel: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
      institution: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
      role: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
      fieldOfStudy: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    }),
    work: new FormGroup({
      publications: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
      additionalInfo: new FormControl('', { nonNullable: true }),
    }),
  });

  get personalGroup(): FormGroup {
    return this.profileForm.get('personal') as FormGroup;
  }

  get academicGroup(): FormGroup {
    return this.profileForm.get('academic') as FormGroup;
  }

  get workGroup(): FormGroup {
    return this.profileForm.get('work') as FormGroup;
  }

  ngOnDestroy(): void {
    const url = this.headshotPreviewUrl();
    if (url) {
      URL.revokeObjectURL(url);
    }
    const videoUrl = this.videoPreviewUrl();
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
    }
  }

  onHeadshotSelected(file: File): void {
    const prevUrl = this.headshotPreviewUrl();
    if (prevUrl) {
      URL.revokeObjectURL(prevUrl);
    }
    this.headshotPreviewUrl.set(URL.createObjectURL(file));
    this.profileForm.get('personal.headshot')?.setValue(file);
    this.profileForm.get('personal.headshot')?.markAsTouched();
  }

  onVideoSelected(file: File): void {
    const prevUrl = this.videoPreviewUrl();
    if (prevUrl) {
      URL.revokeObjectURL(prevUrl);
    }
    this.videoPreviewUrl.set(URL.createObjectURL(file));
    this.profileForm.get('personal.video')?.setValue(file);
    this.profileForm.get('personal.video')?.markAsTouched();
  }

  goToStep(step: number): void {
    this.currentStep.set(step);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  nextStep(): void {
    this.goToStep(this.currentStep() + 1);
  }

  prevStep(): void {
    this.goToStep(this.currentStep() - 1);
  }

  onSubmit(): void {
    if (this.profileForm.valid) {
      this.submitted.set(true);
      // call supabase insert function
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  resetForm(): void {
    this.profileForm.reset();
    const url = this.headshotPreviewUrl();
    if (url) URL.revokeObjectURL(url);
    this.headshotPreviewUrl.set(null);
    const videoUrl = this.videoPreviewUrl();
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    this.videoPreviewUrl.set(null);
    this.submitted.set(false);
    this.currentStep.set(1);
  }
}
