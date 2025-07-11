import React, { useState, useCallback } from 'react';
import { Users, Plus, Trash2, Save, RotateCcw } from 'lucide-react';
import { TeamConfiguration, PlayerStatistics } from '../../types/analytics';
import { cn, fadeIn, cardStyles } from '../ui/utils';

export interface TeamInputFormProps {
  onSubmit: (teamData: TeamConfiguration) => void;
  initialData?: Partial<TeamConfiguration>;
  loading?: boolean;
  className?: string;
}

const defaultPlayerStats: Omit<PlayerStatistics, 'player_id' | 'position'> = {
  serve_accuracy: 0.8,
  serve_speed: 45.0,
  reception_quality: 0.75,
  setting_accuracy: 0.85,
  attack_power: 0.7,
  attack_accuracy: 0.65,
  defense_skill: 0.7,
  blocking_height: 2.9,
  blocking_timing: 0.75,
  fitness_level: 0.8,
  experience_level: 0.6,
  mental_toughness: 0.75,
};

const defaultTeamStats: TeamConfiguration = {
  team_name: '',
  players: Array(6).fill(null).map((_, i) => ({
    ...defaultPlayerStats,
    player_id: `player_${i + 1}`,
    position: i < 3 ? 'front' : 'back',
  })),
  team_chemistry: 0.75,
  coaching_quality: 0.8,
  home_advantage: false,
  recent_form: 0.7,
  opponent_scouting: 0.6,
};

