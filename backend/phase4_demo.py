"""
Demo script for Phase 4: Advanced Analytics Module
Demonstrates SHAP analysis, feature importance, and scenario analysis capabilities.
"""

import asyncio
import json
import time
from decimal import Decimal
from typing import Dict, Any

from src.bvsim.engine.advanced_analytics import AdvancedAnalyticsEngine
from src.bvsim.schemas.analytics import (
    AdvancedAnalyticsRequest, AnalysisType, ScenarioAnalysisRequest
)
from src.bvsim.schemas.team_statistics import TeamStatisticsBase


def create_sample_teams():
    """Create sample teams with realistic statistics."""
    
    elite_team = TeamStatisticsBase(
        name="Elite Professional Team",
        service_ace_percentage=Decimal('15.0'),
        service_error_percentage=Decimal('6.0'),
        serve_success_rate=Decimal('89.0'),
        perfect_pass_percentage=Decimal('42.0'),
        good_pass_percentage=Decimal('48.0'),
        poor_pass_percentage=Decimal('8.0'),
        reception_error_percentage=Decimal('2.0'),
        assist_percentage=Decimal('62.0'),
        ball_handling_error_percentage=Decimal('2.5'),
        attack_kill_percentage=Decimal('52.0'),
        attack_error_percentage=Decimal('12.0'),
        hitting_efficiency=Decimal('0.40'),
        first_ball_kill_percentage=Decimal('15.0'),
        dig_percentage=Decimal('38.0'),
        block_kill_percentage=Decimal('12.0'),
        controlled_block_percentage=Decimal('25.0'),
        blocking_error_percentage=Decimal('3.0')
    )
    
    developing_team = TeamStatisticsBase(
        name="Developing Team",
        service_ace_percentage=Decimal('8.0'),
        service_error_percentage=Decimal('14.0'),
        serve_success_rate=Decimal('72.0'),
        perfect_pass_percentage=Decimal('28.0'),
        good_pass_percentage=Decimal('38.0'),
        poor_pass_percentage=Decimal('22.0'),
        reception_error_percentage=Decimal('12.0'),
        assist_percentage=Decimal('48.0'),
        ball_handling_error_percentage=Decimal('7.0'),
        attack_kill_percentage=Decimal('38.0'),
        attack_error_percentage=Decimal('22.0'),
        hitting_efficiency=Decimal('0.16'),
        first_ball_kill_percentage=Decimal('9.0'),
        dig_percentage=Decimal('28.0'),
        block_kill_percentage=Decimal('6.0'),
        controlled_block_percentage=Decimal('14.0'),
        blocking_error_percentage=Decimal('8.0')
    )
    
    return elite_team, developing_team


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


async def demo_feature_importance(engine: AdvancedAnalyticsEngine, elite_team: TeamStatisticsBase, developing_team: TeamStatisticsBase):
    """Demonstrate feature importance analysis."""
    print_section("FEATURE IMPORTANCE ANALYSIS")
    
    request = AdvancedAnalyticsRequest(
        team_a=elite_team,
        team_b=developing_team,
        analysis_types=[AnalysisType.FEATURE_IMPORTANCE],
        model_type="gradient_boosting",
        num_simulations=2000,
        confidence_level=Decimal('0.95'),
        sensitivity_ranges={}
    )
    
    print("Running feature importance analysis...")
    start_time = time.time()
    result = await engine.run_advanced_analysis(request)
    analysis_time = time.time() - start_time
    
    print(f"Analysis completed in {analysis_time:.2f} seconds")
    print(f"Simulations run: {result.simulation_count}")
    print(f"Reliability score: {result.reliability_score}")
    
    print_subsection("Top 10 Most Important Features")
    for i, feature in enumerate(result.team_a_analytics.feature_importances[:10], 1):
        print(f"{i:2d}. {feature.statistic_name:30s} | Score: {feature.importance_score:6.4f} | {feature.feature_category.value.title()}")
        print(f"    Interpretation: {feature.interpretation}")
    
    return result


