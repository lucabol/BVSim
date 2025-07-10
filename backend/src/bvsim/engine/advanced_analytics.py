"""
Advanced analytics engine with SHAP values and sensitivity analysis.
Implements feature importance, SHAP explanations, and impact assessments.
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import logging
import uuid
import time
from datetime import datetime

# Analytics and ML imports
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
import shap

from ..schemas.analytics import (
    AdvancedAnalyticsRequest, AdvancedAnalyticsResponse, 
    TeamAnalyticsProfile, FeatureImportance, SHAPValue, 
    SHAPAnalysisResult, FeatureImpactAssessment,
    AnalysisType, FeatureCategory, ScenarioAnalysisRequest,
    ScenarioAnalysisResponse, ScenarioResult
)
from ..schemas.team_statistics import TeamStatisticsBase
from ..engine.match_simulator import MatchSimulator

logger = logging.getLogger(__name__)


class AdvancedAnalyticsEngine:
    """Advanced analytics engine for volleyball simulation analysis."""
    
    def __init__(self):
        self.match_simulator = MatchSimulator()
        self.feature_categories = {
            'service_ace_percentage': FeatureCategory.SERVE,
            'service_error_percentage': FeatureCategory.SERVE,
            'serve_success_rate': FeatureCategory.SERVE,
            'perfect_pass_percentage': FeatureCategory.RECEPTION,
            'good_pass_percentage': FeatureCategory.RECEPTION,
            'poor_pass_percentage': FeatureCategory.RECEPTION,
            'reception_error_percentage': FeatureCategory.RECEPTION,
            'assist_percentage': FeatureCategory.SETTING,
            'ball_handling_error_percentage': FeatureCategory.SETTING,
            'attack_kill_percentage': FeatureCategory.ATTACK,
            'attack_error_percentage': FeatureCategory.ATTACK,
            'hitting_efficiency': FeatureCategory.ATTACK,
            'first_ball_kill_percentage': FeatureCategory.ATTACK,
            'dig_percentage': FeatureCategory.DEFENSE,
            'block_kill_percentage': FeatureCategory.BLOCKING,
            'controlled_block_percentage': FeatureCategory.BLOCKING,
            'blocking_error_percentage': FeatureCategory.BLOCKING
        }
    
    async def run_advanced_analysis(self, request: AdvancedAnalyticsRequest) -> AdvancedAnalyticsResponse:
        """Run comprehensive advanced analytics analysis."""
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        logger.info(f"Starting advanced analytics analysis {analysis_id}")
        
        # Generate training data through simulation
        logger.info("Generating training data...")
        training_data = await self._generate_training_data(
            request.team_a, request.team_b, request.num_simulations
        )
        
        # Prepare features and targets
        X, y, feature_names = self._prepare_ml_data(training_data)
        
        # Run requested analyses
        results = {}
        
        if AnalysisType.FEATURE_IMPORTANCE in request.analysis_types:
            logger.info("Running feature importance analysis...")
            results['feature_importance'] = await self._analyze_feature_importance(
                X, y, feature_names, request.model_type
            )
        
        if AnalysisType.SHAP_VALUES in request.analysis_types:
            logger.info("Running SHAP analysis...")
            results['shap_analysis'] = await self._analyze_shap_values(
                X, y, feature_names, request.model_type
            )
        
        if AnalysisType.SENSITIVITY_ANALYSIS in request.analysis_types:
            logger.info("Running sensitivity analysis...")
            results['sensitivity_analysis'] = await self._analyze_sensitivity(
                request.team_a, request.team_b, request.sensitivity_ranges
            )
        
        # Build team profiles
        team_a_profile = self._build_team_profile(
            request.team_a, results, 'team_a'
        )
        
        team_b_profile = None
        if request.team_b:
            team_b_profile = self._build_team_profile(
                request.team_b, results, 'team_b'
            )
        
        # Calculate quality metrics
        convergence_achieved = len(training_data) >= request.num_simulations * 0.95
        margin_of_error = self._calculate_margin_of_error(y, request.confidence_level)
        reliability_score = min(1.0, len(training_data) / request.num_simulations)
        
        analysis_time = time.time() - start_time
        
        return AdvancedAnalyticsResponse(
            analysis_id=analysis_id,
            request=request,
            team_a_analytics=team_a_profile,
            team_b_analytics=team_b_profile,
            shap_analysis=results.get('shap_analysis'),
            head_to_head_insights=self._generate_head_to_head_insights(results) if request.team_b else None,
            simulation_count=len(training_data),
            analysis_time_seconds=analysis_time,
            statistical_power=Decimal('0.95'),  # Simplified
            confidence_level=request.confidence_level,
            convergence_achieved=convergence_achieved,
            margin_of_error=Decimal(str(margin_of_error)),
            reliability_score=Decimal(str(reliability_score)),
            created_at=datetime.now()
        )
    
    async def _generate_training_data(self, team_a: TeamStatisticsBase, 
                                    team_b: Optional[TeamStatisticsBase],
                                    num_simulations: int) -> List[Dict[str, Any]]:
        """Generate training data through Monte Carlo simulation."""
        training_data = []
        
        # Create variations of team statistics for training
        for _ in range(num_simulations):
            # Add noise to team statistics to create variation
            varied_team_a = self._add_statistical_noise(team_a)
            varied_team_b = self._add_statistical_noise(team_b) if team_b else self._generate_random_opponent()
            
            # Simulate match
            match_result = await self.match_simulator.simulate_match(
                varied_team_a, varied_team_b
            )
            
            # Extract features and outcome
            features = self._extract_features(varied_team_a, varied_team_b)
            outcome = 1 if match_result.winner == 'A' else 0
            
            training_data.append({
                'features': features,
                'outcome': outcome,
                'team_a_stats': varied_team_a,
                'team_b_stats': varied_team_b
            })
        
        return training_data
    
    def _add_statistical_noise(self, team: TeamStatisticsBase, noise_level: float = 0.1) -> TeamStatisticsBase:
        """Add realistic noise to team statistics for variation."""
        modified_team = team.model_copy()
        
        # Add Gaussian noise to numerical stats
        for field_name, field_value in team.model_dump().items():
            if field_name == 'name':
                continue
                
            if isinstance(field_value, (int, float, Decimal)):
                current_value = float(field_value)
                noise = np.random.normal(0, current_value * noise_level)
                new_value = max(0, min(100, current_value + noise))  # Keep within bounds
                setattr(modified_team, field_name, Decimal(str(new_value)))
        
        return modified_team
    
    def _generate_random_opponent(self) -> TeamStatisticsBase:
        """Generate a random opponent team for single-team analysis."""
        return TeamStatisticsBase(
            name="Random Opponent",
            service_ace_percentage=Decimal(str(np.random.uniform(5, 15))),
            service_error_percentage=Decimal(str(np.random.uniform(8, 20))),
            serve_success_rate=Decimal(str(np.random.uniform(70, 90))),
            perfect_pass_percentage=Decimal(str(np.random.uniform(25, 45))),
            good_pass_percentage=Decimal(str(np.random.uniform(35, 55))),
            poor_pass_percentage=Decimal(str(np.random.uniform(10, 25))),
            reception_error_percentage=Decimal(str(np.random.uniform(2, 8))),
            assist_percentage=Decimal(str(np.random.uniform(45, 65))),
            ball_handling_error_percentage=Decimal(str(np.random.uniform(1, 5))),
            attack_kill_percentage=Decimal(str(np.random.uniform(35, 55))),
            attack_error_percentage=Decimal(str(np.random.uniform(12, 25))),
            hitting_efficiency=Decimal(str(np.random.uniform(0.15, 0.35))),
            first_ball_kill_percentage=Decimal(str(np.random.uniform(8, 18))),
            dig_percentage=Decimal(str(np.random.uniform(25, 45))),
            block_kill_percentage=Decimal(str(np.random.uniform(5, 15))),
            controlled_block_percentage=Decimal(str(np.random.uniform(10, 25))),
            blocking_error_percentage=Decimal(str(np.random.uniform(2, 8)))
        )
    
    def _extract_features(self, team_a: TeamStatisticsBase, 
                         team_b: TeamStatisticsBase) -> Dict[str, float]:
        """Extract features for machine learning."""
        features = {}
        
        # Team A features (with prefix)
        for field_name, field_value in team_a.model_dump().items():
            if field_name != 'name':
                features[f'team_a_{field_name}'] = float(field_value)
        
        # Team B features (with prefix)
        for field_name, field_value in team_b.model_dump().items():
            if field_name != 'name':
                features[f'team_b_{field_name}'] = float(field_value)
        
        # Derived features (differences)
        for field_name in team_a.model_dump().keys():
            if field_name != 'name':
                diff = float(getattr(team_a, field_name)) - float(getattr(team_b, field_name))
                features[f'diff_{field_name}'] = diff
        
        return features
    
    def _prepare_ml_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare data for machine learning."""
        # Extract features and outcomes
        feature_dicts = [data['features'] for data in training_data]
        outcomes = [data['outcome'] for data in training_data]
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(feature_dicts)
        feature_names = list(df.columns)
        
        # Convert to numpy arrays
        X = df.values
        y = np.array(outcomes)
        
        return X, y, feature_names
    
    async def _analyze_feature_importance(self, X: np.ndarray, y: np.ndarray, 
                                        feature_names: List[str], 
                                        model_type: str) -> List[FeatureImportance]:
        """Analyze feature importance using various methods."""
        
        # Select model based on type
        if model_type == "gradient_boosting":
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        elif model_type == "random_forest":
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == "logistic_regression":
            model = LogisticRegression(random_state=42, max_iter=1000)
            X = StandardScaler().fit_transform(X)  # Scale for logistic regression
        else:
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        # Train model
        model.fit(X, y)
        
        # Get feature importances
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            # For logistic regression, use absolute coefficients
            importances = np.abs(model.coef_[0])
        
        # Create feature importance objects
        feature_importances = []
        for i, (name, importance) in enumerate(zip(feature_names, importances)):
            # Determine category
            category = self._get_feature_category(name)
            
            # Calculate interpretation
            interpretation = self._interpret_feature_importance(name, importance, category)
            
            feature_importances.append(FeatureImportance(
                statistic_name=name,
                feature_category=category,
                importance_score=Decimal(str(importance)),
                marginal_impact=Decimal(str(importance * 0.1)),  # Simplified
                rank=i + 1,
                interpretation=interpretation
            ))
        
        # Sort by importance
        feature_importances.sort(key=lambda x: x.importance_score, reverse=True)
        
        # Update ranks
        for i, fi in enumerate(feature_importances):
            fi.rank = i + 1
        
        return feature_importances[:20]  # Return top 20
    
    async def _analyze_shap_values(self, X: np.ndarray, y: np.ndarray, 
                                 feature_names: List[str], 
                                 model_type: str) -> SHAPAnalysisResult:
        """Analyze SHAP values for feature explanations."""
        
        # Train model
        if model_type == "gradient_boosting":
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        else:
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        model.fit(X, y)
        
        # Create SHAP explainer
        explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values for a subset (for performance)
        sample_size = min(100, len(X))
        sample_indices = np.random.choice(len(X), sample_size, replace=False)
        X_sample = X[sample_indices]
        
        shap_values = explainer.shap_values(X_sample)
        
        # Handle multi-class output (take class 1 for binary classification)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Calculate base value
        base_value = explainer.expected_value
        if isinstance(base_value, np.ndarray):
            base_value = base_value[1]
        
        # Create SHAP value objects
        shap_results = []
        for i, feature_name in enumerate(feature_names):
            avg_shap = np.mean(shap_values[:, i])
            avg_feature_value = np.mean(X_sample[:, i])
            
            category = self._get_feature_category(feature_name)
            impact_direction = "positive" if avg_shap > 0 else "negative" if avg_shap < 0 else "neutral"
            
            shap_results.append(SHAPValue(
                feature_name=feature_name,
                shap_value=Decimal(str(avg_shap)),
                base_value=Decimal(str(base_value)),
                feature_value=Decimal(str(avg_feature_value)),
                category=category,
                impact_direction=impact_direction,
                contribution_percentage=Decimal(str(abs(avg_shap) / np.sum(np.abs(shap_values.mean(axis=0))) * 100))
            ))
        
        # Calculate global feature importance from SHAP
        global_importance = {}
        for shap_val in shap_results:
            global_importance[shap_val.feature_name] = float(abs(shap_val.shap_value))
        
        return SHAPAnalysisResult(
            analysis_id=str(uuid.uuid4()),
            base_prediction=Decimal(str(base_value)),
            shap_values=shap_results,
            feature_interactions={},  # Placeholder for interactions
            global_feature_importance=global_importance,
            model_performance={
                "accuracy": accuracy_score(y, model.predict(X)),
                "auc": roc_auc_score(y, model.predict_proba(X)[:, 1])
            },
            analysis_time_seconds=0.0,  # Placeholder
            created_at=datetime.now()
        )
    
    async def _analyze_sensitivity(self, team_a: TeamStatisticsBase,
                                 team_b: Optional[TeamStatisticsBase],
                                 sensitivity_ranges: Dict[str, List[Decimal]]) -> Dict[str, Any]:
        """Perform sensitivity analysis on key features."""
        # Simplified sensitivity analysis
        results = {}
        
        base_team_b = team_b or self._generate_random_opponent()
        
        # Test each feature if ranges provided
        for feature_name, test_values in sensitivity_ranges.items():
            if hasattr(team_a, feature_name):
                sensitivity_results = []
                
                for test_value in test_values:
                    # Create modified team
                    modified_team = team_a.model_copy()
                    setattr(modified_team, feature_name, test_value)
                    
                    # Run quick simulation
                    match_result = await self.match_simulator.simulate_match(
                        modified_team, base_team_b
                    )
                    
                    win_rate = 1.0 if match_result.winner == 'A' else 0.0
                    sensitivity_results.append({
                        'test_value': float(test_value),
                        'win_rate': win_rate
                    })
                
                results[feature_name] = sensitivity_results
        
        return results
    
    def _build_team_profile(self, team: TeamStatisticsBase, 
                           analysis_results: Dict[str, Any], 
                           team_prefix: str) -> TeamAnalyticsProfile:
        """Build comprehensive team analytics profile."""
        
        # Extract relevant feature importances for this team
        team_features = []
        if 'feature_importance' in analysis_results:
            for fi in analysis_results['feature_importance']:
                if fi.statistic_name.startswith(team_prefix) or fi.statistic_name.startswith('diff_'):
                    team_features.append(fi)
        
        # Extract SHAP values for this team
        team_shap = []
        shap_summary = {}
        if 'shap_analysis' in analysis_results:
            for shap_val in analysis_results['shap_analysis'].shap_values:
                if shap_val.feature_name.startswith(team_prefix):
                    team_shap.append(shap_val)
                    shap_summary[shap_val.feature_name] = float(shap_val.shap_value)
        
        # Calculate category strengths
        category_strengths = {}
        for category in FeatureCategory:
            category_features = [fi for fi in team_features if fi.feature_category == category]
            if category_features:
                avg_importance = sum(float(fi.importance_score) for fi in category_features) / len(category_features)
                category_strengths[category] = Decimal(str(avg_importance))
            else:
                category_strengths[category] = Decimal('0.0')
        
        # Generate recommendations
        top_improvement_areas = []
        training_priorities = {}
        
        sorted_features = sorted(team_features, key=lambda x: x.importance_score, reverse=True)
        for fi in sorted_features[:5]:
            feature_clean_name = fi.statistic_name.replace(f'{team_prefix}_', '').replace('diff_', '')
            top_improvement_areas.append(feature_clean_name)
            
            if float(fi.importance_score) > 0.1:
                training_priorities[feature_clean_name] = "high"
            elif float(fi.importance_score) > 0.05:
                training_priorities[feature_clean_name] = "medium"
            else:
                training_priorities[feature_clean_name] = "low"
        
        # Calculate overall rating (simplified)
        overall_rating = min(100.0, sum(float(v) for v in category_strengths.values()) * 20)
        
        return TeamAnalyticsProfile(
            team_name=team.name,
            overall_rating=Decimal(str(overall_rating)),
            feature_importances=team_features[:10],
            shap_summary=shap_summary,
            shap_details=team_shap[:10],
            sensitivity_results=[],  # Placeholder
            impact_assessments=[],  # Placeholder
            category_strengths=category_strengths,
            top_improvement_areas=top_improvement_areas,
            training_priorities=training_priorities
        )
    
    def _get_feature_category(self, feature_name: str) -> FeatureCategory:
        """Get category for a feature name."""
        # Remove team prefix and diff prefix
        clean_name = feature_name.replace('team_a_', '').replace('team_b_', '').replace('diff_', '')
        
        return self.feature_categories.get(clean_name, FeatureCategory.SERVE)
    
    def _interpret_feature_importance(self, feature_name: str, importance: float, category: FeatureCategory) -> str:
        """Generate human-readable interpretation of feature importance."""
        clean_name = feature_name.replace('team_a_', '').replace('team_b_', '').replace('diff_', '')
        
        if importance > 0.1:
            level = "highly important"
        elif importance > 0.05:
            level = "moderately important"
        else:
            level = "less important"
        
        return f"{clean_name.replace('_', ' ').title()} is {level} for match outcomes in the {category.value} category."
    
    def _calculate_margin_of_error(self, y: np.ndarray, confidence_level: Decimal) -> float:
        """Calculate margin of error for the analysis."""
        # Simplified margin of error calculation
        n = len(y)
        p = np.mean(y)
        
        # Z-score for confidence level
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z = z_scores.get(float(confidence_level), 1.96)
        
        # Calculate margin of error
        margin = z * np.sqrt(p * (1 - p) / n)
        return margin
    
    def _generate_head_to_head_insights(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate head-to-head insights between teams."""
        insights = {
            "key_advantages_team_a": [],
            "key_advantages_team_b": [],
            "closest_matchups": [],
            "predicted_outcome": "close_match"
        }
        
        if 'feature_importance' in results:
            # Find features where teams differ significantly
            for fi in results['feature_importance'][:10]:
                if fi.statistic_name.startswith('diff_'):
                    feature_name = fi.statistic_name.replace('diff_', '')
                    if float(fi.importance_score) > 0.05:
                        insights["closest_matchups"].append(feature_name)
        
        return insights
    
    async def run_scenario_analysis(self, request: ScenarioAnalysisRequest) -> ScenarioAnalysisResponse:
        """Run scenario analysis to test different team configurations."""
        analysis_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Baseline simulation
        baseline_opponent = request.opponent_team or self._generate_random_opponent()
        baseline_result = await self.match_simulator.simulate_match(
            request.base_team, baseline_opponent
        )
        baseline_win_rate = 1.0 if baseline_result.winner == 'A' else 0.0
        
        scenario_results = []
        
        for i, (scenario_name, scenario_config) in enumerate(zip(request.scenario_names, request.scenarios)):
            # Create modified team for scenario
            modified_team = request.base_team.model_copy()
            modified_features = {}
            
            for feature_name, new_value in scenario_config.items():
                if hasattr(modified_team, feature_name):
                    setattr(modified_team, feature_name, new_value)
                    modified_features[feature_name] = new_value
            
            # Run simulations for this scenario
            wins = 0
            for _ in range(request.num_simulations_per_scenario):
                result = await self.match_simulator.simulate_match(
                    modified_team, baseline_opponent
                )
                if result.winner == 'A':
                    wins += 1
            
            scenario_win_rate = wins / request.num_simulations_per_scenario
            win_rate_change = scenario_win_rate - baseline_win_rate
            
            scenario_results.append(ScenarioResult(
                scenario_name=scenario_name,
                modified_features=modified_features,
                predicted_win_rate=Decimal(str(scenario_win_rate)),
                win_rate_change=Decimal(str(win_rate_change)),
                confidence_interval={
                    "lower": Decimal(str(max(0, scenario_win_rate - 0.05))),
                    "upper": Decimal(str(min(1, scenario_win_rate + 0.05)))
                },
                key_improvements=list(modified_features.keys()),
                risk_factors=[],
                cost_benefit_ratio=Decimal(str(win_rate_change / len(modified_features))) if modified_features else Decimal('0')
            ))
        
        # Find best and worst scenarios
        best_scenario = max(scenario_results, key=lambda x: x.predicted_win_rate).scenario_name
        worst_scenario = min(scenario_results, key=lambda x: x.predicted_win_rate).scenario_name
        
        # Most realistic scenario (smallest number of changes)
        most_realistic = min(scenario_results, key=lambda x: len(x.modified_features)).scenario_name
        
        return ScenarioAnalysisResponse(
            analysis_id=analysis_id,
            base_team_name=request.base_team.name,
            scenarios=scenario_results,
            best_scenario=best_scenario,
            worst_scenario=worst_scenario,
            most_realistic_scenario=most_realistic,
            implementation_recommendations=[
                f"Focus on improving {best_scenario} scenario features",
                "Gradual implementation recommended for best results",
                "Monitor progress with regular performance testing"
            ],
            roi_analysis={
                "best_case_improvement": max(float(s.win_rate_change) for s in scenario_results),
                "average_improvement": sum(float(s.win_rate_change) for s in scenario_results) / len(scenario_results),
                "implementation_complexity": sum(len(s.modified_features) for s in scenario_results) / len(scenario_results)
            },
            created_at=datetime.now()
        )
