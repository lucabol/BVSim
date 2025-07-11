/**
 * TypeScript types for Beach Volleyball Simulator Analytics
 * Corresponds to the backend analytics schemas
 */

export interface PlayerStatistics {
  player_id: string;
  position: 'front' | 'back';
  serve_accuracy: number;
  serve_speed: number;
  reception_quality: number;
  setting_accuracy: number;
  attack_power: number;
  attack_accuracy: number;
  defense_skill: number;
  blocking_height: number;
  blocking_timing: number;
  fitness_level: number;
  experience_level: number;
  mental_toughness: number;
}

export interface TeamConfiguration {
  team_name: string;
  players: PlayerStatistics[];
  team_chemistry: number;
  coaching_quality: number;
  home_advantage: boolean;
  recent_form: number;
  opponent_scouting: number;
}

export interface TeamStatistics {
  name: string;
  service_ace_percentage: number;
  service_error_percentage: number;
  serve_success_rate: number;
  perfect_pass_percentage: number;
  good_pass_percentage: number;
  poor_pass_percentage: number;
  reception_error_percentage: number;
  assist_percentage: number;
  ball_handling_error_percentage: number;
  attack_kill_percentage: number;
  attack_error_percentage: number;
  hitting_efficiency: number;
  first_ball_kill_percentage: number;
  dig_percentage: number;
  block_kill_percentage: number;
  controlled_block_percentage: number;
  blocking_error_percentage: number;
}

export type FeatureCategory = 
  | 'serve'
  | 'reception'
  | 'setting'
  | 'attack'
  | 'defense'
  | 'blocking';

export type AnalysisType = 
  | 'feature_importance'
  | 'sensitivity_analysis'
  | 'shap_values'
  | 'correlation_analysis'
  | 'impact_assessment'
  | 'scenario_analysis';

export interface FeatureImportance {
  statistic_name: string;
  feature_category: FeatureCategory;
  importance_score: number;
  marginal_impact: number;
  rank: number;
  interpretation: string;
}

export interface SHAPValue {
  feature_name: string;
  shap_value: number;
  base_value: number;
  feature_value: number | string;
  category: FeatureCategory;
  impact_direction: 'positive' | 'negative' | 'neutral';
  contribution_percentage: number;
}

export interface SHAPAnalysisResult {
  analysis_id: string;
  base_prediction: number;
  shap_values: SHAPValue[];
  feature_interactions: Record<string, Record<string, number>>;
  global_feature_importance: Record<string, number>;
  model_performance: {
    accuracy: number;
    auc: number;
  };
  analysis_time_seconds: number;
  created_at: string;
}

export interface TeamAnalyticsProfile {
  team_name: string;
  overall_rating: number;
  feature_importances: FeatureImportance[];
  shap_summary: Record<string, number>;
  shap_details: SHAPValue[];
  sensitivity_results: any[];
  impact_assessments: any[];
  category_strengths: Record<FeatureCategory, number>;
  top_improvement_areas: string[];
  training_priorities: Record<string, 'high' | 'medium' | 'low'>;
}

export interface ScenarioResult {
  scenario_name: string;
  modified_features: Record<string, number>;
  predicted_win_rate: number;
  win_rate_change: number;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  key_improvements: string[];
  risk_factors: string[];
  cost_benefit_ratio: number;
}

export interface ScenarioAnalysisResponse {
  analysis_id: string;
  base_team_name: string;
  scenarios: ScenarioResult[];
  best_scenario: string;
  worst_scenario: string;
  most_realistic_scenario: string;
  implementation_recommendations: string[];
  roi_analysis: {
    best_case_improvement: number;
    average_improvement: number;
    implementation_complexity: number;
  };
  created_at: string;
}

export interface AdvancedAnalyticsRequest {
  team_a: TeamStatistics;
  team_b?: TeamStatistics;
  analysis_types: AnalysisType[];
  model_type: 'gradient_boosting' | 'random_forest' | 'logistic_regression';
  num_simulations: number;
  confidence_level: number;
  sensitivity_ranges: Record<string, number[]>;
}

export interface AdvancedAnalyticsResponse {
  analysis_id: string;
  request: AdvancedAnalyticsRequest;
  team_a_analytics?: TeamAnalyticsProfile;
  team_b_analytics?: TeamAnalyticsProfile;
  shap_analysis?: SHAPAnalysisResult;
  head_to_head_insights?: Record<string, any>;
  simulation_count: number;
  analysis_time_seconds: number;
  statistical_power: number;
  confidence_level: number;
  convergence_achieved: boolean;
  margin_of_error: number;
  reliability_score: number;
  created_at: string;
}

export interface AnalysisStatus {
  analysis_id: string;
  status: 'running' | 'completed' | 'failed';
  progress: number;
  results?: AdvancedAnalyticsResponse;
  error?: string;
  analysis_time?: number;
}

// Chart data interfaces
export interface ChartDataPoint {
  name: string;
  value: number;
  category?: string;
  color?: string;
}

export interface SHAPChartData {
  feature_name: string;
  shap_value: number;
  abs_shap_value: number;
  impact_direction: 'positive' | 'negative' | 'neutral';
  contribution_percentage: number;
}

export interface ScenarioComparisonData {
  scenario_name: string;
  win_rate: number;
  win_rate_change: number;
  complexity: number;
  roi: number;
}
