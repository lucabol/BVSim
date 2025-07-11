import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  ReferenceLine,
} from 'recharts';
import { FeatureImportance, SHAPAnalysisResult, SHAPValue } from '../../types/analytics';
import { 
  getCategoryColor, 
  getSHAPColor, 
  formatPercentage, 
  formatDecimal,
  getImportanceLevel,
  getImportanceColor,
  cn,
  fadeIn,
  categoryColors
} from '../ui/utils';

export interface FeatureImportanceChartProps {
  data: FeatureImportance[];
  title?: string;
  className?: string;
}

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({
  data,
  title = "Feature Importance",
  className
}) => {
  // Sort by importance and take top 10
  const sortedData = [...data]
    .sort((a, b) => b.importance_score - a.importance_score)
    .slice(0, 10)
    .map(item => ({
      ...item,
      importance_percent: item.importance_score * 100,
      level: getImportanceLevel(item.importance_score),
    }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-md">
          <p className="font-medium">{label}</p>
          <p className="text-blue-600">
            Importance: {formatPercentage(data.importance_score, 2)}
          </p>
          <p className="text-sm text-gray-600 capitalize">
            Level: {data.level}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={cn('bg-white rounded-lg border shadow-sm p-6', fadeIn, className)}>
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={sortedData}
          layout="horizontal"
          margin={{ top: 20, right: 30, left: 80, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            type="number" 
            tickFormatter={(value) => `${value.toFixed(1)}%`}
          />
          <YAxis 
            type="category" 
            dataKey="statistic_name" 
            width={80}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="importance_percent" 
            fill="#3b82f6"
            radius={[0, 4, 4, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-2">
        {['high', 'medium', 'low'].map(level => (
          <div key={level} className="flex items-center space-x-2">
            <div className={cn('w-3 h-3 rounded', getImportanceColor(level as any))} />
            <span className="text-sm text-gray-600 capitalize">{level} Impact</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export interface SHAPAnalysisChartProps {
  data: SHAPAnalysisResult;
  title?: string;
  className?: string;
}

export const SHAPAnalysisChart: React.FC<SHAPAnalysisChartProps> = ({
  data,
  title = "SHAP Analysis",
  className
}) => {
  // Prepare data for visualization
  const chartData = data.shap_values.map((contrib: SHAPValue) => ({
    feature: contrib.feature_name,
    shap_value: contrib.shap_value,
    feature_value: contrib.feature_value,
    direction: contrib.shap_value > 0 ? 'positive' : contrib.shap_value < 0 ? 'negative' : 'neutral',
    abs_shap: Math.abs(contrib.shap_value),
  })).sort((a: any, b: any) => b.abs_shap - a.abs_shap).slice(0, 15);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-md">
          <p className="font-medium">{data.feature}</p>
          <p className="text-sm">Value: {formatDecimal(data.feature_value)}</p>
          <p className={`text-sm ${data.direction === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
            SHAP: {formatDecimal(data.shap_value, 4)}
          </p>
          <p className="text-xs text-gray-600 capitalize">
            Impact: {data.direction}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={cn('bg-white rounded-lg border shadow-sm p-6', fadeIn, className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        <div className="text-sm text-gray-600">
          Base Value: {formatDecimal(data.base_prediction, 4)}
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          layout="horizontal"
          margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis 
            type="category" 
            dataKey="feature" 
            width={100}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine x={0} stroke="#666" strokeDasharray="3 3" />
          <Bar 
            dataKey="shap_value" 
            fill="#3b82f6"
            radius={[0, 4, 4, 0]}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getSHAPColor(entry.direction as 'positive' | 'negative' | 'neutral')} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {/* Summary */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-600">Prediction: </span>
          <span className="font-medium">{formatDecimal(data.base_prediction, 4)}</span>
        </div>
        <div>
          <span className="text-gray-600">Features: </span>
          <span className="font-medium">{data.shap_values.length}</span>
        </div>
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: getSHAPColor('positive') }} />
          <span className="text-sm text-gray-600">Positive Impact</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: getSHAPColor('negative') }} />
          <span className="text-sm text-gray-600">Negative Impact</span>
        </div>
      </div>
    </div>
  );
};

export interface WinProbabilityChartProps {
  scenarios: Array<{
    name: string;
    win_probability: number;
    confidence_interval: [number, number];
  }>;
  title?: string;
  className?: string;
}

export const WinProbabilityChart: React.FC<WinProbabilityChartProps> = ({
  scenarios,
  title = "Win Probability by Scenario",
  className
}) => {
  const chartData = scenarios.map((scenario, index) => ({
    ...scenario,
    win_percent: scenario.win_probability * 100,
    lower_bound: scenario.confidence_interval[0] * 100,
    upper_bound: scenario.confidence_interval[1] * 100,
    error_lower: (scenario.win_probability - scenario.confidence_interval[0]) * 100,
    error_upper: (scenario.confidence_interval[1] - scenario.win_probability) * 100,
    color: getCategoryColor(Object.keys(categoryColors)[index % Object.keys(categoryColors).length]),
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-md">
          <p className="font-medium">{label}</p>
          <p className="text-blue-600">
            Win Rate: {formatPercentage(data.win_probability)}
          </p>
          <p className="text-sm text-gray-600">
            95% CI: {data.lower_bound.toFixed(1)}% - {data.upper_bound.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={cn('bg-white rounded-lg border shadow-sm p-6', fadeIn, className)}>
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="name" 
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            tickFormatter={(value) => `${value}%`}
            domain={[0, 100]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="win_percent" 
            fill="#3b82f6"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export interface SkillDistributionChartProps {
  data: Array<{
    skill: string;
    value: number;
    category: string;
  }>;
  title?: string;
  className?: string;
}

export const SkillDistributionChart: React.FC<SkillDistributionChartProps> = ({
  data,
  title = "Skill Distribution",
  className
}) => {
  const chartData = data.map(item => ({
    ...item,
    percentage: item.value * 100,
    color: getCategoryColor(item.category),
  }));

  return (
    <div className={cn('bg-white rounded-lg border shadow-sm p-6', fadeIn, className)}>
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={100}
            dataKey="percentage"
            label={({ skill, percentage }) => `${skill}: ${percentage.toFixed(1)}%`}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => [`${value.toFixed(1)}%`, 'Skill Level']}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
