"""Pydantic schemas for simulation engine configuration and state."""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum


class SkillLevel(str, Enum):
    """Player skill level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class PlayStyle(str, Enum):
    """Team play style enumeration."""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    TECHNICAL = "technical"


class RallyState(BaseModel):
    """Current state of a rally."""
    
    # Rally identification
    rally_number: int = Field(..., description="Rally number in the set")
    set_number: int = Field(..., description="Current set number")
    
    # Score state
    team_a_score: int = Field(..., ge=0, description="Team A current score")
    team_b_score: int = Field(..., ge=0, description="Team B current score")
    
    # Serving information
    serving_team: str = Field(..., description="Team currently serving (A or B)")
    serve_number: int = Field(..., ge=1, description="Number of this serve attempt")
    
    # Rally tracking
    rally_length: int = Field(..., ge=0, description="Number of touches in rally")
    last_action: Optional[str] = Field(None, description="Last action performed")
    last_action_team: Optional[str] = Field(None, description="Team that performed last action")
    
    # Contextual factors
    pressure_level: Decimal = Field(
        ..., ge=0.0, le=1.0, description="Pressure level (0-1)"
    )
    momentum: Decimal = Field(
        ..., ge=-1.0, le=1.0, description="Momentum (-1 to 1, negative favors B)"
    )
    
    # Environmental factors
    wind_factor: Optional[Decimal] = Field(
        None, ge=0.0, le=2.0, description="Wind impact factor"
    )
    fatigue_factor_a: Decimal = Field(
        ..., ge=0.0, le=1.0, description="Team A fatigue (0 = fresh, 1 = exhausted)"
    )
    fatigue_factor_b: Decimal = Field(
        ..., ge=0.0, le=1.0, description="Team B fatigue (0 = fresh, 1 = exhausted)"
    )


class ProbabilityDistribution(BaseModel):
    """Probability distribution for various outcomes."""
    
    # Serve outcomes
    ace_probability: Decimal = Field(..., ge=0.0, le=1.0)
    service_error_probability: Decimal = Field(..., ge=0.0, le=1.0)
    good_serve_probability: Decimal = Field(..., ge=0.0, le=1.0)
    
    # Reception outcomes (given good serve)
    perfect_reception_probability: Decimal = Field(..., ge=0.0, le=1.0)
    good_reception_probability: Decimal = Field(..., ge=0.0, le=1.0)
    poor_reception_probability: Decimal = Field(..., ge=0.0, le=1.0)
    reception_error_probability: Decimal = Field(..., ge=0.0, le=1.0)
    
    # Attack outcomes (given different reception qualities)
    kill_prob_perfect_pass: Decimal = Field(..., ge=0.0, le=1.0)
    kill_prob_good_pass: Decimal = Field(..., ge=0.0, le=1.0)
    kill_prob_poor_pass: Decimal = Field(..., ge=0.0, le=1.0)
    
    # Error probabilities
    attack_error_prob_perfect_pass: Decimal = Field(..., ge=0.0, le=1.0)
    attack_error_prob_good_pass: Decimal = Field(..., ge=0.0, le=1.0)
    attack_error_prob_poor_pass: Decimal = Field(..., ge=0.0, le=1.0)
    
    # Defense outcomes
    dig_success_probability: Decimal = Field(..., ge=0.0, le=1.0)
    transition_attack_probability: Decimal = Field(..., ge=0.0, le=1.0)
    
    @model_validator(mode='after')
    def validate_probability_sums(self) -> 'ProbabilityDistribution':
        """Validate that related probabilities sum correctly."""
        # Serve outcome probabilities should sum to 1
        serve_sum = (self.ace_probability + 
                    self.service_error_probability + 
                    self.good_serve_probability)
        if abs(serve_sum - Decimal("1.0")) > Decimal("0.001"):
            raise ValueError(f"Serve probabilities must sum to 1.0, got {serve_sum}")
        
        # Reception outcome probabilities should sum to 1
        reception_sum = (self.perfect_reception_probability +
                        self.good_reception_probability +
                        self.poor_reception_probability +
                        self.reception_error_probability)
        if abs(reception_sum - Decimal("1.0")) > Decimal("0.001"):
            raise ValueError(f"Reception probabilities must sum to 1.0, got {reception_sum}")
        
        return self


class SimulationEngineConfig(BaseModel):
    """Configuration for the simulation engine."""
    
    # Basic settings
    enable_momentum: bool = Field(default=True, description="Enable momentum effects")
    enable_fatigue: bool = Field(default=True, description="Enable fatigue effects")
    enable_pressure: bool = Field(default=True, description="Enable pressure effects")
    enable_environmental: bool = Field(default=False, description="Enable environmental factors")
    
    # Momentum configuration
    momentum_decay_rate: Decimal = Field(
        default=Decimal("0.1"), 
        ge=0.0, le=1.0,
        description="Rate at which momentum decays (0-1)"
    )
    momentum_impact_strength: Decimal = Field(
        default=Decimal("0.15"),
        ge=0.0, le=0.5,
        description="Strength of momentum impact on probabilities"
    )
    
    # Fatigue configuration
    fatigue_accumulation_rate: Decimal = Field(
        default=Decimal("0.02"),
        ge=0.0, le=0.1,
        description="Rate at which fatigue accumulates per rally"
    )
    fatigue_impact_strength: Decimal = Field(
        default=Decimal("0.1"),
        ge=0.0, le=0.3,
        description="Strength of fatigue impact on performance"
    )
    
    # Pressure configuration
    pressure_threshold_close: int = Field(
        default=3,
        ge=1, le=5,
        description="Point difference considered 'close' for pressure"
    )
    pressure_threshold_critical: int = Field(
        default=1,
        ge=0, le=2,
        description="Point difference considered 'critical' for pressure"
    )
    pressure_impact_strength: Decimal = Field(
        default=Decimal("0.08"),
        ge=0.0, le=0.2,
        description="Strength of pressure impact on performance"
    )
    
    # Rally length configuration
    max_rally_length: int = Field(
        default=50,
        ge=10, le=100,
        description="Maximum rally length before forced termination"
    )
    rally_length_penalty: Decimal = Field(
        default=Decimal("0.01"),
        ge=0.0, le=0.05,
        description="Performance penalty per rally touch"
    )
    
    # Random seed for reproducibility
    random_seed: Optional[int] = Field(None, description="Random seed for reproducible results")


class ActionOutcome(BaseModel):
    """Outcome of a single action in a rally."""
    
    action_type: str = Field(..., description="Type of action (serve, reception, attack, etc.)")
    outcome: str = Field(..., description="Result of the action")
    performing_team: str = Field(..., description="Team performing the action")
    success: bool = Field(..., description="Whether the action was successful")
    quality_rating: Optional[str] = Field(None, description="Quality of the action")
    point_won: bool = Field(..., description="Whether this action won the point")
    
    # Probability information
    base_probability: Decimal = Field(..., description="Base probability of this outcome")
    adjusted_probability: Decimal = Field(..., description="Probability after adjustments")
    
    # Context factors that influenced the outcome
    momentum_adjustment: Optional[Decimal] = Field(None, description="Momentum adjustment applied")
    fatigue_adjustment: Optional[Decimal] = Field(None, description="Fatigue adjustment applied")
    pressure_adjustment: Optional[Decimal] = Field(None, description="Pressure adjustment applied")


class RallyResult(BaseModel):
    """Complete result of a single rally simulation."""
    
    rally_id: str = Field(..., description="Unique identifier for this rally")
    starting_state: RallyState = Field(..., description="Rally starting state")
    ending_state: RallyState = Field(..., description="Rally ending state")
    
    # Rally outcome
    winning_team: str = Field(..., description="Team that won the rally")
    rally_length: int = Field(..., description="Total number of actions in rally")
    
    # Action sequence
    actions: List[ActionOutcome] = Field(..., description="Sequence of actions in the rally")
    
    # Rally metrics
    total_duration_estimate: Optional[Decimal] = Field(
        None, description="Estimated rally duration in seconds"
    )
    complexity_score: Decimal = Field(
        ..., description="Rally complexity score (0-1)"
    )
    
    # Probability analysis
    initial_win_probability_a: Decimal = Field(..., description="Team A initial win probability")
    final_win_probability_a: Decimal = Field(..., description="Team A final win probability")
    probability_swing: Decimal = Field(..., description="Total probability change during rally")


class EnginePerformanceMetrics(BaseModel):
    """Performance metrics for the simulation engine."""
    
    # Execution metrics
    total_rallies_simulated: int = Field(..., description="Total rallies simulated")
    average_rally_length: Decimal = Field(..., description="Average rally length")
    simulation_speed_rallies_per_second: Decimal = Field(..., description="Simulation speed")
    
    # Memory usage
    peak_memory_usage_mb: Optional[Decimal] = Field(None, description="Peak memory usage")
    
    # Accuracy metrics
    probability_calibration_score: Optional[Decimal] = Field(
        None, description="How well probabilities match actual outcomes"
    )
    
    # Distribution metrics
    rally_length_distribution: Dict[int, int] = Field(
        ..., description="Distribution of rally lengths"
    )
    outcome_distribution: Dict[str, int] = Field(
        ..., description="Distribution of rally outcomes"
    )


class SimulationEngineStatus(BaseModel):
    """Current status of the simulation engine."""
    
    status: str = Field(..., description="Engine status (idle, running, error)")
    current_simulation_id: Optional[int] = Field(None, description="Currently running simulation")
    progress_percentage: Decimal = Field(
        ..., ge=0.0, le=100.0, description="Progress percentage"
    )
    estimated_completion_seconds: Optional[int] = Field(
        None, description="Estimated seconds to completion"
    )
    
    # Current rally being processed
    current_rally_number: Optional[int] = Field(None, description="Current rally number")
    current_set_number: Optional[int] = Field(None, description="Current set number")
    
    # Performance info
    rallies_per_second: Optional[Decimal] = Field(None, description="Current processing speed")
    error_message: Optional[str] = Field(None, description="Error message if status is error")
    
    # Resource usage
    cpu_usage_percent: Optional[Decimal] = Field(None, description="CPU usage percentage")
    memory_usage_mb: Optional[Decimal] = Field(None, description="Memory usage in MB")