async def demo_shap_analysis(engine: AdvancedAnalyticsEngine, elite_team: TeamStatisticsBase, developing_team: TeamStatisticsBase):
    """Demonstrate SHAP value analysis."""
    print_section("SHAP VALUE ANALYSIS")
    
    request = AdvancedAnalyticsRequest(
        team_a=elite_team,
        team_b=developing_team,
        analysis_types=[AnalysisType.SHAP_VALUES],
        model_type="gradient_boosting",
        num_simulations=1500,
        confidence_level=Decimal('0.95'),
        sensitivity_ranges={}
    )
    
    print("Running SHAP analysis for interpretable ML explanations...")
    start_time = time.time()
    result = await engine.run_advanced_analysis(request)
    analysis_time = time.time() - start_time
    
    print(f"Analysis completed in {analysis_time:.2f} seconds")
    
    shap_analysis = result.shap_analysis
    if shap_analysis:
        print(f"Base prediction: {shap_analysis.base_prediction}")
        print(f"Model accuracy: {shap_analysis.model_performance.get('accuracy', 0):.3f}")
        print(f"Model AUC: {shap_analysis.model_performance.get('auc', 0):.3f}")
        
        print_subsection("Top 10 SHAP Value Contributors")
        sorted_shap = sorted(shap_analysis.shap_values, key=lambda x: abs(x.shap_value), reverse=True)
        
        for i, shap_val in enumerate(sorted_shap[:10], 1):
            direction_symbol = "+" if shap_val.impact_direction == "positive" else "-" if shap_val.impact_direction == "negative" else "="
            print(f"{i:2d}. {shap_val.feature_name:30s} | SHAP: {direction_symbol}{abs(shap_val.shap_value):6.4f} | Contribution: {shap_val.contribution_percentage:5.1f}%")
    else:
        print("SHAP analysis not available in this result.")
    
    return result


async def demo_scenario_analysis(engine: AdvancedAnalyticsEngine, developing_team: TeamStatisticsBase):
    """Demonstrate scenario analysis for team improvement."""
    print_section("SCENARIO ANALYSIS - TEAM IMPROVEMENT PLANNING")
    
    # Define improvement scenarios
    scenarios = [
        {"service_ace_percentage": Decimal('12.0')},  # Improve serves
        {"attack_kill_percentage": Decimal('45.0')},  # Improve attack
        {"dig_percentage": Decimal('35.0')},  # Improve defense
        {
            "service_ace_percentage": Decimal('12.0'),
            "attack_kill_percentage": Decimal('45.0')
        },  # Combined improvement
        {
            "service_ace_percentage": Decimal('12.0'),
            "attack_kill_percentage": Decimal('45.0'),
            "dig_percentage": Decimal('35.0')
        }  # Comprehensive improvement
    ]
    
    scenario_names = [
        "Improved Serving",
        "Improved Attack",
        "Improved Defense", 
        "Serve + Attack",
        "Comprehensive Improvement"
    ]
    
    request = ScenarioAnalysisRequest(
        base_team=developing_team,
        opponent_team=None,  # Will generate random opponents
        scenarios=scenarios,
        scenario_names=scenario_names,
        num_simulations_per_scenario=800
    )
    
    print("Running scenario analysis for team improvement strategies...")
    start_time = time.time()
    result = await engine.run_scenario_analysis(request)
    analysis_time = time.time() - start_time
    
    print(f"Analysis completed in {analysis_time:.2f} seconds")
    print(f"Best scenario: {result.best_scenario}")
    print(f"Most realistic scenario: {result.most_realistic_scenario}")
    
    print_subsection("Scenario Results")
    for scenario in result.scenarios:
        change_pct = float(scenario.win_rate_change) * 100
        change_symbol = "+" if change_pct >= 0 else ""
        print(f"• {scenario.scenario_name:25s} | Win Rate: {float(scenario.predicted_win_rate):5.1%} | Change: {change_symbol}{change_pct:5.1f}%")
        print(f"  Modified features: {', '.join(scenario.modified_features)}")
    
    print_subsection("Implementation Recommendations")
    for i, rec in enumerate(result.implementation_recommendations, 1):
        print(f"{i}. {rec}")
    
    print_subsection("ROI Analysis")
    roi = result.roi_analysis
    print(f"Best case improvement: +{roi['best_case_improvement']*100:.1f}% win rate")
    print(f"Average improvement: +{roi['average_improvement']*100:.1f}% win rate")
    print(f"Implementation complexity: {roi['implementation_complexity']:.1f} features per scenario")
    
    return result


