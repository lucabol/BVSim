# Technical Implementation Specifications

## 1. Core Data Models

### 1.1 Team Statistics Model

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal

class TeamStatistics(BaseModel):
    """Team fundamental statistics for simulation input."""
    
    # Team identification
    name: str = Field(..., min_length=1, max_length=255)
    
    # Serve statistics
    service_ace_percentage: Decimal = Field(
        ..., ge=0, le=100, 
        description="Percentage of serves resulting in direct points"
    )
    service_error_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of serves resulting in faults"
    )
    serve_success_rate: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage forcing opponent out of system"
    )
    
    # Reception statistics (Pass Quality Rating distribution)
    perfect_pass_percentage: Decimal = Field(..., ge=0, le=100)
    good_pass_percentage: Decimal = Field(..., ge=0, le=100)
    poor_pass_percentage: Decimal = Field(..., ge=0, le=100)
    reception_error_percentage: Decimal = Field(..., ge=0, le=100)
    
    # Setting statistics
    assist_percentage: Decimal = Field(..., ge=0, le=100)
    ball_handling_error_percentage: Decimal = Field(..., ge=0, le=100)
    
    # Attack statistics
    attack_kill_percentage: Decimal = Field(..., ge=0, le=100)
    attack_error_percentage: Decimal = Field(..., ge=0, le=100)
    hitting_efficiency: Decimal = Field(..., ge=-1, le=1)
    first_ball_kill_percentage: Decimal = Field(..., ge=0, le=100)
    
    # Defense statistics
    dig_percentage: Decimal = Field(..., ge=0, le=100)
    block_kill_percentage: Decimal = Field(..., ge=0, le=100)
    controlled_block_percentage: Decimal = Field(..., ge=0, le=100)
    blocking_error_percentage: Decimal = Field(..., ge=0, le=100)
    
    @validator('*')
    def validate_percentages_sum_to_100(cls, v, values, field):
        """Ensure related percentages sum to reasonable totals."""
        if field.name in ['perfect_pass_percentage', 'good_pass_percentage', 
                         'poor_pass_percentage', 'reception_error_percentage']:
            pass_percentages = [
                values.get('perfect_pass_percentage', 0),
                values.get('good_pass_percentage', 0),
                values.get('poor_pass_percentage', 0),
                values.get('reception_error_percentage', 0)
            ]
            if field.name == 'reception_error_percentage':
                total = sum(pass_percentages) + v
                if not 95 <= total <= 105:  # Allow some tolerance
                    raise ValueError("Reception percentages must sum to ~100%")
        return v

class ConditionalProbabilities(BaseModel):
    """Conditional probabilities for state transitions."""
    
    # Set quality given reception quality
    perfect_set_given_perfect_pass: Decimal = Field(default=0.90)
    perfect_set_given_good_pass: Decimal = Field(default=0.60)
    perfect_set_given_poor_pass: Decimal = Field(default=0.20)
    
    good_set_given_perfect_pass: Decimal = Field(default=0.08)
    good_set_given_good_pass: Decimal = Field(default=0.35)
    good_set_given_poor_pass: Decimal = Field(default=0.60)
    
    # Attack success given set quality
    kill_given_perfect_set: Decimal = Field(default=0.60)
    kill_given_good_set: Decimal = Field(default=0.40)
    kill_given_poor_set: Decimal = Field(default=0.20)
    
    error_given_perfect_set: Decimal = Field(default=0.15)
    error_given_good_set: Decimal = Field(default=0.20)
    error_given_poor_set: Decimal = Field(default=0.35)
