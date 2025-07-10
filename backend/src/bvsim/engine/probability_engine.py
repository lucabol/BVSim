"""Probability calculation engine for rally state transitions."""

from typing import Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
import logging
from dataclasses import dataclass, field
import numpy as np

from .rally_states import (
    RallyState, RallyContext, StateTransition, ActionType, TeamSide,
    get_valid_next_states, is_terminal_state
)
from ..schemas.team_statistics import TeamStatisticsBase


logger = logging.getLogger(__name__)


@dataclass
class TransitionProbabilities:
    """Container for state transition probabilities."""
    
    transitions: Dict[RallyState, Decimal] = field(default_factory=dict)
    base_probabilities: Dict[RallyState, Decimal] = field(default_factory=dict)
    adjusted_probabilities: Dict[RallyState, Decimal] = field(default_factory=dict)
    
    def normalize(self) -> None:
        """Normalize probabilities to sum to 1.0."""
        total = sum(self.transitions.values())
        if total > 0:
            for state in self.transitions:
                self.transitions[state] = self.transitions[state] / total
    
    def get_probability(self, state: RallyState) -> Decimal:
        """Get the probability for a specific state transition."""
        return self.transitions.get(state, Decimal("0.0"))


class ProbabilityEngine:
    """Engine for calculating state transition probabilities based on team statistics."""
    
    def __init__(self):
        """Initialize the probability engine."""
        self.logger = logging.getLogger(__name__)
        
        # Base probability matrices for different skill levels
        self._base_probabilities = self._initialize_base_probabilities()
        
        # Momentum and pressure adjustment factors
        self.momentum_factor = Decimal("0.15")  # Max 15% adjustment
        self.pressure_factor = Decimal("0.10")  # Max 10% adjustment
        self.fatigue_factor = Decimal("0.20")   # Max 20% adjustment
    
    def calculate_transition_probabilities(
        self,
        current_state: RallyState,
        context: RallyContext,
        team_stats: TeamStatisticsBase,
        opponent_stats: TeamStatisticsBase
    ) -> TransitionProbabilities:
        """Calculate transition probabilities from current state."""
        
        valid_states = get_valid_next_states(current_state)
        if not valid_states:
            self.logger.warning(f"No valid transitions from state: {current_state}")
            return TransitionProbabilities()
        
        # Get base probabilities for this state
        base_probs = self._get_base_probabilities(current_state, team_stats, opponent_stats)
        
        # Apply contextual adjustments
        adjusted_probs = self._apply_contextual_adjustments(
            base_probs, context, team_stats, opponent_stats
        )
        
        # Ensure we only include valid transitions
        final_probs = {
            state: prob for state, prob in adjusted_probs.items()
            if state in valid_states
        }
        
        result = TransitionProbabilities(
            transitions=final_probs,
            base_probabilities=base_probs,
            adjusted_probabilities=adjusted_probs
        )
        result.normalize()
        
        return result
    
    def _get_base_probabilities(
        self,
        current_state: RallyState,
        team_stats: TeamStatisticsBase,
        opponent_stats: TeamStatisticsBase
    ) -> Dict[RallyState, Decimal]:
        """Get base probabilities before contextual adjustments."""
        
        if current_state == RallyState.SERVE_READY:
            return self._calculate_serve_probabilities(team_stats)
        
        elif current_state == RallyState.SERVE_IN_PLAY:
            return self._calculate_reception_probabilities(opponent_stats)
        
        elif current_state in [RallyState.RECEPTION_PERFECT, RallyState.RECEPTION_GOOD, RallyState.RECEPTION_POOR]:
            return self._calculate_set_probabilities(team_stats, current_state)
        
        elif current_state in [RallyState.SET_PERFECT, RallyState.SET_GOOD, RallyState.SET_POOR]:
            return self._calculate_attack_probabilities(team_stats, opponent_stats, current_state)
        
        elif current_state == RallyState.ATTACK_IN_PLAY:
            return self._calculate_dig_probabilities(opponent_stats)
        
        elif current_state == RallyState.ATTACK_BLOCKED:
            return self._calculate_block_outcome_probabilities(opponent_stats)
        
        elif current_state == RallyState.BLOCK_CONTROLLED:
            # After a controlled block, ball goes to opposing team for transition
            return {RallyState.TRANSITION_SET: Decimal("0.8"), 
                   RallyState.TRANSITION_ATTACK: Decimal("0.2")}
        
        elif current_state == RallyState.BLOCK_TOUCH:
            # After block touch, ball deflects back to attacking team for digging
            return {RallyState.DIG_POOR: Decimal("0.6"),
                   RallyState.DIG_GOOD: Decimal("0.25"),
                   RallyState.DIG_ERROR: Decimal("0.15")}
        
        elif current_state in [RallyState.DIG_PERFECT, RallyState.DIG_GOOD, RallyState.DIG_POOR]:
            return self._calculate_transition_probabilities_from_dig(team_stats, current_state)
        
        elif current_state in [RallyState.TRANSITION_SET, RallyState.TRANSITION_ATTACK]:
            return self._calculate_transition_attack_probabilities(team_stats, opponent_stats)
        
        else:
            self.logger.warning(f"No probability calculation for state: {current_state}")
            return {}
    
    def _calculate_serve_probabilities(self, team_stats: TeamStatisticsBase) -> Dict[RallyState, Decimal]:
        """Calculate serve outcome probabilities."""
        # Convert percentages to decimals
        ace_prob = team_stats.service_ace_percentage / Decimal("100")
        error_prob = team_stats.service_error_percentage / Decimal("100")
        in_play_prob = Decimal("1.0") - ace_prob - error_prob
        
        return {
            RallyState.SERVE_ACE: ace_prob,
            RallyState.SERVE_ERROR: error_prob,
            RallyState.SERVE_IN_PLAY: in_play_prob
        }
    
    def _calculate_reception_probabilities(self, team_stats: TeamStatisticsBase) -> Dict[RallyState, Decimal]:
        """Calculate reception outcome probabilities."""
        # Use the actual percentage distributions from the schema
        perfect_prob = team_stats.perfect_pass_percentage / Decimal("100")
        good_prob = team_stats.good_pass_percentage / Decimal("100")
        poor_prob = team_stats.poor_pass_percentage / Decimal("100")
        error_prob = team_stats.reception_error_percentage / Decimal("100")
        
        # Normalize to ensure sum = 1.0
        total = perfect_prob + good_prob + poor_prob + error_prob
        if total > 0:
            return {
                RallyState.RECEPTION_PERFECT: perfect_prob / total,
                RallyState.RECEPTION_GOOD: good_prob / total,
                RallyState.RECEPTION_POOR: poor_prob / total,
                RallyState.RECEPTION_ERROR: error_prob / total
            }
        else:
            # Fallback if all zeros
            return {
                RallyState.RECEPTION_PERFECT: Decimal("0.4"),
                RallyState.RECEPTION_GOOD: Decimal("0.4"),
                RallyState.RECEPTION_POOR: Decimal("0.15"),
                RallyState.RECEPTION_ERROR: Decimal("0.05")
            }
    
    def _calculate_set_probabilities(
        self, 
        team_stats: TeamStatisticsBase, 
        reception_state: RallyState
    ) -> Dict[RallyState, Decimal]:
        """Calculate setting outcome probabilities based on reception quality."""
        # Use assist percentage and ball handling error as base
        assist_skill = team_stats.assist_percentage / Decimal("100")
        error_rate = team_stats.ball_handling_error_percentage / Decimal("100")
        
        # Adjust setting quality based on reception quality
        if reception_state == RallyState.RECEPTION_PERFECT:
            skill_modifier = Decimal("1.0")
        elif reception_state == RallyState.RECEPTION_GOOD:
            skill_modifier = Decimal("0.85")
        else:  # RECEPTION_POOR
            skill_modifier = Decimal("0.60")
        
        effective_skill = assist_skill * skill_modifier
        
        perfect_prob = effective_skill * Decimal("0.40")
        good_prob = effective_skill * Decimal("0.45") + (Decimal("1.0") - effective_skill) * Decimal("0.30")
        poor_prob = (Decimal("1.0") - effective_skill) * Decimal("0.60")
        error_prob = error_rate * skill_modifier
        
        total = perfect_prob + good_prob + poor_prob + error_prob
        
        return {
            RallyState.SET_PERFECT: perfect_prob / total,
            RallyState.SET_GOOD: good_prob / total,
            RallyState.SET_POOR: poor_prob / total,
            RallyState.SET_ERROR: error_prob / total
        }
    
    def _calculate_attack_probabilities(
        self,
        team_stats: TeamStatisticsBase,
        opponent_stats: TeamStatisticsBase,
        set_state: RallyState
    ) -> Dict[RallyState, Decimal]:
        """Calculate attack outcome probabilities."""
        # Use hitting efficiency and kill percentage
        attack_skill = team_stats.hitting_efficiency  # -1 to 1 range
        kill_rate = team_stats.attack_kill_percentage / Decimal("100")
        error_rate = team_stats.attack_error_percentage / Decimal("100")
        
        # Opponent blocking
        block_kill_rate = opponent_stats.block_kill_percentage / Decimal("100")
        
        # Adjust attack effectiveness based on set quality
        if set_state == RallyState.SET_PERFECT:
            attack_modifier = Decimal("1.0")
        elif set_state == RallyState.SET_GOOD:
            attack_modifier = Decimal("0.85")
        else:  # SET_POOR
            attack_modifier = Decimal("0.65")
        
        effective_kill_rate = kill_rate * attack_modifier
        effective_error_rate = error_rate / attack_modifier  # Errors increase with poor sets
        
        # Consider opponent's blocking ability
        blocked_prob = block_kill_rate * Decimal("0.3")  # Some attacks get blocked
        kill_prob = effective_kill_rate * (Decimal("1.0") - blocked_prob)
        error_prob = effective_error_rate
        in_play_prob = Decimal("1.0") - kill_prob - blocked_prob - error_prob
        
        # Ensure probabilities are non-negative
        in_play_prob = max(in_play_prob, Decimal("0.1"))
        total = kill_prob + blocked_prob + in_play_prob + error_prob
        
        return {
            RallyState.ATTACK_KILL: kill_prob / total,
            RallyState.ATTACK_BLOCKED: blocked_prob / total,
            RallyState.ATTACK_IN_PLAY: in_play_prob / total,
            RallyState.ATTACK_ERROR: error_prob / total
        }
    
    def _calculate_dig_probabilities(self, team_stats: TeamStatisticsBase) -> Dict[RallyState, Decimal]:
        """Calculate dig outcome probabilities."""
        dig_skill = team_stats.dig_percentage / Decimal("100")  # Convert percentage to decimal
        
        perfect_prob = dig_skill * Decimal("0.20")
        good_prob = dig_skill * Decimal("0.50")
        poor_prob = dig_skill * Decimal("0.25") + (Decimal("1.0") - dig_skill) * Decimal("0.40")
        error_prob = (Decimal("1.0") - dig_skill) * Decimal("0.60")
        
        total = perfect_prob + good_prob + poor_prob + error_prob
        
        return {
            RallyState.DIG_PERFECT: perfect_prob / total,
            RallyState.DIG_GOOD: good_prob / total,
            RallyState.DIG_POOR: poor_prob / total,
            RallyState.DIG_ERROR: error_prob / total
        }
    
    def _calculate_block_outcome_probabilities(self, team_stats: TeamStatisticsBase) -> Dict[RallyState, Decimal]:
        """Calculate block outcome probabilities when attack is blocked."""
        # Use the blocking statistics from the schema
        kill_rate = team_stats.block_kill_percentage / Decimal("100")
        controlled_rate = team_stats.controlled_block_percentage / Decimal("100")
        error_rate = team_stats.blocking_error_percentage / Decimal("100")
        
        # Touch rate is what's left (blocks that deflect but don't control)
        touch_rate = Decimal("1.0") - kill_rate - controlled_rate - error_rate
        touch_rate = max(touch_rate, Decimal("0.0"))  # Ensure non-negative
        
        total = kill_rate + controlled_rate + touch_rate + error_rate
        
        return {
            RallyState.BLOCK_KILL: kill_rate / total,
            RallyState.BLOCK_CONTROLLED: controlled_rate / total,
            RallyState.BLOCK_TOUCH: touch_rate / total,
            RallyState.BLOCK_ERROR: error_rate / total
        }
    
    def _calculate_transition_probabilities_from_dig(
        self,
        team_stats: TeamStatisticsBase,
        dig_state: RallyState
    ) -> Dict[RallyState, Decimal]:
        """Calculate transition probabilities after a dig."""
        
        if dig_state == RallyState.DIG_PERFECT:
            return {RallyState.TRANSITION_SET: Decimal("1.0")}
        elif dig_state == RallyState.DIG_GOOD:
            return {
                RallyState.TRANSITION_SET: Decimal("0.75"),
                RallyState.TRANSITION_ATTACK: Decimal("0.25")
            }
        else:  # DIG_POOR
            return {
                RallyState.TRANSITION_ATTACK: Decimal("0.85"),
                RallyState.ATTACK_ERROR: Decimal("0.15")
            }
    
    def _calculate_transition_attack_probabilities(
        self,
        team_stats: TeamStatisticsBase,
        opponent_stats: TeamStatisticsBase
    ) -> Dict[RallyState, Decimal]:
        """Calculate attack probabilities from transition situations."""
        # Transition attacks are generally less effective
        base_attack_probs = self._calculate_attack_probabilities(
            team_stats, opponent_stats, RallyState.SET_POOR
        )
        
        # Reduce kill probability and increase error/block rates
        kill_prob = base_attack_probs[RallyState.ATTACK_KILL] * Decimal("0.7")
        error_prob = base_attack_probs[RallyState.ATTACK_ERROR] * Decimal("1.3")
        blocked_prob = base_attack_probs[RallyState.ATTACK_BLOCKED] * Decimal("1.2")
        in_play_prob = Decimal("1.0") - kill_prob - error_prob - blocked_prob
        
        return {
            RallyState.ATTACK_KILL: kill_prob,
            RallyState.ATTACK_ERROR: error_prob,
            RallyState.ATTACK_BLOCKED: blocked_prob,
            RallyState.ATTACK_IN_PLAY: max(in_play_prob, Decimal("0.1"))
        }
    
    def _apply_contextual_adjustments(
        self,
        base_probs: Dict[RallyState, Decimal],
        context: RallyContext,
        team_stats: TeamStatisticsBase,
        opponent_stats: TeamStatisticsBase
    ) -> Dict[RallyState, Decimal]:
        """Apply momentum, pressure, and fatigue adjustments to base probabilities."""
        
        adjusted_probs = base_probs.copy()
        
        # Apply momentum effects
        momentum_adjustment = self._calculate_momentum_adjustment(context)
        
        # Apply pressure effects  
        pressure_adjustment = self._calculate_pressure_adjustment(context)
        
        # Apply fatigue effects
        fatigue_adjustment = self._calculate_fatigue_adjustment(context)
        
        # Combine all adjustments
        total_adjustment = momentum_adjustment + pressure_adjustment + fatigue_adjustment
        
        # Apply adjustments to positive outcome probabilities
        positive_states = {RallyState.SERVE_ACE, RallyState.ATTACK_KILL, RallyState.BLOCK_KILL,
                          RallyState.RECEPTION_PERFECT, RallyState.SET_PERFECT, RallyState.DIG_PERFECT}
        
        for state, prob in adjusted_probs.items():
            if state in positive_states:
                # Positive outcomes benefit from positive adjustments
                adjusted_probs[state] = prob * (Decimal("1.0") + total_adjustment)
            else:
                # Negative outcomes are inversely affected
                adjusted_probs[state] = prob * (Decimal("1.0") - total_adjustment * Decimal("0.5"))
        
        return adjusted_probs
    
    def _calculate_momentum_adjustment(self, context: RallyContext) -> Decimal:
        """Calculate momentum-based probability adjustment."""
        return context.momentum * self.momentum_factor
    
    def _calculate_pressure_adjustment(self, context: RallyContext) -> Decimal:
        """Calculate pressure-based probability adjustment."""
        pressure_penalty = context.pressure_level * self.pressure_factor
        return -pressure_penalty  # Pressure hurts performance
    
    def _calculate_fatigue_adjustment(self, context: RallyContext) -> Decimal:
        """Calculate fatigue-based probability adjustment."""
        serving_team = context.get_serving_team()
        
        if serving_team == TeamSide.TEAM_A:
            fatigue_penalty = context.fatigue_team_a * self.fatigue_factor
        else:
            fatigue_penalty = context.fatigue_team_b * self.fatigue_factor
            
        return -fatigue_penalty  # Fatigue hurts performance
    
    def _initialize_base_probabilities(self) -> Dict[str, Dict[RallyState, Decimal]]:
        """Initialize base probability matrices for different scenarios."""
        # This could be loaded from configuration or database
        return {
            "default": {},
            "high_skill": {},
            "low_skill": {}
        }
