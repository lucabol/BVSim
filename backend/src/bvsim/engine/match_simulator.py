"""
Match simulation engine for beach volleyball.
Extends the rally simulation to full match scenarios with momentum and pressure effects.
"""

import asyncio
import time
import uuid
import math
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import logging

from ..schemas.match import (
    MatchFormat, MatchResult, SetResult, MatchSimulationRequest,
    MatchStatistics, MatchSimulationResponse, MomentumState,
    PressureSituation, RallyContext, AdvancedRallyResult
)
from ..schemas.team_statistics import TeamStatisticsBase
from ..engine.rally_simulator import RallySimulator
from ..engine.rally_states import TeamSide
from ..engine.monte_carlo import MonteCarloEngine

logger = logging.getLogger(__name__)


class MomentumEngine:
    """Handles momentum effects during match simulation."""
    
    def __init__(self, enable_momentum: bool = True):
        self.enable_momentum = enable_momentum
        self.momentum_decay_rate = 0.1  # Momentum decays over time
        self.momentum_boost_factor = 0.15  # How much momentum affects probability
    
    def calculate_momentum_effect(self, momentum_state: MomentumState, 
                                serving_team: str) -> Decimal:
        """Calculate momentum effect on serve probability."""
        if not self.enable_momentum:
            return Decimal('0.0')
        
        if serving_team == 'A':
            momentum = momentum_state.team_a_momentum
        else:
            momentum = momentum_state.team_b_momentum
        
        # Apply momentum boost factor
        return momentum * Decimal(str(self.momentum_boost_factor))
    
    def update_momentum(self, momentum_state: MomentumState, 
                       rally_winner: str, serving_team: str) -> MomentumState:
        """Update momentum state after a rally."""
        if not self.enable_momentum:
            return momentum_state
        
        new_state = MomentumState(
            team_a_momentum=momentum_state.team_a_momentum,
            team_b_momentum=momentum_state.team_b_momentum,
            consecutive_points_a=momentum_state.consecutive_points_a,
            consecutive_points_b=momentum_state.consecutive_points_b,
            recent_rally_outcomes=momentum_state.recent_rally_outcomes.copy()
        )
        
        # Update consecutive points
        if rally_winner == 'A':
            new_state.consecutive_points_a += 1
            new_state.consecutive_points_b = 0
        else:
            new_state.consecutive_points_b += 1
            new_state.consecutive_points_a = 0
        
        # Update recent outcomes (keep last 5)
        new_state.recent_rally_outcomes.append(rally_winner)
        if len(new_state.recent_rally_outcomes) > 5:
            new_state.recent_rally_outcomes.pop(0)
        
        # Calculate momentum values
        new_state.team_a_momentum = self._calculate_team_momentum('A', new_state)
        new_state.team_b_momentum = self._calculate_team_momentum('B', new_state)
        
        return new_state
    
    def _calculate_team_momentum(self, team: str, state: MomentumState) -> Decimal:
        """Calculate momentum value for a team based on recent performance."""
        consecutive = (state.consecutive_points_a if team == 'A' 
                      else state.consecutive_points_b)
        
        # Count wins in recent rallies
        recent_wins = sum(1 for outcome in state.recent_rally_outcomes 
                         if outcome == team)
        recent_total = len(state.recent_rally_outcomes)
        
        # Calculate base momentum from consecutive points
        consecutive_momentum = min(consecutive * 0.2, 1.0)
        
        # Calculate momentum from recent performance
        if recent_total > 0:
            recent_momentum = (recent_wins / recent_total - 0.5) * 2  # -1 to 1
        else:
            recent_momentum = 0.0
        
        # Combine and apply decay
        total_momentum = (consecutive_momentum + recent_momentum) / 2
        return Decimal(str(max(-1.0, min(1.0, total_momentum))))


