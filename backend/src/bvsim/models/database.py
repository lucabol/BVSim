"""Database models for the Beach Volleyball Simulator."""

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from ..core.database import Base


class TeamStatistics(Base):
    """Team fundamental statistics for simulation input."""
    
    __tablename__ = "team_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    
    # Serve statistics
    service_ace_percentage = Column(DECIMAL(5, 2), nullable=False)
    service_error_percentage = Column(DECIMAL(5, 2), nullable=False)
    serve_success_rate = Column(DECIMAL(5, 2), nullable=False)
    
    # Reception statistics (Pass Quality Rating distribution)
    perfect_pass_percentage = Column(DECIMAL(5, 2), nullable=False)
    good_pass_percentage = Column(DECIMAL(5, 2), nullable=False)
    poor_pass_percentage = Column(DECIMAL(5, 2), nullable=False)
    reception_error_percentage = Column(DECIMAL(5, 2), nullable=False)
    
    # Setting statistics
    assist_percentage = Column(DECIMAL(5, 2), nullable=False)
    ball_handling_error_percentage = Column(DECIMAL(5, 2), nullable=False)
    
    # Attack statistics
    attack_kill_percentage = Column(DECIMAL(5, 2), nullable=False)
    attack_error_percentage = Column(DECIMAL(5, 2), nullable=False)
    hitting_efficiency = Column(DECIMAL(5, 3), nullable=False)  # Can be negative
    first_ball_kill_percentage = Column(DECIMAL(5, 2), nullable=False)
    
    # Defense statistics
    dig_percentage = Column(DECIMAL(5, 2), nullable=False)
    block_kill_percentage = Column(DECIMAL(5, 2), nullable=False)
    controlled_block_percentage = Column(DECIMAL(5, 2), nullable=False)
    blocking_error_percentage = Column(DECIMAL(5, 2), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    simulations_as_team_a = relationship("Simulation", foreign_keys="Simulation.team_a_id", back_populates="team_a")
    simulations_as_team_b = relationship("Simulation", foreign_keys="Simulation.team_b_id", back_populates="team_b")


class Simulation(Base):
    """Simulation configuration and results."""
    
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Team references
    team_a_id = Column(Integer, ForeignKey("team_statistics.id"), nullable=False)
    team_b_id = Column(Integer, ForeignKey("team_statistics.id"), nullable=False)
    
    # Simulation parameters
    num_points = Column(Integer, nullable=False)
    random_seed = Column(Integer, nullable=True)
    enable_momentum = Column(Boolean, default=False, nullable=False)
    
    # Results
    team_a_wins = Column(Integer, nullable=True)
    team_b_wins = Column(Integer, nullable=True)
    team_a_win_probability = Column(DECIMAL(5, 4), nullable=True)
    team_b_win_probability = Column(DECIMAL(5, 4), nullable=True)
    
    # Status and timing
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    simulation_time_seconds = Column(DECIMAL(10, 3), nullable=True)
    
    # Configuration JSON
    config = Column(JSONB, nullable=True)
    
    # Relationships
    team_a = relationship("TeamStatistics", foreign_keys=[team_a_id], back_populates="simulations_as_team_a")
    team_b = relationship("TeamStatistics", foreign_keys=[team_b_id], back_populates="simulations_as_team_b")
    points = relationship("SimulationPoint", back_populates="simulation", cascade="all, delete-orphan")
    analyses = relationship("ImportanceAnalysis", back_populates="simulation", cascade="all, delete-orphan")


class SimulationPoint(Base):
    """Individual point results from simulation."""
    
    __tablename__ = "simulation_points"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # Point details
    point_number = Column(Integer, nullable=False)
    winner_team = Column(String(1), nullable=False)  # 'A' or 'B'
    serving_team = Column(String(1), nullable=False)  # 'A' or 'B'
    
    # Rally progression stored as JSON
    rally_states = Column(JSONB, nullable=False)
    total_contacts = Column(Integer, nullable=False, default=0)
    rally_duration_ms = Column(Integer, nullable=True)
    
    # Relationship
    simulation = relationship("Simulation", back_populates="points")


class ImportanceAnalysis(Base):
    """Feature importance analysis results."""
    
    __tablename__ = "importance_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # Feature details
    statistic_name = Column(String(255), nullable=False, index=True)
    feature_category = Column(String(100), nullable=False)  # 'serve', 'reception', 'attack', 'defense'
    
    # Importance scores
    importance_score = Column(DECIMAL(10, 6), nullable=False)
    marginal_impact = Column(DECIMAL(8, 4), nullable=False)
    confidence_interval_lower = Column(DECIMAL(8, 4), nullable=True)
    confidence_interval_upper = Column(DECIMAL(8, 4), nullable=True)
    
    # Analysis method and metadata
    method = Column(String(50), nullable=False)  # 'logistic_regression', 'shap', 'combined'
    analysis_config = Column(JSONB, nullable=True)
    
    # Ranking
    rank = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    simulation = relationship("Simulation", back_populates="analyses")
