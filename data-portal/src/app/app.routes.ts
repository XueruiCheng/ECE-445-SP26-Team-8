import { Routes } from '@angular/router';
import { ProfileSubmissionComponent } from './profile-submission/profile-submission.component';

export const routes: Routes = [
  { path: '', component: ProfileSubmissionComponent },
  { path: '**', redirectTo: '' },
];
