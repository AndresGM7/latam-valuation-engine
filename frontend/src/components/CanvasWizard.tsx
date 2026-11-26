/**
 * Main wizard orchestrator. Holds the current step, gates navigation
 * behind zod-validated state, and renders the Stepper + the active
 * step component.
 *
 * The wizard lives inside <WizardProvider> (see App.tsx) so each step
 * can read/write the same BusinessModel via useWizard().
 */

import { useState, useCallback } from "react";

import { Stepper } from "./Stepper";
import { WelcomeStep } from "./steps/WelcomeStep";
import { CustomerSegmentsStep } from "./steps/CustomerSegmentsStep";
import { ValuePropositionStep } from "./steps/ValuePropositionStep";
import { ChannelsStep } from "./steps/ChannelsStep";
import { RevenueStreamsStep } from "./steps/RevenueStreamsStep";
import { KeyBlocksStep } from "./steps/KeyBlocksStep";
import { CostStructureStep } from "./steps/CostStructureStep";
import { ExperimentsStep } from "./steps/ExperimentsStep";
import { ReviewStep } from "./steps/ReviewStep";
import { WIZARD_STEPS } from "./Stepper";

interface StepProps {
  goNext: () => void;
  goBack?: () => void;
}

const STEP_COMPONENTS: Array<(p: StepProps) => React.JSX.Element> = [
  (p) => <WelcomeStep {...p} />,
  (p) => <CustomerSegmentsStep {...p} />,
  (p) => <ValuePropositionStep {...p} />,
  (p) => <ChannelsStep {...p} />,
  (p) => <RevenueStreamsStep {...p} />,
  (p) => <KeyBlocksStep {...p} />,
  (p) => <CostStructureStep {...p} />,
  (p) => <ExperimentsStep {...p} />,
  (p) => <ReviewStep {...p} />,
];

interface CanvasWizardProps {
  initialStep?: number;
  onStepChange?: (step: number) => void;
}

export function CanvasWizard({
  initialStep = 1,
  onStepChange,
}: CanvasWizardProps) {
  const [current, setCurrent] = useState<number>(initialStep);

  const goNext = useCallback(() => {
    setCurrent((c) => {
      const next = Math.min(c + 1, STEP_COMPONENTS.length);
      onStepChange?.(next);
      return next;
    });
  }, [onStepChange]);

  const goBack = useCallback(() => {
    setCurrent((c) => {
      const prev = Math.max(c - 1, 1);
      onStepChange?.(prev);
      return prev;
    });
  }, [onStepChange]);

  const StepComponent = STEP_COMPONENTS[current - 1];

  return (
    <div>
      <div className="mb-8">
        <Stepper current={current} />
      </div>
      <div className="bg-white rounded-xl border border-navy-100 shadow-card p-6 md:p-10">
        <StepComponent goNext={goNext} goBack={current > 1 ? goBack : undefined} />
      </div>
      <div className="text-center text-xs text-navy-400 mt-6">
        latam-valuation-engine · CANVAS Wizard · paso {current}/{WIZARD_STEPS.length}
      </div>
    </div>
  );
}
