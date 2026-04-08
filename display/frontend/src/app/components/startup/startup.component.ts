import { Component, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-startup',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="startup-screen">
      <div class="scanline"></div>
      <div class="content">
        <div class="subtitle fade-in-delay-1">QUANTUM MIRROR</div>
        <h1 class="title fade-in">Choose Your Future</h1>
        <div class="divider fade-in-delay-2"></div>
        <div class="hint fade-in-delay-3">STEP CLOSER TO BEGIN</div>
      </div>
    </div>
  `,
  styleUrl: './startup.component.less'
})
export class StartupComponent {}
