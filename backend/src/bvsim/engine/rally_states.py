"""Rally state definitions for beach volleyball simulation."""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from decimal import Decimal


class RallyState(str, Enum):
    """Enumeration of all possible rally states in beach volleyball."""
    
    # Serve states
    SERVE_READY = "serve_ready"
    SERVE_ACE = "serve_ace"
    SERVE_ERROR = "serve_error"
    SERVE_IN_PLAY = "serve_in_play"
    
    # Reception states  
    RECEPTION_PERFECT = "reception_perfect"
    RECEPTION_GOOD = "reception_good"
    RECEPTION_POOR = "reception_poor"
    RECEPTION_ERROR = "reception_error"
    
    # Setting states
    SET_PERFECT = "set_perfect"
    SET_GOOD = "set_good"
    SET_POOR = "set_poor"
    SET_ERROR = "set_error"
    
    # Attack states
    ATTACK_KILL = "attack_kill"
    ATTACK_ERROR = "attack_error"
    ATTACK_IN_PLAY = "attack_in_play"
    ATTACK_BLOCKED = "attack_blocked"
    
    # Defense states
    DIG_PERFECT = "dig_perfect"
    DIG_GOOD = "dig_good"
    DIG_POOR = "dig_poor"
    DIG_ERROR = "dig_error"
    
    # Block states
    BLOCK_KILL = "block_kill"
    BLOCK_CONTROLLED = "block_controlled"
    BLOCK_ERROR = "block_error"
    BLOCK_TOUCH = "block_touch"
    
    # Transition states
    TRANSITION_ATTACK = "transition_attack"
    TRANSITION_SET = "transition_set"
    
    # Terminal states
    POINT_WON = "point_won"
    POINT_LOST = "point_lost"
    RALLY_CONTINUATION = "rally_continuation"


class ActionType(str, Enum):
    """Types of actions that can occur in a rally."""
    
    SERVE = "serve"
    RECEPTION = "reception"
    SET = "set"
    ATTACK = "attack"
    DIG = "dig"
    BLOCK = "block"
    TRANSITION = "transition"


class TeamSide(str, Enum):
    """Which team is performing the action."""
    
    TEAM_A = "team_a"
    TEAM_B = "team_b"


