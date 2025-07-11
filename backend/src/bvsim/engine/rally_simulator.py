"""Main rally simulation engine for beach volleyball."""

from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal
import logging
import random
from dataclasses import dataclass, field
from enum import Enum

from .rally_states import (
    RallyState, RallyContext, TeamSide, ActionType, 
    is_terminal_state, get_valid_next_states
)
from .probability_engine import ProbabilityEngine, TransitionProbabilities
from ..schemas.team_statistics import TeamStatisticsBase


logger = logging.getLogger(__name__)


class PointOutcome(str, Enum):
    """Possible outcomes of a point."""
    
    TEAM_A_WIN = "team_a_win"
    TEAM_B_WIN = "team_b_win"
    ERROR = "error"


@dataclass
class RallyEvent:
    """Represents a single event in a rally."""
    
    sequence_number: int
    state: RallyState
    action_type: ActionType
    performing_team: TeamSide
    probability: Decimal
    context: RallyContext
    
    # Additional event metadata
    skill_used: Optional[str] = None
    effectiveness: Optional[Decimal] = None
    notes: Optional[str] = None


@dataclass
class RallyResult:
    """Complete result of a simulated rally."""
    
    # Outcome
    winner: TeamSide
    point_outcome: PointOutcome
    rally_length: int
    
    # Rally progression
    events: List[RallyEvent] = field(default_factory=list)
    final_state: Optional[RallyState] = None
    
    # Statistics
    total_probability: Decimal = Decimal("1.0")
    team_a_actions: int = 0
    team_b_actions: int = 0
    
    # Context at end
    final_context: Optional[RallyContext] = None
    
    def get_event_summary(self) -> Dict[str, int]:
        """Get summary of events by action type."""
        summary = {}
        for event in self.events:
            action = event.action_type.value
            summary[action] = summary.get(action, 0) + 1
        return summary
    
    def get_team_performance(self, team: TeamSide) -> Dict[str, Any]:
        """Get performance metrics for a specific team."""
        team_events = [e for e in self.events if e.performing_team == team]
        
        return {
            "total_actions": len(team_events),
            "action_types": [e.action_type.value for e in team_events],
            "avg_effectiveness": sum(e.effectiveness for e in team_events if e.effectiveness) / len(team_events) if team_events else 0,
            "won_point": self.winner == team
        }