```

### 1.2 Rally State Machine

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

class RallyState(Enum):
    """All possible states in a beach volleyball rally."""
    
    # Initial states
    SERVE_ATTEMPT = "serve_attempt"
    
    # Serve outcomes
    SERVE_ACE = "serve_ace"
    SERVE_ERROR = "serve_error"
    SERVE_IN_PLAY = "serve_in_play"
    
    # Reception outcomes
    RECEPTION_PERFECT = "reception_perfect"
    RECEPTION_GOOD = "reception_good" 
    RECEPTION_POOR = "reception_poor"
    RECEPTION_ERROR = "reception_error"
    
    # Set outcomes
    SET_PERFECT = "set_perfect"
    SET_GOOD = "set_good"
    SET_POOR = "set_poor"
    SET_BALL_HANDLING_ERROR = "set_ball_handling_error"
    
    # Attack outcomes
    ATTACK_KILL = "attack_kill"
    ATTACK_ERROR = "attack_error"
    ATTACK_DEFENDED = "attack_defended"
    
    # Defense outcomes
    BLOCK_TERMINAL = "block_terminal"
    BLOCK_CONTROLLED = "block_controlled"
    BLOCK_ERROR = "block_error"
    DIG_SUCCESSFUL = "dig_successful"
    DIG_ERROR = "dig_error"
    
    # Terminal states (point scored)
    POINT_TEAM_A = "point_team_a"
    POINT_TEAM_B = "point_team_b"

@dataclass
class StateTransition:
    """Represents a state transition with probability."""
    from_state: RallyState
    to_state: RallyState
    probability: float
    team: str  # 'A' or 'B'

@dataclass
class RallyResult:
    """Result of a single rally simulation."""
    winner: str  # 'A' or 'B'
    rally_states: List[StateTransition]
    serving_team: str
    total_contacts: int
    rally_duration: Optional[float] = None
```

## 2. Simulation Engine Implementation

### 2.1 Markov Chain Simulator

