"""Monte Carlo simulation engine for beach volleyball match analysis."""

import asyncio
import logging
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional, Tuple, Any
import statistics
import multiprocessing as mp
from enum import Enum

from ..engine import RallySimulator, RallyResult, TeamSide, RallyContext, RallyState
from ..schemas.team_statistics import TeamStatisticsBase


logger = logging.getLogger(__name__)


class MatchFormat(str, Enum):
    """Beach volleyball match formats."""
    
    BEST_OF_1 = "best_of_1"  # Single set to 21
    BEST_OF_3 = "best_of_3"  # Best of 3 sets (first 2 to 21, 3rd to 15)
    TOURNAMENT = "tournament"  # Tournament format with multiple matches


class SetType(str, Enum):
    """Types of sets in beach volleyball."""
    
    REGULAR = "regular"  # First two sets (to 21, win by 2)
    DECIDING = "deciding"  # Third set (to 15, win by 2)


@dataclass
class SetResult:
    """Result of a single set."""
    
    set_number: int
    set_type: SetType
    winner: TeamSide
    team_a_score: int
    team_b_score: int
    rally_count: int
    duration_minutes: Optional[float] = None
    rallies: List[RallyResult] = field(default_factory=list)
    
    @property
    def score_difference(self) -> int:
        """Get the score difference in this set."""
        return abs(self.team_a_score - self.team_b_score)
    
    @property
    def was_close(self) -> bool:
        """Check if this was a close set (within 3 points at any time near the end)."""
        return self.score_difference <= 3


@dataclass
class MatchResult:
    """Result of a complete match."""
    
    match_id: str
    format: MatchFormat
    winner: TeamSide
    sets: List[SetResult] = field(default_factory=list)
    total_rallies: int = 0
    duration_minutes: Optional[float] = None
    
    # Statistical summary
    team_a_sets_won: int = 0
    team_b_sets_won: int = 0
    total_points_a: int = 0
    total_points_b: int = 0
    
    def update_stats(self):
        """Update match statistics from set results."""
        self.team_a_sets_won = sum(1 for s in self.sets if s.winner == TeamSide.TEAM_A)
        self.team_b_sets_won = sum(1 for s in self.sets if s.winner == TeamSide.TEAM_B)
        self.total_points_a = sum(s.team_a_score for s in self.sets)
        self.total_points_b = sum(s.team_b_score for s in self.sets)
        self.total_rallies = sum(s.rally_count for s in self.sets)


@dataclass
class SimulationBatch:
    """Configuration for a batch of simulations."""
    
    num_simulations: int
    team_a_stats: TeamStatisticsBase
    team_b_stats: TeamStatisticsBase
    match_format: MatchFormat
    
    # Simulation parameters
    parallel_workers: Optional[int] = None
    random_seed_base: Optional[int] = None
    include_detailed_results: bool = False
    
    # Context parameters
    momentum_enabled: bool = True
    pressure_enabled: bool = True
    fatigue_enabled: bool = True


@dataclass
class SimulationResults:
    """Aggregated results from Monte Carlo simulations."""
    
    num_simulations: int
    team_a_win_count: int
    team_b_win_count: int
    
    # Win probabilities with confidence intervals
    team_a_win_probability: Decimal
    team_b_win_probability: Decimal
    confidence_interval_95: Tuple[Decimal, Decimal]
    
    # Set statistics
    avg_sets_per_match: float
    set_distribution: Dict[str, int]  # "2-0", "2-1", etc.
    
    # Performance metrics
    avg_match_duration: float
    avg_rallies_per_match: float
    simulation_time_seconds: float
    
    # Detailed results (optional)
    individual_matches: List[MatchResult] = field(default_factory=list)
    
    # Statistical significance
    margin_of_error: Decimal = Decimal("0.0")
    is_statistically_significant: bool = False


