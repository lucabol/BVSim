/**
 * UI utility functions and shared styles
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Color palette for different categories
export const categoryColors = {
  serve: '#3b82f6',      // blue
  reception: '#10b981',   // emerald
  setting: '#f59e0b',     // amber
  attack: '#ef4444',      // red
  defense: '#8b5cf6',     // violet
  blocking: '#06b6d4',    // cyan
} as const;

export const getCategoryColor = (category: string): string => {
  return categoryColors[category as keyof typeof categoryColors] || '#6b7280';
};

// Format numbers for display
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};

export const formatDecimal = (value: number, decimals: number = 3): string => {
  return value.toFixed(decimals);
};

export const formatWinRate = (value: number): string => {
  return formatPercentage(value, 1);
};

// Statistical significance helpers
export const getSignificanceLevel = (pValue: number): 'high' | 'medium' | 'low' => {
  if (pValue < 0.01) return 'high';
  if (pValue < 0.05) return 'medium';
  return 'low';
};

export const getSignificanceColor = (level: 'high' | 'medium' | 'low'): string => {
  switch (level) {
    case 'high': return 'text-green-600';
    case 'medium': return 'text-yellow-600';
    case 'low': return 'text-gray-600';
  }
};

// Feature importance helpers
export const getImportanceLevel = (score: number): 'high' | 'medium' | 'low' => {
  if (score > 0.1) return 'high';
  if (score > 0.05) return 'medium';
  return 'low';
};

export const getImportanceColor = (level: 'high' | 'medium' | 'low'): string => {
  switch (level) {
    case 'high': return 'bg-red-100 text-red-800';
    case 'medium': return 'bg-yellow-100 text-yellow-800';
    case 'low': return 'bg-gray-100 text-gray-800';
  }
};

// SHAP value helpers
export const getSHAPColor = (direction: 'positive' | 'negative' | 'neutral'): string => {
  switch (direction) {
    case 'positive': return '#10b981'; // green
    case 'negative': return '#ef4444'; // red
    case 'neutral': return '#6b7280';  // gray
  }
};

// Animation classes
export const fadeIn = 'animate-in fade-in-0 duration-300';
export const slideUp = 'animate-in slide-in-from-bottom-4 duration-300';
export const slideDown = 'animate-in slide-in-from-top-4 duration-300';

// Loading states
export const shimmer = 'animate-pulse bg-gray-200 rounded';

// Responsive grid classes
export const responsiveGrid = {
  cols1: 'grid grid-cols-1',
  cols2: 'grid grid-cols-1 md:grid-cols-2',
  cols3: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  cols4: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
};

// Card styles
export const cardStyles = {
  base: 'bg-white rounded-lg border shadow-sm',
  padding: 'p-6',
  header: 'border-b pb-4 mb-4',
  hoverable: 'hover:shadow-md transition-shadow duration-200',
};
