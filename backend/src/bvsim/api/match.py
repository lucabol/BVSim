"""
Match simulation API endpoints.
Provides REST API for match-level simulations and tournament brackets.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Optional
import asyncio
import uuid
import logging
from datetime import datetime

from ..schemas.match import (
    MatchSimulationRequest, MatchSimulationResponse,
    TournamentBracket, TournamentResult,
    MatchFormat, MatchResult
)
from ..engine.match_simulator import MatchSimulator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/match", tags=["match-simulation"])

# Global match simulator instance
match_simulator = MatchSimulator()

# In-memory storage for async simulations
simulation_tasks: Dict[str, asyncio.Task] = {}
simulation_results: Dict[str, MatchSimulationResponse] = {}


@router.post("/simulate", response_model=MatchSimulationResponse)
async def simulate_match(request: MatchSimulationRequest):
    """
    Simulate beach volleyball matches with advanced features.
    
    Supports:
    - Best-of-1 and best-of-3 match formats
    - Momentum effects during matches
    - Pressure situation analysis
    - Detailed rally-by-rally breakdown
    - Statistical confidence intervals
    """
    try:
        logger.info(f"Starting match simulation: {request.num_simulations} matches")
        
        # Validate team data
        if request.team_a.name == request.team_b.name:
            raise HTTPException(
                status_code=400,
                detail="Team A and Team B must have different names"
            )
        
        # Run the simulation
        result = await match_simulator.run_match_simulation(request)
        
        logger.info(
            f"Match simulation completed: {result.statistics.total_matches} matches, "
            f"Team A win rate: {float(result.statistics.team_a_win_probability):.3f}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Match simulation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/simulate-async")
async def simulate_match_async(request: MatchSimulationRequest, 
                              background_tasks: BackgroundTasks):
    """
    Start asynchronous match simulation for large datasets.
    
    For simulations with > 5000 matches, this endpoint runs the simulation
    in the background and returns a task ID for status checking.
    """
    if request.num_simulations < 5000:
        raise HTTPException(
            status_code=400,
            detail="Use synchronous endpoint for simulations < 5000 matches"
        )
    
    simulation_id = str(uuid.uuid4())
    
    # Create and store the task
    task = asyncio.create_task(
        _run_background_match_simulation(simulation_id, request)
    )
    simulation_tasks[simulation_id] = task
    
    logger.info(f"Started async match simulation {simulation_id}")
    
    return {
        "simulation_id": simulation_id,
        "status": "started",
        "estimated_time_minutes": request.num_simulations / 1000 * 2,  # Rough estimate
        "check_status_url": f"/match/status/{simulation_id}"
    }


@router.get("/status/{simulation_id}")
async def get_simulation_status(simulation_id: str):
    """Check the status of an asynchronous match simulation."""
    
    if simulation_id not in simulation_tasks:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    task = simulation_tasks[simulation_id]
    
    if task.done():
        if simulation_id in simulation_results:
            # Simulation completed successfully
            result = simulation_results[simulation_id]
            return {
                "simulation_id": simulation_id,
                "status": "completed",
                "result": result
            }
        else:
            # Simulation failed
            try:
                task.result()  # This will raise the exception
            except Exception as e:
                return {
                    "simulation_id": simulation_id,
                    "status": "failed",
                    "error": str(e)
                }
    else:
        # Still running
        return {
            "simulation_id": simulation_id,
            "status": "running",
            "message": "Simulation in progress..."
        }


@router.post("/single-match", response_model=MatchResult)
async def simulate_single_match(request: MatchSimulationRequest):
    """
    Simulate a single match between two teams.
    
    Returns detailed match result including:
    - Set-by-set scores
    - Rally-by-rally breakdown (if requested)
    - Momentum and pressure analytics
    """
    try:
        # Override num_simulations to 1 for single match
        single_match_request = request.model_copy()
        single_match_request.num_simulations = 1
        single_match_request.include_rally_details = True
        
        # Simulate single match
        result = await match_simulator.simulate_match(
            request.team_a,
            request.team_b,
            request.match_format,
            request.momentum_effects,
            request.pressure_effects
        )
        
        logger.info(f"Single match simulated: {result.winner} wins")
        return result
        
    except Exception as e:
        logger.error(f"Single match simulation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/quick-comparison")
async def quick_match_comparison(request: MatchSimulationRequest):
    """
    Quick comparison between two teams using simplified simulation.
    
    Provides fast insights for team matchup analysis without
    full Monte Carlo simulation.
    """
    try:
        # Run a quick 100-match simulation
        quick_request = request.model_copy()
        quick_request.num_simulations = 100
        quick_request.include_rally_details = False
        quick_request.momentum_effects = False
        quick_request.pressure_effects = False
        
        result = await match_simulator.run_match_simulation(quick_request)
        
        # Simplified response format
        comparison = {
            "team_a": {
                "name": request.team_a.name,
                "win_probability": float(result.statistics.team_a_win_probability),
                "expected_sets_per_match": float(result.statistics.avg_sets_per_match) 
                                         if result.statistics.team_a_win_probability > 0.5 
                                         else 3.0 - float(result.statistics.avg_sets_per_match)
            },
            "team_b": {
                "name": request.team_b.name,
                "win_probability": float(result.statistics.team_b_win_probability),
                "expected_sets_per_match": float(result.statistics.avg_sets_per_match) 
                                         if result.statistics.team_b_win_probability > 0.5 
                                         else 3.0 - float(result.statistics.avg_sets_per_match)
            },
            "competitiveness": {
                "margin_of_error": float(result.statistics.margin_of_error),
                "is_close_matchup": result.statistics.margin_of_error < 0.15,
                "favorite": "Team A" if result.statistics.team_a_win_probability > 0.5 else "Team B",
                "confidence_level": "high" if result.statistics.is_statistically_significant else "medium"
            },
            "simulation_meta": {
                "matches_simulated": result.statistics.total_matches,
                "simulation_time": result.simulation_time_seconds
            }
        }
        
        return comparison
        
    except Exception as e:
        logger.error(f"Quick comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


async def _run_background_match_simulation(simulation_id: str, 
                                         request: MatchSimulationRequest):
    """Run match simulation in background task."""
    try:
        result = await match_simulator.run_match_simulation(request)
        simulation_results[simulation_id] = result
        logger.info(f"Background match simulation {simulation_id} completed")
        
    except Exception as e:
        logger.error(f"Background match simulation {simulation_id} failed: {str(e)}")
        raise
    finally:
        # Clean up task reference
        if simulation_id in simulation_tasks:
            del simulation_tasks[simulation_id]


# Tournament simulation endpoints (placeholder for future implementation)

@router.post("/tournament/create", response_model=Dict[str, str])
async def create_tournament_bracket(bracket: TournamentBracket):
    """Create a tournament bracket (placeholder for Phase 4)."""
    # This will be implemented in Phase 4
    return {
        "tournament_id": bracket.tournament_id,
        "status": "created",
        "message": "Tournament bracket created (simulation not yet implemented)"
    }


@router.get("/tournament/{tournament_id}/simulate")
async def simulate_tournament(tournament_id: str):
    """Simulate an entire tournament bracket (placeholder for Phase 4)."""
    # This will be implemented in Phase 4
    return {
        "tournament_id": tournament_id,
        "status": "not_implemented",
        "message": "Tournament simulation will be available in Phase 4"
    }