class MonteCarloEngine:
    """High-performance Monte Carlo simulation engine for beach volleyball."""
    
    def __init__(self, max_workers: Optional[int] = None):
        """Initialize the Monte Carlo engine."""
        self.max_workers = max_workers or min(8, mp.cpu_count())
        self.rally_simulator = RallySimulator()
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self._simulation_count = 0
        self._total_simulation_time = 0.0
    
    async def run_simulation_batch(self, batch: SimulationBatch) -> SimulationResults:
        """Run a batch of Monte Carlo simulations."""
        
        start_time = time.time()
        self.logger.info(f"Starting Monte Carlo simulation: {batch.num_simulations} matches")
        
        # Prepare simulation tasks
        chunk_size = max(1, batch.num_simulations // self.max_workers)
        tasks = []
        
        for i in range(0, batch.num_simulations, chunk_size):
            end_idx = min(i + chunk_size, batch.num_simulations)
            task_count = end_idx - i
            seed = (batch.random_seed_base + i) if batch.random_seed_base else None
            
            tasks.append(self._simulate_matches_chunk(
                task_count, batch, seed
            ))
        
        # Execute simulations in parallel
        chunk_results = await asyncio.gather(*tasks)
        
        # Aggregate results
        all_matches = []
        for chunk in chunk_results:
            all_matches.extend(chunk)
        
        # Calculate statistics
        results = self._calculate_statistics(all_matches, batch, time.time() - start_time)
        
        self.logger.info(f"Simulation completed: A={results.team_a_win_probability:.1%}, "
                        f"B={results.team_b_win_probability:.1%}")
        
        return results
    
    async def _simulate_matches_chunk(
        self, 
        count: int, 
        batch: SimulationBatch, 
        seed_base: Optional[int]
    ) -> List[MatchResult]:
        """Simulate a chunk of matches in a separate process."""
        
        loop = asyncio.get_event_loop()
        
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                self._run_matches_sync, 
                count, batch, seed_base
            )
            return await loop.run_in_executor(None, future.result)
    
    @staticmethod
    def _run_matches_sync(
        count: int, 
        batch: SimulationBatch, 
        seed_base: Optional[int]
    ) -> List[MatchResult]:
        """Synchronous match simulation for use in process pool."""
        
        simulator = RallySimulator()
        matches = []
        
        for i in range(count):
            if seed_base:
                simulator.set_random_seed(seed_base + i)
            
            match = MonteCarloEngine._simulate_single_match(
                simulator, batch, f"match_{seed_base or 0}_{i}"
            )
            matches.append(match)
        
        return matches
    
    @staticmethod
    def _simulate_single_match(
        simulator: RallySimulator,
        batch: SimulationBatch,
        match_id: str
    ) -> MatchResult:
        """Simulate a single complete match."""
        
        match_result = MatchResult(
            match_id=match_id,
            format=batch.match_format,
            winner=TeamSide.TEAM_A  # Will be updated
        )
        
        set_number = 1
        serving_team = TeamSide.TEAM_A
        
        while not MonteCarloEngine._is_match_complete(match_result, batch.match_format):
            # Determine set type
            set_type = SetType.DECIDING if (
                batch.match_format == MatchFormat.BEST_OF_3 and 
                len(match_result.sets) == 2 and
                match_result.team_a_sets_won == 1 and 
                match_result.team_b_sets_won == 1
            ) else SetType.REGULAR
            
            # Simulate the set
            set_result = MonteCarloEngine._simulate_single_set(
                simulator, batch, set_number, set_type, serving_team
            )
            
            match_result.sets.append(set_result)
            match_result.update_stats()
            
            # Alternate serving for next set
            serving_team = TeamSide.TEAM_B if serving_team == TeamSide.TEAM_A else TeamSide.TEAM_A
            set_number += 1
        
        # Determine match winner
        match_result.winner = (
            TeamSide.TEAM_A if match_result.team_a_sets_won > match_result.team_b_sets_won
            else TeamSide.TEAM_B
        )
        
        return match_result
    
    @staticmethod
    def _simulate_single_set(
        simulator: RallySimulator,
        batch: SimulationBatch,
        set_number: int,
        set_type: SetType,
        serving_team: TeamSide
    ) -> SetResult:
        """Simulate a single set."""
        
        # Set winning conditions
        target_score = 15 if set_type == SetType.DECIDING else 21
        min_lead = 2
        
        team_a_score = 0
        team_b_score = 0
        rallies = []
        current_server = serving_team
        
        while True:
            # Create rally context
            context = RallyContext(
                current_state=RallyState.SERVE_READY,
                serving_team=current_server,
                rally_length=0,
                team_a_score=team_a_score,
                team_b_score=team_b_score,
                set_number=set_number
            )
            
            # Add pressure and momentum if enabled
            if batch.pressure_enabled:
                context.pressure_level = MonteCarloEngine._calculate_pressure(
                    team_a_score, team_b_score, target_score
                )
            
            if batch.momentum_enabled and rallies:
                context.momentum = MonteCarloEngine._calculate_momentum(rallies[-3:])
            
            # Simulate rally
            rally_result = simulator.simulate_rally(
                current_server, batch.team_a_stats, batch.team_b_stats, context
            )
            
            if batch.include_detailed_results:
                rallies.append(rally_result)
            
            # Update score
            if rally_result.winner == TeamSide.TEAM_A:
                team_a_score += 1
            else:
                team_b_score += 1
            
            # Check for set completion
            if MonteCarloEngine._is_set_complete(
                team_a_score, team_b_score, target_score, min_lead
            ):
                break
            
            # Determine next server (winner serves in beach volleyball)
            current_server = rally_result.winner
        
        # Create set result
        set_winner = TeamSide.TEAM_A if team_a_score > team_b_score else TeamSide.TEAM_B
        
        return SetResult(
            set_number=set_number,
            set_type=set_type,
            winner=set_winner,
            team_a_score=team_a_score,
            team_b_score=team_b_score,
            rally_count=len(rallies),
            rallies=rallies if batch.include_detailed_results else []
        )
    
    @staticmethod
    def _is_set_complete(
        team_a_score: int, 
        team_b_score: int, 
        target_score: int, 
        min_lead: int
    ) -> bool:
        """Check if a set is complete."""
        
        max_score = max(team_a_score, team_b_score)
        lead = abs(team_a_score - team_b_score)
        
        return max_score >= target_score and lead >= min_lead
    
    @staticmethod
    def _is_match_complete(match_result: MatchResult, format: MatchFormat) -> bool:
        """Check if a match is complete."""
        
        if format == MatchFormat.BEST_OF_1:
            return len(match_result.sets) >= 1
        
        elif format == MatchFormat.BEST_OF_3:
            return match_result.team_a_sets_won >= 2 or match_result.team_b_sets_won >= 2
        
        return False
    
    @staticmethod
    def _calculate_pressure(
        team_a_score: int, 
        team_b_score: int, 
        target_score: int
    ) -> Decimal:
        """Calculate pressure level based on score situation."""
        
        max_score = max(team_a_score, team_b_score)
        score_ratio = max_score / target_score
        
        # Pressure increases as we get closer to the target score
        if score_ratio >= 0.8:  # Above 80% of target
            return Decimal(str(min(1.0, (score_ratio - 0.8) * 5)))
        else:
            return Decimal("0.0")
    
    @staticmethod
    def _calculate_momentum(recent_rallies: List[RallyResult]) -> Decimal:
        """Calculate momentum based on recent rally results."""
        
        if not recent_rallies:
            return Decimal("0.0")
        
        # Count wins for each team in recent rallies
        team_a_wins = sum(1 for r in recent_rallies if r.winner == TeamSide.TEAM_A)
        team_b_wins = len(recent_rallies) - team_a_wins
        
        # Calculate momentum (-1 to 1)
        momentum = (team_a_wins - team_b_wins) / len(recent_rallies)
        return Decimal(str(max(-1.0, min(1.0, momentum))))
    
    def _calculate_statistics(
        self, 
        matches: List[MatchResult], 
        batch: SimulationBatch,
        simulation_time: float
    ) -> SimulationResults:
        """Calculate aggregated statistics from simulation results."""
        
        if not matches:
            raise ValueError("No simulation results to analyze")
        
        # Basic win counts
        team_a_wins = sum(1 for m in matches if m.winner == TeamSide.TEAM_A)
        team_b_wins = len(matches) - team_a_wins
        
        # Win probabilities
        team_a_prob = Decimal(str(team_a_wins / len(matches)))
        team_b_prob = Decimal(str(team_b_wins / len(matches)))
        
        # Confidence interval (95%)
        confidence_interval = self._calculate_confidence_interval(team_a_prob, len(matches))
        
        # Set distribution
        set_distribution = {}
        for match in matches:
            sets_key = f"{match.team_a_sets_won}-{match.team_b_sets_won}"
            set_distribution[sets_key] = set_distribution.get(sets_key, 0) + 1
        
        # Performance metrics
        avg_sets = statistics.mean(len(m.sets) for m in matches)
        avg_rallies = statistics.mean(m.total_rallies for m in matches)
        
        # Statistical significance
        margin_of_error = self._calculate_margin_of_error(len(matches))
        is_significant = margin_of_error < Decimal("0.05")  # 5% margin
        
        return SimulationResults(
            num_simulations=len(matches),
            team_a_win_count=team_a_wins,
            team_b_win_count=team_b_wins,
            team_a_win_probability=team_a_prob,
            team_b_win_probability=team_b_prob,
            confidence_interval_95=confidence_interval,
            avg_sets_per_match=avg_sets,
            set_distribution=set_distribution,
            avg_match_duration=0.0,  # TODO: Calculate from actual timing
            avg_rallies_per_match=avg_rallies,
            simulation_time_seconds=simulation_time,
            individual_matches=matches if batch.include_detailed_results else [],
            margin_of_error=margin_of_error,
            is_statistically_significant=is_significant
        )
    
    def _calculate_confidence_interval(
        self, 
        probability: Decimal, 
        sample_size: int
    ) -> Tuple[Decimal, Decimal]:
        """Calculate 95% confidence interval for win probability."""
        
        import math
        
        p = float(probability)
        n = sample_size
        
        # Standard error
        se = math.sqrt(p * (1 - p) / n)
        
        # 95% confidence interval (z = 1.96)
        margin = 1.96 * se
        
        lower = max(0.0, p - margin)
        upper = min(1.0, p + margin)
        
        return (Decimal(str(lower)), Decimal(str(upper)))
    
    def _calculate_margin_of_error(self, sample_size: int) -> Decimal:
        """Calculate margin of error for the given sample size."""
        
        import math
        
        # For 95% confidence level with p=0.5 (worst case)
        margin = 1.96 * math.sqrt(0.25 / sample_size)
        return Decimal(str(margin))
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the engine."""
        
        avg_time = (
            self._total_simulation_time / self._simulation_count 
            if self._simulation_count > 0 else 0.0
        )
        
        return {
            "total_simulations": self._simulation_count,
            "total_time_seconds": self._total_simulation_time,
            "average_time_per_simulation": avg_time,
            "max_workers": self.max_workers,
            "simulations_per_second": 1 / avg_time if avg_time > 0 else 0
        }