```python
import numpy as np
from typing import Dict, List, Tuple
import logging

class BeachVolleyballMarkovChain:
    """Markov chain implementation for beach volleyball rally simulation."""
    
    def __init__(self, team_a_stats: TeamStatistics, team_b_stats: TeamStatistics):
        self.team_a = team_a_stats
        self.team_b = team_b_stats
        self.conditional_probs = ConditionalProbabilities()
        self.rng = np.random.RandomState()
        self.logger = logging.getLogger(__name__)
        
        # Build transition probability matrix
        self.transition_matrix = self._build_transition_matrix()
    
    def set_random_seed(self, seed: int) -> None:
        """Set random seed for reproducible simulations."""
        self.rng = np.random.RandomState(seed)
    
    def simulate_rally(self, serving_team: str) -> RallyResult:
        """Simulate a single rally starting with serve."""
        current_state = RallyState.SERVE_ATTEMPT
        rally_history: List[StateTransition] = []
        contact_count = 0
        
        while not self._is_terminal_state(current_state):
            # Determine which team is currently acting
            acting_team = self._get_acting_team(current_state, serving_team, rally_history)
            
            # Get transition probabilities for current state
            transitions = self._get_state_transitions(current_state, acting_team)
            
            # Sample next state
            next_state = self._sample_next_state(transitions)
            
            # Record transition
            transition = StateTransition(
                from_state=current_state,
                to_state=next_state,
                probability=transitions[next_state],
                team=acting_team
            )
            rally_history.append(transition)
            
            # Update state and contact count
            current_state = next_state
            if self._counts_as_contact(current_state):
                contact_count += 1
        
        # Determine winner from terminal state
        winner = self._determine_winner(current_state, serving_team)
        
        return RallyResult(
            winner=winner,
            rally_states=rally_history,
            serving_team=serving_team,
            total_contacts=contact_count
        )
    
    def _build_transition_matrix(self) -> Dict[RallyState, Dict[RallyState, float]]:
        """Build the complete transition probability matrix."""
        matrix = {}
        
        # Build transitions for each possible state
        for state in RallyState:
            if not self._is_terminal_state(state):
                matrix[state] = self._calculate_state_transitions(state)
        
        return matrix
    
    def _get_state_transitions(self, state: RallyState, team: str) -> Dict[RallyState, float]:
        """Get transition probabilities for current state and team."""
        team_stats = self.team_a if team == 'A' else self.team_b
        
        if state == RallyState.SERVE_ATTEMPT:
            return self._serve_transitions(team_stats)
        elif state == RallyState.SERVE_IN_PLAY:
            # Reception by receiving team
            receiving_team = 'B' if team == 'A' else 'A'
            receiving_stats = self.team_b if receiving_team == 'B' else self.team_a
            return self._reception_transitions(receiving_stats)
        elif state in [RallyState.RECEPTION_PERFECT, RallyState.RECEPTION_GOOD, RallyState.RECEPTION_POOR]:
            return self._set_transitions(team_stats, state)
        elif state in [RallyState.SET_PERFECT, RallyState.SET_GOOD, RallyState.SET_POOR]:
            return self._attack_transitions(team_stats, state)
        elif state == RallyState.ATTACK_DEFENDED:
            # Defense by opposing team
            defending_team = 'B' if team == 'A' else 'A'
            defending_stats = self.team_b if defending_team == 'B' else self.team_a
            return self._defense_transitions(defending_stats)
        else:
            return {}
    
    def _serve_transitions(self, team_stats: TeamStatistics) -> Dict[RallyState, float]:
        """Calculate serve outcome probabilities."""
        ace_prob = float(team_stats.service_ace_percentage / 100)
        error_prob = float(team_stats.service_error_percentage / 100)
        in_play_prob = 1.0 - ace_prob - error_prob
        
        return {
            RallyState.SERVE_ACE: ace_prob,
            RallyState.SERVE_ERROR: error_prob,
            RallyState.SERVE_IN_PLAY: in_play_prob
        }
    
    def _reception_transitions(self, team_stats: TeamStatistics) -> Dict[RallyState, float]:
        """Calculate reception outcome probabilities."""
        return {
            RallyState.RECEPTION_PERFECT: float(team_stats.perfect_pass_percentage / 100),
            RallyState.RECEPTION_GOOD: float(team_stats.good_pass_percentage / 100),
            RallyState.RECEPTION_POOR: float(team_stats.poor_pass_percentage / 100),
            RallyState.RECEPTION_ERROR: float(team_stats.reception_error_percentage / 100)
        }
    
    def _set_transitions(self, team_stats: TeamStatistics, reception_state: RallyState) -> Dict[RallyState, float]:
        """Calculate set outcome probabilities given reception quality."""
        ball_handling_error = float(team_stats.ball_handling_error_percentage / 100)
        
        if reception_state == RallyState.RECEPTION_PERFECT:
            perfect_prob = float(self.conditional_probs.perfect_set_given_perfect_pass)
            good_prob = float(self.conditional_probs.good_set_given_perfect_pass)
        elif reception_state == RallyState.RECEPTION_GOOD:
            perfect_prob = float(self.conditional_probs.perfect_set_given_good_pass)
            good_prob = float(self.conditional_probs.good_set_given_good_pass)
        else:  # RECEPTION_POOR
            perfect_prob = float(self.conditional_probs.perfect_set_given_poor_pass)
            good_prob = float(self.conditional_probs.good_set_given_poor_pass)
        
        # Adjust for ball handling errors
        perfect_prob *= (1 - ball_handling_error)
        good_prob *= (1 - ball_handling_error)
        poor_prob = (1 - perfect_prob - good_prob - ball_handling_error)
        
        return {
            RallyState.SET_PERFECT: perfect_prob,
            RallyState.SET_GOOD: good_prob,
            RallyState.SET_POOR: poor_prob,
            RallyState.SET_BALL_HANDLING_ERROR: ball_handling_error
        }
    
    def _attack_transitions(self, team_stats: TeamStatistics, set_state: RallyState) -> Dict[RallyState, float]:
        """Calculate attack outcome probabilities given set quality."""
        if set_state == RallyState.SET_PERFECT:
            kill_prob = float(self.conditional_probs.kill_given_perfect_set)
            error_prob = float(self.conditional_probs.error_given_perfect_set)
        elif set_state == RallyState.SET_GOOD:
            kill_prob = float(self.conditional_probs.kill_given_good_set)
            error_prob = float(self.conditional_probs.error_given_good_set)
        else:  # SET_POOR
            kill_prob = float(self.conditional_probs.kill_given_poor_set)
            error_prob = float(self.conditional_probs.error_given_poor_set)
        
        defended_prob = 1.0 - kill_prob - error_prob
        
        return {
            RallyState.ATTACK_KILL: kill_prob,
            RallyState.ATTACK_ERROR: error_prob,
            RallyState.ATTACK_DEFENDED: defended_prob
        }
    
    def _defense_transitions(self, team_stats: TeamStatistics) -> Dict[RallyState, float]:
        """Calculate defense outcome probabilities."""
        # Simplified model - can be enhanced with block vs dig logic
        dig_success = float(team_stats.dig_percentage / 100)
        block_kill = float(team_stats.block_kill_percentage / 100)
        controlled_block = float(team_stats.controlled_block_percentage / 100)
        block_error = float(team_stats.blocking_error_percentage / 100)
        
        # Simple allocation between blocking and digging
        block_attempt_prob = 0.4  # 40% of defenses involve blocking
        dig_attempt_prob = 0.6   # 60% are pure digs
        
        transitions = {}
        
        # Blocking outcomes
        if block_attempt_prob > 0:
            transitions[RallyState.BLOCK_TERMINAL] = block_attempt_prob * block_kill
            transitions[RallyState.BLOCK_CONTROLLED] = block_attempt_prob * controlled_block
            transitions[RallyState.BLOCK_ERROR] = block_attempt_prob * block_error
        
        # Digging outcomes
        if dig_attempt_prob > 0:
            transitions[RallyState.DIG_SUCCESSFUL] = dig_attempt_prob * dig_success
            transitions[RallyState.DIG_ERROR] = dig_attempt_prob * (1 - dig_success)
        
        # Normalize probabilities
        total = sum(transitions.values())
        if total > 0:
            transitions = {k: v / total for k, v in transitions.items()}
        
        return transitions
    
    def _sample_next_state(self, transitions: Dict[RallyState, float]) -> RallyState:
        """Sample next state based on transition probabilities."""
        states = list(transitions.keys())
        probabilities = list(transitions.values())
        
        # Ensure probabilities sum to 1
        total_prob = sum(probabilities)
        if total_prob > 0:
            probabilities = [p / total_prob for p in probabilities]
        
        return self.rng.choice(states, p=probabilities)
    
    def _is_terminal_state(self, state: RallyState) -> bool:
        """Check if state ends the rally."""
        terminal_states = {
            RallyState.SERVE_ACE,
            RallyState.SERVE_ERROR,
            RallyState.RECEPTION_ERROR,
            RallyState.SET_BALL_HANDLING_ERROR,
            RallyState.ATTACK_KILL,
            RallyState.ATTACK_ERROR,
            RallyState.BLOCK_TERMINAL,
            RallyState.BLOCK_ERROR,
            RallyState.DIG_ERROR,
            RallyState.POINT_TEAM_A,
            RallyState.POINT_TEAM_B
        }
        return state in terminal_states
    
    def _determine_winner(self, terminal_state: RallyState, serving_team: str) -> str:
        """Determine rally winner from terminal state."""
        if terminal_state in [RallyState.SERVE_ACE]:
            return serving_team
        elif terminal_state in [RallyState.SERVE_ERROR, RallyState.RECEPTION_ERROR]:
            return 'B' if serving_team == 'A' else 'A'
        elif terminal_state == RallyState.ATTACK_KILL:
            # Need to track which team was attacking - simplified for now
            return serving_team  # This needs more sophisticated tracking
        # ... handle all terminal states
        
        return serving_team  # Default fallback
    
    def _get_acting_team(self, state: RallyState, serving_team: str, history: List[StateTransition]) -> str:
        """Determine which team is acting in current state."""
        # Complex logic to track team possession through rally
        # This is a simplified version
        if state == RallyState.SERVE_ATTEMPT:
            return serving_team
        elif state == RallyState.SERVE_IN_PLAY:
            return 'B' if serving_team == 'A' else 'A'
        # ... more complex possession tracking needed
        
        return serving_team  # Simplified fallback
    
    def _counts_as_contact(self, state: RallyState) -> bool:
        """Check if state represents a ball contact."""
        contact_states = {
            RallyState.SERVE_ATTEMPT,
            RallyState.RECEPTION_PERFECT,
            RallyState.RECEPTION_GOOD,
            RallyState.RECEPTION_POOR,
            RallyState.SET_PERFECT,
            RallyState.SET_GOOD,
            RallyState.SET_POOR,
            RallyState.ATTACK_KILL,
            RallyState.ATTACK_ERROR,
            RallyState.ATTACK_DEFENDED,
            RallyState.BLOCK_TERMINAL,
            RallyState.BLOCK_CONTROLLED,
            RallyState.DIG_SUCCESSFUL
        }
        return state in contact_states
```

