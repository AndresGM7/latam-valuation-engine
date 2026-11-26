"""Bland & Osterwalder's 44 experiments library.

From "Testing Business Ideas" (2019), Strategyzer.

Each experiment is a structured way to gather evidence for one of the 3 types of
fit (desirability / feasibility / viability). The library organizes them by:

    Stage 1 — Idea Search (Discovery): shape the idea, design the team, hypothesize
    Stage 2 — Testing (Discovery + Validation): run small experiments
    Stage 3 — Decide: evidence-based go/no-go
    Stage 4 — Manage & Scale: systematize testing across the org

We model these as `Experiment` dataclasses with metadata (duration, cost, fit_type,
evidence_strength). The frontend wizard lets the entrepreneur pick experiments to
run, track outcomes, and feed evidence into the FitScore computation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import FitType


class ExperimentStage(str, Enum):
    DISCOVERY = "discovery"      # shape the idea, find direction
    VALIDATION = "validation"    # confirm direction with strong evidence
    DECIDE = "decide"            # pivot, persevere, or kill
    SCALE = "scale"              # systematize across the org


class CostLevel(str, Enum):
    FREE = "free"          # 0 USD, just time
    LOW = "low"            # < $100
    MEDIUM = "medium"      # $100-$1000
    HIGH = "high"          # > $1000


class DurationDays(int, Enum):
    HOURS_1 = 1
    DAYS_3 = 3
    WEEKS_1 = 7
    WEEKS_2 = 14
    MONTH_1 = 30
    MONTHS_3 = 90


@dataclass(frozen=True)
class Experiment:
    """One experiment from the Bland/Osterwalder library."""

    id: str
    name: str
    description: str
    stage: ExperimentStage
    fit_type: FitType  # which risk it addresses
    cost: CostLevel
    duration: DurationDays
    evidence_strength: int = 0  # 1-5; how strong is the evidence it produces?
    page_reference: str = ""  # page in the book

    def __str__(self) -> str:
        return f"[{self.id}] {self.name} ({self.fit_type.value})"


# ------------------------------------------------------------
# EXPERIMENT LIBRARY (subset — full library has 44)
# Each ID follows the pattern: S{section}-{number}
# S1 = Discovery, S2 = Test, S3 = Decide, S4 = Scale
# ------------------------------------------------------------

EXPERIMENTS: dict[str, Experiment] = {
    # ---- STAGE 1: DISCOVERY ----
    "S1-01": Experiment(
        id="S1-01", name="Customer interviews",
        description=(
            "Conduct 10-20 in-depth interviews with people in your target segment. "
            "Ask about jobs, pains, gains. NOT about your solution."
        ),
        stage=ExperimentStage.DISCOVERY, fit_type=FitType.PROBLEM_SOLUTION,
        cost=CostLevel.FREE, duration=DurationDays.WEEKS_2, evidence_strength=4,
        page_reference="p.103",
    ),
    "S1-02": Experiment(
        id="S1-02", name="Day-in-the-life shadowing",
        description=(
            "Spend a day observing a potential customer in their environment. "
            "Take notes on what they actually do, not what they say they do."
        ),
        stage=ExperimentStage.DISCOVERY, fit_type=FitType.PROBLEM_SOLUTION,
        cost=CostLevel.FREE, duration=DurationDays.DAYS_3, evidence_strength=5,
        page_reference="p.115",
    ),
    "S1-03": Experiment(
        id="S1-03", name="Problem-solution fit survey",
        description=(
            "Survey 50-100 people in your segment about importance of jobs and "
            "satisfaction with existing solutions. Calculate opportunity scores."
        ),
        stage=ExperimentStage.DISCOVERY, fit_type=FitType.PROBLEM_SOLUTION,
        cost=CostLevel.LOW, duration=DurationDays.WEEKS_2, evidence_strength=4,
        page_reference="p.107",
    ),
    "S1-04": Experiment(
        id="S1-04", name="Exploratory interviews",
        description=(
            "Less structured interviews to discover unmet jobs and unexpected "
            "customer segments you might have missed."
        ),
        stage=ExperimentStage.DISCOVERY, fit_type=FitType.PROBLEM_SOLUTION,
        cost=CostLevel.FREE, duration=DurationDays.WEEKS_1, evidence_strength=3,
        page_reference="p.111",
    ),

    # ---- STAGE 2: TESTING ----
    "S2-01": Experiment(
        id="S2-01", name="Landing page smoke test",
        description=(
            "Build a single landing page describing your value proposition. "
            "Drive paid traffic (USD 200-500). Measure sign-up conversion."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.PROBLEM_SOLUTION,
        cost=CostLevel.LOW, duration=DurationDays.WEEKS_1, evidence_strength=3,
        page_reference="p.149",
    ),
    "S2-02": Experiment(
        id="S2-02", name="Explainer video A/B test",
        description=(
            "Create two short videos (60 sec) explaining your value proposition. "
            "A/B test with target segment. Measure comprehension + relevance."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.PROBLEM_SOLUTION,
        cost=CostLevel.MEDIUM, duration=DurationDays.WEEKS_2, evidence_strength=3,
        page_reference="p.151",
    ),
    "S2-03": Experiment(
        id="S2-03", name="Concierge MVP",
        description=(
            "Manually deliver your value proposition to 5-10 customers. No tech. "
            "Measure satisfaction, time-to-value, and willingness to pay."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.PRODUCT_MARKET,
        cost=CostLevel.MEDIUM, duration=DurationDays.MONTH_1, evidence_strength=4,
        page_reference="p.179",
    ),
    "S2-04": Experiment(
        id="S2-04", name="Wizard of Oz MVP",
        description=(
            "Customers interact with what looks like a product, but a human "
            "behind the scenes does the work. Tests full value chain."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.PRODUCT_MARKET,
        cost=CostLevel.MEDIUM, duration=DurationDays.MONTH_1, evidence_strength=4,
        page_reference="p.183",
    ),
    "S2-05": Experiment(
        id="S2-05", name="Single-feature MVP",
        description=(
            "Build the ONE feature that delivers your value proposition. "
            "Measure activation, retention, and qualitative feedback."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.PRODUCT_MARKET,
        cost=CostLevel.HIGH, duration=DurationDays.MONTHS_3, evidence_strength=5,
        page_reference="p.187",
    ),
    "S2-06": Experiment(
        id="S2-06", name="Fake-door test",
        description=(
            "Add a button/feature to an existing channel that promises the product. "
            "Measure click-through and intent signals. "
            "Use before building."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.PROBLEM_SOLUTION,
        cost=CostLevel.LOW, duration=DurationDays.WEEKS_1, evidence_strength=2,
        page_reference="p.155",
    ),
    "S2-07": Experiment(
        id="S2-07", name="Pricing page test",
        description=(
            "Test different price points with target customers using a "
            "Van Westendorp or Gabor-Granger analysis."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.BUSINESS_MODEL,
        cost=CostLevel.LOW, duration=DurationDays.WEEKS_1, evidence_strength=4,
        page_reference="p.215",
    ),
    "S2-08": Experiment(
        id="S2-08", name="Willingness-to-pay survey",
        description=(
            "Use Van Westendorp PSM to find the optimal price range. "
            "Survey 100+ people in segment."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.BUSINESS_MODEL,
        cost=CostLevel.LOW, duration=DurationDays.WEEKS_2, evidence_strength=4,
        page_reference="p.217",
    ),
    "S2-09": Experiment(
        id="S2-09", name="Conjoint analysis",
        description=(
            "Quantify how customers value different product attributes. "
            "Most rigorous pricing research; needs 200+ respondents."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.BUSINESS_MODEL,
        cost=CostLevel.MEDIUM, duration=DurationDays.WEEKS_2, evidence_strength=5,
        page_reference="p.221",
    ),
    "S2-10": Experiment(
        id="S2-10", name="Cost structure walk-through",
        description=(
            "Build a detailed cost model with suppliers and operations. "
            "Validate unit economics with the real cost data."
        ),
        stage=ExperimentStage.VALIDATION, fit_type=FitType.BUSINESS_MODEL,
        cost=CostLevel.FREE, duration=DurationDays.WEEKS_1, evidence_strength=3,
        page_reference="p.225",
    ),

    # ---- STAGE 3: DECIDE ----
    "S3-01": Experiment(
        id="S3-01", name="Pivot or persevere decision",
        description=(
            "After 3+ validation experiments, score fit evidence. "
            "If < 60/100 across all 3 fits, consider a pivot."
        ),
        stage=ExperimentStage.DECIDE, fit_type=FitType.BUSINESS_MODEL,
        cost=CostLevel.FREE, duration=DurationDays.DAYS_3, evidence_strength=3,
        page_reference="p.249",
    ),
    "S3-02": Experiment(
        id="S3-02", name="Kill or scale decision",
        description=(
            "If strong fit across all 3, prepare for scale: financial model, "
            "go-to-market plan, fundraising."
        ),
        stage=ExperimentStage.DECIDE, fit_type=FitType.BUSINESS_MODEL,
        cost=CostLevel.FREE, duration=DurationDays.WEEKS_1, evidence_strength=3,
        page_reference="p.255",
    ),

    # ---- STAGE 4: SCALE ----
    "S4-01": Experiment(
        id="S4-01", name="Experiment review board",
        description=(
            "Weekly review of experiments across teams. Share learnings, "
            "kill weak experiments early."
        ),
        stage=ExperimentStage.SCALE, fit_type=FitType.BUSINESS_MODEL,
        cost=CostLevel.FREE, duration=DurationDays.WEEKS_1, evidence_strength=3,
        page_reference="p.323",
    ),
    "S4-02": Experiment(
        id="S4-02", name="Testing portfolio dashboard",
        description=(
            "Build a dashboard of experiments, evidence scores, and decisions. "
            "Make testing visible to executives."
        ),
        stage=ExperimentStage.SCALE, fit_type=FitType.BUSINESS_MODEL,
        cost=CostLevel.MEDIUM, duration=DurationDays.MONTH_1, evidence_strength=3,
        page_reference="p.327",
    ),
}


def experiments_for_stage(stage: ExperimentStage) -> list[Experiment]:
    """Return all experiments for a given stage."""
    return [e for e in EXPERIMENTS.values() if e.stage == stage]


def experiments_for_fit(fit_type: FitType) -> list[Experiment]:
    """Return all experiments that gather evidence for a given fit type."""
    return [e for e in EXPERIMENTS.values() if e.fit_type == fit_type]


def get_experiment(exp_id: str) -> Experiment:
    if exp_id not in EXPERIMENTS:
        raise KeyError(f"Unknown experiment: {exp_id!r}. Available: {list(EXPERIMENTS)}")
    return EXPERIMENTS[exp_id]


def recommend_experiments(business_model, max_n: int = 5) -> list[Experiment]:
    """Recommend experiments based on which fit types have weakest evidence.

    Heuristic: focus on the FIT TYPE with the lowest current score.
    """
    from .model import FitType

    fits = {f.fit_type: f.score for f in business_model.fit_scores}
    if not fits:
        # No scores yet — start with discovery
        return experiments_for_stage(ExperimentStage.DISCOVERY)[:max_n]

    weakest = min(fits.items(), key=lambda kv: kv[1])
    candidates = experiments_for_fit(weakest[0])
    return candidates[:max_n]
