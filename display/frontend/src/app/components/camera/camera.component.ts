import { Component, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-camera',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="camera-screen">
      <div class="frame-container">
        <div class="corner top-left"></div>
        <div class="corner top-right"></div>
        <div class="corner bottom-left"></div>
        <div class="corner bottom-right"></div>

        <div class="feed-area">
          <div class="scan-line"></div>
          <div class="feed-placeholder">
            <div class="crosshair"></div>
          </div>
        </div>

        <div class="status-bar">
          <span class="status-dot"></span>
          <span class="status-text">SCANNING</span>
        </div>
      </div>

      <div class="instructions">HOLD STILL — ANALYZING FEATURES</div>
    </div>
  `,
  styleUrl: './camera.component.less'
})
export class CameraComponent {}
