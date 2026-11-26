"""Business Model Canvas + Value Proposition Design modules.

This is the user-facing wizard backend.
- model.py: data structures (BusinessModel, ValueProposition, etc.)
- scoring.py: 3 types of fit (problem-solution, product-market, business-model)
- experiments.py: Bland's 44 experiments library
- derivations.py: derive financial inputs from a filled BusinessModel
"""

from .model import (
    BusinessModel,
    Channel,
    ChannelType,
    CostStructure,
    CustomerGain,
    CustomerJob,
    CustomerPain,
    CustomerProfileBlock,
    CustomerSegment,
    CustomerSegmentType,
    FitScore,
    FitType,
    GainType,
    JobType,
    KeyActivity,
    KeyPartner,
    KeyResource,
    RelationshipType,
    RevenueStream,
    RevenueStreamType,
    ValueProposition,
    ValuePropositionBlock,
    compute_business_model_fit,
    compute_problem_solution_fit,
    smallest_viable_audience,
)
from .experiments import (
    Experiment,
    ExperimentStage,
    CostLevel,
    DurationDays,
    EXPERIMENTS,
    experiments_for_stage,
    experiments_for_fit,
    get_experiment,
    recommend_experiments,
)

__all__ = [
    "BusinessModel", "ValueProposition", "ValuePropositionBlock",
    "CustomerSegment", "CustomerProfileBlock", "CustomerJob", "CustomerPain", "CustomerGain",
    "Channel", "ChannelType", "CustomerSegmentType", "RelationshipType",
    "RevenueStream", "RevenueStreamType", "JobType", "GainType",
    "KeyResource", "KeyActivity", "KeyPartner", "CostStructure",
    "FitScore", "FitType", "compute_business_model_fit", "compute_problem_solution_fit",
    "smallest_viable_audience",
    "Experiment", "ExperimentStage", "CostLevel", "DurationDays", "EXPERIMENTS",
    "experiments_for_stage", "experiments_for_fit", "get_experiment", "recommend_experiments",
]
