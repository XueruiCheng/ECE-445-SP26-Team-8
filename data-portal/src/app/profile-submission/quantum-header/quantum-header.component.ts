import {
  Component,
  ElementRef,
  OnDestroy,
  afterNextRender,
  inject,
  input,
  signal,
  viewChild,
} from '@angular/core';
import { Router } from '@angular/router';
import { SupabaseService } from '../../supabase.service';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  color: string;
  phase: number;
}

@Component({
  selector: 'app-quantum-header',
  templateUrl: './quantum-header.component.html',
  styleUrl: './quantum-header.component.less',
})
export class QuantumHeaderComponent implements OnDestroy {
  readonly showTitle = input(true);
  private canvas = viewChild<ElementRef<HTMLCanvasElement>>('canvas');

  protected readonly supabase = inject(SupabaseService);
  private readonly router = inject(Router);
  protected dropdownOpen = signal(false);

  toggleDropdown(): void {
    this.dropdownOpen.update(v => !v);
  }

  async signOut(): Promise<void> {
    await this.supabase.signOut();
    this.dropdownOpen.set(false);
    this.router.navigate(['/login']);
  }
  private animationId = 0;
  private particles: Particle[] = [];
  private resizeHandler: (() => void) | null = null;

  constructor() {
    afterNextRender(() => this.initCanvas());
  }

  ngOnDestroy(): void {
    cancelAnimationFrame(this.animationId);
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
    }
  }

  private initCanvas(): void {
    const canvasEl = this.canvas()?.nativeElement;
    if (!canvasEl) return;

    const ctx = canvasEl.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvasEl.width = window.innerWidth;
      canvasEl.height = window.innerHeight;
    };
    resize();
    this.resizeHandler = resize;
    window.addEventListener('resize', resize);

    const colors = [
      'rgba(232, 74, 39, 0.35)',
      'rgba(255, 111, 66, 0.3)',
      'rgba(19, 41, 75, 0.3)',
      'rgba(232, 74, 39, 0.15)',
    ];

    for (let i = 0; i < 45; i++) {
      this.particles.push({
        x: Math.random() * canvasEl.width,
        y: Math.random() * canvasEl.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.3,
        radius: Math.random() * 2 + 1,
        color: colors[Math.floor(Math.random() * colors.length)],
        phase: Math.random() * Math.PI * 2,
      });
    }

    let frame = 0;
    const animate = () => {
      frame++;
      // Render every 2nd frame for performance
      if (frame % 2 === 0) {
        this.draw(ctx, canvasEl.width, canvasEl.height);
      }
      this.animationId = requestAnimationFrame(animate);
    };
    animate();
  }

  private draw(ctx: CanvasRenderingContext2D, w: number, h: number): void {
    ctx.clearRect(0, 0, w, h);

    const connectionDistance = 120;
    const time = Date.now() * 0.001;

    for (const p of this.particles) {
      p.x += p.vx;
      p.y += p.vy + Math.sin(time + p.phase) * 0.15;

      if (p.x < 0) p.x = w;
      if (p.x > w) p.x = 0;
      if (p.y < 0) p.y = h;
      if (p.y > h) p.y = 0;
    }

    // Draw connections
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const dx = this.particles[i].x - this.particles[j].x;
        const dy = this.particles[i].y - this.particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < connectionDistance) {
          const alpha = (1 - dist / connectionDistance) * 0.15;
          ctx.beginPath();
          ctx.strokeStyle = `rgba(232, 74, 39, ${alpha})`;
          ctx.lineWidth = 0.5;
          ctx.moveTo(this.particles[i].x, this.particles[i].y);
          ctx.lineTo(this.particles[j].x, this.particles[j].y);
          ctx.stroke();
        }
      }
    }

    // Draw particles
    for (const p of this.particles) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();
    }
  }
}