class PressureEngine:
    """Handles pressure effects during match simulation."""
    
    def __init__(self, enable_pressure: bool = True):
        self.enable_pressure = enable_pressure
        self.pressure_effect_factor = 0.1  # How much pressure affects performance
    
    def analyze_pressure_situation(self, set_number: int, team_a_score: int, 
                                 team_b_score: int, serving_team: str) -> PressureSituation:
        """Analyze the current pressure situation."""
        # Determine if it's set point or match point
        is_set_point = (team_a_score >= 20 and team_a_score >= team_b_score + 1) or \
                      (team_b_score >= 20 and team_b_score >= team_a_score + 1)
        
        is_match_point = is_set_point and ((set_number == 1) or 
                                          (set_number == 3))
        
        score_diff = abs(team_a_score - team_b_score)
        serving_team_behind = ((serving_team == 'A' and team_a_score < team_b_score) or
                              (serving_team == 'B' and team_b_score < team_a_score))
        
        # Calculate pressure level (0.0 to 1.0)
        pressure_level = 0.0
        if is_match_point:
            pressure_level += 0.5
        elif is_set_point:
            pressure_level += 0.3
        
        # Add pressure based on score closeness
        if score_diff <= 2:
            pressure_level += 0.2
        elif score_diff <= 5:
            pressure_level += 0.1
        
        # Add pressure for being behind while serving
        if serving_team_behind:
            pressure_level += 0.2
        
        return PressureSituation(
            is_set_point=is_set_point,
            is_match_point=is_match_point,
            score_differential=score_diff,
            serving_team_behind=serving_team_behind,
            pressure_level=Decimal(str(min(1.0, pressure_level)))
        )
    
    def calculate_pressure_effect(self, pressure: PressureSituation, 
                                serving_team: str) -> Decimal:
        """Calculate pressure effect on performance."""
        if not self.enable_pressure:
            return Decimal('0.0')
        
        # Pressure generally hurts the team under pressure
        pressure_penalty = pressure.pressure_level * Decimal(str(self.pressure_effect_factor))
        
        # If serving team is behind, they feel more pressure
        if pressure.serving_team_behind:
            return -pressure_penalty
        else:
            # If serving team is ahead, they feel less pressure
            return pressure_penalty * Decimal('0.5')


