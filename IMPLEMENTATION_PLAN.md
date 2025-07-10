# Beach Volleyball Point Simulator - Implementation Plan

## Executive Summary

This implementation plan outlines the development approach for the probabilistic beach volleyball point simulation and impact analysis application. The project will be implemented using Python following clean architecture principles with FastAPI for the backend and a modern web frontend.

## 1. Project Structure and Architecture

### 1.1 Technology Stack

**Backend:**
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (primary), Redis (caching)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Async**: asyncio/aiohttp
- **Analytics**: scikit-learn, SHAP, NumPy, SciPy, pandas
- **Testing**: pytest, pytest-asyncio

**Frontend:**
- **Framework**: React with TypeScript
- **State Management**: Zustand
- **UI Components**: shadcn/ui
- **Charts**: Recharts
- **HTTP Client**: axios

**DevOps:**
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Code Quality**: black, isort, flake8, mypy

### 1.2 Project Structure

```
BVSim/
├── backend/
│   ├── src/
│   │   ├── bvsim/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                    # FastAPI app entry point
│   │   │   ├── config/                    # Configuration settings
│   │   │   ├── models/                    # Database models
│   │   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── controllers/               # API endpoints
│   │   │   ├── services/                  # Business logic
│   │   │   ├── repositories/              # Data access layer
│   │   │   ├── simulation/                # Simulation engine
│   │   │   │   ├── markov_chain.py
│   │   │   │   ├── monte_carlo.py
│   │   │   │   └── rally_states.py
│   │   │   ├── analytics/                 # Statistical analysis
│   │   │   │   ├── importance_analysis.py
│   │   │   │   ├── logistic_regression.py
│   │   │   │   └── shap_analysis.py
│   │   │   └── utils/                     # Utility functions
│   │   └── requirements.txt
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── utils/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .github/workflows/
└── README.md
```

## 2. Implementation Phases

### Phase 1: Foundation and Core Models (Weeks 1-3)

#### Week 1: Project Setup
- [ ] Initialize project structure
- [ ] Set up development environment with Poetry/pip-tools
- [ ] Configure Docker containers
- [ ] Set up CI/CD pipeline
- [ ] Create database schema
- [ ] Implement basic FastAPI application

#### Week 2: Data Models and Schemas
- [ ] Define Pydantic schemas for team statistics input
- [ ] Create database models for:
  - Team statistics
  - Simulation results
  - Rally states
  - Analysis results
- [ ] Implement data validation
- [ ] Create database migrations

#### Week 3: Core Domain Models
- [ ] Implement fundamental skill enums and constants
- [ ] Create team statistics model with validation
- [ ] Implement rally state definitions
- [ ] Create probability distribution models
- [ ] Unit tests for core models

### Phase 2: Simulation Engine (Weeks 4-6)

#### Week 4: Markov Chain Implementation
```python
# Key components to implement:
class RallyState(Enum):
    SERVE_ATTEMPT = "serve_attempt"
    SERVE_ACE = "serve_ace"
    SERVE_ERROR = "serve_error"
    RECEPTION_PERFECT = "reception_perfect"
    RECEPTION_GOOD = "reception_good"
    RECEPTION_POOR = "reception_poor"
    RECEPTION_ERROR = "reception_error"
    # ... more states

class MarkovChain:
    def __init__(self, team_a_stats: TeamStats, team_b_stats: TeamStats):
        self.transition_matrix = self._build_transition_matrix()
    
    def simulate_rally(self) -> RallyResult:
        # Implement rally simulation logic
        pass
```

#### Week 5: Monte Carlo Simulation
- [ ] Implement Monte Carlo simulation engine
- [ ] Create conditional probability calculations
- [ ] Implement momentum effects (optional)
- [ ] Parallel processing for large simulations
- [ ] Memory optimization for large datasets

#### Week 6: Rally Flow Logic
- [ ] Implement serve mechanics
- [ ] Reception quality determination
- [ ] Setting conditional probabilities
- [ ] Attack outcome logic
- [ ] Defense and blocking mechanics
- [ ] Counter-attack cycles

### Phase 3: API Layer and Services (Weeks 7-8)

#### Week 7: Service Layer
```python
class SimulationService:
    async def run_simulation(
        self, 
        team_a_stats: TeamStats, 
        team_b_stats: TeamStats,
        num_points: int = 10000,
        random_seed: Optional[int] = None
    ) -> SimulationResult:
        # Business logic for running simulations
        pass

class AnalyticsService:
    async def analyze_importance(
        self, 
        simulation_data: List[PointResult]
    ) -> ImportanceAnalysis:
        # Statistical importance analysis
        pass
```