### 2.2 Monte Carlo Simulation Engine

```python
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
import asyncio
from typing import List, Optional
import time

@dataclass
class SimulationConfig:
    """Configuration for Monte Carlo simulation."""
    num_points: int = 10000
    random_seed: Optional[int] = None
    parallel_workers: Optional[int] = None
    batch_size: int = 1000
    enable_momentum: bool = False
    momentum_params: Optional[Dict[str, float]] = None

@dataclass
class SimulationResult:
    """Results from Monte Carlo simulation."""
    team_a_wins: int
    team_b_wins: int
    total_points: int
    team_a_win_probability: float
    team_b_win_probability: float
    point_results: List[RallyResult]
    simulation_time: float
    config: SimulationConfig

class MonteCarloSimulator:
    """Monte Carlo simulation engine for beach volleyball points."""
    
    def __init__(self, team_a_stats: TeamStatistics, team_b_stats: TeamStatistics):
        self.team_a = team_a_stats
        self.team_b = team_b_stats
        self.markov_chain = BeachVolleyballMarkovChain(team_a_stats, team_b_stats)
        self.logger = logging.getLogger(__name__)
    
    async def run_simulation(self, config: SimulationConfig) -> SimulationResult:
        """Run Monte Carlo simulation with specified configuration."""
        start_time = time.time()
        
        if config.random_seed is not None:
            self.markov_chain.set_random_seed(config.random_seed)
        
        if config.parallel_workers and config.num_points >= 1000:
            point_results = await self._run_parallel_simulation(config)
        else:
            point_results = self._run_sequential_simulation(config)
        
        # Calculate results
        team_a_wins = sum(1 for result in point_results if result.winner == 'A')
        team_b_wins = len(point_results) - team_a_wins
        
        simulation_time = time.time() - start_time
        
        return SimulationResult(
            team_a_wins=team_a_wins,
            team_b_wins=team_b_wins,
            total_points=len(point_results),
            team_a_win_probability=team_a_wins / len(point_results),
            team_b_win_probability=team_b_wins / len(point_results),
            point_results=point_results,
            simulation_time=simulation_time,
            config=config
        )
    
    def _run_sequential_simulation(self, config: SimulationConfig) -> List[RallyResult]:
        """Run simulation sequentially in single process."""
        results = []
        serving_team = 'A'  # Start with team A serving
        
        for point_num in range(config.num_points):
            # Simulate single point
            result = self.markov_chain.simulate_rally(serving_team)
            results.append(result)
            
            # Update serving team for next point
            if result.winner != serving_team:
                serving_team = 'B' if serving_team == 'A' else 'A'
            
            # Apply momentum effects if enabled
            if config.enable_momentum:
                self._apply_momentum_effects(results, config.momentum_params)
        
        return results
    
    async def _run_parallel_simulation(self, config: SimulationConfig) -> List[RallyResult]:
        """Run simulation in parallel across multiple processes."""
        num_workers = config.parallel_workers or cpu_count()
        points_per_worker = config.num_points // num_workers
        
        # Create tasks for each worker
        tasks = []
        for worker_id in range(num_workers):
            worker_points = points_per_worker
            if worker_id == num_workers - 1:  # Last worker gets remainder
                worker_points += config.num_points % num_workers
            
            worker_config = SimulationConfig(
                num_points=worker_points,
                random_seed=config.random_seed + worker_id if config.random_seed else None,
                batch_size=config.batch_size,
                enable_momentum=False  # Disable momentum for parallel execution
            )
            
            task = asyncio.create_task(
                self._run_worker_simulation(worker_config)
            )
            tasks.append(task)
        
        # Wait for all workers to complete
        worker_results = await asyncio.gather(*tasks)
        
        # Combine results from all workers
        combined_results = []
        for results in worker_results:
            combined_results.extend(results)
        
        return combined_results
    
    async def _run_worker_simulation(self, config: SimulationConfig) -> List[RallyResult]:
        """Run simulation for a single worker."""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._run_sequential_simulation, config)
            return await loop.run_in_executor(None, lambda: future.result())
    
    def _apply_momentum_effects(self, results: List[RallyResult], momentum_params: Optional[Dict[str, float]]) -> None:
        """Apply momentum effects to modify probabilities."""
        if not momentum_params or len(results) < 2:
            return
        
        # Count consecutive wins on serve for last few points
        recent_results = results[-3:]  # Look at last 3 points
        consecutive_serve_wins = 0
        
        current_server = results[-1].serving_team
        for result in reversed(recent_results):
            if result.serving_team == current_server and result.winner == current_server:
                consecutive_serve_wins += 1
            else:
                break
        
        # Apply momentum boost based on consecutive wins
        if consecutive_serve_wins > 0:
            momentum_boost = momentum_params.get(f'm{consecutive_serve_wins}', 0)
            if momentum_boost > 0:
                # Modify transition probabilities for next point
                # This is a simplified implementation
                self.logger.debug(f"Applying momentum boost: {momentum_boost}")
```

