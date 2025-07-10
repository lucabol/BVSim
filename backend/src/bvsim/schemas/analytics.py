"""Pydantic schemas for analytics and importance analysis."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal
from datetime import datetime
from enum import Enum

from .team_statistics import TeamStatisticsBase


class AnalysisMethod(str, Enum):
    """Analysis method enumeration."""
    LOGISTIC_REGRESSION = "logistic_regression"
    SHAP = "shap"
    COMBINED = "combined"
    PERMUTATION_IMPORTANCE = "permutation_importance"
    GRADIENT_BOOSTING = "gradient_boosting"


class FeatureCategory(str, Enum):
    """Feature category enumeration."""
    SERVE = "serve"
    RECEPTION = "reception"
    SETTING = "setting"
    ATTACK = "attack"
    DEFENSE = "defense"
    BLOCKING = "blocking"


class AnalysisType(str, Enum):
    """Types of analytics analysis."""
    FEATURE_IMPORTANCE = "feature_importance"
    SENSITIVITY_ANALYSIS = "sensitivity_analysis"
    SHAP_VALUES = "shap_values"
    CORRELATION_ANALYSIS = "correlation_analysis"
    IMPACT_ASSESSMENT = "impact_assessment"
    SCENARIO_ANALYSIS = "scenario_analysis"


class SHAPValue(BaseModel):
    """SHAP value for a specific feature in a prediction."""
    feature_name: str
    shap_value: Decimal
    base_value: Decimal
    feature_value: Union[Decimal, str]
    category: FeatureCategory
    impact_direction: str = Field(..., pattern=r"^(positive|negative|neutral)$")
    contribution_percentage: Decimal = Field(..., ge=0.0, le=100.0)


class SHAPAnalysisResult(BaseModel):
    """Complete SHAP analysis results."""
    analysis_id: str
    base_prediction: Decimal
    shap_values: List[SHAPValue]
    feature_interactions: Dict[str, Dict[str, Decimal]]
    global_feature_importance: Dict[str, Decimal]
    model_performance: Dict[str, Decimal]
    analysis_time_seconds: float
    created_at: datetime


class FeatureImportance(BaseModel):
    """Individual feature importance result."""
    
    statistic_name: str = Field(..., description="Name of the statistic")
    feature_category: FeatureCategory = Field(..., description="Category of the feature")
    importance_score: Decimal = Field(..., description="Importance score (0-1)")
    marginal_impact: Decimal = Field(
        ..., description="Marginal impact on win probability"
    )
    confidence_interval_lower: Optional[Decimal] = Field(
        None, description="Lower bound of confidence interval"
    )
    confidence_interval_upper: Optional[Decimal] = Field(
        None, description="Upper bound of confidence interval"
    )
    rank: Optional[int] = Field(None, description="Importance ranking")
    
    # Human-readable interpretation
    interpretation: str = Field(
        ..., description="Human-readable impact description"
    )


class ImportanceAnalysisResult(BaseModel):
    """Complete importance analysis results."""
    
    simulation_id: int = Field(..., description="Source simulation ID")
    method: AnalysisMethod = Field(..., description="Analysis method used")
    
    # Feature importance rankings
    feature_importances: List[FeatureImportance] = Field(
        ..., description="List of feature importances, ranked by importance"
    )
    
    # Analysis metadata
    total_features_analyzed: int = Field(..., description="Total features analyzed")
    analysis_time_seconds: Decimal = Field(..., description="Analysis execution time")
    sample_size: int = Field(..., description="Sample size used for analysis")
    
    # Model performance metrics
    model_accuracy: Optional[Decimal] = Field(None, description="Model accuracy")
    model_auc: Optional[Decimal] = Field(None, description="Model AUC score")
    
    # Analysis configuration
    analysis_config: Optional[Dict[str, Any]] = Field(
        None, description="Analysis configuration parameters"
    )
    
    created_at: datetime = Field(..., description="Analysis creation time")


class SensitivityAnalysisRequest(BaseModel):
    """Request for sensitivity analysis."""
    
    simulation_id: int = Field(..., description="Source simulation ID")
    statistic_name: str = Field(..., description="Statistic to analyze")
    change_amounts: List[Decimal] = Field(
        ..., description="List of change amounts to test (e.g., [1.0, 2.0, 5.0])"
    )
    change_type: str = Field(
        default="percentage_points",
        description="Type of change: 'percentage_points' or 'multiplier'"
    )


class SensitivityDataPoint(BaseModel):
    """Single data point in sensitivity analysis."""
    
    change_amount: Decimal = Field(..., description="Amount of change applied")
    baseline_value: Decimal = Field(..., description="Original statistic value")
    new_value: Decimal = Field(..., description="Modified statistic value")
    baseline_win_probability: Decimal = Field(..., description="Original win probability")
    new_win_probability: Decimal = Field(..., description="New win probability")
    absolute_change: Decimal = Field(..., description="Absolute change in win probability")
    relative_change: Decimal = Field(..., description="Relative change in win probability")


class SensitivityAnalysisResult(BaseModel):
    """Sensitivity analysis results."""
    
    simulation_id: int = Field(..., description="Source simulation ID")
    statistic_name: str = Field(..., description="Analyzed statistic")
    feature_category: FeatureCategory = Field(..., description="Feature category")
    
    # Sensitivity data points
    data_points: List[SensitivityDataPoint] = Field(
        ..., description="Sensitivity analysis data points"
    )
    
    # Summary statistics
    average_marginal_impact: Decimal = Field(
        ..., description="Average marginal impact per unit change"
    )
    elasticity: Decimal = Field(
        ..., description="Elasticity measure (% change in output / % change in input)"
    )
    
    # Analysis metadata
    analysis_time_seconds: Decimal = Field(..., description="Analysis execution time")
    created_at: datetime = Field(..., description="Analysis creation time")


class ComparisonAnalysisRequest(BaseModel):
    """Request for comparing multiple teams or scenarios."""
    
    simulation_ids: List[int] = Field(..., description="List of simulation IDs to compare")
    comparison_type: str = Field(
        default="team_comparison",
        description="Type of comparison: 'team_comparison' or 'scenario_analysis'"
    )
    include_confidence_intervals: bool = Field(
        default=True,
        description="Include confidence intervals in results"
    )


class TeamComparisonResult(BaseModel):
    """Team comparison analysis result."""
    
    team_a_id: int
    team_b_id: int
    team_a_name: str
    team_b_name: str
    
    # Win probability comparison
    team_a_win_probability: Decimal
    team_b_win_probability: Decimal
    probability_difference: Decimal
    
    # Key differentiating factors
    top_advantages_team_a: List[FeatureImportance]
    top_advantages_team_b: List[FeatureImportance]
    
    # Recommendations
    improvement_recommendations_team_a: List[str]
    improvement_recommendations_team_b: List[str]


class AnalyticsOverview(BaseModel):
    """Overview of all analytics for a simulation."""
    
    simulation_id: int
    simulation_status: str
    
    # Available analyses
    has_importance_analysis: bool
    has_sensitivity_analysis: bool
    has_comparison_analysis: bool
    
    # Quick insights
    top_3_most_important_factors: List[FeatureImportance]
    biggest_improvement_opportunity: Optional[FeatureImportance] = None
    
    # Analysis timestamps
    last_analysis_update: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Export schemas
class AnalyticsExportRequest(BaseModel):
    """Request for exporting analytics data."""
    
    simulation_ids: List[int] = Field(..., description="Simulations to export")
    export_format: str = Field(
        default="json",
        description="Export format: 'json', 'csv', 'excel'"
    )
    include_raw_data: bool = Field(
        default=False,
        description="Include raw simulation point data"
    )
    include_visualizations: bool = Field(
        default=True,
        description="Include visualization data"
    )


class AnalyticsExportResponse(BaseModel):
    """Response for analytics export."""
    
    export_id: str = Field(..., description="Export job ID")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    status: str = Field(..., description="Export status")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    expires_at: Optional[datetime] = Field(None, description="Download link expiration")
    created_at: datetime = Field(..., description="Export creation time")


class AdvancedAnalyticsRequest(BaseModel):
    """Request for advanced analytics with SHAP and sensitivity analysis."""
    team_a: TeamStatisticsBase
    team_b: Optional[TeamStatisticsBase] = None
    analysis_types: List[AnalysisType] = Field(default=[AnalysisType.FEATURE_IMPORTANCE, AnalysisType.SHAP_VALUES])
    num_simulations: int = Field(default=5000, ge=1000, le=50000)
    sensitivity_ranges: Dict[str, List[Decimal]] = Field(default_factory=dict)
    confidence_level: Decimal = Field(default=Decimal('0.95'), ge=Decimal('0.80'), le=Decimal('0.99'))
    include_interaction_effects: bool = Field(default=True)
    model_type: str = Field(default="gradient_boosting", pattern=r"^(logistic_regression|random_forest|gradient_boosting|neural_network)$")
    random_seed: Optional[int] = None


class FeatureImpactAssessment(BaseModel):
    """Comprehensive impact assessment for a feature."""
    feature_name: str
    category: FeatureCategory
    current_value: Decimal
    
    # Impact metrics
    importance_rank: int
    shap_contribution: Decimal
    sensitivity_to_change: Decimal
    improvement_potential: Decimal
    
    # Recommendations
    recommended_target: Optional[Decimal] = None
    expected_win_rate_improvement: Optional[Decimal] = None
    training_priority: str = Field(..., pattern=r"^(high|medium|low)$")
    
    # Context
    percentile_rank: Decimal = Field(..., ge=0.0, le=100.0)
    comparison_to_elite: Decimal


class TeamAnalyticsProfile(BaseModel):
    """Comprehensive analytics profile for a team."""
    team_name: str
    overall_rating: Decimal = Field(..., ge=0.0, le=100.0)
    
    # Feature importance rankings
    feature_importances: List[FeatureImportance]
    
    # SHAP analysis
    shap_summary: Dict[str, Decimal]
    shap_details: List[SHAPValue]
    
    # Sensitivity analysis
    sensitivity_results: List[SensitivityAnalysisResult]
    
    # Impact assessments
    impact_assessments: List[FeatureImpactAssessment]
    
    # Category strengths
    category_strengths: Dict[FeatureCategory, Decimal]
    
    # Recommendations
    top_improvement_areas: List[str]
    training_priorities: Dict[str, str]


class AdvancedAnalyticsResponse(BaseModel):
    """Response from advanced analytics analysis."""
    analysis_id: str
    request: AdvancedAnalyticsRequest
    
    # Core results
    team_a_analytics: TeamAnalyticsProfile
    team_b_analytics: Optional[TeamAnalyticsProfile] = None
    
    # SHAP analysis
    shap_analysis: Optional[SHAPAnalysisResult] = None
    
    # Comparative analysis
    head_to_head_insights: Optional[Dict[str, Any]] = None
    
    # Meta information
    simulation_count: int
    analysis_time_seconds: float
    statistical_power: Decimal
    confidence_level: Decimal
    
    # Quality metrics
    convergence_achieved: bool
    margin_of_error: Decimal
    reliability_score: Decimal = Field(..., ge=0.0, le=1.0)
    
    created_at: datetime


class ScenarioAnalysisRequest(BaseModel):
    """Request for scenario-based analytics."""
    base_team: TeamStatisticsBase
    scenarios: List[Dict[str, Decimal]]
    scenario_names: List[str]
    opponent_team: Optional[TeamStatisticsBase] = None
    analysis_depth: str = Field(default="standard", pattern=r"^(basic|standard|comprehensive)$")
    num_simulations_per_scenario: int = Field(default=1000, ge=500, le=10000)


class ScenarioResult(BaseModel):
    """Result of a single scenario analysis."""
    scenario_name: str
    modified_features: Dict[str, Decimal]
    predicted_win_rate: Decimal
    win_rate_change: Decimal
    confidence_interval: Dict[str, Decimal]
    key_improvements: List[str]
    risk_factors: List[str]
    cost_benefit_ratio: Optional[Decimal] = None


class ScenarioAnalysisResponse(BaseModel):
    """Response from scenario analysis."""
    analysis_id: str
    base_team_name: str
    scenarios: List[ScenarioResult]
    best_scenario: str
    worst_scenario: str
    most_realistic_scenario: str
    implementation_recommendations: List[str]
    roi_analysis: Dict[str, Decimal]
    created_at: datetime
