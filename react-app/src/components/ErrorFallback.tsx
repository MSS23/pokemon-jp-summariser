import React from 'react';
import { 
  ExclamationTriangleIcon, 
  ArrowPathIcon, 
  HomeIcon,
  DocumentTextIcon 
} from '@heroicons/react/24/outline';

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ 
  error, 
  resetErrorBoundary 
}) => {
  const handleReset = () => {
    resetErrorBoundary();
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  const handleReportError = () => {
    const errorReport = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    
    // In production, you'd send this to your error reporting service
    console.error('Error Report:', errorReport);
    
    // For now, just copy to clipboard
    navigator.clipboard.writeText(JSON.stringify(errorReport, null, 2));
    alert('Error details copied to clipboard. Please report this to support.');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
        <div className="text-center">
          {/* Pokemon-themed error icon */}
          <div className="relative mb-6">
            <div className="w-24 h-24 mx-auto bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
              <ExclamationTriangleIcon className="w-12 h-12 text-red-600 dark:text-red-400" />
            </div>
            {/* Pikachu ears */}
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
              <div className="w-3 h-6 bg-yellow-400 rounded-full"></div>
            </div>
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 ml-4">
              <div className="w-3 h-6 bg-yellow-400 rounded-full"></div>
            </div>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Oops! Something went wrong
          </h1>
          
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
            It looks like a wild error appeared! Don't worry, our team has been notified.
          </p>

          {/* Error details (collapsible in production) */}
          <details className="mb-6 text-left">
            <summary className="cursor-pointer text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-2">
              Error Details
            </summary>
            <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 text-sm font-mono text-gray-800 dark:text-gray-200 overflow-auto max-h-40">
              <div className="mb-2">
                <strong>Message:</strong> {error.message}
              </div>
              {error.stack && (
                <div>
                  <strong>Stack:</strong>
                  <pre className="whitespace-pre-wrap text-xs mt-1">
                    {error.stack}
                  </pre>
                </div>
              )}
            </div>
          </details>

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleReset}
              className="flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <ArrowPathIcon className="w-5 h-5 mr-2" />
              Try Again
            </button>
            
            <button
              onClick={handleGoHome}
              className="flex items-center justify-center px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
            >
              <HomeIcon className="w-5 h-5 mr-2" />
              Go Home
            </button>
            
            <button
              onClick={handleReportError}
              className="flex items-center justify-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              <DocumentTextIcon className="w-5 h-5 mr-2" />
              Report Error
            </button>
          </div>

          {/* Helpful tips */}
          <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              💡 Quick Fixes
            </h3>
            <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <li>• Refresh the page</li>
              <li>• Clear your browser cache</li>
              <li>• Check your internet connection</li>
              <li>• Try a different browser</li>
            </ul>
          </div>

          {/* Contact support */}
          <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
            Still having issues?{' '}
            <a 
              href="mailto:support@pokemon-vgc.com" 
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Contact our support team
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorFallback; 