class RallySimulator:
    """Simulates individual beach volleyball rallies."""
    
    def __init__(self, probability_engine: Optional[ProbabilityEngine] = None):
        """Initialize the rally simulator."""
        self.probability_engine = probability_engine or ProbabilityEngine()
        self.logger = logging.getLogger(__name__)
        
        # Simulation limits to prevent infinite rallies
        self.max_rally_length = 50
        self.max_state_transitions = 100
        
        # Random seed for reproducible testing
        self._random_seed: Optional[int] = None
    
    def set_random_seed(self, seed: int) -> None:
        """Set random seed for reproducible simulations."""
        self._random_seed = seed
        random.seed(seed)
    
    def simulate_rally(
        self,
        serving_team: TeamSide,
        team_a_stats: TeamStatisticsBase,
        team_b_stats: TeamStatisticsBase,
        initial_context: Optional[RallyContext] = None
    ) -> RallyResult:
        """Simulate a complete rally from serve to point completion."""
        
        # Initialize context
        context = initial_context or RallyContext(
            current_state=RallyState.SERVE_READY,
            serving_team=serving_team,
            rally_length=0,
            team_a_score=0,
            team_b_score=0,
            set_number=1
        )
        
        # Initialize result tracking
        result = RallyResult(
            winner=serving_team,  # Will be updated
            point_outcome=PointOutcome.ERROR,
            rally_length=0,
            events=[],
            final_context=context
        )
        
        current_state = RallyState.SERVE_READY
        sequence_number = 1
        total_transitions = 0
        
        self.logger.debug(f"Starting rally simulation: {serving_team} serving")
        
        try:
            while not is_terminal_state(current_state) and total_transitions < self.max_state_transitions:
                # Calculate transition probabilities first (using current acting team as baseline)
                baseline_acting_team = self._get_acting_team(current_state, context)
                acting_stats = team_a_stats if baseline_acting_team == TeamSide.TEAM_A else team_b_stats
                opponent_stats = team_b_stats if baseline_acting_team == TeamSide.TEAM_A else team_a_stats
                
                transition_probs = self.probability_engine.calculate_transition_probabilities(
                    current_state, context, acting_stats, opponent_stats
                )
                
                if not transition_probs.transitions:
                    self.logger.warning(f"No valid transitions from state: {current_state}")
                    break
                
                # Select next state based on probabilities
                next_state = self._select_next_state(transition_probs)
                probability = transition_probs.get_probability(next_state)
                
                # NOW determine which team performs the next state action
                acting_team = self._get_acting_team_dynamic(next_state, context, result.events)
                
                # Create rally event
                event = RallyEvent(
                    sequence_number=sequence_number,
                    state=next_state,
                    action_type=self._get_action_type(current_state, next_state),
                    performing_team=acting_team,
                    probability=probability,
                    context=context,
                    skill_used=self._get_skill_used(current_state, next_state),
                    effectiveness=self._calculate_effectiveness(next_state, acting_stats)
                )
                
                result.events.append(event)
                result.total_probability *= probability
                
                # Update counts
                if acting_team == TeamSide.TEAM_A:
                    result.team_a_actions += 1
                else:
                    result.team_b_actions += 1
                
                # Update context for next iteration
                context = self._update_context(context, next_state, acting_team)
                current_state = next_state
                sequence_number += 1
                total_transitions += 1
                
                self.logger.debug(f"Transition {total_transitions}: {current_state} by {acting_team}")
            
            # Determine final outcome
            result.winner, result.point_outcome = self._determine_point_outcome(
                current_state, context, result.events
            )
            result.final_state = current_state
            result.rally_length = total_transitions
            result.final_context = context
            
            self.logger.debug(f"Rally completed: {result.winner} wins after {result.rally_length} actions")
            
        except Exception as e:
            self.logger.error(f"Error in rally simulation: {e}")
            result.point_outcome = PointOutcome.ERROR
            result.final_state = current_state
        
        return result
    
    def simulate_multiple_rallies(
        self,
        num_rallies: int,
        serving_team: TeamSide,
        team_a_stats: TeamStatisticsBase,
        team_b_stats: TeamStatisticsBase,
        base_context: Optional[RallyContext] = None
    ) -> List[RallyResult]:
        """Simulate multiple rallies and return results."""
        
        results = []
        
        for i in range(num_rallies):
            # Alternate serving team for realistic simulation
            current_serving_team = serving_team if i % 2 == 0 else (
                TeamSide.TEAM_B if serving_team == TeamSide.TEAM_A else TeamSide.TEAM_A
            )
            
            # Create context for this rally
            context = base_context or RallyContext(
                current_state=RallyState.SERVE_READY,
                serving_team=current_serving_team,
                rally_length=0,
                team_a_score=0,
                team_b_score=0,
                set_number=1
            )
            
            result = self.simulate_rally(
                current_serving_team, team_a_stats, team_b_stats, context
            )
            results.append(result)
            
            if i % 100 == 0 and i > 0:
                self.logger.info(f"Completed {i} rally simulations")
        
        return results
    
    def _get_acting_team_dynamic(self, state: RallyState, context: RallyContext, events: List[RallyEvent]) -> TeamSide:
        """Determine which team is performing the current action based on rally flow and previous events."""
        
        # If no events yet, use the basic logic
        if not events:
            return self._get_acting_team(state, context)
        
        # Look at the last event to determine current possession
        last_event = events[-1]
        last_performing_team = last_event.performing_team
        
        # Special handling for serve reception - always the receiving team
        if state in [RallyState.RECEPTION_PERFECT, RallyState.RECEPTION_GOOD, RallyState.RECEPTION_POOR]:
            # If the last event was a serve, the receiving team handles reception
            if last_event.state in [RallyState.SERVE_IN_PLAY]:
                return context.get_receiving_team()
        
        # Set actions are performed by the team that just received
        elif state in [RallyState.SET_PERFECT, RallyState.SET_GOOD, RallyState.SET_POOR, RallyState.SET_ERROR]:
            # If the last action was a reception, the same team sets
            if last_event.state in [RallyState.RECEPTION_PERFECT, RallyState.RECEPTION_GOOD, RallyState.RECEPTION_POOR]:
                return last_performing_team  # Same team that received
        
        # Attack actions are performed by the team that just set
        elif state in [RallyState.ATTACK_IN_PLAY, RallyState.ATTACK_KILL, RallyState.TRANSITION_ATTACK]:
            # If the last action was a set, the same team attacks
            if last_event.state in [RallyState.SET_PERFECT, RallyState.SET_GOOD, RallyState.SET_POOR, RallyState.TRANSITION_SET]:
                return last_performing_team  # Same team that set
        
        # Block actions are performed by the team defending against an attack
        elif state in [RallyState.ATTACK_BLOCKED]:
            # If the last action was an attack, the defending team blocks
            if last_event.state in [RallyState.ATTACK_IN_PLAY, RallyState.TRANSITION_ATTACK]:
                return TeamSide.TEAM_A if last_performing_team == TeamSide.TEAM_B else TeamSide.TEAM_B
        
        # Defensive actions are performed by the team that is NOT attacking
        elif state in [
            RallyState.DIG_PERFECT, RallyState.DIG_GOOD, RallyState.DIG_POOR,
            RallyState.BLOCK_CONTROLLED, RallyState.BLOCK_TOUCH
        ]:
            # If the last action was an attack, the defending team is the opposite
            if last_event.state in [RallyState.ATTACK_IN_PLAY, RallyState.ATTACK_BLOCKED, RallyState.TRANSITION_ATTACK]:
                return TeamSide.TEAM_A if last_performing_team == TeamSide.TEAM_B else TeamSide.TEAM_B
        
        # Transition logic based on the current state and who performed the last action
        elif state in [RallyState.TRANSITION_SET, RallyState.TRANSITION_ATTACK]:
            # Transition actions are performed by the team that just gained possession
            # This happens after a dig or block, so the team that just defended now attacks
            
            # If the last action was a dig or block, the same team continues with transition
            if last_event.state in [
                RallyState.DIG_PERFECT, RallyState.DIG_GOOD, RallyState.DIG_POOR,
                RallyState.BLOCK_CONTROLLED, RallyState.BLOCK_TOUCH
            ]:
                return last_performing_team  # Same team that dug/blocked
            
            # If the last action was a transition set, the same team attacks
            elif last_event.state == RallyState.TRANSITION_SET:
                return last_performing_team  # Same team that set
                
        # For all other states, use the standard logic
        return self._get_acting_team(state, context)

    def _get_acting_team(self, state: RallyState, context: RallyContext) -> TeamSide:
        """Determine which team is performing the current action based on volleyball flow."""
        
        # Serving team always serves
        if state in [RallyState.SERVE_READY]:
            return context.serving_team
        
        # Receiving team handles serve reception and first ball attack sequence
        elif state in [
            RallyState.RECEPTION_PERFECT, RallyState.RECEPTION_GOOD, RallyState.RECEPTION_POOR,
            RallyState.SET_PERFECT, RallyState.SET_GOOD, RallyState.SET_POOR,
            RallyState.ATTACK_IN_PLAY, RallyState.ATTACK_BLOCKED
        ]:
            return context.get_receiving_team()
        
        # Serving team defends against first attack
        elif state in [
            RallyState.DIG_PERFECT, RallyState.DIG_GOOD, RallyState.DIG_POOR,
            RallyState.BLOCK_CONTROLLED, RallyState.BLOCK_TOUCH
        ]:
            return context.serving_team
        
        # Transition actions: performed by the team that just defended (gained possession)
        elif state in [RallyState.TRANSITION_SET, RallyState.TRANSITION_ATTACK]:
            # The team that just dug/blocked is now attacking
            # This is the serving team after they defended the first attack
            return context.serving_team
        
        else:
            # Default fallback
            return context.serving_team
    
    def _select_next_state(self, transition_probs: TransitionProbabilities) -> RallyState:
        """Select the next state based on transition probabilities."""
        
        states = list(transition_probs.transitions.keys())
        probabilities = [float(prob) for prob in transition_probs.transitions.values()]
        
        if not states:
            raise ValueError("No valid state transitions available")
        
        # Use weighted random selection
        return random.choices(states, weights=probabilities, k=1)[0]
    
    def _get_action_type(self, current_state: RallyState, next_state: RallyState) -> ActionType:
        """Determine the action type for the transition."""
        
        if current_state == RallyState.SERVE_READY:
            return ActionType.SERVE
        elif "reception" in next_state.value:
            return ActionType.RECEPTION
        elif "set" in next_state.value:
            return ActionType.SET
        elif "attack" in next_state.value:
            return ActionType.ATTACK
        elif "dig" in next_state.value:
            return ActionType.DIG
        elif "block" in next_state.value:
            return ActionType.BLOCK
        elif "transition" in next_state.value:
            return ActionType.TRANSITION
        else:
            return ActionType.SERVE  # Default
    
    def _get_skill_used(self, current_state: RallyState, next_state: RallyState) -> Optional[str]:
        """Determine which skill was used for this transition."""
        
        action_type = self._get_action_type(current_state, next_state)
        
        skill_mapping = {
            ActionType.SERVE: "serve_effectiveness",
            ActionType.RECEPTION: "serve_receive",
            ActionType.SET: "setting_accuracy",
            ActionType.ATTACK: "attack_efficiency",
            ActionType.DIG: "digging_efficiency",
            ActionType.BLOCK: "blocking_effectiveness"
        }
        
        return skill_mapping.get(action_type)
    
    def _calculate_effectiveness(
        self, 
        state: RallyState, 
        team_stats: TeamStatisticsBase
    ) -> Optional[Decimal]:
        """Calculate the effectiveness of the action based on the outcome state."""
        
        # Positive outcomes
        if state in [
            RallyState.SERVE_ACE, RallyState.ATTACK_KILL, RallyState.BLOCK_KILL,
            RallyState.RECEPTION_PERFECT, RallyState.SET_PERFECT, RallyState.DIG_PERFECT
        ]:
            return Decimal("1.0")
        
        # Good outcomes
        elif state in [
            RallyState.RECEPTION_GOOD, RallyState.SET_GOOD, RallyState.DIG_GOOD,
            RallyState.BLOCK_CONTROLLED, RallyState.ATTACK_IN_PLAY
        ]:
            return Decimal("0.75")
        
        # Poor outcomes
        elif state in [
            RallyState.RECEPTION_POOR, RallyState.SET_POOR, RallyState.DIG_POOR,
            RallyState.BLOCK_TOUCH, RallyState.ATTACK_BLOCKED
        ]:
            return Decimal("0.25")
        
        # Error outcomes
        elif "error" in state.value:
            return Decimal("0.0")
        
        else:
            return None
    
    def _update_context(
        self, 
        context: RallyContext, 
        new_state: RallyState, 
        acting_team: TeamSide
    ) -> RallyContext:
        """Update rally context after a state transition."""
        
        # Create new context (immutable update)
        new_context = RallyContext(
            current_state=new_state,
            serving_team=context.serving_team,
            rally_length=context.rally_length + 1,
            team_a_score=context.team_a_score,
            team_b_score=context.team_b_score,
            set_number=context.set_number,
            momentum=context.momentum,
            pressure_level=context.pressure_level,
            fatigue_team_a=context.fatigue_team_a,
            fatigue_team_b=context.fatigue_team_b,
            wind_factor=context.wind_factor
        )
        
        # Update momentum based on positive/negative outcomes
        momentum_change = self._calculate_momentum_change(new_state, acting_team)
        if acting_team == TeamSide.TEAM_A:
            new_context.momentum = max(Decimal("-1.0"), min(Decimal("1.0"), 
                context.momentum + momentum_change))
        else:
            new_context.momentum = max(Decimal("-1.0"), min(Decimal("1.0"), 
                context.momentum - momentum_change))
        
        # Increase pressure as rally gets longer
        if new_context.rally_length > 10:
            new_context.pressure_level = min(Decimal("1.0"), 
                Decimal("0.1") * (new_context.rally_length - 10))
        
        return new_context
    
    def _calculate_momentum_change(self, state: RallyState, acting_team: TeamSide) -> Decimal:
        """Calculate momentum change based on the outcome state."""
        
        if state in [RallyState.SERVE_ACE, RallyState.ATTACK_KILL, RallyState.BLOCK_KILL]:
            return Decimal("0.3")  # Big positive momentum
        elif state in [RallyState.RECEPTION_PERFECT, RallyState.SET_PERFECT]:
            return Decimal("0.1")  # Small positive momentum
        elif "error" in state.value:
            return Decimal("-0.3")  # Big negative momentum
        elif state in [RallyState.RECEPTION_POOR, RallyState.SET_POOR]:
            return Decimal("-0.1")  # Small negative momentum
        else:
            return Decimal("0.0")  # No momentum change
    
    def _determine_point_outcome(
        self, 
        final_state: RallyState, 
        context: RallyContext,
        events: List[RallyEvent]
    ) -> Tuple[TeamSide, PointOutcome]:
        """Determine who won the point based on the final state."""
        
        # Direct terminal states
        if final_state == RallyState.SERVE_ACE:
            return context.serving_team, (
                PointOutcome.TEAM_A_WIN if context.serving_team == TeamSide.TEAM_A 
                else PointOutcome.TEAM_B_WIN
            )
        
        elif final_state in [RallyState.ATTACK_KILL, RallyState.BLOCK_KILL]:
            # Determine winner based on who performed the winning action using dynamic logic
            # If the last event matches the final state, use that team directly
            if events and events[-1].state == final_state:
                acting_team = events[-1].performing_team
            else:
                acting_team = self._get_acting_team_dynamic(final_state, context, events)
            return acting_team, (
                PointOutcome.TEAM_A_WIN if acting_team == TeamSide.TEAM_A 
                else PointOutcome.TEAM_B_WIN
            )
        
        elif "error" in final_state.value:
            # Error means the acting team loses
            # If the last event matches the final state, use that team directly
            if events and events[-1].state == final_state:
                acting_team = events[-1].performing_team
            else:
                acting_team = self._get_acting_team_dynamic(final_state, context, events)
            losing_team = acting_team
            winning_team = (
                TeamSide.TEAM_B if losing_team == TeamSide.TEAM_A 
                else TeamSide.TEAM_A
            )
            return winning_team, (
                PointOutcome.TEAM_A_WIN if winning_team == TeamSide.TEAM_A 
                else PointOutcome.TEAM_B_WIN
            )
        
        else:
            # Shouldn't reach here with proper terminal states
            self.logger.warning(f"Unexpected final state: {final_state}")
            return context.serving_team, PointOutcome.ERROR
