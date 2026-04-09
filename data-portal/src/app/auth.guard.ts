import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SupabaseService } from './supabase.service';

export const authGuard: CanActivateFn = async () => {
  const supabase = inject(SupabaseService);
  const router = inject(Router);

  if (supabase.isAuthenticated()) {
    return true;
  }

  const { data } = await supabase.getSessionDirect();
  if (data.session) {
    return true;
  }

  return router.createUrlTree(['/']);
};
