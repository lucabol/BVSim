"""
Tests for advanced analytics engine with SHAP values and feature importance.
"""

import pytest
import numpy as np
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from src.bvsim.engine.advanced_analytics import AdvancedAnalyticsEngine
from src.bvsim.schemas.analytics import (
    AdvancedAnalyticsRequest, AnalysisType, ScenarioAnalysisRequest
)
from src.bvsim.schemas.team_statistics import TeamStatisticsBase


@pytest.fixture
def sample_team_a():
    """Sample team A statistics."""
    return TeamStatisticsBase(
        name="Team A",
        service_ace_percentage=Decimal('12.0'),
        service_error_percentage=Decimal('8.0'),
        serve_success_rate=Decimal('85.0'),
        perfect_pass_percentage=Decimal('35.0'),
        good_pass_percentage=Decimal('45.0'),
        poor_pass_percentage=Decimal('15.0'),
        reception_error_percentage=Decimal('5.0'),
        assist_percentage=Decimal('55.0'),
        ball_handling_error_percentage=Decimal('3.0'),
        attack_kill_percentage=Decimal('45.0'),
        attack_error_percentage=Decimal('15.0'),
        hitting_efficiency=Decimal('0.30'),
        first_ball_kill_percentage=Decimal('12.0'),
        dig_percentage=Decimal('35.0'),
        block_kill_percentage=Decimal('10.0'),
        controlled_block_percentage=Decimal('20.0'),
        blocking_error_percentage=Decimal('4.0')
    )


@pytest.fixture
def sample_team_b():
    """Sample team B statistics."""
    return TeamStatisticsBase(
        name="Team B",
        service_ace_percentage=Decimal('10.0'),
        service_error_percentage=Decimal('10.0'),
        serve_success_rate=Decimal('80.0'),
        perfect_pass_percentage=Decimal('30.0'),
        good_pass_percentage=Decimal('40.0'),
        poor_pass_percentage=Decimal('20.0'),
        reception_error_percentage=Decimal('10.0'),
        assist_percentage=Decimal('50.0'),
        ball_handling_error_percentage=Decimal('5.0'),
        attack_kill_percentage=Decimal('40.0'),
        attack_error_percentage=Decimal('20.0'),
        hitting_efficiency=Decimal('0.20'),
        first_ball_kill_percentage=Decimal('10.0'),
        dig_percentage=Decimal('30.0'),
        block_kill_percentage=Decimal('8.0'),
        controlled_block_percentage=Decimal('15.0'),
        blocking_error_percentage=Decimal('6.0')
    )


@pytest.fixture
def analytics_engine():
    """Create analytics engine instance."""
    return AdvancedAnalyticsEngine()


@pytest.fixture
def basic_analytics_request(sample_team_a, sample_team_b):
    """Basic analytics request for testing."""
    return AdvancedAnalyticsRequest(
        team_a=sample_team_a,
        team_b=sample_team_b,
        analysis_types=[AnalysisType.FEATURE_IMPORTANCE],
        model_type="gradient_boosting",
        num_simulations=1000,  # Minimum required
        confidence_level=Decimal('0.95'),
        sensitivity_ranges={}
    )


