import { Component, effect, inject } from '@angular/core';
import { Router } from '@angular/router';
import { SupabaseService } from '../supabase.service';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrl: './login.component.less',
})
export class LoginComponent {
  private supabase = inject(SupabaseService);
  private router = inject(Router);

  constructor() {
    effect(() => {
      if (this.supabase.isAuthenticated()) {
        this.router.navigate(['/profile']);
      }
    });
  }

  signInWithGoogle(): void {
    this.supabase.signInWithGoogle();
  }

  signInWithMicrosoft(): void {
    this.supabase.signInWithMicrosoft();
  }
}
