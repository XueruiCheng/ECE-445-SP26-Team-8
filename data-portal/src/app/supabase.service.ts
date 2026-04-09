import { Injectable, signal, computed } from '@angular/core';
import { createClient, SupabaseClient, Session } from '@supabase/supabase-js';
import { environment } from '../environment';
import { Profile } from './profile-submission/profile-submission.component';

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
      options: { redirectTo: window.location.origin },
    });
  }

  async signInWithMicrosoft(): Promise<void> {
    await this.supabase.auth.signInWithOAuth({
      provider: 'azure',
      options: { 
        scopes: 'email profile',
        redirectTo: window.location.origin 
      },
    });
  }

  async signOut(): Promise<void> {
    await this.supabase.auth.signOut();
  }

  getTodos() {
    return this.supabase.from('todos').select('*');
  }

  async upsertProfile(profile : Profile): Promise<void> {
    const { data, error } = await this.supabase
      .from('profiles')
      .upsert(profile, { onConflict : 'id'})

    if (error) {
      throw error;
    }
  }

  async getUser() {
    const { data : { user } } = await this.supabase.auth.getUser();

    if (!user) {
      throw new Error('No authenticated user');
    }

    return user;
  }

  async uploadHeadshot(userId: string, file: File): Promise<string> {
    const filePath = `${userId}/headshot.${file.name.split('.').pop()}`;
    const { error } = await this.supabase.storage
      .from('headshots')
      .upload(filePath, file, { upsert: true });

    if (error) {
      throw error;
    }

    return filePath;
  }

  async uploadBioVideo(userId: string, file: File): Promise<string> {
    const filePath = `${userId}/bio_video.mp4`;
    const { error } = await this.supabase.storage
      .from('bio_videos')
      .upload(filePath, file, { upsert: true });

    if (error) {
      throw error;
    }

    return filePath;
  }

  async getHeadshotSignedUrl(path: string): Promise<string> {
    const { data, error } = await this.supabase.storage
      .from('headshots')
      .createSignedUrl(path, 3600);

    if (error) {
      throw error;
    }

    return data.signedUrl;
  }

  async getBioVideoSignedUrl(path: string): Promise<string> {
    const { data, error } = await this.supabase.storage
      .from('bio_videos')
      .createSignedUrl(path, 3600);

    if (error) {
      throw error;
    }

    return data.signedUrl;
  }
}