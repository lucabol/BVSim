import React from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';
import { cn, shimmer, fadeIn } from './utils';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };

  return (
    <Loader2 
      className={cn(
        'animate-spin text-blue-600',
        sizeClasses[size],
        className
      )} 
    />
  );
};

export interface LoadingCardProps {
  title?: string;
  description?: string;
  className?: string;
}

export const LoadingCard: React.FC<LoadingCardProps> = ({
  title = "Loading...",
  description,
  className
}) => {
  return (
    <div className={cn(
      'bg-white rounded-lg border shadow-sm p-6',
      fadeIn,
      className
    )}>
      <div className="flex items-center space-x-3 mb-4">
        <LoadingSpinner />
        <div>
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          {description && (
            <p className="text-sm text-gray-500">{description}</p>
          )}
        </div>
      </div>
      
      {/* Skeleton content */}
      <div className="space-y-3">
        <div className={cn(shimmer, 'h-4 w-3/4')} />
        <div className={cn(shimmer, 'h-4 w-1/2')} />
        <div className={cn(shimmer, 'h-20 w-full')} />
      </div>
    </div>
  );
};

export interface LoadingTableProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export const LoadingTable: React.FC<LoadingTableProps> = ({
  rows = 5,
  columns = 4,
  className
}) => {
  return (
    <div className={cn('bg-white rounded-lg border shadow-sm', className)}>
      <div className="p-6">
        <div className={cn(shimmer, 'h-6 w-48 mb-4')} />
        
        <div className="space-y-3">
          {/* Header */}
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {Array.from({ length: columns }).map((_, i) => (
              <div key={i} className={cn(shimmer, 'h-4 w-full')} />
            ))}
          </div>
          
          {/* Rows */}
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <div key={rowIndex} className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <div key={colIndex} className={cn(shimmer, 'h-4 w-full')} />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  title = "Error",
  message,
  onRetry,
  className
}) => {
  return (
    <div className={cn(
      'bg-red-50 border border-red-200 rounded-lg p-6',
      fadeIn,
      className
    )}>
      <div className="flex items-start space-x-3">
        <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-lg font-medium text-red-900 mb-2">{title}</h3>
          <p className="text-red-700 mb-4">{message}</p>
          
          {onRetry && (
            <button
              onClick={onRetry}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors duration-200"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export interface EmptyStateProps {
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  action,
  icon,
  className
}) => {
  return (
    <div className={cn(
      'bg-white rounded-lg border shadow-sm p-12 text-center',
      fadeIn,
      className
    )}>
      {icon && (
        <div className="mb-4 flex justify-center text-gray-400">
          {icon}
        </div>
      )}
      
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      
      {description && (
        <p className="text-gray-500 mb-6 max-w-md mx-auto">{description}</p>
      )}
      
      {action && (
        <button
          onClick={action.onClick}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors duration-200"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};
