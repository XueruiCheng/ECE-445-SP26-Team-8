import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { MirrorState, MatchResult } from '../models/mirror-state.model';

@Injectable({ providedIn: 'root' })
export class MirrorStateService {
  private stateSubject = new BehaviorSubject<MirrorState>(MirrorState.IDLE);
  private matchResultSubject = new BehaviorSubject<MatchResult | null>(null);

  state$ = this.stateSubject.asObservable();
  matchResult$ = this.matchResultSubject.asObservable();

  get currentState(): MirrorState {
    return this.stateSubject.value;
  }

  goToIdle(): void {
    this.matchResultSubject.next(null);
    this.stateSubject.next(MirrorState.IDLE);
  }

  goToStartup(): void {
    this.stateSubject.next(MirrorState.STARTUP);
  }

  goToCamera(): void {
    this.stateSubject.next(MirrorState.CAMERA);
  }

  goToOutput(result: MatchResult): void {
    this.matchResultSubject.next(result);
    this.stateSubject.next(MirrorState.OUTPUT);
  }

  cycleState(): void {
    const order = [MirrorState.IDLE, MirrorState.STARTUP, MirrorState.CAMERA, MirrorState.OUTPUT];
    const currentIndex = order.indexOf(this.currentState);
    const nextIndex = (currentIndex + 1) % order.length;
    const nextState = order[nextIndex];

    if (nextState === MirrorState.OUTPUT) {
      this.goToOutput(this.getMockResult());
    } else {
      this.stateSubject.next(nextState);
    }
  }

  private getMockResult(): MatchResult {
    return {
      name: 'Marcela Carena',
      similarity: 0.87,
      role: 'Research Faculty Office of Executive Leadership',
      position: 'Executive Director',
      research_areas: ['Particle Physics'],
      image_url: '/images/Marcela Carena.jpg',
      profile_url: 'https://perimeterinstitute.ca/people/marcela-carena'
    };
  }
}