#### Week 8: API Controllers
- [ ] Simulation endpoints
- [ ] Team statistics CRUD operations
- [ ] Analysis endpoints
- [ ] File upload for batch input
- [ ] Real-time simulation status

### Phase 4: Analytics Module (Weeks 9-11)

#### Week 9: Statistical Analysis Foundation
- [ ] Implement logistic regression analysis
- [ ] Feature importance calculation
- [ ] Data preprocessing for analysis
- [ ] Statistical significance testing

#### Week 10: SHAP Implementation
```python
class SHAPAnalyzer:
    def __init__(self, simulation_data: pd.DataFrame):
        self.data = simulation_data
        self.model = LogisticRegression()
    
    def calculate_shap_values(self) -> Dict[str, float]:
        # Implement SHAP value calculation
        pass
    
    def generate_importance_ranking(self) -> List[FeatureImportance]:
        # Generate ranked importance list
        pass
```

#### Week 11: Sensitivity Analysis
- [ ] Marginal impact calculations
- [ ] Confidence interval estimation
- [ ] Visualization data preparation
- [ ] Performance optimization

### Phase 5: Frontend Development (Weeks 12-15)

#### Week 12: Core UI Components
- [ ] Team statistics input forms
- [ ] Simulation parameter configuration
- [ ] Basic simulation results display
- [ ] Navigation and layout

#### Week 13: Data Visualization
- [ ] Importance analysis charts
- [ ] Rally flow visualization
- [ ] Statistical comparison tables
- [ ] Interactive sensitivity analysis

#### Week 14: Advanced Features
- [ ] Real-time simulation progress
- [ ] Export functionality
- [ ] Simulation history
- [ ] Batch processing interface

#### Week 15: UI/UX Polish
- [ ] Responsive design
- [ ] Error handling and validation
- [ ] Loading states
- [ ] User experience optimization

### Phase 6: Integration and Testing (Weeks 16-17)

#### Week 16: Integration Testing
- [ ] End-to-end API testing
- [ ] Frontend-backend integration
- [ ] Performance testing
- [ ] Database optimization

#### Week 17: System Testing
- [ ] Load testing with large simulations
- [ ] User acceptance testing
- [ ] Security testing
- [ ] Documentation completion

### Phase 7: Deployment and Documentation (Week 18)

- [ ] Production deployment setup
- [ ] Database migrations
- [ ] Monitoring and logging
- [ ] User documentation
- [ ] API documentation
- [ ] Performance monitoring

## 3. Key Implementation Details

### 3.1 Database Schema

```sql
-- Core tables
CREATE TABLE team_statistics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    -- Serve statistics
    service_ace_percentage DECIMAL(5,2),
    service_error_percentage DECIMAL(5,2),
    serve_success_rate DECIMAL(5,2),
    -- Reception statistics
    perfect_pass_percentage DECIMAL(5,2),
    good_pass_percentage DECIMAL(5,2),
    poor_pass_percentage DECIMAL(5,2),
    reception_error_percentage DECIMAL(5,2),
    -- Attack statistics
    attack_kill_percentage DECIMAL(5,2),
    attack_error_percentage DECIMAL(5,2),
    hitting_efficiency DECIMAL(5,2),
    -- Defense statistics
    dig_percentage DECIMAL(5,2),
    block_kill_percentage DECIMAL(5,2),
    controlled_block_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    team_a_id INTEGER REFERENCES team_statistics(id),
    team_b_id INTEGER REFERENCES team_statistics(id),
    num_points INTEGER NOT NULL,
    random_seed INTEGER,
    team_a_win_probability DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE simulation_points (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulations(id),
    point_number INTEGER NOT NULL,
    winner_team VARCHAR(1) NOT NULL, -- 'A' or 'B'
    rally_states JSONB, -- Store rally progression
    serving_team VARCHAR(1) NOT NULL
);

CREATE TABLE importance_analyses (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulations(id),
    statistic_name VARCHAR(255) NOT NULL,
    importance_score DECIMAL(10,6),
    marginal_impact DECIMAL(5,2),
    confidence_interval_lower DECIMAL(5,2),
    confidence_interval_upper DECIMAL(5,2),
    method VARCHAR(50) -- 'logistic_regression' or 'shap'
);
```

### 3.2 Core Simulation Algorithm

