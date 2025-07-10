"""Pydantic schemas for team statistics."""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Self, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum


class TeamStatisticsBase(BaseModel):
    """Base schema for team statistics."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Team name")
    
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
    perfect_pass_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of perfect receptions (allows all options)"
    )
    good_pass_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of good receptions (limited options, multiple attackers)"
    )
    poor_pass_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of poor receptions (predictable set)"
    )
    reception_error_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of reception errors/overpasses"
    )
    
    # Setting statistics
    assist_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of sets leading to kills"
    )
    ball_handling_error_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of setting faults"
    )
    
    # Attack statistics
    attack_kill_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of attacks resulting in points"
    )
    attack_error_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of attack faults"
    )
    hitting_efficiency: Decimal = Field(
        ..., ge=-1, le=1,
        description="(Kills - Errors) / Total Attempts"
    )
    first_ball_kill_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of points scored immediately after receiving serve"
    )
    
    # Defense statistics
    dig_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of attacked balls successfully passed"
    )
    block_kill_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of blocks resulting in immediate points"
    )
    controlled_block_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of blocks that slow/redirect attacks"
    )
    blocking_error_percentage: Decimal = Field(
        ..., ge=0, le=100,
        description="Percentage of blocking faults"
    )
    
    @model_validator(mode='after')
    def validate_percentages(self) -> Self:
        """Validate all percentage relationships."""
        # Check serve percentages
        serve_total = self.service_ace_percentage + self.service_error_percentage
        if serve_total > 100:
            raise ValueError("Service ace and error percentages cannot exceed 100%")
        
        # Check reception percentages sum to ~100%
        reception_total = (
            self.perfect_pass_percentage + 
            self.good_pass_percentage + 
            self.poor_pass_percentage + 
            self.reception_error_percentage
        )
        if not (95 <= reception_total <= 105):
            raise ValueError(
                f"Reception percentages must sum to ~100%, got {reception_total}%"
            )
        
        # Check attack percentages
        attack_total = self.attack_kill_percentage + self.attack_error_percentage
        if attack_total > 100:
            raise ValueError("Attack kill and error percentages cannot exceed 100%")
        
        return self


class TeamStatisticsCreate(TeamStatisticsBase):
    """Schema for creating team statistics."""
    pass


class TeamStatisticsUpdate(BaseModel):
    """Schema for updating team statistics."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    
    # All statistics are optional for updates
    service_ace_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    service_error_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    serve_success_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    
    perfect_pass_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    good_pass_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    poor_pass_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    reception_error_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    assist_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    ball_handling_error_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    attack_kill_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    attack_error_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    hitting_efficiency: Optional[Decimal] = Field(None, ge=-1, le=1)
    first_ball_kill_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    dig_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    block_kill_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    controlled_block_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    blocking_error_percentage: Optional[Decimal] = Field(None, ge=0, le=100)


class TeamStatisticsInDB(TeamStatisticsBase):
    """Schema for team statistics in database."""
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        orm_mode = True


class TeamStatisticsResponse(TeamStatisticsInDB):
    """Schema for team statistics API response."""
    pass


# Summary statistics for quick overview
class TeamStatisticsSummary(BaseModel):
    """Summary schema for team statistics."""
    
    id: int
    name: str
    
    # Key performance indicators
    overall_serve_effectiveness: Decimal = Field(
        ..., description="Combined serve ace rate minus error rate"
    )
    reception_quality_score: Decimal = Field(
        ..., description="Weighted average of reception quality"
    )
    offensive_efficiency: Decimal = Field(
        ..., description="Attack kill rate minus error rate"
    )
    defensive_effectiveness: Decimal = Field(
        ..., description="Combined dig and block success rate"
    )
    
    created_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True


class StatisticCategory(str, Enum):
    """Categories of team statistics."""
    SERVING = "serving"
    RECEPTION = "reception"
    SETTING = "setting"
    ATTACK = "attack"
    DEFENSE = "defense"
    ALL = "all"


class TeamStatisticsImport(BaseModel):
    """Schema for importing team statistics from file."""
    
    file_format: str = Field(..., description="File format (csv, excel, json)")
    data: List[Dict[str, Any]] = Field(..., description="Statistics data to import")
    update_existing: bool = Field(default=False, description="Update existing teams")
    validate_percentages: bool = Field(default=True, description="Validate percentage constraints")


class TeamStatisticsBatch(BaseModel):
    """Schema for batch operations on team statistics."""
    
    operation: str = Field(..., description="Batch operation type")
    team_ids: List[int] = Field(..., description="List of team IDs")
    data: Optional[Dict[str, Any]] = Field(None, description="Operation data")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")


class TeamStatisticsExport(BaseModel):
    """Schema for exporting team statistics."""
    
    team_ids: Optional[List[int]] = Field(None, description="Specific teams to export")
    categories: List[StatisticCategory] = Field(default=[StatisticCategory.ALL], description="Categories to include")
    format: str = Field(default="json", description="Export format")
    include_metadata: bool = Field(default=True, description="Include metadata")
    include_summary: bool = Field(default=True, description="Include summary statistics")
