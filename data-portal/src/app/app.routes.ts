import { Routes } from '@angular/router';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'profile',
    loadComponent: () =>
      import('./profile-submission/profile-submission.component').then(
        (m) => m.ProfileSubmissionComponent
      ),
    canActivate: [authGuard],
  },
  { path: '**', redirectTo: '' },
];
