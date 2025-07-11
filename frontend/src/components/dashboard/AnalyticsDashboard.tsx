import React, { useState, useCallback } from 'react';
import { Activity, BarChart3, Users, TrendingUp, Brain, Target } from 'lucide-react';
import { useAnalyticsOperations, useAnalyticsData } from '../../hooks/useAnalytics';
import { TeamConfiguration, AnalysisType } from '../../types/analytics';
import { TeamInputForm } from '../forms/TeamInputForm';
import { 
  FeatureImportanceChart, 
  SHAPAnalysisChart, 
  WinProbabilityChart
} from '../charts/AnalyticsCharts';
import { LoadingCard, ErrorMessage, EmptyState } from '../ui/LoadingAndError';
import { cn, fadeIn, cardStyles, responsiveGrid } from '../ui/utils';

type TabType = 'setup' | 'analytics' | 'comparison' | 'insights';

export interface AnalyticsDashboardProps {
  className?: string;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ className }) => {
  const [activeTab, setActiveTab] = useState<TabType>('setup');
  const [teamA, setTeamA] = useState<TeamConfiguration | null>(null);
  const [teamB, setTeamB] = useState<TeamConfiguration | null>(null);
  const [analysisTypes] = useState<AnalysisType[]>([
    'feature_importance',
    'shap_values',
    'scenario_analysis'
  ]);

  const { 
    runFullAnalysis
  } = useAnalyticsOperations();

  const {
    currentAnalysis,
    currentScenarioAnalysis,
    featureImportance,
    shapAnalysis,
    isLoading,
    error
  } = useAnalyticsData();

  const handleTeamSubmit = useCallback((teamData: TeamConfiguration, teamType: 'A' | 'B') => {
    if (teamType === 'A') {
      setTeamA(teamData);
    } else {
      setTeamB(teamData);
    }
    
    // Auto-switch to analytics tab when first team is configured
    if (teamType === 'A' && activeTab === 'setup') {
      setActiveTab('analytics');
    }
  }, [activeTab]);

  const handleRunAnalysis = useCallback(async () => {
    if (!teamA) return;

    try {
      const teamAStats = {
        name: teamA.team_name,
        // Convert team configuration to team statistics
        // This would need mapping logic based on your backend requirements
        service_ace_percentage: 0.1,
        service_error_percentage: 0.05,
        serve_success_rate: 0.85,
        perfect_pass_percentage: 0.3,
        good_pass_percentage: 0.5,
        poor_pass_percentage: 0.15,
        reception_error_percentage: 0.05,
        assist_percentage: 0.4,
        ball_handling_error_percentage: 0.02,
        attack_kill_percentage: 0.45,
        attack_error_percentage: 0.1,
        hitting_efficiency: 0.35,
        first_ball_kill_percentage: 0.5,
        dig_percentage: 0.6,
        block_kill_percentage: 0.15,
        controlled_block_percentage: 0.25,
        blocking_error_percentage: 0.05,
      };

      const teamBStats = teamB ? {
        name: teamB.team_name,
        // Similar conversion for team B
        service_ace_percentage: 0.08,
        service_error_percentage: 0.06,
        serve_success_rate: 0.82,
        perfect_pass_percentage: 0.28,
        good_pass_percentage: 0.48,
        poor_pass_percentage: 0.18,
        reception_error_percentage: 0.06,
        assist_percentage: 0.38,
        ball_handling_error_percentage: 0.03,
        attack_kill_percentage: 0.42,
        attack_error_percentage: 0.12,
        hitting_efficiency: 0.30,
        first_ball_kill_percentage: 0.47,
        dig_percentage: 0.58,
        block_kill_percentage: 0.12,
        controlled_block_percentage: 0.22,
        blocking_error_percentage: 0.06,
      } : undefined;

      await runFullAnalysis(teamAStats, teamBStats, analysisTypes, 1000);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  }, [teamA, teamB, analysisTypes, runFullAnalysis]);

  const tabs = [
    { id: 'setup' as const, label: 'Team Setup', icon: Users },
    { id: 'analytics' as const, label: 'Analytics', icon: BarChart3 },
    { id: 'comparison' as const, label: 'Comparison', icon: TrendingUp },
    { id: 'insights' as const, label: 'Insights', icon: Brain },
  ];

  return (
    <div className={cn('min-h-screen bg-gray-50 p-6', className)}>
      {/* Header */}
      <div className={cn(cardStyles.base, cardStyles.padding, 'mb-6', fadeIn)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Beach Volleyball Analytics</h1>
              <p className="text-gray-600">Advanced team performance analysis and insights</p>
            </div>
          </div>
          
          {teamA && (
            <button
              onClick={handleRunAnalysis}
              disabled={isLoading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <Target className="h-4 w-4" />
              <span>{isLoading ? 'Analyzing...' : 'Run Analysis'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-6 bg-white rounded-lg p-1 shadow-sm">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
              activeTab === id
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            )}
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'setup' && (
          <div className={responsiveGrid.cols2}>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Team A</h2>
              <TeamInputForm
                onSubmit={(data) => handleTeamSubmit(data, 'A')}
                initialData={teamA || undefined}
                loading={isLoading}
              />
            </div>
            
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Team B (Optional)</h2>
              <TeamInputForm
                onSubmit={(data) => handleTeamSubmit(data, 'B')}
                initialData={teamB || undefined}
                loading={isLoading}
              />
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {error && (
              <ErrorMessage
                title="Analysis Error"
                message={error}
                onRetry={() => window.location.reload()}
              />
            )}

            {isLoading && (
              <div className={responsiveGrid.cols2}>
                <LoadingCard title="Running Analysis..." description="Analyzing team performance and generating insights" />
                <LoadingCard title="Computing SHAP Values..." description="Calculating feature importance and impact" />
              </div>
            )}

            {!teamA && !isLoading && (
              <EmptyState
                title="No Team Configured"
                description="Please configure at least Team A in the setup tab to run analytics."
                action={{
                  label: "Go to Setup",
                  onClick: () => setActiveTab('setup'),
                }}
                icon={<Users className="h-12 w-12" />}
              />
            )}

            {currentAnalysis && (
              <div className="space-y-6">
                {/* Feature Importance */}
                {featureImportance && featureImportance.length > 0 && (
                  <FeatureImportanceChart
                    data={featureImportance}
                    title="Feature Importance Analysis"
                  />
                )}

                {/* SHAP Analysis */}
                {shapAnalysis && (
                  <SHAPAnalysisChart
                    data={shapAnalysis}
                    title="SHAP Value Analysis"
                  />
                )}

                {/* Win Probability Scenarios */}
                {currentScenarioAnalysis && currentScenarioAnalysis.scenarios.length > 0 && (
                  <WinProbabilityChart
                    scenarios={currentScenarioAnalysis.scenarios.map(scenario => ({
                      name: scenario.scenario_name,
                      win_probability: scenario.predicted_win_rate,
                      confidence_interval: [
                        scenario.confidence_interval.lower,
                        scenario.confidence_interval.upper
                      ],
                    }))}
                    title="Scenario Analysis"
                  />
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="space-y-6">
            {!teamA || !teamB ? (
              <EmptyState
                title="Team Comparison Unavailable"
                description="Please configure both Team A and Team B to enable comparison analysis."
                action={{
                  label: "Configure Teams",
                  onClick: () => setActiveTab('setup'),
                }}
                icon={<Users className="h-12 w-12" />}
              />
            ) : (
              <div className={responsiveGrid.cols2}>
                <div className={cn(cardStyles.base, cardStyles.padding)}>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">{teamA.team_name}</h3>
                  {/* Team A comparison metrics */}
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Team Chemistry:</span>
                      <span className="font-medium">{(teamA.team_chemistry * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Coaching Quality:</span>
                      <span className="font-medium">{(teamA.coaching_quality * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Recent Form:</span>
                      <span className="font-medium">{(teamA.recent_form * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Players:</span>
                      <span className="font-medium">{teamA.players.length}</span>
                    </div>
                  </div>
                </div>

                <div className={cn(cardStyles.base, cardStyles.padding)}>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">{teamB.team_name}</h3>
                  {/* Team B comparison metrics */}
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Team Chemistry:</span>
                      <span className="font-medium">{(teamB.team_chemistry * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Coaching Quality:</span>
                      <span className="font-medium">{(teamB.coaching_quality * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Recent Form:</span>
                      <span className="font-medium">{(teamB.recent_form * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Players:</span>
                      <span className="font-medium">{teamB.players.length}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-6">
            {!currentAnalysis ? (
              <EmptyState
                title="No Analysis Available"
                description="Run an analysis first to see detailed insights and recommendations."
                action={{
                  label: "Run Analysis",
                  onClick: handleRunAnalysis,
                }}
                icon={<Brain className="h-12 w-12" />}
              />
            ) : (
              <div className={responsiveGrid.cols1}>
                <div className={cn(cardStyles.base, cardStyles.padding)}>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Summary</h3>
                  <div className="space-y-4">
                    <div>
                      <span className="text-gray-600">Analysis ID:</span>
                      <span className="ml-2 font-mono text-sm">{currentAnalysis.analysis_id}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Simulation Count:</span>
                      <span className="ml-2 font-medium">{currentAnalysis.simulation_count.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Analysis Time:</span>
                      <span className="ml-2 font-medium">{currentAnalysis.analysis_time_seconds.toFixed(2)}s</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Confidence Level:</span>
                      <span className="ml-2 font-medium">{(currentAnalysis.confidence_level * 100).toFixed(0)}%</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Reliability Score:</span>
                      <span className="ml-2 font-medium">{(currentAnalysis.reliability_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
