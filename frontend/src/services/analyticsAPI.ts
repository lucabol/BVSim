/**
 * API service for Beach Volleyball Simulator Analytics
 * Handles communication with the FastAPI backend
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import {
  AdvancedAnalyticsRequest,
  AdvancedAnalyticsResponse,
  AnalysisStatus,
  ScenarioAnalysisResponse,
  TeamStatistics,
  FeatureImportance,
  SHAPAnalysisResult,
} from '../types/analytics';

class AnalyticsAPIService {
  private api: AxiosInstance;

  constructor() {
    const baseURL = typeof window !== 'undefined' 
      ? window.__VITE_API_BASE_URL__ || 'http://localhost:8000'
      : 'http://localhost:8000';

    this.api = axios.create({
      baseURL,
      timeout: 300000, // 5 minutes for long-running analytics
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for debugging
    this.api.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error: AxiosError) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Run comprehensive advanced analytics analysis
   */
  async runAdvancedAnalysis(request: AdvancedAnalyticsRequest): Promise<AdvancedAnalyticsResponse> {
    const response = await this.api.post<AdvancedAnalyticsResponse>(
      '/analytics/advanced-analysis',
      request
    );
    return response.data;
  }

  /**
   * Start advanced analytics analysis in the background
   */
  async runAdvancedAnalysisAsync(request: AdvancedAnalyticsRequest): Promise<{ analysis_id: string; status: string }> {
    const response = await this.api.post<{ analysis_id: string; status: string }>(
      '/analytics/advanced-analysis-async',
      request
    );
    return response.data;
  }

  /**
   * Get the status of a background analysis
   */
  async getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
    const response = await this.api.get<AnalysisStatus>(
      `/analytics/advanced-analysis/${analysisId}`
    );
    return response.data;
  }

  /**
   * Run scenario analysis for strategic planning
   */
  async runScenarioAnalysis(request: {
    base_team: TeamStatistics;
    opponent_team?: TeamStatistics;
    scenarios: Record<string, number>[];
    scenario_names: string[];
    num_simulations_per_scenario: number;
  }): Promise<ScenarioAnalysisResponse> {
    const response = await this.api.post<ScenarioAnalysisResponse>(
      '/analytics/scenario-analysis',
      request
    );
    return response.data;
  }

  /**
   * Get feature importance analysis
   */
  async getFeatureImportance(
    teamA: TeamStatistics,
    teamB?: TeamStatistics,
    modelType: string = 'gradient_boosting',
    numSimulations: number = 1000
  ): Promise<{ feature_importance: FeatureImportance[]; analysis_time: number; simulation_count: number }> {
    const response = await this.api.post(
      '/analytics/feature-importance',
      {
        team_a: teamA,
        team_b: teamB,
        model_type: modelType,
        num_simulations: numSimulations,
      }
    );
    return response.data;
  }

  /**
   * Get SHAP analysis for interpretable ML
   */
  async getSHAPAnalysis(
    teamA: TeamStatistics,
    teamB?: TeamStatistics,
    modelType: string = 'gradient_boosting',
    numSimulations: number = 1000
  ): Promise<{ shap_analysis: SHAPAnalysisResult; analysis_time: number; simulation_count: number }> {
    const response = await this.api.post(
      '/analytics/shap-analysis',
      {
        team_a: teamA,
        team_b: teamB,
        model_type: modelType,
        num_simulations: numSimulations,
      }
    );
    return response.data;
  }

  /**
   * Get sensitivity analysis
   */
  async getSensitivityAnalysis(
    teamA: TeamStatistics,
    teamB?: TeamStatistics,
    sensitivityRanges?: Record<string, number[]>
  ): Promise<{ team_name: string; sensitivity_results: any[]; analysis_time: number }> {
    const response = await this.api.post(
      '/analytics/sensitivity-analysis',
      {
        team_a: teamA,
        team_b: teamB,
        sensitivity_ranges: sensitivityRanges,
      }
    );
    return response.data;
  }

  /**
   * Get team analytics profile
   */
  async getTeamProfile(
    teamName: string,
    teamStats: TeamStatistics,
    comparisonTeam?: TeamStatistics
  ): Promise<{
    team_profile: any;
    overall_rating: number;
    analysis_time: number;
  }> {
    const response = await this.api.post(
      `/analytics/team-profile/${encodeURIComponent(teamName)}`,
      {
        team_name: teamName,
        team_stats: teamStats,
        comparison_team: comparisonTeam,
      }
    );
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.api.get('/health');
    return response.data;
  }

  /**
   * Get API info
   */
  async getAPIInfo(): Promise<any> {
    const response = await this.api.get('/api/info');
    return response.data;
  }
}

// Export singleton instance
export const analyticsAPI = new AnalyticsAPIService();
export default analyticsAPI;