This technical specification provides the detailed implementation foundation for the core simulation engine. The next steps would be to implement the API layer, analytics module, and frontend according to the implementation plan timeline.

<function_calls>
<invoke name="create_file">
<parameter name="content"># Beach Volleyball Simulator - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+

## Development Setup

### 1. Clone and Setup Project

```bash
git clone <repository-url>
cd BVSim
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file in backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/bvsim
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 4. Database Setup

```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Run database migrations
alembic upgrade head
```

### 5. Start Development Servers

```bash
# Backend (Terminal 1)
cd backend
uvicorn bvsim.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

## Project Structure Overview

```
BVSim/
├── backend/
│   ├── src/bvsim/           # Main application code
│   ├── tests/               # Test files
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/                # React TypeScript code
│   ├── public/             # Static assets
│   └── package.json
└── docker-compose.yml      # Local development services
```

## Key Implementation Files

### Core Models
- `backend/src/bvsim/models/team_statistics.py` - Team statistics data model
- `backend/src/bvsim/models/simulation.py` - Simulation result models

### Simulation Engine
- `backend/src/bvsim/simulation/markov_chain.py` - Markov chain implementation
- `backend/src/bvsim/simulation/monte_carlo.py` - Monte Carlo simulator
- `backend/src/bvsim/simulation/rally_states.py` - Rally state definitions

### API Layer
- `backend/src/bvsim/controllers/simulation.py` - Simulation endpoints
- `backend/src/bvsim/controllers/analytics.py` - Analysis endpoints

### Analytics
- `backend/src/bvsim/analytics/importance_analysis.py` - Feature importance
- `backend/src/bvsim/analytics/shap_analysis.py` - SHAP value calculation

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Production Build

```bash
# Build containers
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables (Production)

```env
DATABASE_URL=postgresql://user:password@db:5432/bvsim
REDIS_URL=redis://redis:6379
SECRET_KEY=strong-production-secret
DEBUG=False
CORS_ORIGINS=["https://yourdomain.com"]
```

## Contributing

1. Create feature branch
2. Implement changes with tests
3. Run code quality checks
4. Submit pull request

## Support

For questions or issues, please refer to:
- Implementation Plan: `IMPLEMENTATION_PLAN.md`
- Technical Specs: `TECHNICAL_SPECS.md`
- Project documentation in `/docs`
