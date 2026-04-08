import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-step-indicator',
  templateUrl: './step-indicator.component.html',
  styleUrl: './step-indicator.component.less',
})
export class StepIndicatorComponent {
  currentStep = input.required<number>();
  totalSteps = input<number>(4);
  stepLabels = input<string[]>([
    'Personal Info',
    'Academic Info',
    'Publications',
    'Review',
  ]);

  stepSelected = output<number>();

  steps(): number[] {
    return Array.from({ length: this.totalSteps() }, (_, i) => i + 1);
  }

  onStepClick(step: number): void {
    if (step < this.currentStep()) {
      this.stepSelected.emit(step);
    }
  }
}
