import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AnalyticsData {
  total_searches: number;
  total_teams_viewed: number;
  total_summaries: number;
  favorite_pokemon: Array<[string, number]>;
  recent_activity: Array<{
    type: string;
    details: string;
    timestamp: string;
  }>;
}

interface AnalyticsContextType {
  analytics: AnalyticsData;
  trackSearch: (query: string) => void;
  trackTeamView: (teamId: string) => void;
  trackSummary: (url: string) => void;
  loading: boolean;
}

const defaultAnalytics: AnalyticsData = {
  total_searches: 0,
  total_teams_viewed: 0,
  total_summaries: 0,
  favorite_pokemon: [],
  recent_activity: [],
};

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};

interface AnalyticsProviderProps {
  children: ReactNode;
}

export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({ children }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData>(defaultAnalytics);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load analytics from localStorage
    const savedAnalytics = localStorage.getItem('analytics');
    if (savedAnalytics) {
      try {
        setAnalytics(JSON.parse(savedAnalytics));
      } catch (error) {
        console.error('Error parsing saved analytics:', error);
      }
    }
    setLoading(false);
  }, []);

  const saveAnalytics = (newAnalytics: AnalyticsData) => {
    localStorage.setItem('analytics', JSON.stringify(newAnalytics));
    setAnalytics(newAnalytics);
  };

  const trackSearch = (query: string) => {
    const newAnalytics = {
      ...analytics,
      total_searches: analytics.total_searches + 1,
      recent_activity: [
        {
          type: 'search',
          details: `Searched for: ${query}`,
          timestamp: new Date().toISOString(),
        },
        ...analytics.recent_activity.slice(0, 9), // Keep last 10 activities
      ],
    };
    saveAnalytics(newAnalytics);
  };

  const trackTeamView = (teamId: string) => {
    const newAnalytics = {
      ...analytics,
      total_teams_viewed: analytics.total_teams_viewed + 1,
      recent_activity: [
        {
          type: 'team_view',
          details: `Viewed team: ${teamId}`,
          timestamp: new Date().toISOString(),
        },
        ...analytics.recent_activity.slice(0, 9),
      ],
    };
    saveAnalytics(newAnalytics);
  };

  const trackSummary = (url: string) => {
    const newAnalytics = {
      ...analytics,
      total_summaries: analytics.total_summaries + 1,
      recent_activity: [
        {
          type: 'summary',
          details: `Generated summary for: ${url}`,
          timestamp: new Date().toISOString(),
        },
        ...analytics.recent_activity.slice(0, 9),
      ],
    };
    saveAnalytics(newAnalytics);
  };

  const value: AnalyticsContextType = {
    analytics,
    trackSearch,
    trackTeamView,
    trackSummary,
    loading,
  };

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
}; 