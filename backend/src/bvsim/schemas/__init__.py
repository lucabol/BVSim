"""Pydantic schemas for BVSim API."""

from .team_statistics import (
    TeamStatisticsBase,
    TeamStatisticsCreate,
    TeamStatisticsUpdate,
    TeamStatisticsResponse,
    TeamStatisticsImport,
    TeamStatisticsBatch,
    TeamStatisticsExport,
    StatisticCategory
)

from .simulation import (
    SimulationCreate,
    SimulationUpdate,
    SimulationResponse,
    SimulationBatch,
    SimulationStatus,
    SimulationFilters,
    SimulationPoint,
    SetResult,
    MatchResult,
    SimulationConfiguration,
    SimulationSummary
)

from .analytics import (
    AnalysisMethod,
    FeatureCategory,
    FeatureImportance,
    ImportanceAnalysisResult,
    SensitivityAnalysisRequest,
    SensitivityDataPoint,
    SensitivityAnalysisResult,
    ComparisonAnalysisRequest,
    TeamComparisonResult,
    AnalyticsOverview,
    AnalyticsExportRequest,
    AnalyticsExportResponse
)

from .engine import (
    SkillLevel,
    PlayStyle,
    RallyState,
    ProbabilityDistribution,
    SimulationEngineConfig,
    ActionOutcome,
    RallyResult,
    EnginePerformanceMetrics,
    SimulationEngineStatus
)

# Common response schemas
from .common import (
    ErrorResponse,
    SuccessResponse,
    PaginatedResponse,
    HealthCheck,
    BulkOperationResult
)

__all__ = [
    # Team Statistics
    "TeamStatisticsBase",
    "TeamStatisticsCreate", 
    "TeamStatisticsUpdate",
    "TeamStatisticsResponse",
    "TeamStatisticsImport",
    "TeamStatisticsBatch",
    "TeamStatisticsExport",
    "StatisticCategory",
    
    # Simulation
    "SimulationCreate",
    "SimulationUpdate",
    "SimulationResponse", 
    "SimulationBatch",
    "SimulationStatus",
    "SimulationFilters",
    "SimulationPoint",
    "SetResult",
    "MatchResult",
    "SimulationConfiguration",
    "SimulationSummary",
    
    # Analytics
    "AnalysisMethod",
    "FeatureCategory",
    "FeatureImportance",
    "ImportanceAnalysisResult",
    "SensitivityAnalysisRequest",
    "SensitivityDataPoint", 
    "SensitivityAnalysisResult",
    "ComparisonAnalysisRequest",
    "TeamComparisonResult",
    "AnalyticsOverview",
    "AnalyticsExportRequest",
    "AnalyticsExportResponse",
    
    # Engine
    "SkillLevel",
    "PlayStyle",
    "RallyState",
    "ProbabilityDistribution",
    "SimulationEngineConfig",
    "ActionOutcome",
    "RallyResult",
    "EnginePerformanceMetrics",
    "SimulationEngineStatus",
    
    # Common
    "ErrorResponse",
    "SuccessResponse",
    "PaginatedResponse",
    "HealthCheck",
    "BulkOperationResult"
]
