"""
Match-level schemas for beach volleyball simulation.
Defines data models for matches, sets, and tournaments.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Annotated
from enum import Enum
from datetime import datetime
from decimal import Decimal

from .team_statistics import TeamStatisticsBase


"""
Match-level schemas for beach volleyball simulation.
Defines data models for matches, sets, and tournaments.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any, Annotated
from enum import Enum
from datetime import datetime
from decimal import Decimal

from .team_statistics import TeamStatisticsBase


class MatchFormat(str, Enum):
    """Supported match formats."""
    BEST_OF_ONE = "best_of_1"
    BEST_OF_THREE = "best_of_3"


class SetResult(BaseModel):
    """Result of a single set in a match."""
    set_number: int = Field(..., ge=1, le=3)
    team_a_score: int = Field(..., ge=0)
    team_b_score: int = Field(..., ge=0)
    winner: Annotated[str, Field(pattern=r"^[AB]$")]
    total_rallies: int = Field(..., ge=0)
    duration_seconds: Optional[float] = None
    rally_results: Optional[List[Dict[str, Any]]] = None


class MatchResult(BaseModel):
    """Complete result of a beach volleyball match."""
    match_id: str
    team_a_name: str
    team_b_name: str
    match_format: MatchFormat
    winner: Annotated[str, Field(pattern=r"^[AB]$")]
    sets: List[SetResult]
    total_duration_seconds: Optional[float] = None
    match_date: Optional[datetime] = None
    
    @field_validator('sets')
    @classmethod
    def validate_sets(cls, v, info):
        """Validate set results match the match format."""
        if info.data:
            match_format = info.data.get('match_format')
            if match_format == MatchFormat.BEST_OF_ONE and len(v) != 1:
                raise ValueError("Best-of-1 match must have exactly 1 set")
            elif match_format == MatchFormat.BEST_OF_THREE and not (2 <= len(v) <= 3):
                raise ValueError("Best-of-3 match must have 2 or 3 sets")
        return v


class MatchSimulationRequest(BaseModel):
    """Request for match simulation."""
    team_a: TeamStatisticsBase
    team_b: TeamStatisticsBase
    match_format: MatchFormat = MatchFormat.BEST_OF_THREE
    num_simulations: int = Field(default=1000, ge=1, le=100000)
    include_rally_details: bool = Field(default=False)
    momentum_effects: bool = Field(default=True)
    pressure_effects: bool = Field(default=True)
    random_seed: Optional[int] = None


class MatchStatistics(BaseModel):
    """Statistical analysis of match simulation results."""
    total_matches: int
    team_a_wins: int
    team_b_wins: int
    team_a_win_probability: Decimal
    team_b_win_probability: Decimal
    confidence_interval_lower: Decimal
    confidence_interval_upper: Decimal
    margin_of_error: Decimal
    is_statistically_significant: bool
    
    # Set-level statistics
    avg_sets_per_match: Decimal
    straight_set_wins_a: int  # 2-0 wins for team A
    straight_set_wins_b: int  # 2-0 wins for team B
    three_set_matches: int    # Matches that went to 3 sets
    
    # Rally-level insights
    avg_rallies_per_set: Decimal
    avg_rally_length: Decimal  # Average number of contacts per rally
    longest_rally_contacts: int
    shortest_rally_contacts: int


class MatchSimulationResponse(BaseModel):
    """Response from match simulation."""
    simulation_id: str
    request: MatchSimulationRequest
    statistics: MatchStatistics
    sample_matches: Optional[List[MatchResult]] = None
    simulation_time_seconds: float
    created_at: datetime


class TournamentBracket(BaseModel):
    """Tournament bracket configuration."""
    tournament_id: str
    name: str
    teams: Annotated[List[TeamStatisticsBase], Field(min_length=4, max_length=64)]
    match_format: MatchFormat = MatchFormat.BEST_OF_THREE
    elimination_format: Annotated[str, Field(pattern=r"^(single|double)$")] = "single"
    
    @field_validator('teams')
    @classmethod
    def validate_team_count(cls, v):
        """Ensure team count is a power of 2."""
        count = len(v)
        if count & (count - 1) != 0:
            raise ValueError("Number of teams must be a power of 2 (4, 8, 16, 32, 64)")
        return v


class TournamentMatch(BaseModel):
    """A match within a tournament bracket."""
    match_id: str
    round_number: int
    position_in_round: int
    team_a: Optional[TeamStatisticsBase] = None
    team_b: Optional[TeamStatisticsBase] = None
    result: Optional[MatchResult] = None
    next_match_id: Optional[str] = None  # Winner advances to this match


class TournamentResult(BaseModel):
    """Complete tournament simulation result."""
    tournament_id: str
    winner: TeamStatisticsBase
    runner_up: TeamStatisticsBase
    matches: List[TournamentMatch]
    total_simulation_time: float
    bracket_size: int


class MomentumState(BaseModel):
    """Current momentum state in a match."""
    team_a_momentum: Decimal = Field(default=Decimal('0.0'), ge=Decimal('-1.0'), le=Decimal('1.0'))
    team_b_momentum: Decimal = Field(default=Decimal('0.0'), ge=Decimal('-1.0'), le=Decimal('1.0'))
    consecutive_points_a: int = Field(default=0, ge=0)
    consecutive_points_b: int = Field(default=0, ge=0)
    recent_rally_outcomes: List[str] = Field(default_factory=list, max_length=5)


class PressureSituation(BaseModel):
    """Pressure situation analysis for a rally."""
    is_set_point: bool = False
    is_match_point: bool = False
    score_differential: int = 0
    serving_team_behind: bool = False
    pressure_level: Decimal = Field(default=Decimal('0.0'), ge=Decimal('0.0'), le=Decimal('1.0'))


class RallyContext(BaseModel):
    """Complete context for a rally simulation."""
    set_number: int
    team_a_score: int
    team_b_score: int
    serving_team: Annotated[str, Field(pattern=r"^[AB]$")]
    momentum: Optional[MomentumState] = None
    pressure: Optional[PressureSituation] = None
    rally_number: int = 1


class AdvancedRallyResult(BaseModel):
    """Enhanced rally result with context and analytics."""
    basic_result: Dict[str, Any]  # From our existing rally simulation
    context: RallyContext
    rally_analytics: Dict[str, Any]
    momentum_change: Optional[Decimal] = None
    pressure_effect: Optional[Decimal] = None
