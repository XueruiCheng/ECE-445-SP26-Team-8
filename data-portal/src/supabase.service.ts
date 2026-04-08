import { Injectable, signal, computed } from '@angular/core';
import { createClient, SupabaseClient, Session } from '@supabase/supabase-js';
import { environment } from './environments/environment';

@Injectable({
  providedIn: 'root',
})
export class SupabaseService {
  private supabase: SupabaseClient;

  private _session = signal<Session | null>(null);
  readonly session = this._session.asReadonly();
  readonly user = computed(() => this._session()?.user ?? null);
  readonly isAuthenticated = computed(() => this._session() !== null);

  constructor() {
    this.supabase = createClient(
      environment.supabaseUrl,
      environment.supabaseKey
    );

    this.supabase.auth.getSession().then(({ data }) => {
      this._session.set(data.session);
    });

    this.supabase.auth.onAuthStateChange((_event, session) => {
      this._session.set(session);
    });
  }

  getSessionDirect() {
    return this.supabase.auth.getSession();
  }

  async signInWithGoogle(): Promise<void> {
    await this.supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin + '/profile' },
    });
  }

  async signInWithMicrosoft(): Promise<void> {
    await this.supabase.auth.signInWithOAuth({
      provider: 'azure',
      options: { redirectTo: window.location.origin + '/profile' },
    });
  }

  async signOut(): Promise<void> {
    await this.supabase.auth.signOut();
  }

  getTodos() {
    return this.supabase.from('todos').select('*');
  }
}