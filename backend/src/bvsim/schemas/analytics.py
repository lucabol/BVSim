"""Pydantic schemas for analytics and importance analysis."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum


class AnalysisMethod(str, Enum):
    """Analysis method enumeration."""
    LOGISTIC_REGRESSION = "logistic_regression"
    SHAP = "shap"
    COMBINED = "combined"


class FeatureCategory(str, Enum):
    """Feature category enumeration."""
    SERVE = "serve"
    RECEPTION = "reception"
    SETTING = "setting"
    ATTACK = "attack"
    DEFENSE = "defense"


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