async def demo_team_profile(engine: AdvancedAnalyticsEngine, developing_team: TeamStatisticsBase):
    """Demonstrate comprehensive team analytics profile."""
    print_section("TEAM ANALYTICS PROFILE")
    
    request = AdvancedAnalyticsRequest(
        team_a=developing_team,
        team_b=None,
        analysis_types=[AnalysisType.FEATURE_IMPORTANCE, AnalysisType.SHAP_VALUES],
        model_type="gradient_boosting",
        num_simulations=1500,
        confidence_level=Decimal('0.95'),
        sensitivity_ranges={}
    )
    
    print(f"Generating comprehensive analytics profile for {developing_team.name}...")
    result = await engine.run_advanced_analysis(request)
    
    profile = result.team_a_analytics
    print(f"Overall Rating: {profile.overall_rating}/100")
    
    print_subsection("Category Strengths")
    from src.bvsim.schemas.analytics import FeatureCategory
    for category, strength in profile.category_strengths.items():
        category_name = category.value.replace('_', ' ').title()
        strength_level = "Strong" if float(strength) > 0.15 else "Moderate" if float(strength) > 0.08 else "Needs Work"
        print(f"• {category_name:12s}: {float(strength):5.3f} ({strength_level})")
    
    print_subsection("Top Improvement Areas")
    for i, area in enumerate(profile.top_improvement_areas[:5], 1):
        priority = profile.training_priorities.get(area, "medium")
        print(f"{i}. {area.replace('_', ' ').title()} (Priority: {priority.title()})")
    
    return result


async def main():
    """Run the complete Phase 4 demonstration."""
    print("🏐 Beach Volleyball Simulator - Phase 4 Advanced Analytics Demo")
    print("=" * 60)
    print("Demonstrating SHAP analysis, feature importance, and scenario analysis")
    
    # Initialize engine and teams
    engine = AdvancedAnalyticsEngine()
    elite_team, developing_team = create_sample_teams()
    
    print(f"\nTeams for analysis:")
    print(f"• Elite Team: {elite_team.name}")
    print(f"• Developing Team: {developing_team.name}")
    
    # Run demonstrations
    try:
        # Feature importance analysis
        feature_result = await demo_feature_importance(engine, elite_team, developing_team)
        
        # SHAP analysis
        shap_result = await demo_shap_analysis(engine, elite_team, developing_team)
        
        # Scenario analysis
        scenario_result = await demo_scenario_analysis(engine, developing_team)
        
        # Team profile
        profile_result = await demo_team_profile(engine, developing_team)
        
        print_section("DEMONSTRATION COMPLETE")
        print("✅ Feature Importance Analysis: Shows which stats matter most for winning")
        print("✅ SHAP Value Analysis: Explains how each feature contributes to predictions")
        print("✅ Scenario Analysis: Tests team improvement strategies")
        print("✅ Team Analytics Profile: Comprehensive team assessment")
        print("\nPhase 4 Advanced Analytics Module is fully functional!")
        
        # Save sample results
        demo_results = {
            "feature_importance_sample": [
                {
                    "name": fi.statistic_name,
                    "score": float(fi.importance_score),
                    "category": fi.feature_category.value
                }
                for fi in feature_result.team_a_analytics.feature_importances[:5]
            ],
            "scenario_analysis_sample": [
                {
                    "name": scenario.scenario_name,
                    "win_rate": float(scenario.predicted_win_rate),
                    "change": float(scenario.win_rate_change)
                }
                for scenario in scenario_result.scenarios
            ]
        }
        
        with open("phase4_demo_results.json", "w") as f:
            json.dump(demo_results, f, indent=2)
        
        print(f"\n📊 Sample results saved to: phase4_demo_results.json")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
