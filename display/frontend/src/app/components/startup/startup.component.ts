import { Component, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-startup',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="startup-screen">
      <div class="scanline"></div>
      <div class="content">
        <h1 class="title fade-in">Choose Your Future</h1>
        <div class="divider fade-in-delay-2"></div>
      </div>
    </div>
  `,
  styleUrl: './startup.component.less'
})
export class StartupComponent {
  
}