class MatchSimulator:
    """Simulates complete beach volleyball matches with advanced features."""
    
    def __init__(self):
        self.rally_simulator = RallySimulator()
        self.monte_carlo_engine = MonteCarloEngine()
        self.momentum_engine = MomentumEngine()
        self.pressure_engine = PressureEngine()
    
    async def simulate_match(self, team_a: TeamStatisticsBase, 
                           team_b: TeamStatisticsBase,
                           match_format: MatchFormat = MatchFormat.BEST_OF_THREE,
                           enable_momentum: bool = True,
                           enable_pressure: bool = True) -> MatchResult:
        """Simulate a single match between two teams."""
        
        self.momentum_engine.enable_momentum = enable_momentum
        self.pressure_engine.enable_pressure = enable_pressure
        
        match_id = str(uuid.uuid4())
        sets: List[SetResult] = []
        sets_won_a = 0
        sets_won_b = 0
        set_number = 1
        
        # Initialize momentum state
        momentum_state = MomentumState()
        
        while True:
            # Simulate the set
            set_result = await self._simulate_set(
                team_a, team_b, set_number, momentum_state
            )
            sets.append(set_result)
            
            # Update set wins
            if set_result.winner == 'A':
                sets_won_a += 1
            else:
                sets_won_b += 1
            
            # Check if match is complete
            if match_format == MatchFormat.BEST_OF_ONE:
                winner = 'A' if sets_won_a > sets_won_b else 'B'
                break
            elif match_format == MatchFormat.BEST_OF_THREE:
                if sets_won_a == 2:
                    winner = 'A'
                    break
                elif sets_won_b == 2:
                    winner = 'B'
                    break
                elif set_number == 3:
                    # This shouldn't happen, but just in case
                    winner = 'A' if sets_won_a > sets_won_b else 'B'
                    break
            
            set_number += 1
        
        return MatchResult(
            match_id=match_id,
            team_a_name=team_a.name,
            team_b_name=team_b.name,
            match_format=match_format,
            winner=winner,
            sets=sets,
            match_date=datetime.now()
        )
    
    async def _simulate_set(self, team_a: TeamStatisticsBase, 
                          team_b: TeamStatisticsBase, set_number: int,
                          momentum_state: MomentumState) -> SetResult:
        """Simulate a single set."""
        team_a_score = 0
        team_b_score = 0
        serving_team = 'A'  # Team A serves first
        rally_number = 1
        rally_results = []
        
        while True:
            # Create rally context
            context = RallyContext(
                set_number=set_number,
                team_a_score=team_a_score,
                team_b_score=team_b_score,
                serving_team=serving_team,
                momentum=momentum_state,
                rally_number=rally_number
            )
            
            # Analyze pressure situation
            pressure_situation = self.pressure_engine.analyze_pressure_situation(
                set_number, team_a_score, team_b_score, serving_team
            )
            context.pressure = pressure_situation
            
            # Simulate rally with context effects
            rally_result = await self._simulate_rally_with_effects(
                team_a, team_b, context
            )
            
            rally_results.append(rally_result)
            
            # Update score
            if rally_result.basic_result['winner'] == 'A':
                team_a_score += 1
            else:
                team_b_score += 1
            
            # Update momentum
            momentum_state = self.momentum_engine.update_momentum(
                momentum_state, rally_result.basic_result['winner'], serving_team
            )
            
            # Check for set completion (21 points, win by 2)
            if (team_a_score >= 21 and team_a_score >= team_b_score + 2) or \
               (team_b_score >= 21 and team_b_score >= team_a_score + 2):
                set_winner = 'A' if team_a_score > team_b_score else 'B'
                break
            
            # Change server if rally lost
            if rally_result.basic_result['winner'] != serving_team:
                serving_team = 'B' if serving_team == 'A' else 'A'
            
            rally_number += 1
        
        return SetResult(
            set_number=set_number,
            team_a_score=team_a_score,
            team_b_score=team_b_score,
            winner=set_winner,
            total_rallies=len(rally_results),
            rally_results=[r.basic_result for r in rally_results]
        )
    
    async def _simulate_rally_with_effects(self, team_a: TeamStatisticsBase,
                                         team_b: TeamStatisticsBase,
                                         context: RallyContext) -> AdvancedRallyResult:
        """Simulate a rally with momentum and pressure effects."""
        
        # Calculate effects
        momentum_effect = Decimal('0.0')
        pressure_effect = Decimal('0.0')
        
        if context.momentum:
            momentum_effect = self.momentum_engine.calculate_momentum_effect(
                context.momentum, context.serving_team
            )
        
        if context.pressure:
            pressure_effect = self.pressure_engine.calculate_pressure_effect(
                context.pressure, context.serving_team
            )
        
        # Apply effects to team statistics (simplified)
        modified_team_a = self._apply_effects_to_team(
            team_a, momentum_effect if context.serving_team == 'A' else Decimal('0.0'),
            pressure_effect if context.serving_team == 'A' else Decimal('0.0')
        )
        modified_team_b = self._apply_effects_to_team(
            team_b, momentum_effect if context.serving_team == 'B' else Decimal('0.0'),
            pressure_effect if context.serving_team == 'B' else Decimal('0.0')
        )
        
        # Simulate the rally
        rally_result = self.rally_simulator.simulate_rally(
            serving_team=TeamSide.TEAM_A if context.serving_team == 'A' else TeamSide.TEAM_B,
            team_a_stats=modified_team_a,
            team_b_stats=modified_team_b
        )
        
        # Convert RallyResult to dictionary format for compatibility
        basic_result = {
            'winner': rally_result.winner.value,
            'rally_length': rally_result.rally_length,
            'total_contacts': rally_result.team_a_actions + rally_result.team_b_actions,
            'point_outcome': rally_result.point_outcome.value,
            'final_state': rally_result.final_state.value if rally_result.final_state else None,
            'events': [
                {
                    'sequence': event.sequence_number,
                    'state': event.state.value,
                    'action': event.action_type.value,
                    'team': event.performing_team.value,
                    'probability': float(event.probability)
                }
                for event in rally_result.events
            ]
        }
        
        # Create analytics
        rally_analytics = {
            'rally_length': rally_result.rally_length,
            'total_contacts': rally_result.team_a_actions + rally_result.team_b_actions,
            'serving_team': context.serving_team,
            'momentum_applied': float(momentum_effect),
            'pressure_applied': float(pressure_effect),
            'team_a_actions': rally_result.team_a_actions,
            'team_b_actions': rally_result.team_b_actions
        }
        
        return AdvancedRallyResult(
            basic_result=basic_result,
            context=context,
            rally_analytics=rally_analytics,
            momentum_change=momentum_effect,
            pressure_effect=pressure_effect
        )
    
    def _apply_effects_to_team(self, team: TeamStatisticsBase, 
                             momentum_effect: Decimal, 
                             pressure_effect: Decimal) -> TeamStatisticsBase:
        """Apply momentum and pressure effects to team statistics."""
        # This is a simplified implementation
        # In a full implementation, you'd modify specific stats based on the effects
        
        total_effect = momentum_effect + pressure_effect
        effect_multiplier = 1.0 + float(total_effect)
        
        # Apply effect to key performance metrics (simplified)
        modified_team = team.model_copy()
        
        # Modify service stats
        if hasattr(modified_team, 'service_ace_percentage'):
            modified_team.service_ace_percentage = max(
                Decimal('0.0'),
                modified_team.service_ace_percentage * Decimal(str(effect_multiplier))
            )
        
        return modified_team
    
    async def run_match_simulation(self, request: MatchSimulationRequest) -> MatchSimulationResponse:
        """Run Monte Carlo simulation of matches."""
        start_time = time.time()
        simulation_id = str(uuid.uuid4())
        
        # Run simulations
        if request.num_simulations >= 1000:
            results = await self._run_parallel_match_simulation(request)
        else:
            results = await self._run_sequential_match_simulation(request)
        
        # Calculate statistics
        statistics = self._calculate_match_statistics(results)
        
        # Get sample matches
        sample_matches = results[:min(5, len(results))] if request.include_rally_details else None
        
        simulation_time = time.time() - start_time
        
        return MatchSimulationResponse(
            simulation_id=simulation_id,
            request=request,
            statistics=statistics,
            sample_matches=sample_matches,
            simulation_time_seconds=simulation_time,
            created_at=datetime.now()
        )
    
    async def _run_sequential_match_simulation(self, request: MatchSimulationRequest) -> List[MatchResult]:
        """Run match simulations sequentially."""
        results = []
        
        for i in range(request.num_simulations):
            result = await self.simulate_match(
                request.team_a,
                request.team_b,
                request.match_format,
                request.momentum_effects,
                request.pressure_effects
            )
            results.append(result)
        
        return results
    
    async def _run_parallel_match_simulation(self, request: MatchSimulationRequest) -> List[MatchResult]:
        """Run match simulations in parallel."""
        # For now, use sequential simulation
        # In production, this would use ProcessPoolExecutor
        return await self._run_sequential_match_simulation(request)
    
    def _calculate_match_statistics(self, results: List[MatchResult]) -> MatchStatistics:
        """Calculate comprehensive statistics from match results."""
        total_matches = len(results)
        team_a_wins = sum(1 for r in results if r.winner == 'A')
        team_b_wins = total_matches - team_a_wins
        
        # Calculate probabilities and confidence intervals
        team_a_prob = Decimal(str(team_a_wins / total_matches))
        team_b_prob = Decimal(str(team_b_wins / total_matches))
        
        # Calculate 95% confidence interval using normal approximation
        z_score = 1.96  # 95% confidence
        margin_of_error = Decimal(str(
            z_score * math.sqrt(float(team_a_prob * (1 - team_a_prob)) / total_matches)
        ))
        
        ci_lower = max(Decimal('0.0'), team_a_prob - margin_of_error)
        ci_upper = min(Decimal('1.0'), team_a_prob + margin_of_error)
        
        # Set-level statistics
        total_sets = sum(len(r.sets) for r in results)
        avg_sets_per_match = Decimal(str(total_sets / total_matches))
        
        straight_set_wins_a = sum(1 for r in results 
                                 if r.winner == 'A' and len(r.sets) == 2)
        straight_set_wins_b = sum(1 for r in results 
                                 if r.winner == 'B' and len(r.sets) == 2)
        three_set_matches = sum(1 for r in results if len(r.sets) == 3)
        
        # Rally-level statistics
        all_rallies = []
        for result in results:
            for set_result in result.sets:
                all_rallies.extend(set_result.rally_results or [])
        
        if all_rallies:
            avg_rallies_per_set = Decimal(str(len(all_rallies) / total_sets))
            rally_lengths = [r.get('rally_length', 0) for r in all_rallies]
            avg_rally_length = Decimal(str(sum(rally_lengths) / len(rally_lengths)))
            longest_rally = max(rally_lengths) if rally_lengths else 0
            shortest_rally = min(rally_lengths) if rally_lengths else 0
        else:
            avg_rallies_per_set = Decimal('0.0')
            avg_rally_length = Decimal('0.0')
            longest_rally = 0
            shortest_rally = 0
        
        return MatchStatistics(
            total_matches=total_matches,
            team_a_wins=team_a_wins,
            team_b_wins=team_b_wins,
            team_a_win_probability=team_a_prob,
            team_b_win_probability=team_b_prob,
            confidence_interval_lower=ci_lower,
            confidence_interval_upper=ci_upper,
            margin_of_error=margin_of_error,
            is_statistically_significant=margin_of_error < Decimal('0.1'),
            avg_sets_per_match=avg_sets_per_match,
            straight_set_wins_a=straight_set_wins_a,
            straight_set_wins_b=straight_set_wins_b,
            three_set_matches=three_set_matches,
            avg_rallies_per_set=avg_rallies_per_set,
            avg_rally_length=avg_rally_length,
            longest_rally_contacts=longest_rally,
            shortest_rally_contacts=shortest_rally
        )
