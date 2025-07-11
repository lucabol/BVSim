/**
 * Zustand store for analytics state management
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  TeamStatistics,
  AdvancedAnalyticsResponse,
  AnalysisStatus,
  ScenarioAnalysisResponse,
  FeatureImportance,
  SHAPAnalysisResult,
} from '../types/analytics';

interface AnalyticsState {
  // Current analysis data
  currentAnalysis: AdvancedAnalyticsResponse | null;
  currentScenarioAnalysis: ScenarioAnalysisResponse | null;
  
  // Team data
  teamA: TeamStatistics | null;
  teamB: TeamStatistics | null;
  
  // Analysis status
  isLoading: boolean;
  error: string | null;
  analysisProgress: number;
  
  // Background analysis tracking
  backgroundAnalyses: Record<string, AnalysisStatus>;
  
  // Quick analysis results
  featureImportance: FeatureImportance[] | null;
  shapAnalysis: SHAPAnalysisResult | null;
  
  // UI state
  selectedTab: 'overview' | 'features' | 'shap' | 'scenarios' | 'comparison';
  
  // Actions
  setTeamA: (team: TeamStatistics | null) => void;
  setTeamB: (team: TeamStatistics | null) => void;
  setCurrentAnalysis: (analysis: AdvancedAnalyticsResponse | null) => void;
  setCurrentScenarioAnalysis: (analysis: ScenarioAnalysisResponse | null) => void;
  setFeatureImportance: (features: FeatureImportance[] | null) => void;
  setSHAPAnalysis: (shap: SHAPAnalysisResult | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setAnalysisProgress: (progress: number) => void;
  updateBackgroundAnalysis: (id: string, status: AnalysisStatus) => void;
  setSelectedTab: (tab: 'overview' | 'features' | 'shap' | 'scenarios' | 'comparison') => void;
  clearAnalysis: () => void;
  reset: () => void;
}

const initialState = {
  currentAnalysis: null,
  currentScenarioAnalysis: null,
  teamA: null,
  teamB: null,
  isLoading: false,
  error: null,
  analysisProgress: 0,
  backgroundAnalyses: {},
  featureImportance: null,
  shapAnalysis: null,
  selectedTab: 'overview' as const,
};

export const useAnalyticsStore = create<AnalyticsState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setTeamA: (team) => {
        set({ teamA: team, error: null }, false, 'setTeamA');
      },

      setTeamB: (team) => {
        set({ teamB: team, error: null }, false, 'setTeamB');
      },

      setCurrentAnalysis: (analysis) => {
        set(
          { 
            currentAnalysis: analysis,
            error: null,
            isLoading: false,
            analysisProgress: analysis ? 100 : 0,
          },
          false,
          'setCurrentAnalysis'
        );
      },

      setCurrentScenarioAnalysis: (analysis) => {
        set(
          { 
            currentScenarioAnalysis: analysis,
            error: null,
            isLoading: false,
          },
          false,
          'setCurrentScenarioAnalysis'
        );
      },

      setFeatureImportance: (features) => {
        set({ featureImportance: features }, false, 'setFeatureImportance');
      },

      setSHAPAnalysis: (shap) => {
        set({ shapAnalysis: shap }, false, 'setSHAPAnalysis');
      },

      setLoading: (loading) => {
        set({ isLoading: loading, error: loading ? null : get().error }, false, 'setLoading');
      },

      setError: (error) => {
        set({ error, isLoading: false }, false, 'setError');
      },

      setAnalysisProgress: (progress) => {
        set({ analysisProgress: Math.max(0, Math.min(100, progress)) }, false, 'setAnalysisProgress');
      },

      updateBackgroundAnalysis: (id, status) => {
        set(
          (state) => ({
            backgroundAnalyses: {
              ...state.backgroundAnalyses,
              [id]: status,
            },
          }),
          false,
          'updateBackgroundAnalysis'
        );
      },

      setSelectedTab: (tab) => {
        set({ selectedTab: tab }, false, 'setSelectedTab');
      },

      clearAnalysis: () => {
        set({
          currentAnalysis: null,
          currentScenarioAnalysis: null,
          featureImportance: null,
          shapAnalysis: null,
          error: null,
          analysisProgress: 0,
        }, false, 'clearAnalysis');
      },

      reset: () => {
        set(initialState, false, 'reset');
      },
    }),
    {
      name: 'analytics-store',
      // Only store essential data in localStorage
      partialize: (state: AnalyticsState) => ({
        teamA: state.teamA,
        teamB: state.teamB,
        selectedTab: state.selectedTab,
      }),
    }
  )
);

// Selectors for commonly used computed values
export const useTeamAProfile = () => {
  const currentAnalysis = useAnalyticsStore((state) => state.currentAnalysis);
  return currentAnalysis?.team_a_analytics || null;
};

export const useTeamBProfile = () => {
  const currentAnalysis = useAnalyticsStore((state) => state.currentAnalysis);
  return currentAnalysis?.team_b_analytics || null;
};

export const useAnalysisReady = () => {
  const { teamA, isLoading } = useAnalyticsStore((state) => ({
    teamA: state.teamA,
    isLoading: state.isLoading,
  }));
  return teamA !== null && !isLoading;
};

export const useHasResults = () => {
  const { currentAnalysis, featureImportance, shapAnalysis } = useAnalyticsStore((state) => ({
    currentAnalysis: state.currentAnalysis,
    featureImportance: state.featureImportance,
    shapAnalysis: state.shapAnalysis,
  }));
  return currentAnalysis !== null || featureImportance !== null || shapAnalysis !== null;
};
