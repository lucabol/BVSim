# 🏐 Beach Volleyball Simulator (BVSim)

**High-performance Monte Carlo simulation engine for beach volleyball match prediction and statistical analysis**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Performance](https://img.shields.io/badge/Performance-500%2B%20sim%2Fsec-brightgreen.svg)](#performance)

## 🎯 Overview

BVSim is a sophisticated simulation engine that models beach volleyball matches with incredible detail and accuracy. Using Monte Carlo methods and parallel processing, it can simulate thousands of matches in seconds while providing statistical analysis with confidence intervals.

## ✨ Features

### 🚀 **High-Performance Simulation**
- **500+ simulations per second** with parallel processing
- **47 volleyball-specific rally states** with realistic transitions  
- **Statistical analysis** with 95% confidence intervals
- **Multiple match formats** (best-of-1, best-of-3)

### 🎮 **Advanced Game Mechanics**
- **Skill-based probability engine** with contextual adjustments
- **Realistic volleyball flow**: serve → reception → set → attack → dig → transition
- **Team-specific statistics** affecting all game aspects
- **Momentum, pressure, and fatigue effects** (configurable)

### 🌐 **REST API Integration**
- **FastAPI-powered** with automatic documentation
- **Async processing** for large simulations
- **Real-time status tracking** for background jobs
- **Comprehensive error handling** and validation

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- pip or poetry for package management

### Installation

```bash
# Clone the repository
git clone https://github.com/lucabol/BVSim.git
cd BVSim

# Install dependencies
cd backend
pip install -r requirements.txt

# Run the server
python -m uvicorn src.bvsim.main:app --reload --port 8000
```

### Basic Usage

```bash
# Health check
curl http://localhost:8000/health

# Simulate a single rally
curl -X POST "http://localhost:8000/rally/simulate" \
  -H "Content-Type: application/json" \
  -d @test_rally_request.json

# Run Monte Carlo simulation (1000 matches)
curl -X POST "http://localhost:8000/simulation/monte-carlo" \
  -H "Content-Type: application/json" \
  -d @test_monte_carlo_request.json
```

## 📊 Performance Benchmarks

| Simulation Size | Processing Time | Simulations/Second | Accuracy |
|----------------|-----------------|-------------------|----------|
| 100 matches    | ~0.3 seconds    | 330+ sim/sec     | ±9.8%    |
| 1,000 matches  | ~2.8 seconds    | 360+ sim/sec     | ±3.1%    |
| 5,000 matches  | ~9.9 seconds    | 507+ sim/sec     | ±1.4%    |

*Tested on: Intel i7, 16GB RAM, Windows 11*

## 🏗️ Architecture

```
BVSim/
├── backend/src/bvsim/
│   ├── engine/           # Core simulation engine
│   │   ├── rally_states.py      # 47 volleyball states
│   │   ├── probability_engine.py # Skill-based calculations
│   │   ├── rally_simulator.py   # Individual rally simulation
│   │   └── monte_carlo.py       # Parallel Monte Carlo engine
│   ├── api/              # FastAPI endpoints
│   │   ├── rally.py             # Rally simulation API
│   │   └── monte_carlo.py       # Monte Carlo API
│   ├── schemas/          # Pydantic data models
│   └── core/             # Database and config
├── tests/                # Comprehensive test suite
└── docs/                 # Documentation
```

## 🎯 API Endpoints

### Core Simulation
- `POST /rally/simulate` - Simulate individual rally
- `POST /simulation/monte-carlo` - Synchronous Monte Carlo simulation
- `POST /simulation/quick-simulation` - Quick skill-based simulation
- `POST /simulation/monte-carlo-async` - Asynchronous large simulations

### Monitoring
- `GET /health` - System health check
- `GET /simulation/status/{id}` - Check async simulation status
- `GET /docs` - Interactive API documentation

## 📈 Sample Results

```json
{
  "simulation_id": "567e4ec6-cbfa-4148-83ca-0145dfab2728",
  "num_simulations": 5000,
  "team_a_win_probability": 0.1678,
  "team_b_win_probability": 0.8322,
  "confidence_interval_lower": 0.1574,
  "confidence_interval_upper": 0.1782,
  "margin_of_error": 0.0139,
  "is_statistically_significant": true,
  "avg_sets_per_match": 2.398,
  "simulation_time_seconds": 9.86,
  "simulations_per_second": 506.99
}
```

## 🧪 Testing

```bash
# Run the comprehensive test suite
cd backend
python test_monte_carlo.py

# Performance benchmarking
python -m pytest tests/ -v
```

## 🛠️ Development Phases

- ✅ **Phase 1**: Rally State Engine (Weeks 1-3)
- ✅ **Phase 2**: Monte Carlo Simulation (Current)
- 🔄 **Phase 3**: Advanced Analytics (Weeks 4-6)
- 📅 **Phase 4**: Machine Learning Integration (Weeks 7-9)
- 📅 **Phase 5**: Real-time Tournament Simulation (Weeks 10-12)
- 📅 **Phase 6**: Web Frontend (Weeks 13-15)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- Beach volleyball community for gameplay insights
- FastAPI team for the excellent framework
- Python scientific computing ecosystem (NumPy, SciPy, etc.)

## 📧 Contact

**Luca Bolognese** - [@lucabol](https://github.com/lucabol)

Project Link: [https://github.com/lucabol/BVSim](https://github.com/lucabol/BVSim)

---

*Built with ❤️ for the beach volleyball community*

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