@dataclass
class StateTransition:
    """Represents a state transition with probability."""
    
    from_state: RallyState
    to_state: RallyState
    probability: Decimal
    action_type: ActionType
    performing_team: TeamSide
    conditions: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate probability is between 0 and 1."""
        if not (0 <= self.probability <= 1):
            raise ValueError(f"Probability must be between 0 and 1, got {self.probability}")


@dataclass
class RallyContext:
    """Context information for the current rally state."""
    
    # Current state
    current_state: RallyState
    serving_team: TeamSide
    rally_length: int
    
    # Score context
    team_a_score: int
    team_b_score: int
    set_number: int
    
    # Momentum and pressure factors
    momentum: Decimal = Decimal("0.0")  # -1 to 1
    pressure_level: Decimal = Decimal("0.0")  # 0 to 1
    
    # Environmental factors
    fatigue_team_a: Decimal = Decimal("0.0")  # 0 to 1
    fatigue_team_b: Decimal = Decimal("0.0")  # 0 to 1
    wind_factor: Optional[Decimal] = None  # 0 to 2
    
    def get_serving_team(self) -> TeamSide:
        """Get the currently serving team."""
        return self.serving_team
    
    def get_receiving_team(self) -> TeamSide:
        """Get the currently receiving team."""
        return TeamSide.TEAM_B if self.serving_team == TeamSide.TEAM_A else TeamSide.TEAM_A
    
    def is_close_score(self, threshold: int = 3) -> bool:
        """Check if the score is close (within threshold points)."""
        return abs(self.team_a_score - self.team_b_score) <= threshold
    
    def is_critical_point(self) -> bool:
        """Check if this is a critical point (close to winning)."""
        # Standard beach volleyball: first to 21, win by 2
        team_a_close = self.team_a_score >= 19
        team_b_close = self.team_b_score >= 19
        return team_a_close or team_b_close


# State transition mappings
TERMINAL_STATES = {
    RallyState.SERVE_ACE,
    RallyState.SERVE_ERROR,
    RallyState.RECEPTION_ERROR,
    RallyState.SET_ERROR,
    RallyState.ATTACK_KILL,
    RallyState.ATTACK_ERROR,
    RallyState.DIG_ERROR,
    RallyState.BLOCK_KILL,
    RallyState.BLOCK_ERROR,
    RallyState.POINT_WON,
    RallyState.POINT_LOST
}

CONTINUATION_STATES = {
    RallyState.SERVE_IN_PLAY,
    RallyState.RECEPTION_PERFECT,
    RallyState.RECEPTION_GOOD,
    RallyState.RECEPTION_POOR,
    RallyState.SET_PERFECT,
    RallyState.SET_GOOD,
    RallyState.SET_POOR,
    RallyState.ATTACK_IN_PLAY,
    RallyState.ATTACK_BLOCKED,
    RallyState.DIG_PERFECT,
    RallyState.DIG_GOOD,
    RallyState.DIG_POOR,
    RallyState.BLOCK_CONTROLLED,
    RallyState.BLOCK_TOUCH,
    RallyState.TRANSITION_ATTACK,
    RallyState.TRANSITION_SET,
    RallyState.RALLY_CONTINUATION
}

# Valid state transitions mapping
VALID_TRANSITIONS: Dict[RallyState, List[RallyState]] = {
    RallyState.SERVE_READY: [
        RallyState.SERVE_ACE,
        RallyState.SERVE_ERROR,
        RallyState.SERVE_IN_PLAY
    ],
    
    RallyState.SERVE_IN_PLAY: [
        RallyState.RECEPTION_PERFECT,
        RallyState.RECEPTION_GOOD,
        RallyState.RECEPTION_POOR,
        RallyState.RECEPTION_ERROR
    ],
    
    RallyState.RECEPTION_PERFECT: [
        RallyState.SET_PERFECT,
        RallyState.SET_GOOD,
        RallyState.SET_ERROR
    ],
    
    RallyState.RECEPTION_GOOD: [
        RallyState.SET_PERFECT,
        RallyState.SET_GOOD,
        RallyState.SET_POOR,
        RallyState.SET_ERROR
    ],
    
    RallyState.RECEPTION_POOR: [
        RallyState.SET_POOR,
        RallyState.SET_ERROR,
        RallyState.ATTACK_ERROR  # Emergency attack
    ],
    
    RallyState.SET_PERFECT: [
        RallyState.ATTACK_KILL,
        RallyState.ATTACK_IN_PLAY,
        RallyState.ATTACK_ERROR,
        RallyState.ATTACK_BLOCKED
    ],
    
    RallyState.SET_GOOD: [
        RallyState.ATTACK_KILL,
        RallyState.ATTACK_IN_PLAY,
        RallyState.ATTACK_ERROR,
        RallyState.ATTACK_BLOCKED
    ],
    
    RallyState.SET_POOR: [
        RallyState.ATTACK_IN_PLAY,
        RallyState.ATTACK_ERROR,
        RallyState.ATTACK_BLOCKED
    ],
    
    RallyState.ATTACK_IN_PLAY: [
        RallyState.DIG_PERFECT,
        RallyState.DIG_GOOD,
        RallyState.DIG_POOR,
        RallyState.DIG_ERROR
    ],
    
    RallyState.ATTACK_BLOCKED: [
        RallyState.BLOCK_KILL,
        RallyState.BLOCK_CONTROLLED,
        RallyState.BLOCK_TOUCH
    ],
    
    RallyState.DIG_PERFECT: [
        RallyState.TRANSITION_SET
    ],
    
    RallyState.DIG_GOOD: [
        RallyState.TRANSITION_SET,
        RallyState.TRANSITION_ATTACK
    ],
    
    RallyState.DIG_POOR: [
        RallyState.TRANSITION_ATTACK,    # Direct attack (emergency)
        RallyState.TRANSITION_SET,       # Poor set attempt
        RallyState.ATTACK_ERROR          # Direct error
    ],
    
    RallyState.BLOCK_CONTROLLED: [
        RallyState.TRANSITION_SET
    ],
    
    RallyState.BLOCK_TOUCH: [
        RallyState.DIG_PERFECT,
        RallyState.DIG_GOOD,
        RallyState.DIG_POOR,
        RallyState.DIG_ERROR
    ],
    
    RallyState.TRANSITION_SET: [
        RallyState.ATTACK_KILL,
        RallyState.ATTACK_IN_PLAY,
        RallyState.ATTACK_ERROR,
        RallyState.ATTACK_BLOCKED
    ],
    
    RallyState.TRANSITION_ATTACK: [
        RallyState.ATTACK_KILL,
        RallyState.ATTACK_IN_PLAY,
        RallyState.ATTACK_ERROR,
        RallyState.ATTACK_BLOCKED
    ]
}


def is_terminal_state(state: RallyState) -> bool:
    """Check if a state is terminal (ends the rally)."""
    return state in TERMINAL_STATES


def is_continuation_state(state: RallyState) -> bool:
    """Check if a state continues the rally."""
    return state in CONTINUATION_STATES


def get_valid_next_states(current_state: RallyState) -> List[RallyState]:
    """Get list of valid next states from current state."""
    return VALID_TRANSITIONS.get(current_state, [])
