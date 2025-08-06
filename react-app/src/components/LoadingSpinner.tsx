import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  text = 'Loading Pokemon VGC Summariser...',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  };

  const textSizes = {
    sm: 'text-sm',
    md: 'text-lg',
    lg: 'text-xl'
  };

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center ${className}`}>
      <div className="text-center">
        <div className="relative">
          {/* Pokemon-themed loading animation */}
          <div className={`${sizeClasses[size]} animate-spin rounded-full border-4 border-gray-200 dark:border-gray-700 mx-auto mb-4`}>
            <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-600 animate-pulse"></div>
            <div className="absolute inset-2 rounded-full bg-gradient-to-br from-red-400 to-blue-500 opacity-20 animate-pulse"></div>
          </div>
          
          {/* Pikachu ears effect */}
          <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
            <div className="w-2 h-4 bg-yellow-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          </div>
          <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 ml-3">
            <div className="w-2 h-4 bg-yellow-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          </div>
        </div>
        
        <h2 className={`font-semibold text-gray-700 dark:text-gray-300 ${textSizes[size]} animate-pulse`}>
          {text}
        </h2>
        
        {/* Loading dots */}
        <div className="flex justify-center mt-4 space-x-1">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner; 