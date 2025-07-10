"""
Advanced analytics API endpoints.
Provides SHAP analysis, feature importance, and scenario testing capabilities.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from decimal import Decimal
import logging
import asyncio
import uuid
from datetime import datetime

from ..schemas.analytics import (
    AdvancedAnalyticsRequest, AdvancedAnalyticsResponse,
    ScenarioAnalysisRequest, ScenarioAnalysisResponse,
    AnalysisType
)
from ..schemas.team_statistics import TeamStatisticsBase
from ..engine.advanced_analytics import AdvancedAnalyticsEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])

# Global storage for async analysis results (in production, use Redis or database)
_analysis_results: Dict[str, Dict[str, Any]] = {}


@router.post("/advanced-analysis", response_model=AdvancedAnalyticsResponse)
async def run_advanced_analysis(request: AdvancedAnalyticsRequest):
    """
    Run comprehensive advanced analytics analysis with SHAP values and feature importance.
    
    This endpoint performs machine learning analysis on volleyball team statistics to provide:
    - Feature importance rankings
    - SHAP value explanations  
    - Sensitivity analysis
    - Team analytics profiles
    """
    try:
        logger.info(f"Starting advanced analytics for team: {request.team_a.name}")
        
        engine = AdvancedAnalyticsEngine()
        result = await engine.run_advanced_analysis(request)
        
        logger.info(f"Advanced analytics completed in {result.analysis_time_seconds:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Advanced analytics failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advanced analytics failed: {str(e)}"
        )


@router.post("/advanced-analysis-async")
async def run_advanced_analysis_async(
    request: AdvancedAnalyticsRequest, 
    background_tasks: BackgroundTasks
):
    """
    Start advanced analytics analysis in the background for large-scale studies.
    Returns an analysis ID that can be used to check progress and retrieve results.
    """
    analysis_id = str(uuid.uuid4())
    
    # Store initial status
    _analysis_results[analysis_id] = {
        "status": "running",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "request": request.model_dump()
    }
    
    # Start background analysis
    background_tasks.add_task(_run_background_analysis, analysis_id, request)
    
    return {
        "analysis_id": analysis_id,
        "status": "started",
        "message": "Advanced analytics analysis started in background",
        "estimated_completion_time": "5-10 minutes for large datasets"
    }


@router.get("/advanced-analysis/{analysis_id}")
async def get_advanced_analysis_status(analysis_id: str):
    """Get the status and results of a background advanced analytics analysis."""
    
    if analysis_id not in _analysis_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {analysis_id} not found"
        )
    
    result = _analysis_results[analysis_id]
    
    if result["status"] == "completed":
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "results": result["results"],
            "analysis_time": result.get("analysis_time", 0)
        }
    elif result["status"] == "failed":
        return {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": result.get("error", "Unknown error"),
            "progress": result.get("progress", 0)
        }
    else:
        return {
            "analysis_id": analysis_id,
            "status": "running",
            "progress": result.get("progress", 0),
            "message": "Analysis in progress..."
        }


@router.post("/scenario-analysis", response_model=ScenarioAnalysisResponse)
async def run_scenario_analysis(request: ScenarioAnalysisRequest):
    """
    Run scenario analysis to test different team improvement strategies.
    
    This endpoint simulates various "what-if" scenarios by modifying team statistics
    and measuring the impact on win rates and performance.
    """
    try:
        logger.info(f"Starting scenario analysis for team: {request.base_team.name}")
        
        engine = AdvancedAnalyticsEngine()
        result = await engine.run_scenario_analysis(request)
        
        logger.info(f"Scenario analysis completed with {len(result.scenarios)} scenarios")
        return result
        
    except Exception as e:
        logger.error(f"Scenario analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario analysis failed: {str(e)}"
        )


@router.post("/feature-importance")
async def analyze_feature_importance(
    team_a: TeamStatisticsBase,
    team_b: Optional[TeamStatisticsBase] = None,
    model_type: str = "gradient_boosting",
    num_simulations: int = 1000
):
    """
    Quick feature importance analysis without full advanced analytics.
    
    Returns the most important statistical features that influence match outcomes.
    """
    try:
        request = AdvancedAnalyticsRequest(
            team_a=team_a,
            team_b=team_b,
            analysis_types=[AnalysisType.FEATURE_IMPORTANCE],
            model_type=model_type,
            num_simulations=num_simulations,
            confidence_level=Decimal('0.95'),
            sensitivity_ranges={}
        )
        
        engine = AdvancedAnalyticsEngine()
        result = await engine.run_advanced_analysis(request)
        
        return {
            "feature_importance": result.team_a_analytics.feature_importances if result.team_a_analytics else [],
            "analysis_time": result.analysis_time_seconds,
            "simulation_count": result.simulation_count
        }
        
    except Exception as e:
        logger.error(f"Feature importance analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature importance analysis failed: {str(e)}"
        )


@router.post("/shap-analysis")
async def analyze_shap_values(
    team_a: TeamStatisticsBase,
    team_b: Optional[TeamStatisticsBase] = None,
    model_type: str = "gradient_boosting",
    num_simulations: int = 1000
):
    """
    SHAP (SHapley Additive exPlanations) analysis for interpretable ML explanations.
    
    Returns SHAP values that explain how each feature contributes to predictions.
    """
    try:
        request = AdvancedAnalyticsRequest(
            team_a=team_a,
            team_b=team_b,
            analysis_types=[AnalysisType.SHAP_VALUES],
            model_type=model_type,
            num_simulations=num_simulations,
            confidence_level=Decimal('0.95'),
            sensitivity_ranges={}
        )
        
        engine = AdvancedAnalyticsEngine()
        result = await engine.run_advanced_analysis(request)
        
        return {
            "shap_analysis": result.shap_analysis,
            "analysis_time": result.analysis_time_seconds,
            "simulation_count": result.simulation_count
        }
        
    except Exception as e:
        logger.error(f"SHAP analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP analysis failed: {str(e)}"
        )


@router.post("/sensitivity-analysis")
async def analyze_sensitivity(
    team_a: TeamStatisticsBase,
    team_b: Optional[TeamStatisticsBase] = None,
    sensitivity_ranges: Optional[Dict[str, list]] = None
):
    """
    Sensitivity analysis to understand how changes in specific stats affect outcomes.
    
    Tests how variations in key statistics impact win probability.
    """
    try:
        if sensitivity_ranges is None:
            # Default sensitivity ranges for key stats
            sensitivity_ranges = {
                "service_ace_percentage": [5.0, 10.0, 15.0, 20.0],
                "attack_kill_percentage": [35.0, 40.0, 45.0, 50.0],
                "dig_percentage": [25.0, 30.0, 35.0, 40.0]
            }
        
        # Convert list values to Decimal
        decimal_ranges = {}
        for key, values in sensitivity_ranges.items():
            decimal_ranges[key] = [Decimal(str(v)) for v in values]
        
        request = AdvancedAnalyticsRequest(
            team_a=team_a,
            team_b=team_b,
            analysis_types=[AnalysisType.SENSITIVITY_ANALYSIS],
            model_type="gradient_boosting",
            num_simulations=500,  # Fewer simulations for sensitivity
            confidence_level=Decimal('0.95'),
            sensitivity_ranges=decimal_ranges
        )
        
        engine = AdvancedAnalyticsEngine()
        result = await engine.run_advanced_analysis(request)
        
        return {
            "team_name": team_a.name,
            "sensitivity_results": result.team_a_analytics.sensitivity_results if result.team_a_analytics else [],
            "analysis_time": result.analysis_time_seconds
        }
        
    except Exception as e:
        logger.error(f"Sensitivity analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sensitivity analysis failed: {str(e)}"
        )


@router.get("/team-profile/{team_name}")
async def get_team_analytics_profile(
    team_name: str,
    team_stats: TeamStatisticsBase,
    comparison_team: Optional[TeamStatisticsBase] = None
):
    """
    Get a comprehensive analytics profile for a team.
    
    Provides feature importance, strengths/weaknesses, and improvement recommendations.
    """
    try:
        request = AdvancedAnalyticsRequest(
            team_a=team_stats,
            team_b=comparison_team,
            analysis_types=[AnalysisType.FEATURE_IMPORTANCE, AnalysisType.SHAP_VALUES],
            model_type="gradient_boosting",
            num_simulations=800,
            confidence_level=Decimal('0.95'),
            sensitivity_ranges={}
        )
        
        engine = AdvancedAnalyticsEngine()
        result = await engine.run_advanced_analysis(request)
        
        return {
            "team_profile": result.team_a_analytics,
            "overall_rating": result.team_a_analytics.overall_rating if result.team_a_analytics else 0,
            "analysis_time": result.analysis_time_seconds
        }
        
    except Exception as e:
        logger.error(f"Team profile analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Team profile analysis failed: {str(e)}"
        )


async def _run_background_analysis(analysis_id: str, request: AdvancedAnalyticsRequest):
    """Run advanced analytics analysis in the background."""
    try:
        # Update progress
        _analysis_results[analysis_id]["progress"] = 10
        
        engine = AdvancedAnalyticsEngine()
        
        # Update progress during analysis
        _analysis_results[analysis_id]["progress"] = 50
        
        result = await engine.run_advanced_analysis(request)
        
        # Store completed results
        _analysis_results[analysis_id] = {
            "status": "completed",
            "progress": 100,
            "results": result.model_dump(),
            "analysis_time": result.analysis_time_seconds,
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Background analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background analysis {analysis_id} failed: {str(e)}")
        _analysis_results[analysis_id] = {
            "status": "failed",
            "progress": _analysis_results[analysis_id].get("progress", 0),
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }
