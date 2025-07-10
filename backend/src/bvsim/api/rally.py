"""Rally simulation endpoints for testing the engine."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from decimal import Decimal
import logging

from ..engine import RallySimulator, TeamSide, RallyContext, RallyState
from ..schemas.team_statistics import TeamStatisticsBase
from ..schemas.common import SuccessResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/rally", tags=["Rally Simulation"])
logger = logging.getLogger(__name__)


class SimulateRallyRequest(BaseModel):
    """Request to simulate a single rally."""
    
    serving_team: TeamSide = Field(..., description="Which team serves first")
    team_a_stats: TeamStatisticsBase = Field(..., description="Team A statistics")
    team_b_stats: TeamStatisticsBase = Field(..., description="Team B statistics")
    
    # Optional context
    team_a_score: Optional[int] = Field(0, description="Team A current score")
    team_b_score: Optional[int] = Field(0, description="Team B current score")
    set_number: Optional[int] = Field(1, description="Current set number")
    momentum: Optional[Decimal] = Field(Decimal("0.0"), description="Current momentum (-1 to 1)")
    pressure_level: Optional[Decimal] = Field(Decimal("0.0"), description="Pressure level (0 to 1)")


class SimulateMultipleRalliesRequest(BaseModel):
    """Request to simulate multiple rallies."""
    
    num_rallies: int = Field(..., ge=1, le=10000, description="Number of rallies to simulate")
    serving_team: TeamSide = Field(..., description="Which team serves first")
    team_a_stats: TeamStatisticsBase = Field(..., description="Team A statistics")
    team_b_stats: TeamStatisticsBase = Field(..., description="Team B statistics")
    
    # Optional parameters
    random_seed: Optional[int] = Field(None, description="Random seed for reproducible results")


class RallyEventResponse(BaseModel):
    """Response format for rally events."""
    
    sequence_number: int
    state: str
    action_type: str
    performing_team: str
    probability: Decimal
    effectiveness: Optional[Decimal] = None


class RallyResultResponse(BaseModel):
    """Response format for rally results."""
    
    winner: TeamSide
    point_outcome: str
    rally_length: int
    final_state: str
    total_probability: Decimal
    team_a_actions: int
    team_b_actions: int
    events: List[RallyEventResponse]


class MultipleRalliesResultResponse(BaseModel):
    """Response format for multiple rally results."""
    
    num_rallies: int
    team_a_wins: int
    team_b_wins: int
    team_a_win_percentage: float
    team_b_win_percentage: float
    average_rally_length: float
    event_type_distribution: dict
    individual_results: List[RallyResultResponse]


# Initialize rally simulator
rally_simulator = RallySimulator()


@router.post("/simulate", response_model=RallyResultResponse)
async def simulate_rally(request: SimulateRallyRequest):
    """Simulate a single beach volleyball rally."""
    
    try:
        # Create rally context
        context = RallyContext(
            current_state=RallyState.SERVE_READY,
            serving_team=request.serving_team,
            rally_length=0,
            team_a_score=request.team_a_score,
            team_b_score=request.team_b_score,
            set_number=request.set_number,
            momentum=request.momentum,
            pressure_level=request.pressure_level
        )
        
        # Simulate the rally
        result = rally_simulator.simulate_rally(
            serving_team=request.serving_team,
            team_a_stats=request.team_a_stats,
            team_b_stats=request.team_b_stats,
            initial_context=context
        )
        
        # Convert events to response format
        events = [
            RallyEventResponse(
                sequence_number=event.sequence_number,
                state=event.state.value,
                action_type=event.action_type.value,
                performing_team=event.performing_team.value,
                probability=event.probability,
                effectiveness=event.effectiveness
            )
            for event in result.events
        ]
        
        response = RallyResultResponse(
            winner=result.winner,
            point_outcome=result.point_outcome.value,
            rally_length=result.rally_length,
            final_state=result.final_state.value if result.final_state else "unknown",
            total_probability=result.total_probability,
            team_a_actions=result.team_a_actions,
            team_b_actions=result.team_b_actions,
            events=events
        )
        
        logger.info(f"Rally simulated: {result.winner} wins after {result.rally_length} actions")
        return response
        
    except Exception as e:
        logger.error(f"Error simulating rally: {e}")
        raise HTTPException(status_code=500, detail=f"Rally simulation failed: {str(e)}")


@router.post("/simulate-multiple", response_model=MultipleRalliesResultResponse)  
async def simulate_multiple_rallies(request: SimulateMultipleRalliesRequest):
    """Simulate multiple beach volleyball rallies for statistical analysis."""
    
    try:
        # Set random seed if provided
        if request.random_seed is not None:
            rally_simulator.set_random_seed(request.random_seed)
        
        # Simulate multiple rallies
        results = rally_simulator.simulate_multiple_rallies(
            num_rallies=request.num_rallies,
            serving_team=request.serving_team,
            team_a_stats=request.team_a_stats,
            team_b_stats=request.team_b_stats
        )
        
        # Calculate statistics
        team_a_wins = sum(1 for r in results if r.winner == TeamSide.TEAM_A)
        team_b_wins = sum(1 for r in results if r.winner == TeamSide.TEAM_B)
        avg_rally_length = sum(r.rally_length for r in results) / len(results) if results else 0
        
        # Event type distribution
        all_events = [event for result in results for event in result.events]
        event_types = {}
        for event in all_events:
            action = event.action_type.value
            event_types[action] = event_types.get(action, 0) + 1
        
        # Convert individual results to response format
        individual_results = []
        for result in results:
            events = [
                RallyEventResponse(
                    sequence_number=event.sequence_number,
                    state=event.state.value,
                    action_type=event.action_type.value,
                    performing_team=event.performing_team.value,
                    probability=event.probability,
                    effectiveness=event.effectiveness
                )
                for event in result.events
            ]
            
            individual_results.append(RallyResultResponse(
                winner=result.winner,
                point_outcome=result.point_outcome.value,
                rally_length=result.rally_length,
                final_state=result.final_state.value if result.final_state else "unknown",
                total_probability=result.total_probability,
                team_a_actions=result.team_a_actions,
                team_b_actions=result.team_b_actions,
                events=events
            ))
        
        response = MultipleRalliesResultResponse(
            num_rallies=request.num_rallies,
            team_a_wins=team_a_wins,
            team_b_wins=team_b_wins,
            team_a_win_percentage=team_a_wins / request.num_rallies * 100 if request.num_rallies > 0 else 0,
            team_b_win_percentage=team_b_wins / request.num_rallies * 100 if request.num_rallies > 0 else 0,
            average_rally_length=avg_rally_length,
            event_type_distribution=event_types,
            individual_results=individual_results
        )
        
        logger.info(f"Simulated {request.num_rallies} rallies: A={team_a_wins}, B={team_b_wins}")
        return response
        
    except Exception as e:
        logger.error(f"Error simulating multiple rallies: {e}")
        raise HTTPException(status_code=500, detail=f"Multiple rally simulation failed: {str(e)}")


@router.get("/test-teams")
async def get_test_teams():
    """Get pre-configured test team statistics for demo purposes."""
    
    def create_test_team(name: str, skill_level: float) -> TeamStatisticsBase:
        """Helper to create test team stats."""
        ace_pct = skill_level * 8
        serve_error_pct = (1 - skill_level) * 12
        
        perfect_pass_pct = skill_level * 35
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
    
    teams = {
        "elite_team": create_test_team("Elite Team", 0.9),
        "strong_team": create_test_team("Strong Team", 0.8),
        "average_team": create_test_team("Average Team", 0.7),
        "developing_team": create_test_team("Developing Team", 0.6),
        "beginner_team": create_test_team("Beginner Team", 0.5)
    }
    
    return SuccessResponse(
        message="Test teams retrieved successfully",
        data=teams
    )