```python
class RallySimulator:
    def __init__(self, team_a_stats: TeamStats, team_b_stats: TeamStats):
        self.team_a = team_a_stats
        self.team_b = team_b_stats
        self.rng = np.random.RandomState()
    
    def simulate_point(self, serving_team: Team) -> PointResult:
        """Simulate a single point using Markov chain logic."""
        current_state = RallyState.SERVE_ATTEMPT
        rally_history = []
        
        while not self._is_terminal_state(current_state):
            # Get transition probabilities based on current state and team stats
            transitions = self._get_transition_probabilities(
                current_state, serving_team
            )
            
            # Sample next state
            next_state = self._sample_transition(transitions)
            rally_history.append((current_state, next_state))
            current_state = next_state
        
        # Determine point winner from terminal state
        winner = self._determine_winner(current_state)
        
        return PointResult(
            winner=winner,
            rally_states=rally_history,
            serving_team=serving_team
        )
    
    def _get_transition_probabilities(
        self, state: RallyState, serving_team: Team
    ) -> Dict[RallyState, float]:
        """Calculate conditional probabilities for state transitions."""
        # Implementation depends on current state and team statistics
        pass
```

### 3.3 Statistical Analysis Pipeline

```python
class ImportanceAnalyzer:
    def __init__(self, simulation_results: List[PointResult]):
        self.data = self._prepare_dataset(simulation_results)
    
    def analyze_feature_importance(self) -> ImportanceAnalysis:
        """Run both logistic regression and SHAP analysis."""
        # Logistic regression analysis
        lr_results = self._logistic_regression_analysis()
        
        # SHAP analysis
        shap_results = self._shap_analysis()
        
        # Combine and rank features
        combined_ranking = self._combine_rankings(lr_results, shap_results)
        
        return ImportanceAnalysis(
            logistic_regression=lr_results,
            shap_values=shap_results,
            combined_ranking=combined_ranking
        )
    
    def calculate_marginal_impact(
        self, feature: str, change_amount: float
    ) -> MarginalImpact:
        """Calculate the impact of changing a specific statistic."""
        # Run sensitivity analysis
        pass
```

## 4. Performance Considerations

### 4.1 Optimization Strategies

1. **Simulation Performance**:
   - Use NumPy for vectorized operations
   - Implement parallel processing with multiprocessing
   - Cache transition probability matrices
   - Use memory-efficient data structures

2. **Database Optimization**:
   - Index frequently queried columns
   - Partition large tables by simulation_id
   - Use connection pooling
   - Implement read replicas for analytics

3. **API Performance**:
   - Implement async endpoints
   - Use Redis for caching
   - Background job processing for large simulations
   - API rate limiting

### 4.2 Scalability Planning

```python
# Example of parallel simulation processing
class ParallelSimulator:
    def __init__(self, num_workers: int = None):
        self.num_workers = num_workers or cpu_count()
    
    async def run_large_simulation(
        self, 
        team_a_stats: TeamStats,
        team_b_stats: TeamStats,
        total_points: int
    ) -> SimulationResult:
        """Run simulation across multiple processes."""
        points_per_worker = total_points // self.num_workers
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(
                    self._simulate_batch, 
                    team_a_stats, 
                    team_b_stats, 
                    points_per_worker
                )
                for _ in range(self.num_workers)
            ]
            
            results = await asyncio.gather(*futures)
            return self._combine_results(results)
```

## 5. Testing Strategy

### 5.1 Unit Testing
- Test individual components in isolation
- Mock external dependencies
- Achieve >90% code coverage
- Property-based testing for statistical functions

### 5.2 Integration Testing
- Test API endpoints end-to-end
- Database integration tests
- Simulation accuracy validation

### 5.3 Performance Testing
- Load testing with large simulations
- Memory usage monitoring
- Response time benchmarks

## 6. Deployment and DevOps

### 6.1 Containerization

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["uvicorn", "bvsim.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/bvsim
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: bvsim
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 7. Risk Mitigation

### 7.1 Technical Risks
- **Performance bottlenecks**: Implement profiling and monitoring early
- **Statistical accuracy**: Validate against known datasets
- **Scalability limits**: Design for horizontal scaling from start
- **Data integrity**: Implement comprehensive validation

### 7.2 Project Risks
- **Scope creep**: Maintain clear phase boundaries
- **Integration complexity**: Start integration testing early
- **Performance requirements**: Set clear benchmarks upfront

## 8. Success Metrics

### 8.1 Technical Metrics
- Simulation accuracy (validated against real match data)
- Performance benchmarks (10,000 points < 30 seconds)
- System reliability (99.9% uptime)
- Code quality (>90% test coverage)

### 8.2 User Experience Metrics
- Simulation completion time
- API response times
- User interface responsiveness
- Error rates

## 9. Future Enhancements Roadmap

### Short-term (6 months)
- Player-specific statistics
- Enhanced momentum modeling
- Real-time match integration

### Medium-term (12 months)
- Machine learning for probability derivation
- Advanced visualization features
- Mobile application

### Long-term (18+ months)
- Multi-sport adaptation
- Predictive modeling
- Commercial API offering

This implementation plan provides a structured approach to building the beach volleyball simulation application while maintaining code quality, performance, and scalability requirements.