class TestAdvancedAnalyticsEngine:
    """Test cases for AdvancedAnalyticsEngine."""
    
    @pytest.mark.asyncio
    async def test_feature_importance_analysis(self, analytics_engine, basic_analytics_request):
        """Test feature importance analysis."""
        result = await analytics_engine.run_advanced_analysis(basic_analytics_request)
        
        assert result is not None
        assert result.analysis_id is not None
        assert result.team_a_analytics is not None
        assert len(result.team_a_analytics.feature_importances) > 0
        assert result.simulation_count == 100
        assert result.analysis_time_seconds > 0
        assert result.reliability_score > 0
    
    @pytest.mark.asyncio
    async def test_shap_analysis(self, analytics_engine, sample_team_a, sample_team_b):
        """Test SHAP values analysis."""
        request = AdvancedAnalyticsRequest(
            team_a=sample_team_a,
            team_b=sample_team_b,
            analysis_types=[AnalysisType.SHAP_VALUES],
            model_type="gradient_boosting",
            num_simulations=1000,
            confidence_level=Decimal('0.95'),
            sensitivity_ranges={}
        )
        
        result = await analytics_engine.run_advanced_analysis(request)
        
        assert result.shap_analysis is not None
        assert result.shap_analysis.base_prediction is not None
        assert len(result.shap_analysis.shap_values) > 0
        assert result.shap_analysis.global_feature_importance is not None
        
        # Check SHAP values have required fields
        shap_val = result.shap_analysis.shap_values[0]
        assert shap_val.feature_name is not None
        assert shap_val.shap_value is not None
        assert shap_val.impact_direction in ["positive", "negative", "neutral"]
    
    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self, analytics_engine, sample_team_a, sample_team_b):
        """Test sensitivity analysis."""
        sensitivity_ranges = {
            "service_ace_percentage": [Decimal('8.0'), Decimal('12.0'), Decimal('16.0')],
            "attack_kill_percentage": [Decimal('40.0'), Decimal('45.0'), Decimal('50.0')]
        }
        
        request = AdvancedAnalyticsRequest(
            team_a=sample_team_a,
            team_b=sample_team_b,
            analysis_types=[AnalysisType.SENSITIVITY_ANALYSIS],
            model_type="gradient_boosting",
            num_simulations=1000,
            confidence_level=Decimal('0.95'),
            sensitivity_ranges=sensitivity_ranges
        )
        
        result = await analytics_engine.run_advanced_analysis(request)
        
        assert result is not None
        assert result.team_a_analytics is not None
        # Sensitivity results would be in the analytics response
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self, analytics_engine, sample_team_a, sample_team_b):
        """Test all analysis types together."""
        request = AdvancedAnalyticsRequest(
            team_a=sample_team_a,
            team_b=sample_team_b,
            analysis_types=[
                AnalysisType.FEATURE_IMPORTANCE,
                AnalysisType.SHAP_VALUES,
                AnalysisType.SENSITIVITY_ANALYSIS
            ],
            model_type="gradient_boosting",
            num_simulations=1000,
            confidence_level=Decimal('0.95'),
            sensitivity_ranges={
                "service_ace_percentage": [Decimal('10.0'), Decimal('15.0')]
            }
        )
        
        result = await analytics_engine.run_advanced_analysis(request)
        
        assert result is not None
        assert result.team_a_analytics is not None
        assert result.shap_analysis is not None
        assert len(result.team_a_analytics.feature_importances) > 0
        assert result.head_to_head_insights is not None
    
    @pytest.mark.asyncio
    async def test_single_team_analysis(self, analytics_engine, sample_team_a):
        """Test analysis with only one team (opponent generated)."""
        request = AdvancedAnalyticsRequest(
            team_a=sample_team_a,
            team_b=None,
            analysis_types=[AnalysisType.FEATURE_IMPORTANCE],
            model_type="gradient_boosting",
            num_simulations=1000,
            confidence_level=Decimal('0.95'),
            sensitivity_ranges={}
        )
        
        result = await analytics_engine.run_advanced_analysis(request)
        
        assert result is not None
        assert result.team_a_analytics is not None
        assert result.team_b_analytics is None
        assert result.head_to_head_insights is None
    
    @pytest.mark.asyncio
    async def test_scenario_analysis(self, analytics_engine, sample_team_a, sample_team_b):
        """Test scenario analysis functionality."""
        scenarios = [
            {"service_ace_percentage": Decimal('15.0')},
            {"attack_kill_percentage": Decimal('50.0')},
            {"service_ace_percentage": Decimal('15.0'), "attack_kill_percentage": Decimal('50.0')}
        ]
        
        request = ScenarioAnalysisRequest(
            base_team=sample_team_a,
            opponent_team=sample_team_b,
            scenarios=scenarios,
            scenario_names=["Improved Serves", "Improved Attack", "Combined Improvement"],
            num_simulations_per_scenario=10
        )
        
        result = await analytics_engine.run_scenario_analysis(request)
        
        assert result is not None
        assert len(result.scenarios) == 3
        assert result.best_scenario is not None
        assert result.worst_scenario is not None
        assert result.most_realistic_scenario is not None
        assert len(result.implementation_recommendations) > 0
        
        # Check scenario results
        scenario = result.scenarios[0]
        assert scenario.scenario_name == "Improved Serves"
        assert scenario.predicted_win_rate is not None
        assert scenario.win_rate_change is not None
        assert len(scenario.modified_features) > 0
    
    def test_feature_extraction(self, analytics_engine, sample_team_a, sample_team_b):
        """Test feature extraction from team statistics."""
        features = analytics_engine._extract_features(sample_team_a, sample_team_b)
        
        assert len(features) > 0
        assert "team_a_service_ace_percentage" in features
        assert "team_b_service_ace_percentage" in features
        assert "diff_service_ace_percentage" in features
        
        # Check that difference is calculated correctly
        expected_diff = float(sample_team_a.service_ace_percentage) - float(sample_team_b.service_ace_percentage)
        assert features["diff_service_ace_percentage"] == expected_diff
    
    def test_statistical_noise_addition(self, analytics_engine, sample_team_a):
        """Test adding statistical noise to team stats."""
        noisy_team = analytics_engine._add_statistical_noise(sample_team_a, noise_level=0.1)
        
        assert noisy_team.name == sample_team_a.name
        
        # Stats should be different but within reasonable bounds
        original_ace = float(sample_team_a.service_ace_percentage)
        noisy_ace = float(noisy_team.service_ace_percentage)
        
        assert abs(noisy_ace - original_ace) <= original_ace * 0.3  # Should be within 30%
        assert 0 <= noisy_ace <= 100  # Should be within valid percentage bounds
    
    def test_random_opponent_generation(self, analytics_engine):
        """Test generation of random opponent teams."""
        opponent = analytics_engine._generate_random_opponent()
        
        assert opponent.name == "Random Opponent"
        assert 0 <= float(opponent.service_ace_percentage) <= 100
        assert 0 <= float(opponent.attack_kill_percentage) <= 100
        assert 0 <= float(opponent.dig_percentage) <= 100
    
    def test_feature_category_mapping(self, analytics_engine):
        """Test feature category mapping."""
        from src.bvsim.schemas.analytics import FeatureCategory
        
        category = analytics_engine._get_feature_category("team_a_service_ace_percentage")
        assert category == FeatureCategory.SERVE
        
        category = analytics_engine._get_feature_category("diff_attack_kill_percentage")
        assert category == FeatureCategory.ATTACK
        
        category = analytics_engine._get_feature_category("team_b_dig_percentage")
        assert category == FeatureCategory.DEFENSE
    
    def test_margin_of_error_calculation(self, analytics_engine):
        """Test margin of error calculation."""
        y = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
        margin = analytics_engine._calculate_margin_of_error(y, Decimal('0.95'))
        
        assert 0 <= margin <= 1
        assert isinstance(margin, float)
    
    @pytest.mark.asyncio
    async def test_different_model_types(self, analytics_engine, sample_team_a, sample_team_b):
        """Test different ML model types."""
        model_types = ["gradient_boosting", "random_forest", "logistic_regression"]
        
        for model_type in model_types:
            request = AdvancedAnalyticsRequest(
                team_a=sample_team_a,
                team_b=sample_team_b,
                analysis_types=[AnalysisType.FEATURE_IMPORTANCE],
                model_type=model_type,
                num_simulations=1000,
                confidence_level=Decimal('0.95'),
                sensitivity_ranges={}
            )
            
            result = await analytics_engine.run_advanced_analysis(request)
            
            assert result is not None
            assert result.team_a_analytics is not None
            assert len(result.team_a_analytics.feature_importances) > 0
    
    @pytest.mark.asyncio
    async def test_performance_with_large_simulations(self, analytics_engine, basic_analytics_request):
        """Test performance with larger number of simulations."""
        basic_analytics_request.num_simulations = 500
        
        result = await analytics_engine.run_advanced_analysis(basic_analytics_request)
        
        assert result is not None
        assert result.simulation_count >= 400  # Allow for some failure tolerance
        assert result.analysis_time_seconds > 0
        assert result.reliability_score >= 0.8  # Should be high with more simulations
    
    def test_team_profile_building(self, analytics_engine, sample_team_a):
        """Test building comprehensive team profiles."""
        # Mock analysis results
        mock_feature_importance = []
        mock_shap_analysis = type('MockSHAP', (), {
            'shap_values': []
        })()
        
        analysis_results = {
            'feature_importance': mock_feature_importance,
            'shap_analysis': mock_shap_analysis
        }
        
        profile = analytics_engine._build_team_profile(
            sample_team_a, analysis_results, 'team_a'
        )
        
        assert profile.team_name == sample_team_a.name
        assert profile.overall_rating is not None
        assert isinstance(profile.category_strengths, dict)
        assert isinstance(profile.top_improvement_areas, list)
        assert isinstance(profile.training_priorities, dict)


