/**
 * Custom hooks for analytics operations
 */

import { useCallback } from 'react';
import { useAnalyticsStore } from '../stores/analyticsStore';
import analyticsAPI from '../services/analyticsAPI';
import {
  AdvancedAnalyticsRequest,
  TeamStatistics,
  AnalysisType,
} from '../types/analytics';

export const useAnalyticsOperations = () => {
  const {
    setCurrentAnalysis,
    setCurrentScenarioAnalysis,
    setFeatureImportance,
    setSHAPAnalysis,
    setLoading,
    setError,
    setAnalysisProgress,
    updateBackgroundAnalysis,
    teamA,
    teamB,
  } = useAnalyticsStore();

  const runFullAnalysis = useCallback(async (
    customTeamA?: TeamStatistics,
    customTeamB?: TeamStatistics,
    analysisTypes: AnalysisType[] = ['feature_importance', 'shap_values'],
    numSimulations: number = 2000
  ) => {
    const analysisTeamA = customTeamA || teamA;
    if (!analysisTeamA) {
      setError('Team A is required for analysis');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setAnalysisProgress(10);

      const request: AdvancedAnalyticsRequest = {
        team_a: analysisTeamA,
        team_b: customTeamB || teamB || undefined,
        analysis_types: analysisTypes,
        model_type: 'gradient_boosting',
        num_simulations: numSimulations,
        confidence_level: 0.95,
        sensitivity_ranges: {},
      };

      setAnalysisProgress(30);
      const result = await analyticsAPI.runAdvancedAnalysis(request);
      setAnalysisProgress(90);
      
      setCurrentAnalysis(result);
      setAnalysisProgress(100);
      
      return result;
    } catch (error) {
      console.error('Full analysis failed:', error);
      setError(error instanceof Error ? error.message : 'Analysis failed');
      setAnalysisProgress(0);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [teamA, teamB, setCurrentAnalysis, setLoading, setError, setAnalysisProgress]);

  const runBackgroundAnalysis = useCallback(async (
    customTeamA?: TeamStatistics,
    customTeamB?: TeamStatistics,
    analysisTypes: AnalysisType[] = ['feature_importance', 'shap_values', 'sensitivity_analysis'],
    numSimulations: number = 5000
  ) => {
    const analysisTeamA = customTeamA || teamA;
    if (!analysisTeamA) {
      setError('Team A is required for analysis');
      return null;
    }

    try {
      setLoading(true);
      setError(null);

      const request: AdvancedAnalyticsRequest = {
        team_a: analysisTeamA,
        team_b: customTeamB || teamB || undefined,
        analysis_types: analysisTypes,
        model_type: 'gradient_boosting',
        num_simulations: numSimulations,
        confidence_level: 0.95,
        sensitivity_ranges: {
          service_ace_percentage: [8, 12, 16, 20],
          attack_kill_percentage: [35, 40, 45, 50],
          dig_percentage: [25, 30, 35, 40],
        },
      };

      const { analysis_id } = await analyticsAPI.runAdvancedAnalysisAsync(request);
      
      updateBackgroundAnalysis(analysis_id, {
        analysis_id,
        status: 'running',
        progress: 0,
      });

      // Poll for status updates
      const pollStatus = async () => {
        try {
          const status = await analyticsAPI.getAnalysisStatus(analysis_id);
          updateBackgroundAnalysis(analysis_id, status);
          
          if (status.status === 'completed' && status.results) {
            setCurrentAnalysis(status.results);
            return status.results;
          } else if (status.status === 'failed') {
            setError(`Background analysis failed: ${status.error || 'Unknown error'}`);
            return null;
          } else {
            // Continue polling
            setTimeout(pollStatus, 5000);
          }
        } catch (error) {
          console.error('Status polling failed:', error);
          setError('Failed to check analysis status');
        }
      };

      setTimeout(pollStatus, 2000);
      return analysis_id;
    } catch (error) {
      console.error('Background analysis failed:', error);
      setError(error instanceof Error ? error.message : 'Background analysis failed');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [teamA, teamB, updateBackgroundAnalysis, setCurrentAnalysis, setLoading, setError]);

  const runQuickFeatureAnalysis = useCallback(async (
    customTeamA?: TeamStatistics,
    customTeamB?: TeamStatistics
  ) => {
    const analysisTeamA = customTeamA || teamA;
    if (!analysisTeamA) {
      setError('Team A is required for feature analysis');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await analyticsAPI.getFeatureImportance(
        analysisTeamA,
        customTeamB || teamB || undefined,
        'gradient_boosting',
        1500
      );

      setFeatureImportance(result.feature_importance);
      return result;
    } catch (error) {
      console.error('Feature analysis failed:', error);
      setError(error instanceof Error ? error.message : 'Feature analysis failed');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [teamA, teamB, setFeatureImportance, setLoading, setError]);

  const runQuickSHAPAnalysis = useCallback(async (
    customTeamA?: TeamStatistics,
    customTeamB?: TeamStatistics
  ) => {
    const analysisTeamA = customTeamA || teamA;
    if (!analysisTeamA) {
      setError('Team A is required for SHAP analysis');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await analyticsAPI.getSHAPAnalysis(
        analysisTeamA,
        customTeamB || teamB || undefined,
        'gradient_boosting',
        1500
      );

      setSHAPAnalysis(result.shap_analysis);
      return result;
    } catch (error) {
      console.error('SHAP analysis failed:', error);
      setError(error instanceof Error ? error.message : 'SHAP analysis failed');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [teamA, teamB, setSHAPAnalysis, setLoading, setError]);

  const runScenarioAnalysis = useCallback(async (
    baseTeam: TeamStatistics,
    scenarios: { name: string; changes: Record<string, number> }[],
    opponentTeam?: TeamStatistics
  ) => {
    try {
      setLoading(true);
      setError(null);

      const result = await analyticsAPI.runScenarioAnalysis({
        base_team: baseTeam,
        opponent_team: opponentTeam,
        scenarios: scenarios.map(s => s.changes),
        scenario_names: scenarios.map(s => s.name),
        num_simulations_per_scenario: 1000,
      });

      setCurrentScenarioAnalysis(result);
      return result;
    } catch (error) {
      console.error('Scenario analysis failed:', error);
      setError(error instanceof Error ? error.message : 'Scenario analysis failed');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setCurrentScenarioAnalysis, setLoading, setError]);

  return {
    runFullAnalysis,
    runBackgroundAnalysis,
    runQuickFeatureAnalysis,
    runQuickSHAPAnalysis,
    runScenarioAnalysis,
  };
};

export const useAnalyticsData = () => {
  const {
    currentAnalysis,
    currentScenarioAnalysis,
    featureImportance,
    shapAnalysis,
    isLoading,
    error,
    analysisProgress,
  } = useAnalyticsStore();

  return {
    currentAnalysis,
    currentScenarioAnalysis,
    featureImportance,
    shapAnalysis,
    isLoading,
    error,
    analysisProgress,
    hasFeatureImportance: Boolean(featureImportance && featureImportance.length > 0),
    hasSHAPAnalysis: Boolean(shapAnalysis && shapAnalysis.shap_values.length > 0),
    hasCurrentAnalysis: Boolean(currentAnalysis),
    hasScenarioAnalysis: Boolean(currentScenarioAnalysis),
  };
};
