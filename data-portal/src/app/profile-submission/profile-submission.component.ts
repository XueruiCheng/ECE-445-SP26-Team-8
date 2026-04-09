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

export interface Profile {
  id: string;
  email: string;
  full_name: string | null;
  headshot_path: string | null;
  bio_video_path: string | null;
  short_bio: string | null;
  personal_website: string | null;
  education_level: string | null;
  institution: string | null;
  role_title: string | null;
  field_of_study: string | null;
  publications: string | null;
  additional_info: string | null;
}

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
  submitting = signal(false);
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

  async onSubmit(): Promise<void> {
    if (this.profileForm.valid) {
      this.submitting.set(true);
      window.scrollTo({ top: 0, behavior: 'smooth' });

      try {
        const user = await this.supabase.getUser();

        const headshotFile = this.profileForm.controls.personal.controls.headshot.value;
        const videoFile = this.profileForm.controls.personal.controls.video.value;

        const [headshotPath, videoPath] = await Promise.all([
          headshotFile ? this.supabase.uploadHeadshot(user.id, headshotFile) : Promise.resolve(null),
          videoFile ? this.supabase.uploadBioVideo(user.id, videoFile) : Promise.resolve(null),
        ]);

        const profile : Profile = {
          id: user.id,
          email: user.email ?? '',
          full_name: this.profileForm.controls.personal.controls.name.value,
          headshot_path: headshotPath,
          bio_video_path: videoPath,
          short_bio: this.profileForm.controls.personal.controls.bio.value,
          personal_website: this.profileForm.controls.personal.controls.website.value || null,
          education_level: this.profileForm.controls.academic.controls.educationLevel.value,
          institution: this.profileForm.controls.academic.controls.institution.value,
          role_title: this.profileForm.controls.academic.controls.role.value,
          field_of_study: this.profileForm.controls.academic.controls.fieldOfStudy.value,
          publications: this.profileForm.controls.work.controls.publications.value,
          additional_info: this.profileForm.controls.work.controls.additionalInfo.value || null,
        };

        await this.supabase.upsertProfile(profile);
        this.submitted.set(true);
      } catch (err) {
        console.error('Profile submission error:', err);
        this.submitting.set(false);
      }
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
    this.submitting.set(false);
    this.currentStep.set(1);
  }
}
