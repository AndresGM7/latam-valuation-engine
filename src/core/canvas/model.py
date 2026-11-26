"""Business Model Canvas + Value Proposition Design modules.

Origin: Osterwalder & Pigneur (2010) Business Model Generation,
        Osterwalder et al. (2014) Value Proposition Design,
        Bland & Osterwalder (2019) Testing Business Ideas,
        and your "Planeación Financiera bajo CANVAS" methodology
        (Andrés Felipe Giraldo M. & Harold Mauricio Ramos P.).

This module is the heart of the user-facing wizard. The flow:

1. **Ideación**: cliente describe su idea / motivación (workshop Trascender módulo I)
2. **Lienzo Modelo de Negocio**: 9 bloques BMC clásicos
3. **Lienzo Propuesta de Valor**: 3 bloques del cliente + 3 del producto (encaje)
4. **Identificar trabajos de gran valor**: clasificar trabajos según 5 criterios
5. **Calcular encaje**: score automático de los 3 tipos de encaje (Bland/Osterwalder)
6. **Plantar entradas al motor financiero**: traducir CANVAS a inputs DCF/WACC

The output is a structured `BusinessModel` that can be:
- Exported as PDF report
- Fed into the valuation engine (Monte Carlo DCF)
- Compared against industry benchmarks
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


# ------------------------------------------------------------
# ENUMS & CANONICAL VOCABULARY
# ------------------------------------------------------------

class CustomerSegmentType(str, Enum):
    """How the segment is defined (Seth Godin: smallest viable audience)."""

    MASS_MARKET = "mass_market"
    NICHE = "niche"
    SEGMENTED = "segmented"
    DIVERSIFIED = "diversified"
    MULTI_SIDED = "multi_sided"


class RelationshipType(str, Enum):
    """How the business interacts with each segment."""

    PERSONAL_ASSISTANCE = "personal_assistance"
    DEDICATED_PERSONAL = "dedicated_personal_assistance"
    SELF_SERVICE = "self_service"
    AUTOMATED = "automated"
    COMMUNITY = "community"
    CO_CREATION = "co_creation"


class ChannelType(str, Enum):
    """How the value proposition is delivered."""

    AWARENESS = "awareness"   # how customers learn about you
    EVALUATION = "evaluation"  # how they evaluate your PV
    PURCHASE = "purchase"     # how they buy
    DELIVERY = "delivery"     # how the PV gets to them
    AFTER_SALES = "after_sales"


class RevenueStreamType(str, Enum):
    """For each stream, how money flows."""

    ONE_TIME_SALE = "one_time_sale"
    SUBSCRIPTION = "subscription"
    USAGE_FEE = "usage_fee"
    LENDING = "lending"
    LICENSING = "licensing"
    ADVERTISING = "advertising"
    MARKETPLACE_COMMISSION = "marketplace_commission"
    LEASING = "leasing"


class JobType(str, Enum):
    """The job the customer is trying to get done (Value Proposition Design)."""

    FUNCTIONAL = "functional"      # practical task
    SOCIAL = "social"              # how they want to be perceived
    EMOTIONAL = "emotional"        # how they want to feel


class GainType(str, Enum):
    """What would delight the customer (Value Proposition Design)."""

    REQUIRED = "required"
    EXPECTED = "expected"
    DESIRED = "desired"
    UNEXPECTED = "unexpected"


# ------------------------------------------------------------
# CORE DATA STRUCTURES
# ------------------------------------------------------------

@dataclass
class CustomerJob:
    """A job the customer is trying to get done (functional/social/emotional)."""

    description: str
    job_type: JobType = JobType.FUNCTIONAL
    importance_score: int = 0  # 1-5, from "Identifica trabajos de gran valor"
    # 5-dimension scoring per Osterwalder/Bland:
    importance: int = 0   # 1-5: How important is this job?
    satisfaction: int = 0  # 1-5: How satisfied are customers with existing solutions?
    # If satisfaction << importance: this is a "great job" opportunity

    def opportunity_score(self) -> float:
        """Osterwalder's opportunity score: importance - satisfaction.

        Positive = unmet need; > 1.5 = strong opportunity.
        """
        return float(self.importance - self.satisfaction)


@dataclass
class CustomerPain:
    """A frustration, obstacle, or risk the customer experiences."""

    description: str
    severity: int = 0  # 1-5: how bad is this pain?
    frequency: int = 0  # 1-5: how often do they experience it?


@dataclass
class CustomerGain:
    """An outcome or benefit the customer wants."""

    description: str
    relevance: int = 0  # 1-5
    gain_type: GainType = GainType.EXPECTED


@dataclass
class ValuePropositionBlock:
    """The Value Proposition side of the VPD canvas."""

    products_services: list[str] = field(default_factory=list)
    pain_relievers: list[str] = field(default_factory=list)
    gain_creators: list[str] = field(default_factory=list)


@dataclass
class CustomerProfileBlock:
    """The Customer side of the VPD canvas."""

    jobs: list[CustomerJob] = field(default_factory=list)
    pains: list[CustomerPain] = field(default_factory=list)
    gains: list[CustomerGain] = field(default_factory=list)


@dataclass
class CustomerSegment:
    """One of the 9 CANVAS building blocks: Segments de Clientes."""

    name: str
    description: str = ""
    segment_type: CustomerSegmentType = CustomerSegmentType.NICHE
    # This is the "smallest viable audience" (Seth Godin)
    demographic: dict[str, str] = field(default_factory=dict)
    psychographic: dict[str, str] = field(default_factory=dict)
    # Profile from VPD canvas
    profile: CustomerProfileBlock = field(default_factory=CustomerProfileBlock)
    # Relationship from BMC
    relationships: list[RelationshipType] = field(default_factory=list)


@dataclass
class ValueProposition:
    """The heart: what value we deliver and to whom."""

    headline: str  # One-sentence value proposition
    description: str = ""
    block: ValuePropositionBlock = field(default_factory=ValuePropositionBlock)
    target_segment_names: list[str] = field(default_factory=list)
    # Optional differential vs. competitors
    alternatives: list[str] = field(default_factory=list)


@dataclass
class Channel:
    """CANVAS Canales: how the PV reaches customers."""

    name: str
    channel_type: ChannelType
    description: str = ""
    cost_pct_of_revenue: float = 0.0  # for sensitivity analysis


@dataclass
class RevenueStream:
    """CANVAS Fuentes de Ingreso."""

    name: str
    stream_type: RevenueStreamType
    pricing_mechanism: str = ""
    estimated_arpu_usd_per_year: float = 0.0  # for DCF inputs
    estimated_volume_year_1: int = 0  # initial customers/transactions
    growth_rate_pct_year: float = 0.0  # for projection
    # Optional: tiered pricing
    tiers: dict[str, float] = field(default_factory=dict)


@dataclass
class KeyResource:
    """CANVAS Recursos Clave."""

    name: str
    resource_type: str = "physical"  # physical, intellectual, human, financial
    description: str = ""
    estimated_capex_usd: float = 0.0  # for DCF inversion_inicial


@dataclass
class KeyActivity:
    """CANVAS Actividades Clave."""

    name: str
    description: str = ""
    estimated_opex_usd_per_year: float = 0.0  # for PyG costs


@dataclass
class KeyPartner:
    """CANVAS Asociaciones / Aliados Clave."""

    name: str
    partner_type: str  # supplier, distributor, joint_venture, etc.
    description: str = ""
    estimated_cost_usd_per_year: float = 0.0


@dataclass
class CostStructure:
    """CANVAS Estructura de Costos."""

    fixed_costs_usd_per_year: float = 0.0
    variable_costs_pct_of_revenue: float = 0.0
    key_resource_costs: dict[str, float] = field(default_factory=dict)
    key_activity_costs: dict[str, float] = field(default_factory=dict)
    partner_costs: dict[str, float] = field(default_factory=dict)


# ------------------------------------------------------------
# SCORING: 3 TYPES OF FIT (OSTERWALDER / BLAND)
# ------------------------------------------------------------

class FitType(str, Enum):
    PROBLEM_SOLUTION = "problem_solution"  # Encaje problema-solución
    PRODUCT_MARKET = "product_market"     # Encaje producto-mercado
    BUSINESS_MODEL = "business_model"     # Encaje modelo de negocio


@dataclass
class FitScore:
    """Evidence score for one of the 3 types of fit.

    Score range 0-100. > 70 = strong evidence of fit.
    """

    fit_type: FitType
    score: float
    evidence_count: int = 0
    confidence: str = "low"  # low, medium, high
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------
# AGGREGATE: BusinessModel = the whole canvas
# ------------------------------------------------------------

@dataclass
class BusinessModel:
    """The complete Business Model Canvas + Value Proposition Design."""

    # Identity
    business_name: str
    country: str = "CO"  # country code
    industry: Optional[str] = None  # Damodaran industry for beta lookup
    as_of: date = field(default_factory=date.today)
    version: str = "1.0"

    # The 9 CANVAS blocks
    customer_segments: list[CustomerSegment] = field(default_factory=list)
    value_propositions: list[ValueProposition] = field(default_factory=list)
    channels: list[Channel] = field(default_factory=list)
    customer_relationships: dict[str, list[RelationshipType]] = field(default_factory=dict)
    revenue_streams: list[RevenueStream] = field(default_factory=list)
    key_resources: list[KeyResource] = field(default_factory=list)
    key_activities: list[KeyActivity] = field(default_factory=list)
    key_partners: list[KeyPartner] = field(default_factory=list)
    cost_structure: CostStructure = field(default_factory=CostStructure)

    # Evidence
    fit_scores: list[FitScore] = field(default_factory=list)
    experiments_run: list[str] = field(default_factory=list)  # from Bland's 44

    # Computed
    @property
    def total_addressable_revenue_usd_year_1(self) -> float:
        """Sum of year-1 revenue across streams."""
        return sum(s.estimated_arpu_usd_per_year * s.estimated_volume_year_1 for s in self.revenue_streams)

    @property
    def total_capex_usd(self) -> float:
        return sum(r.estimated_capex_usd for r in self.key_resources)

    @property
    def total_opex_usd_per_year(self) -> float:
        total = self.cost_structure.fixed_costs_usd_per_year
        total += sum(a.estimated_opex_usd_per_year for a in self.key_activities)
        total += sum(p.estimated_cost_usd_per_year for p in self.key_partners)
        return total

    def to_financial_inputs(self, horizon_years: int = 5) -> dict:
        """Translate the CANVAS into DCF inputs (revenues, costs, capex).

        Mapping (from your Planeación Financiera bajo CANVAS guide):
            Ingresos <- Revenue Streams
            Costos   <- Key Resources + Channels
            Gastos   <- Key Activities + Partners + Customer Relationships
        """
        # Project revenues
        revenues = []
        for year in range(1, horizon_years + 1):
            y_rev = 0.0
            for s in self.revenue_streams:
                # Grow volume by growth_rate
                growth = (1 + s.growth_rate_pct_year / 100.0) ** (year - 1)
                y_rev += s.estimated_arpu_usd_per_year * s.estimated_volume_year_1 * growth
            revenues.append(y_rev)

        # Project costs (variable + fixed + opex)
        variable_costs_pct = self.cost_structure.variable_costs_pct_of_revenue / 100.0
        costs = []
        for y_rev in revenues:
            y_var = y_rev * variable_costs_pct
            y_fix = self.cost_structure.fixed_costs_usd_per_year
            y_opex = sum(a.estimated_opex_usd_per_year for a in self.key_activities)
            y_partners = sum(p.estimated_cost_usd_per_year for p in self.key_partners)
            costs.append(y_var + y_fix + y_opex + y_partners)

        free_cash_flow = [r - c for r, c in zip(revenues, costs)]

        return {
            "revenues": revenues,
            "costs": costs,
            "free_cash_flow": free_cash_flow,
            "inversion_inicial": self.total_capex_usd,
            "horizon_years": horizon_years,
            "country": self.country,
            "industry": self.industry,
            "source": "BusinessModel.to_financial_inputs()",
        }


# ------------------------------------------------------------
# WIZARD HELPERS
# ------------------------------------------------------------

def smallest_viable_audience(segments: list[CustomerSegment]) -> CustomerSegment:
    """Pick the 'smallest viable audience' (Seth Godin) from multiple segments.

    Heuristic: prefer the segment with the highest combination of:
    - narrowness (smaller is better if not zero)
    - specificity in demographics/psychographics
    - single primary job
    Returns: the segment that scores highest.
    """
    if not segments:
        raise ValueError("No customer segments defined.")
    if len(segments) == 1:
        return segments[0]

    def score_segment(s: CustomerSegment) -> float:
        sc = 0.0
        # Smaller/more defined segments score higher
        if s.segment_type == CustomerSegmentType.NICHE:
            sc += 3.0
        elif s.segment_type == CustomerSegmentType.SEGMENTED:
            sc += 2.0
        elif s.segment_type == CustomerSegmentType.MULTI_SIDED:
            sc += 1.0
        # Specificity (more demographic/psychographic = more focused)
        sc += 0.5 * len(s.demographic)
        sc += 0.5 * len(s.psychographic)
        # Fewer jobs = more focused (Seth Godin: be the best to one)
        if s.profile.jobs:
            sc += 2.0 / max(1, len(s.profile.jobs))
        return sc

    return max(segments, key=score_segment)


def compute_problem_solution_fit(business_model: BusinessModel) -> FitScore:
    """Encaje problema-solución: do the jobs/pains/gains matter to customers?

    Evidence criteria (from Bland & Osterwalder):
    - Customer jobs have importance_score > 0
    - Pain severity and frequency are non-zero
    - Gain relevance is non-zero
    - Pain relievers / gain creators in PV address the top pains/gains
    """
    notes: list[str] = []
    evidence = 0
    score = 0.0
    total = 0

    for seg in business_model.customer_segments:
        for job in seg.profile.jobs:
            total += 1
            if job.importance > 0:
                evidence += 1
                score += job.importance / 5.0
            # Opportunity score = importance - satisfaction
            if job.opportunity_score() >= 1.5:
                notes.append(f"Gran oportunidad: '{job.description}' (opportunity={job.opportunity_score():.1f})")
        for pain in seg.profile.pains:
            total += 1
            if pain.severity >= 4 and pain.frequency >= 3:
                evidence += 1
                score += 0.8
                notes.append(f"Pain extremo: '{pain.description}'")
        for gain in seg.profile.gains:
            total += 1
            if gain.relevance >= 4:
                evidence += 1
                score += 0.6

    if total == 0:
        return FitScore(fit_type=FitType.PROBLEM_SOLUTION, score=0, confidence="low",
                        notes=["No jobs, pains, or gains defined."])

    # Normalize: best possible is each item scoring 1.0
    raw_pct = 100.0 * score / total
    confidence = "high" if evidence >= 5 else "medium" if evidence >= 2 else "low"
    return FitScore(fit_type=FitType.PROBLEM_SOLUTION, score=round(raw_pct, 1),
                    evidence_count=evidence, confidence=confidence, notes=notes)


def compute_business_model_fit(business_model: BusinessModel) -> FitScore:
    """Encaje modelo de negocio: can the PV be embedded in a profitable/scalable model?

    Evidence criteria:
    - Revenue streams have ARPUs and volumes defined
    - Costs are quantified (variable + fixed)
    - The unit economics work: ARPU > (variable cost / volume)
    """
    notes: list[str] = []
    score = 0.0
    items = 0

    # Revenue coverage
    if business_model.revenue_streams:
        items += 1
        if all(s.estimated_arpu_usd_per_year > 0 and s.estimated_volume_year_1 > 0
               for s in business_model.revenue_streams):
            score += 1.0
            notes.append(f"Revenue streams cuantificados: {len(business_model.revenue_streams)} streams, "
                         f"Year-1 ARR ${business_model.total_addressable_revenue_usd_year_1:,.0f}")
        elif any(s.estimated_arpu_usd_per_year > 0 for s in business_model.revenue_streams):
            score += 0.5
            notes.append("Revenue streams parcialmente cuantificados")
        else:
            notes.append("⚠️ Revenue streams sin cuantificar")

    # Cost coverage
    if business_model.cost_structure.fixed_costs_usd_per_year > 0 or \
       business_model.cost_structure.variable_costs_pct_of_revenue > 0:
        items += 1
        score += 1.0
        notes.append(f"Costos cuantificados: ${business_model.total_opex_usd_per_year:,.0f} opex/año")
    else:
        notes.append("⚠️ Costos sin cuantificar")

    # Unit economics
    if business_model.revenue_streams and business_model.cost_structure.variable_costs_pct_of_revenue:
        for s in business_model.revenue_streams:
            arpu = s.estimated_arpu_usd_per_year
            var_cost = arpu * (business_model.cost_structure.variable_costs_pct_of_revenue / 100.0)
            contribution_margin = arpu - var_cost
            items += 1
            if contribution_margin > 0:
                margin_pct = 100.0 * contribution_margin / arpu if arpu else 0
                score += min(1.0, margin_pct / 50.0)
                notes.append(f"Stream '{s.name}': contribution margin {margin_pct:.1f}%")
            else:
                notes.append(f"⚠️ Stream '{s.name}': unit economics negativos")

    raw_pct = 100.0 * score / max(1, items)
    confidence = "high" if score >= items * 0.7 else "medium" if score >= items * 0.4 else "low"
    return FitScore(fit_type=FitType.BUSINESS_MODEL, score=round(raw_pct, 1),
                    evidence_count=int(score), confidence=confidence, notes=notes)