export const TeamInputForm: React.FC<TeamInputFormProps> = ({
  onSubmit,
  initialData,
  loading = false,
  className
}) => {
  const [teamData, setTeamData] = useState<TeamConfiguration>({
    ...defaultTeamStats,
    ...initialData,
  });

  const [activePlayerIndex, setActivePlayerIndex] = useState<number>(0);

  const handleTeamFieldChange = useCallback((field: keyof TeamConfiguration, value: any) => {
    setTeamData((prev: TeamConfiguration) => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  const handlePlayerFieldChange = useCallback((playerIndex: number, field: keyof PlayerStatistics, value: any) => {
    setTeamData((prev: TeamConfiguration) => ({
      ...prev,
      players: prev.players.map((player, index) =>
        index === playerIndex
          ? { ...player, [field]: value }
          : player
      ),
    }));
  }, []);

  const addPlayer = useCallback(() => {
    if (teamData.players.length < 12) {
      setTeamData((prev: TeamConfiguration) => ({
        ...prev,
        players: [
          ...prev.players,
          {
            ...defaultPlayerStats,
            player_id: `player_${prev.players.length + 1}`,
            position: prev.players.length < 6 ? 'front' : 'back',
          },
        ],
      }));
    }
  }, [teamData.players.length]);

  const removePlayer = useCallback((playerIndex: number) => {
    if (teamData.players.length > 6) {
      setTeamData((prev: TeamConfiguration) => ({
        ...prev,
        players: prev.players.filter((_, index) => index !== playerIndex),
      }));
      
      if (activePlayerIndex >= teamData.players.length - 1) {
        setActivePlayerIndex(Math.max(0, teamData.players.length - 2));
      }
    }
  }, [teamData.players.length, activePlayerIndex]);

  const resetForm = useCallback(() => {
    setTeamData({ ...defaultTeamStats, ...initialData });
    setActivePlayerIndex(0);
  }, [initialData]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(teamData);
  }, [teamData, onSubmit]);

  const playerStatFields = [
    { key: 'serve_accuracy', label: 'Serve Accuracy', min: 0, max: 1, step: 0.01 },
    { key: 'serve_speed', label: 'Serve Speed (km/h)', min: 20, max: 80, step: 0.5 },
    { key: 'reception_quality', label: 'Reception Quality', min: 0, max: 1, step: 0.01 },
    { key: 'setting_accuracy', label: 'Setting Accuracy', min: 0, max: 1, step: 0.01 },
    { key: 'attack_power', label: 'Attack Power', min: 0, max: 1, step: 0.01 },
    { key: 'attack_accuracy', label: 'Attack Accuracy', min: 0, max: 1, step: 0.01 },
    { key: 'defense_skill', label: 'Defense Skill', min: 0, max: 1, step: 0.01 },
    { key: 'blocking_height', label: 'Blocking Height (m)', min: 2.0, max: 3.5, step: 0.1 },
    { key: 'blocking_timing', label: 'Blocking Timing', min: 0, max: 1, step: 0.01 },
    { key: 'fitness_level', label: 'Fitness Level', min: 0, max: 1, step: 0.01 },
    { key: 'experience_level', label: 'Experience Level', min: 0, max: 1, step: 0.01 },
    { key: 'mental_toughness', label: 'Mental Toughness', min: 0, max: 1, step: 0.01 },
  ] as const;

  return (
    <div className={cn(cardStyles.base, cardStyles.padding, fadeIn, className)}>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div className={cn(cardStyles.header, 'flex items-center justify-between')}>
          <div className="flex items-center space-x-3">
            <Users className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Team Configuration</h2>
          </div>
          
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={resetForm}
              className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Team Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Team Name
            </label>
            <input
              type="text"
              value={teamData.team_name}
              onChange={(e) => handleTeamFieldChange('team_name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter team name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Team Chemistry
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={teamData.team_chemistry}
              onChange={(e) => handleTeamFieldChange('team_chemistry', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-gray-600 mt-1">
              {(teamData.team_chemistry * 100).toFixed(0)}%
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Coaching Quality
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={teamData.coaching_quality}
              onChange={(e) => handleTeamFieldChange('coaching_quality', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-gray-600 mt-1">
              {(teamData.coaching_quality * 100).toFixed(0)}%
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recent Form
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={teamData.recent_form}
              onChange={(e) => handleTeamFieldChange('recent_form', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-gray-600 mt-1">
              {(teamData.recent_form * 100).toFixed(0)}%
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Opponent Scouting
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={teamData.opponent_scouting}
              onChange={(e) => handleTeamFieldChange('opponent_scouting', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-gray-600 mt-1">
              {(teamData.opponent_scouting * 100).toFixed(0)}%
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="home_advantage"
              checked={teamData.home_advantage}
              onChange={(e) => handleTeamFieldChange('home_advantage', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="home_advantage" className="ml-2 text-sm font-medium text-gray-700">
              Home Advantage
            </label>
          </div>
        </div>

        {/* Players Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Players ({teamData.players.length})
            </h3>
            
            <button
              type="button"
              onClick={addPlayer}
              disabled={teamData.players.length >= 12}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Add Player</span>
            </button>
          </div>

          {/* Player Tabs */}
          <div className="flex flex-wrap gap-2 mb-4">
            {teamData.players.map((player, index) => (
              <button
                key={player.player_id}
                type="button"
                onClick={() => setActivePlayerIndex(index)}
                className={cn(
                  'px-3 py-2 rounded-md text-sm font-medium transition-colors',
                  activePlayerIndex === index
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                Player {index + 1}
                {teamData.players.length > 6 && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      removePlayer(index);
                    }}
                    className="ml-2 text-red-400 hover:text-red-600"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                )}
              </button>
            ))}
          </div>

          {/* Active Player Form */}
          {teamData.players[activePlayerIndex] && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Position
                </label>
                <select
                  value={teamData.players[activePlayerIndex].position}
                  onChange={(e) => handlePlayerFieldChange(activePlayerIndex, 'position', e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="front">Front Row</option>
                  <option value="back">Back Row</option>
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {playerStatFields.map(({ key, label, min, max, step }) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {label}
                    </label>
                    <input
                      type="range"
                      min={min}
                      max={max}
                      step={step}
                      value={teamData.players[activePlayerIndex][key as keyof PlayerStatistics]}
                      onChange={(e) => handlePlayerFieldChange(
                        activePlayerIndex, 
                        key as keyof PlayerStatistics, 
                        parseFloat(e.target.value)
                      )}
                      className="w-full"
                    />
                    <div className="text-sm text-gray-600 mt-1">
                      {key.includes('speed') || key.includes('height') 
                        ? (teamData.players[activePlayerIndex][key as keyof PlayerStatistics] as number).toFixed(1)
                        : `${((teamData.players[activePlayerIndex][key as keyof PlayerStatistics] as number) * 100).toFixed(0)}%`
                      }
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !teamData.team_name.trim()}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>{loading ? 'Saving...' : 'Save Team'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