@pytest.mark.integration
class TestAdvancedAnalyticsIntegration:
    """Integration tests for advanced analytics with actual ML models."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis_pipeline(self, sample_team_a, sample_team_b):
        """Test complete end-to-end analytics pipeline."""
        engine = AdvancedAnalyticsEngine()
        
        request = AdvancedAnalyticsRequest(
            team_a=sample_team_a,
            team_b=sample_team_b,
            analysis_types=[
                AnalysisType.FEATURE_IMPORTANCE,
                AnalysisType.SHAP_VALUES
            ],
            model_type="gradient_boosting",
            num_simulations=100,
            confidence_level=Decimal('0.95'),
            sensitivity_ranges={}
        )
        
        result = await engine.run_advanced_analysis(request)
        
        # Validate complete response structure
        assert result.analysis_id is not None
        assert result.team_a_analytics is not None
        assert result.team_b_analytics is not None
        assert result.shap_analysis is not None
        assert result.head_to_head_insights is not None
        
        # Validate analytics quality
        assert result.convergence_achieved in [True, False]
        assert 0 <= float(result.reliability_score) <= 1
        assert 0 <= float(result.margin_of_error) <= 1
        assert float(result.statistical_power) > 0
        
        # Validate team profiles
        team_a_profile = result.team_a_analytics
        assert len(team_a_profile.feature_importances) > 0
        assert team_a_profile.overall_rating > 0
        assert len(team_a_profile.category_strengths) > 0
        
        # Validate SHAP analysis
        shap_analysis = result.shap_analysis
        assert len(shap_analysis.shap_values) > 0
        assert len(shap_analysis.global_feature_importance) > 0
        assert "accuracy" in shap_analysis.model_performance
        assert "auc" in shap_analysis.model_performance
