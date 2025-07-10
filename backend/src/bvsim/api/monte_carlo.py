"""API endpoints for Monte Carlo simulation engine."""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
from decimal import Decimal
import asyncio
import uuid
import time
import logging

from ..engine.monte_carlo import (
    MonteCarloEngine, SimulationBatch, SimulationResults, 
    MatchFormat, MatchResult, SetResult
)
from ..schemas.team_statistics import TeamStatisticsBase
from ..schemas.common import SuccessResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/simulation", tags=["Monte Carlo Simulation"])
logger = logging.getLogger(__name__)


class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo simulation."""
    
    num_simulations: int = Field(
        ..., 
        ge=100, 
        le=100000, 
        description="Number of simulations to run (100-100,000)"
    )
    team_a_stats: TeamStatisticsBase = Field(..., description="Team A statistics")
    team_b_stats: TeamStatisticsBase = Field(..., description="Team B statistics")
    match_format: MatchFormat = Field(
        default=MatchFormat.BEST_OF_3, 
        description="Match format"
    )
    
    # Simulation options
    parallel_workers: Optional[int] = Field(
        None, 
        ge=1, 
        le=16, 
        description="Number of parallel workers (auto-detect if not specified)"
    )
    random_seed: Optional[int] = Field(
        None, 
        description="Random seed for reproducible results"
    )
    include_detailed_results: bool = Field(
        default=False, 
        description="Include individual match results (impacts performance)"
    )
    
    # Context options
    momentum_enabled: bool = Field(default=True, description="Enable momentum effects")
    pressure_enabled: bool = Field(default=True, description="Enable pressure effects")
    fatigue_enabled: bool = Field(default=True, description="Enable fatigue effects")


class QuickSimulationRequest(BaseModel):
    """Quick simulation request with minimal options."""
    
    team_a_name: str = Field(..., description="Team A name")
    team_b_name: str = Field(..., description="Team B name")
    team_a_skill_level: float = Field(
        ..., 
        ge=0.1, 
        le=1.0, 
        description="Team A skill level (0.1-1.0)"
    )
    team_b_skill_level: float = Field(
        ..., 
        ge=0.1, 
        le=1.0, 
        description="Team B skill level (0.1-1.0)"
    )
    num_simulations: int = Field(
        default=1000, 
        ge=100, 
        le=10000, 
        description="Number of simulations"
    )


class SetResultResponse(BaseModel):
    """Response format for set results."""
    
    set_number: int
    set_type: str
    winner: str
    team_a_score: int
    team_b_score: int
    rally_count: int
    was_close: bool


class MatchResultResponse(BaseModel):
    """Response format for match results."""
    
    match_id: str
    format: str
    winner: str
    team_a_sets_won: int
    team_b_sets_won: int
    total_points_a: int
    total_points_b: int
    total_rallies: int
    sets: List[SetResultResponse]


class SimulationResultsResponse(BaseModel):
    """Response format for simulation results."""
    
    simulation_id: str
    num_simulations: int
    
    # Win probabilities
    team_a_win_probability: Decimal
    team_b_win_probability: Decimal
    team_a_win_count: int
    team_b_win_count: int
    
    # Confidence intervals
    confidence_interval_lower: Decimal
    confidence_interval_upper: Decimal
    margin_of_error: Decimal
    is_statistically_significant: bool
    
    # Match statistics
    avg_sets_per_match: float
    avg_rallies_per_match: float
    set_distribution: Dict[str, int]
    
    # Performance metrics
    simulation_time_seconds: float
    simulations_per_second: float
    
    # Detailed results (optional)
    individual_matches: Optional[List[MatchResultResponse]] = None


class SimulationStatus(BaseModel):
    """Status of a running simulation."""
    
    simulation_id: str
    status: str  # "running", "completed", "failed"
    progress_percentage: Optional[float] = None
    estimated_completion_seconds: Optional[float] = None
    result: Optional[SimulationResultsResponse] = None
    error_message: Optional[str] = None


# Global engine instance
monte_carlo_engine = MonteCarloEngine()

# In-memory storage for simulation status (in production, use Redis/database)
simulation_status: Dict[str, SimulationStatus] = {}


def create_team_stats_from_skill_level(name: str, skill_level: float) -> TeamStatisticsBase:
    """Create team statistics from a skill level (0.1-1.0)."""
    
    # Convert skill level to volleyball percentages
    ace_pct = skill_level * 8  # 0.8% to 8% ace rate
    serve_error_pct = (1 - skill_level) * 12  # 12% to 1.2% error rate
    
    perfect_pass_pct = skill_level * 35  # 3.5% to 35%
    good_pass_pct = skill_level * 30 + (1 - skill_level) * 25
    poor_pass_pct = (1 - skill_level) * 30
    reception_error_pct = (1 - skill_level) * 15
    
    # Normalize reception percentages
    reception_total = perfect_pass_pct + good_pass_pct + poor_pass_pct + reception_error_pct
    if reception_total > 0:
        perfect_pass_pct = perfect_pass_pct / reception_total * 100
        good_pass_pct = good_pass_pct / reception_total * 100
        poor_pass_pct = poor_pass_pct / reception_total * 100
        reception_error_pct = reception_error_pct / reception_total * 100
    
    return TeamStatisticsBase(
        name=name,
        service_ace_percentage=Decimal(str(ace_pct)),
        service_error_percentage=Decimal(str(serve_error_pct)),
        serve_success_rate=Decimal(str(skill_level * 60)),
        perfect_pass_percentage=Decimal(str(perfect_pass_pct)),
        good_pass_percentage=Decimal(str(good_pass_pct)),
        poor_pass_percentage=Decimal(str(poor_pass_pct)),
        reception_error_percentage=Decimal(str(reception_error_pct)),
        assist_percentage=Decimal(str(skill_level * 45)),
        ball_handling_error_percentage=Decimal(str((1 - skill_level) * 8)),
        attack_kill_percentage=Decimal(str(skill_level * 35)),
        attack_error_percentage=Decimal(str((1 - skill_level) * 15)),
        hitting_efficiency=Decimal(str(skill_level * 0.6 - 0.1)),
        first_ball_kill_percentage=Decimal(str(skill_level * 25)),
        dig_percentage=Decimal(str(skill_level * 70)),
        block_kill_percentage=Decimal(str(skill_level * 12)),
        controlled_block_percentage=Decimal(str(skill_level * 25)),
        blocking_error_percentage=Decimal(str((1 - skill_level) * 8))
    )


def convert_simulation_results(
    results: SimulationResults, 
    simulation_id: str
) -> SimulationResultsResponse:
    """Convert internal simulation results to API response format."""
    
    # Convert individual matches if included
    individual_matches = None
    if results.individual_matches:
        individual_matches = []
        for match in results.individual_matches:
            sets = [
                SetResultResponse(
                    set_number=s.set_number,
                    set_type=s.set_type.value,
                    winner=s.winner.value,
                    team_a_score=s.team_a_score,
                    team_b_score=s.team_b_score,
                    rally_count=s.rally_count,
                    was_close=s.was_close
                )
                for s in match.sets
            ]
            
            individual_matches.append(MatchResultResponse(
                match_id=match.match_id,
                format=match.format.value,
                winner=match.winner.value,
                team_a_sets_won=match.team_a_sets_won,
                team_b_sets_won=match.team_b_sets_won,
                total_points_a=match.total_points_a,
                total_points_b=match.total_points_b,
                total_rallies=match.total_rallies,
                sets=sets
            ))
    
    return SimulationResultsResponse(
        simulation_id=simulation_id,
        num_simulations=results.num_simulations,
        team_a_win_probability=results.team_a_win_probability,
        team_b_win_probability=results.team_b_win_probability,
        team_a_win_count=results.team_a_win_count,
        team_b_win_count=results.team_b_win_count,
        confidence_interval_lower=results.confidence_interval_95[0],
        confidence_interval_upper=results.confidence_interval_95[1],
        margin_of_error=results.margin_of_error,
        is_statistically_significant=results.is_statistically_significant,
        avg_sets_per_match=results.avg_sets_per_match,
        avg_rallies_per_match=results.avg_rallies_per_match,
        set_distribution=results.set_distribution,
        simulation_time_seconds=results.simulation_time_seconds,
        simulations_per_second=results.num_simulations / results.simulation_time_seconds,
        individual_matches=individual_matches
    )


@router.post("/monte-carlo", response_model=SimulationResultsResponse)
async def run_monte_carlo_simulation(request: MonteCarloRequest):
    """Run a Monte Carlo simulation for match prediction."""
    
    try:
        simulation_id = str(uuid.uuid4())
        
        # Create simulation batch
        batch = SimulationBatch(
            num_simulations=request.num_simulations,
            team_a_stats=request.team_a_stats,
            team_b_stats=request.team_b_stats,
            match_format=request.match_format,
            parallel_workers=request.parallel_workers,
            random_seed_base=request.random_seed,
            include_detailed_results=request.include_detailed_results,
            momentum_enabled=request.momentum_enabled,
            pressure_enabled=request.pressure_enabled,
            fatigue_enabled=request.fatigue_enabled
        )
        
        # Run simulation
        results = await monte_carlo_engine.run_simulation_batch(batch)
        
        # Convert to response format
        response = convert_simulation_results(results, simulation_id)
        
        logger.info(f"Monte Carlo simulation completed: {simulation_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in Monte Carlo simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/quick-simulation", response_model=SimulationResultsResponse)
async def run_quick_simulation(request: QuickSimulationRequest):
    """Run a quick simulation with simplified team inputs."""
    
    try:
        # Create team statistics from skill levels
        team_a_stats = create_team_stats_from_skill_level(
            request.team_a_name, request.team_a_skill_level
        )
        team_b_stats = create_team_stats_from_skill_level(
            request.team_b_name, request.team_b_skill_level
        )
        
        # Create full Monte Carlo request
        mc_request = MonteCarloRequest(
            num_simulations=request.num_simulations,
            team_a_stats=team_a_stats,
            team_b_stats=team_b_stats,
            match_format=MatchFormat.BEST_OF_3,
            parallel_workers=None,
            random_seed=None,
            include_detailed_results=False
        )
        
        return await run_monte_carlo_simulation(mc_request)
        
    except Exception as e:
        logger.error(f"Error in quick simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Quick simulation failed: {str(e)}")


@router.post("/monte-carlo-async", response_model=Dict[str, str])
async def start_monte_carlo_simulation_async(
    request: MonteCarloRequest, 
    background_tasks: BackgroundTasks
):
    """Start a Monte Carlo simulation in the background."""
    
    simulation_id = str(uuid.uuid4())
    
    # Initialize status
    simulation_status[simulation_id] = SimulationStatus(
        simulation_id=simulation_id,
        status="running",
        progress_percentage=0.0
    )
    
    # Start background task
    background_tasks.add_task(
        _run_simulation_background, 
        simulation_id, 
        request
    )
    
    return {
        "simulation_id": simulation_id,
        "status": "started",
        "status_url": f"/simulation/status/{simulation_id}"
    }


@router.get("/status/{simulation_id}", response_model=SimulationStatus)
async def get_simulation_status(simulation_id: str):
    """Get the status of a running simulation."""
    
    if simulation_id not in simulation_status:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return simulation_status[simulation_id]


@router.get("/performance", response_model=Dict[str, Any])
async def get_engine_performance():
    """Get performance statistics for the Monte Carlo engine."""
    
    stats = monte_carlo_engine.get_performance_stats()
    
    return SuccessResponse(
        message="Performance statistics retrieved",
        data=stats
    )


@router.get("/benchmark", response_model=Dict[str, Any])
async def run_performance_benchmark():
    """Run a performance benchmark of the simulation engine."""
    
    try:
        # Create test teams
        team_a = create_team_stats_from_skill_level("Team A", 0.7)
        team_b = create_team_stats_from_skill_level("Team B", 0.7)
        
        # Run benchmark with different simulation counts
        benchmarks = {}
        test_counts = [100, 500, 1000, 5000]
        
        for count in test_counts:
            start_time = time.time()
            
            batch = SimulationBatch(
                num_simulations=count,
                team_a_stats=team_a,
                team_b_stats=team_b,
                match_format=MatchFormat.BEST_OF_3,
                include_detailed_results=False
            )
            
            results = await monte_carlo_engine.run_simulation_batch(batch)
            elapsed_time = time.time() - start_time
            
            benchmarks[f"{count}_simulations"] = {
                "simulation_count": count,
                "time_seconds": elapsed_time,
                "simulations_per_second": count / elapsed_time,
                "team_a_win_rate": float(results.team_a_win_probability),
                "margin_of_error": float(results.margin_of_error)
            }
        
        return SuccessResponse(
            message="Performance benchmark completed",
            data={
                "benchmarks": benchmarks,
                "engine_stats": monte_carlo_engine.get_performance_stats()
            }
        )
        
    except Exception as e:
        logger.error(f"Error in performance benchmark: {e}")
        raise HTTPException(status_code=500, detail=f"Benchmark failed: {str(e)}")


async def _run_simulation_background(simulation_id: str, request: MonteCarloRequest):
    """Run simulation in the background and update status."""
    
    try:
        # Update status to running
        simulation_status[simulation_id].status = "running"
        simulation_status[simulation_id].progress_percentage = 10.0
        
        # Create simulation batch
        batch = SimulationBatch(
            num_simulations=request.num_simulations,
            team_a_stats=request.team_a_stats,
            team_b_stats=request.team_b_stats,
            match_format=request.match_format,
            parallel_workers=request.parallel_workers,
            random_seed_base=request.random_seed,
            include_detailed_results=request.include_detailed_results,
            momentum_enabled=request.momentum_enabled,
            pressure_enabled=request.pressure_enabled,
            fatigue_enabled=request.fatigue_enabled
        )
        
        # Update progress
        simulation_status[simulation_id].progress_percentage = 50.0
        
        # Run simulation
        results = await monte_carlo_engine.run_simulation_batch(batch)
        
        # Convert results
        response = convert_simulation_results(results, simulation_id)
        
        # Update status to completed
        simulation_status[simulation_id].status = "completed"
        simulation_status[simulation_id].progress_percentage = 100.0
        simulation_status[simulation_id].result = response
        
        logger.info(f"Background simulation completed: {simulation_id}")
        
    except Exception as e:
        logger.error(f"Background simulation failed: {simulation_id}, {e}")
        simulation_status[simulation_id].status = "failed"
        simulation_status[simulation_id].error_message = str(e)
