"""Pydantic schemas for simulations."""

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any, Self
from decimal import Decimal
from datetime import datetime
from enum import Enum


class SimulationStatus(str, Enum):
    """Simulation status enumeration."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SimulationConfigBase(BaseModel):
    """Base configuration for simulations."""
    
    num_points: int = Field(
        default=10000,
        ge=100,
        le=1000000,
        description="Number of points to simulate"
    )
    random_seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility"
    )
    enable_momentum: bool = Field(
        default=False,
        description="Enable momentum effects in simulation"
    )
    parallel_workers: Optional[int] = Field(
        default=None,
        ge=1,
        le=16,
        description="Number of parallel workers (auto-detect if None)"
    )


class SimulationCreate(SimulationConfigBase):
    """Schema for creating a new simulation."""
    
    team_a_id: int = Field(..., description="Team A statistics ID")
    team_b_id: int = Field(..., description="Team B statistics ID")
    
    @model_validator(mode='after')
    def validate_teams_different(self) -> Self:
        """Ensure teams are different."""
        if self.team_a_id == self.team_b_id:
            raise ValueError("Team A and Team B must be different")
        return self


class RallyStateTransition(BaseModel):
    """Individual state transition in a rally."""
    
    from_state: str = Field(..., description="Source state")
    to_state: str = Field(..., description="Target state") 
    probability: Decimal = Field(..., description="Transition probability")
    team: str = Field(..., description="Acting team (A or B)")


class PointResult(BaseModel):
    """Result of a single simulated point."""
    
    point_number: int = Field(..., description="Point number in simulation")
    winner_team: str = Field(..., description="Winning team (A or B)")
    serving_team: str = Field(..., description="Serving team (A or B)")
    rally_states: List[RallyStateTransition] = Field(
        ..., description="Rally state progression"
    )
    total_contacts: int = Field(..., description="Total ball contacts in rally")
    rally_duration_ms: Optional[int] = Field(
        None, description="Rally duration in milliseconds"
    )


class SimulationResult(BaseModel):
    """Complete simulation results."""
    
    team_a_wins: int = Field(..., description="Points won by Team A")
    team_b_wins: int = Field(..., description="Points won by Team B")
    total_points: int = Field(..., description="Total points simulated")
    team_a_win_probability: Decimal = Field(
        ..., description="Team A win probability"
    )
    team_b_win_probability: Decimal = Field(
        ..., description="Team B win probability"
    )
    simulation_time_seconds: Decimal = Field(
        ..., description="Simulation execution time"
    )


class SimulationInDB(SimulationConfigBase):
    """Schema for simulation in database."""
    
    id: int
    team_a_id: int
    team_b_id: int
    
    # Results (optional until completed)
    team_a_wins: Optional[int] = None
    team_b_wins: Optional[int] = None
    team_a_win_probability: Optional[Decimal] = None
    team_b_win_probability: Optional[Decimal] = None
    
    # Status and timing
    status: SimulationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    simulation_time_seconds: Optional[Decimal] = None
    
    # Configuration JSON
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True


class SimulationResponse(SimulationInDB):
    """Schema for simulation API response."""
    
    # Include team information
    team_a: Optional[Dict[str, Any]] = None
    team_b: Optional[Dict[str, Any]] = None
    
    # Include summary statistics if completed
    result_summary: Optional[SimulationResult] = None


class SimulationSummary(BaseModel):
    """Summary schema for simulation listings."""
    
    id: int
    team_a_id: int
    team_b_id: int
    team_a_name: str
    team_b_name: str
    num_points: int
    status: SimulationStatus
    team_a_win_probability: Optional[Decimal] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class SimulationProgress(BaseModel):
    """Schema for simulation progress updates."""
    
    simulation_id: int
    status: SimulationStatus
    progress_percentage: Decimal = Field(ge=0, le=100)
    points_completed: int
    total_points: int
    estimated_time_remaining_seconds: Optional[int] = None
    current_team_a_wins: Optional[int] = None
    current_team_b_wins: Optional[int] = None


# Batch simulation schemas
class BatchSimulationCreate(BaseModel):
    """Schema for creating batch simulations."""
    
    simulations: List[SimulationCreate] = Field(
        ..., 
        description="List of simulations to run (1-10 items)"
    )
    run_parallel: bool = Field(
        default=True,
        description="Run simulations in parallel"
    )
    
    @model_validator(mode='after')
    def validate_simulation_count(self) -> Self:
        """Validate simulation count is within limits."""
        if not (1 <= len(self.simulations) <= 10):
            raise ValueError("Must provide between 1 and 10 simulations")
        return self


class BatchSimulationResponse(BaseModel):
    """Schema for batch simulation response."""
    
    batch_id: str
    total_simulations: int
    completed_simulations: int
    failed_simulations: int
    simulation_ids: List[int]
    status: str  # 'running', 'completed', 'failed'
    created_at: datetime


class SimulationUpdate(BaseModel):
    """Schema for updating simulation settings."""
    
    status: Optional[SimulationStatus] = None
    num_points: Optional[int] = Field(None, ge=100, le=1000000)
    enable_momentum: Optional[bool] = None
    parallel_workers: Optional[int] = Field(None, ge=1, le=16)


class SimulationBatch(BaseModel):
    """Schema for batch operations on simulations."""
    
    operation: str = Field(..., description="Batch operation type")
    simulation_ids: List[int] = Field(..., description="List of simulation IDs")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")


class SimulationFilters(BaseModel):
    """Schema for filtering simulations."""
    
    status: Optional[List[SimulationStatus]] = None
    team_a_id: Optional[int] = None
    team_b_id: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_points: Optional[int] = None
    max_points: Optional[int] = None


class SimulationPoint(BaseModel):
    """Individual simulation point result."""
    
    point_id: int
    simulation_id: int
    point_number: int
    serving_team: str
    winning_team: str
    rally_length: int
    sequence_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        orm_mode = True


class SetResult(BaseModel):
    """Set-level results for match simulation."""
    
    set_number: int
    team_a_score: int
    team_b_score: int
    winner: str
    set_duration_minutes: Optional[Decimal] = None


class MatchResult(BaseModel):
    """Complete match simulation result."""
    
    sets: List[SetResult]
    match_winner: str
    total_sets_played: int
    team_a_sets_won: int
    team_b_sets_won: int
    match_duration_minutes: Optional[Decimal] = None


class SimulationConfiguration(BaseModel):
    """Extended simulation configuration."""
    
    # Basic settings
    num_points: int = Field(default=10000, ge=100, le=1000000)
    random_seed: Optional[int] = None
    parallel_workers: Optional[int] = Field(None, ge=1, le=16)
    
    # Advanced settings
    enable_momentum: bool = Field(default=False)
    enable_fatigue: bool = Field(default=False)
    enable_pressure: bool = Field(default=False)
    enable_environmental_factors: bool = Field(default=False)
    
    # Analysis settings
    save_point_details: bool = Field(default=False)
    calculate_importance: bool = Field(default=False)
    run_sensitivity_analysis: bool = Field(default=False)
    
    # Performance settings
    memory_limit_mb: Optional[int] = Field(None, ge=100, le=8192)
    timeout_minutes: Optional[int] = Field(None, ge=1, le=60)
