/**
 * App shell. Top-level layout: header + <Outlet/> routed between
 * the 10-step wizard (steps 1-9) and the dedicated /results page.
 */

import {
  Route,
  Routes,
  Link,
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useEffect } from "react";

import { CanvasWizard } from "./components/CanvasWizard";
import { ResultsStep } from "./components/steps/ResultsStep";
import { WizardProvider } from "./lib/wizardStore";

const STEP_PATH: Record<number, string> = {
  1: "/welcome",
  2: "/segments",
  3: "/value-prop",
  4: "/channels",
  5: "/revenue",
  6: "/key-blocks",
  7: "/costs",
  8: "/experiments",
  9: "/review",
};

function WizardRoute() {
  const location = useLocation();
  const navigate = useNavigate();

  // Map pathname to current step
  const matched = Object.entries(STEP_PATH).find(
    ([, path]) => path === location.pathname,
  );
  const current = matched ? Number(matched[0]) : 1;

  return (
    <CanvasWizard
      initialStep={current}
      onStepChange={(step) => navigate(STEP_PATH[step] || "/welcome")}
    />
  );
}

export default function App() {
  // Ensure top of page on every route change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
  });

  return (
    <WizardProvider>
      <div className="min-h-screen bg-navy-50/40">
        <header className="bg-white border-b border-navy-100">
          <div className="max-w-6xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between">
            <Link to="/welcome" className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-md bg-navy-900 text-white flex items-center justify-center font-semibold">
                LV
              </div>
              <div>
                <div className="text-sm font-semibold text-navy-900 leading-tight">
                  latam-valuation-engine
                </div>
                <div className="text-xs text-navy-500">
                  CANVAS Wizard · DCF Monte Carlo
                </div>
              </div>
            </Link>
            <nav className="flex items-center gap-3 text-sm">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="text-navy-600 hover:text-navy-900"
              >
                API docs
              </a>
              <Link to="/review" className="btn-secondary">
                Ir a revisión
              </Link>
            </nav>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-4 md:px-8 py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/welcome" replace />} />
            <Route path="/welcome" element={<WizardRoute />} />
            <Route path="/segments" element={<WizardRoute />} />
            <Route path="/value-prop" element={<WizardRoute />} />
            <Route path="/channels" element={<WizardRoute />} />
            <Route path="/revenue" element={<WizardRoute />} />
            <Route path="/key-blocks" element={<WizardRoute />} />
            <Route path="/costs" element={<WizardRoute />} />
            <Route path="/experiments" element={<WizardRoute />} />
            <Route path="/review" element={<WizardRoute />} />
            <Route path="/results" element={<ResultsStep />} />
            <Route path="*" element={<Navigate to="/welcome" replace />} />
          </Routes>
        </main>
        <footer className="border-t border-navy-100 bg-white">
          <div className="max-w-6xl mx-auto px-4 md:px-8 py-4 text-xs text-navy-500 flex items-center justify-between">
            <span>
              Built for entrepreneurs in Latam. Methodology: Osterwalder + Bland.
            </span>
            <span className="font-mono">v1.0.0</span>
          </div>
        </footer>
      </div>
    </WizardProvider>
  );
}
