"""
Tests for advanced analytics API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from src.bvsim.main import app
from src.bvsim.schemas.team_statistics import TeamStatisticsBase


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_team_stats():
    """Sample team statistics for testing."""
    return {
        "name": "Test Team",
        "service_ace_percentage": 12.0,
        "service_error_percentage": 8.0,
        "serve_success_rate": 85.0,
        "perfect_pass_percentage": 35.0,
        "good_pass_percentage": 45.0,
        "poor_pass_percentage": 15.0,
        "reception_error_percentage": 5.0,
        "assist_percentage": 55.0,
        "ball_handling_error_percentage": 3.0,
        "attack_kill_percentage": 45.0,
        "attack_error_percentage": 15.0,
        "hitting_efficiency": 0.30,
        "first_ball_kill_percentage": 12.0,
        "dig_percentage": 35.0,
        "block_kill_percentage": 10.0,
        "controlled_block_percentage": 20.0,
        "blocking_error_percentage": 4.0
    }


@pytest.fixture
def opponent_team_stats():
    """Opponent team statistics for testing."""
    return {
        "name": "Opponent Team",
        "service_ace_percentage": 10.0,
        "service_error_percentage": 10.0,
        "serve_success_rate": 80.0,
        "perfect_pass_percentage": 30.0,
        "good_pass_percentage": 40.0,
        "poor_pass_percentage": 20.0,
        "reception_error_percentage": 10.0,
        "assist_percentage": 50.0,
        "ball_handling_error_percentage": 5.0,
        "attack_kill_percentage": 40.0,
        "attack_error_percentage": 20.0,
        "hitting_efficiency": 0.20,
        "first_ball_kill_percentage": 10.0,
        "dig_percentage": 30.0,
        "block_kill_percentage": 8.0,
        "controlled_block_percentage": 15.0,
        "blocking_error_percentage": 6.0
    }


class TestAdvancedAnalyticsAPI:
    """Test cases for advanced analytics API endpoints."""
    
    def test_advanced_analysis_endpoint(self, client, sample_team_stats, opponent_team_stats):
        """Test the main advanced analysis endpoint."""
        request_data = {
            "team_a": sample_team_stats,
            "team_b": opponent_team_stats,
            "analysis_types": ["feature_importance", "shap_values"],
            "model_type": "gradient_boosting",
            "num_simulations": 1000,
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "analysis_id" in data
        assert "team_a_analytics" in data
        assert "team_b_analytics" in data
        assert "shap_analysis" in data
        assert "simulation_count" in data
        assert "analysis_time_seconds" in data
        assert data["simulation_count"] > 0
        assert data["analysis_time_seconds"] > 0
    
    def test_advanced_analysis_async_endpoint(self, client, sample_team_stats):
        """Test the async advanced analysis endpoint."""
        request_data = {
            "team_a": sample_team_stats,
            "team_b": None,
            "analysis_types": ["feature_importance"],
            "model_type": "gradient_boosting",
            "num_simulations": 100,
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis-async", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "analysis_id" in data
        assert "status" in data
        assert data["status"] == "started"
        
        # Test status endpoint
        analysis_id = data["analysis_id"]
        status_response = client.get(f"/analytics/advanced-analysis/{analysis_id}")
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "status" in status_data
        assert status_data["status"] in ["running", "completed", "failed"]
    
    def test_feature_importance_endpoint(self, client, sample_team_stats):
        """Test the feature importance analysis endpoint."""
        params = {
            "team_a": sample_team_stats,
            "model_type": "gradient_boosting",
            "num_simulations": 1000
        }
        
        response = client.post("/analytics/feature-importance", json=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "feature_importance" in data
        assert "analysis_time" in data
        assert "simulation_count" in data
        assert len(data["feature_importance"]) > 0
        
        # Check feature importance structure
        feature = data["feature_importance"][0]
        assert "statistic_name" in feature
        assert "importance_score" in feature
        assert "rank" in feature
        assert "interpretation" in feature
    
    def test_shap_analysis_endpoint(self, client, sample_team_stats, opponent_team_stats):
        """Test the SHAP analysis endpoint."""
        params = {
            "team_a": sample_team_stats,
            "team_b": opponent_team_stats,
            "model_type": "gradient_boosting",
            "num_simulations": 30
        }
        
        response = client.post("/analytics/shap-analysis", json=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "shap_analysis" in data
        assert "analysis_time" in data
        assert "simulation_count" in data
        
        shap_analysis = data["shap_analysis"]
        assert "base_prediction" in shap_analysis
        assert "shap_values" in shap_analysis
        assert "global_feature_importance" in shap_analysis
        assert len(shap_analysis["shap_values"]) > 0
        
        # Check SHAP value structure
        shap_value = shap_analysis["shap_values"][0]
        assert "feature_name" in shap_value
        assert "shap_value" in shap_value
        assert "impact_direction" in shap_value
        assert shap_value["impact_direction"] in ["positive", "negative", "neutral"]
    
    def test_sensitivity_analysis_endpoint(self, client, sample_team_stats):
        """Test the sensitivity analysis endpoint."""
        params = {
            "team_a": sample_team_stats,
            "sensitivity_ranges": {
                "service_ace_percentage": [8.0, 12.0, 16.0],
                "attack_kill_percentage": [40.0, 45.0, 50.0]
            }
        }
        
        response = client.post("/analytics/sensitivity-analysis", json=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "team_name" in data
        assert "sensitivity_results" in data
        assert "analysis_time" in data
        assert data["team_name"] == sample_team_stats["name"]
    
    def test_scenario_analysis_endpoint(self, client, sample_team_stats, opponent_team_stats):
        """Test the scenario analysis endpoint."""
        request_data = {
            "base_team": sample_team_stats,
            "opponent_team": opponent_team_stats,
            "scenarios": [
                {"service_ace_percentage": 15.0},
                {"attack_kill_percentage": 50.0},
                {"service_ace_percentage": 15.0, "attack_kill_percentage": 50.0}
            ],
            "scenario_names": ["Better Serves", "Better Attack", "Combined"],
            "num_simulations_per_scenario": 10
        }
        
        response = client.post("/analytics/scenario-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "analysis_id" in data
        assert "base_team_name" in data
        assert "scenarios" in data
        assert "best_scenario" in data
        assert "worst_scenario" in data
        assert "most_realistic_scenario" in data
        assert len(data["scenarios"]) == 3
        
        # Check scenario structure
        scenario = data["scenarios"][0]
        assert "scenario_name" in scenario
        assert "predicted_win_rate" in scenario
        assert "win_rate_change" in scenario
        assert "modified_features" in scenario
    
    def test_team_profile_endpoint(self, client, sample_team_stats):
        """Test the team analytics profile endpoint."""
        params = {
            "team_name": "Test Team",
            "team_stats": sample_team_stats
        }
        
        response = client.post("/analytics/team-profile/Test%20Team", json=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "team_profile" in data
        assert "overall_rating" in data
        assert "analysis_time" in data
        
        profile = data["team_profile"]
        assert "team_name" in profile
        assert "overall_rating" in profile
        assert "feature_importances" in profile
        assert "category_strengths" in profile
    
    def test_invalid_team_data(self, client):
        """Test handling of invalid team data."""
        invalid_data = {
            "team_a": {
                "name": "Invalid Team",
                "service_ace_percentage": "invalid"  # Should be numeric
            },
            "analysis_types": ["feature_importance"],
            "model_type": "gradient_boosting",
            "num_simulations": 10,
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        incomplete_data = {
            "team_a": {
                "name": "Incomplete Team"
                # Missing required statistics
            },
            "analysis_types": ["feature_importance"],
            "model_type": "gradient_boosting",
            "num_simulations": 10,
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_analysis_type(self, client, sample_team_stats):
        """Test handling of invalid analysis types."""
        request_data = {
            "team_a": sample_team_stats,
            "analysis_types": ["invalid_analysis_type"],
            "model_type": "gradient_boosting",
            "num_simulations": 10,
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_unsupported_model_type(self, client, sample_team_stats):
        """Test handling of unsupported model types."""
        request_data = {
            "team_a": sample_team_stats,
            "analysis_types": ["feature_importance"],
            "model_type": "unsupported_model",
            "num_simulations": 10,
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis", json=request_data)
        
        # Should still work as it defaults to gradient_boosting
        assert response.status_code == 200
    
    def test_large_simulation_count(self, client, sample_team_stats):
        """Test handling of large simulation counts."""
        request_data = {
            "team_a": sample_team_stats,
            "analysis_types": ["feature_importance"],
            "model_type": "gradient_boosting",
            "num_simulations": 2000,  # Large number
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis", json=request_data)
        
        # Should work but might take longer
        assert response.status_code == 200
        data = response.json()
        assert data["simulation_count"] > 1000
    
    def test_nonexistent_analysis_status(self, client):
        """Test querying status of non-existent analysis."""
        fake_id = "non-existent-analysis-id"
        response = client.get(f"/analytics/advanced-analysis/{fake_id}")
        
        assert response.status_code == 404
    
    def test_minimal_analytics_request(self, client, sample_team_stats):
        """Test analytics with minimal required data."""
        request_data = {
            "team_a": sample_team_stats,
            "analysis_types": ["feature_importance"],
            "model_type": "gradient_boosting",
            "num_simulations": 20,
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["team_a_analytics"] is not None
        assert data["team_b_analytics"] is None  # No team B provided
        assert data["head_to_head_insights"] is None
    
    def test_different_confidence_levels(self, client, sample_team_stats):
        """Test different confidence levels."""
        confidence_levels = [0.90, 0.95, 0.99]
        
        for confidence in confidence_levels:
            request_data = {
                "team_a": sample_team_stats,
                "analysis_types": ["feature_importance"],
                "model_type": "gradient_boosting",
                "num_simulations": 30,
                "confidence_level": confidence,
                "sensitivity_ranges": {}
            }
            
            response = client.post("/analytics/advanced-analysis", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert float(data["confidence_level"]) == confidence
    
    def test_sensitivity_analysis_default_ranges(self, client, sample_team_stats):
        """Test sensitivity analysis with default ranges."""
        params = {
            "team_a": sample_team_stats
            # No sensitivity_ranges provided - should use defaults
        }
        
        response = client.post("/analytics/sensitivity-analysis", json=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "team_name" in data
        assert "sensitivity_results" in data
        assert data["team_name"] == sample_team_stats["name"]


@pytest.mark.integration
class TestAdvancedAnalyticsAPIIntegration:
    """Integration tests for analytics API with realistic scenarios."""
    
    def test_real_team_comparison_analysis(self, client):
        """Test analysis with realistic team data."""
        team_strong = {
            "name": "Strong Team",
            "service_ace_percentage": 15.0,
            "service_error_percentage": 5.0,
            "serve_success_rate": 90.0,
            "perfect_pass_percentage": 40.0,
            "good_pass_percentage": 50.0,
            "poor_pass_percentage": 8.0,
            "reception_error_percentage": 2.0,
            "assist_percentage": 60.0,
            "ball_handling_error_percentage": 2.0,
            "attack_kill_percentage": 50.0,
            "attack_error_percentage": 10.0,
            "hitting_efficiency": 0.40,
            "first_ball_kill_percentage": 15.0,
            "dig_percentage": 40.0,
            "block_kill_percentage": 12.0,
            "controlled_block_percentage": 25.0,
            "blocking_error_percentage": 3.0
        }
        
        team_weak = {
            "name": "Developing Team",
            "service_ace_percentage": 8.0,
            "service_error_percentage": 15.0,
            "serve_success_rate": 70.0,
            "perfect_pass_percentage": 25.0,
            "good_pass_percentage": 35.0,
            "poor_pass_percentage": 25.0,
            "reception_error_percentage": 15.0,
            "assist_percentage": 45.0,
            "ball_handling_error_percentage": 8.0,
            "attack_kill_percentage": 35.0,
            "attack_error_percentage": 25.0,
            "hitting_efficiency": 0.10,
            "first_ball_kill_percentage": 8.0,
            "dig_percentage": 25.0,
            "block_kill_percentage": 6.0,
            "controlled_block_percentage": 12.0,
            "blocking_error_percentage": 8.0
        }
        
        request_data = {
            "team_a": team_strong,
            "team_b": team_weak,
            "analysis_types": ["feature_importance", "shap_values"],
            "model_type": "gradient_boosting",
            "num_simulations": 100,
            "confidence_level": 0.95,
            "sensitivity_ranges": {}
        }
        
        response = client.post("/analytics/advanced-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Strong team should have higher overall rating
        strong_rating = float(data["team_a_analytics"]["overall_rating"])
        weak_rating = float(data["team_b_analytics"]["overall_rating"])
        
        assert strong_rating > weak_rating
        
        # Should have meaningful head-to-head insights
        assert data["head_to_head_insights"] is not None
        assert len(data["head_to_head_insights"]) > 0
    
    def test_progressive_improvement_scenarios(self, client):
        """Test scenario analysis for team improvement."""
        base_team = {
            "name": "Improving Team",
            "service_ace_percentage": 10.0,
            "service_error_percentage": 12.0,
            "serve_success_rate": 75.0,
            "perfect_pass_percentage": 30.0,
            "good_pass_percentage": 40.0,
            "poor_pass_percentage": 20.0,
            "reception_error_percentage": 10.0,
            "assist_percentage": 50.0,
            "ball_handling_error_percentage": 5.0,
            "attack_kill_percentage": 40.0,
            "attack_error_percentage": 20.0,
            "hitting_efficiency": 0.20,
            "first_ball_kill_percentage": 10.0,
            "dig_percentage": 30.0,
            "block_kill_percentage": 8.0,
            "controlled_block_percentage": 15.0,
            "blocking_error_percentage": 6.0
        }
        
        # Progressive improvement scenarios
        scenarios = [
            {"service_ace_percentage": 12.0},  # Small improvement
            {"service_ace_percentage": 15.0},  # Moderate improvement
            {"service_ace_percentage": 18.0},  # Large improvement
            {
                "service_ace_percentage": 15.0,
                "attack_kill_percentage": 45.0
            }  # Combined improvement
        ]
        
        request_data = {
            "base_team": base_team,
            "scenarios": scenarios,
            "scenario_names": [
                "Small Serve Improvement",
                "Moderate Serve Improvement", 
                "Large Serve Improvement",
                "Combined Improvement"
            ],
            "num_simulations_per_scenario": 50
        }
        
        response = client.post("/analytics/scenario-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        scenarios_data = data["scenarios"]
        
        # Win rates should generally increase with improvements
        win_rates = [float(s["predicted_win_rate"]) for s in scenarios_data]
        
        # Check that improvements generally lead to better outcomes
        assert win_rates[1] >= win_rates[0]  # Moderate >= Small
        assert win_rates[2] >= win_rates[1]  # Large >= Moderate
        
        # Combined improvement should be best or close to best
        combined_win_rate = win_rates[3]
        max_single_improvement = max(win_rates[:3])
        assert combined_win_rate >= max_single_improvement * 0.95
