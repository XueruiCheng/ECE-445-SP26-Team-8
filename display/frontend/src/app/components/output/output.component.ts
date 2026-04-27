import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { MirrorStateService } from '../../services/mirror-state.service';
import { apiUrl } from '../../services/websocket.service';

@Component({
  selector: 'app-output',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (mirrorState.matchResult$ | async; as result) {
      <div class="output-screen">
        <div class="result-container">
          <div class="image-panel fade-in">
            <div class="image-frame">
              <img [src]="resolveUrl(result.image_url)" [alt]="result.name" />
            </div>
            <div class="match-badge">
              <span class="match-pct">{{ (result.similarity * 100).toFixed(0) }}%</span>
              <span class="match-label">MATCH</span>
            </div>
          </div>

          <div class="info-panel">
            <div class="label fade-in-delay-1">YOUR MATCH</div>
            <h1 class="name fade-in-delay-1">{{ result.name }}</h1>
            <div class="position fade-in-delay-2">{{ result.position }}</div>
            <div class="role fade-in-delay-2">{{ result.role }}</div>

            <div class="research-areas fade-in-delay-3">
              @for (area of result.research_areas; track area) {
                <span class="chip">{{ area }}</span>
              }
            </div>

            @if (result.summary) {
              <div class="summary-block fade-in-delay-4">
                <div class="summary-label">SUMMARY</div>
                <p class="summary-text">{{ result.summary }}</p>
              </div>
            }
          </div>
        </div>
      </div>
    }
  `,
  styleUrl: './output.component.less'
})
export class OutputComponent {
  mirrorState = inject(MirrorStateService);
  resolveUrl = apiUrl;
}
