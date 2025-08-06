import { useAnalytics } from '../context/AnalyticsContext';
import { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  MagnifyingGlassIcon, 
  DocumentTextIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  UserGroupIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface TranslatedTeam {
  id: string;
  pokemon: string;
  level: number;
  hp: { current: number; max: number };
  status: string;
  teraType: string;
  item: string;
  ability: string;
  types: string[];
  moves: Array<{ name: string; bp: number; checked: boolean }>;
  stats: {
    hp: { base: number; evs: number; ivs: number; final: number };
    attack: { base: number; evs: number; ivs: number; final: number };
    defense: { base: number; evs: number; ivs: number; final: number };
    spAtk: { base: number; evs: number; ivs: number; final: number };
    spDef: { base: number; evs: number; ivs: number; final: number };
    speed: { base: number; evs: number; ivs: number; final: number };
  };
  bst: number;
  remainingEvs: number;
  nature: string;
  articleTitle: string;
  translatedDate: string;
  articleUrl: string;
}

const Analytics = () => {
  const { analytics } = useAnalytics();
  const [translatedTeams, setTranslatedTeams] = useState<TranslatedTeam[]>([]);
  const [popularPokemon, setPopularPokemon] = useState<Array<[string, number]>>([]);

  useEffect(() => {
    // Load translated teams from localStorage
    const savedTeams = localStorage.getItem('translatedTeams');
    if (savedTeams) {
      try {
        const teams = JSON.parse(savedTeams);
        setTranslatedTeams(teams);
        
        // Calculate popular Pokemon from teams
        const pokemonCount: { [key: string]: number } = {};
        teams.forEach((team: TranslatedTeam) => {
          pokemonCount[team.pokemon] = (pokemonCount[team.pokemon] || 0) + 1;
        });
        
        const sortedPokemon = Object.entries(pokemonCount)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 6);
        
        setPopularPokemon(sortedPokemon);
      } catch (error) {
        console.error('Error loading saved teams:', error);
      }
    }
  }, []);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hours ago`;
    return `${Math.floor(diffInMinutes / 1440)} days ago`;
  };

  const stats = [
    {
      name: 'Total Searches',
      value: analytics.total_searches,
      icon: MagnifyingGlassIcon,
      color: 'text-blue-400'
    },
    {
      name: 'Teams Analyzed',
      value: analytics.total_summaries,
      icon: DocumentTextIcon,
      color: 'text-green-400'
    },
    {
      name: 'Teams Viewed',
      value: analytics.total_teams_viewed,
      icon: ChartBarIcon,
      color: 'text-purple-400'
    },
    {
      name: 'Total Teams',
      value: translatedTeams.length,
      icon: UserGroupIcon,
      color: 'text-yellow-400'
    }
  ];

  const hasData = analytics.total_searches > 0 || analytics.total_summaries > 0 || translatedTeams.length > 0;

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Analytics Dashboard</h1>
          <p className="text-gray-200 text-lg">
            Track your translation activity and view usage insights
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-200">{stat.name}</p>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {!hasData ? (
          /* Empty State */
          <div className="card text-center py-12">
            <ExclamationTriangleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No Analytics Data Yet</h3>
            <p className="text-gray-300 mb-6">
              Start analyzing Pokemon articles to see your analytics here
            </p>
            <div className="flex justify-center space-x-4">
              <div className="text-center">
                <DocumentTextIcon className="h-8 w-8 text-blue-400 mx-auto mb-2" />
                <p className="text-sm text-gray-300">Analyze Articles</p>
              </div>
              <div className="text-center">
                <MagnifyingGlassIcon className="h-8 w-8 text-green-400 mx-auto mb-2" />
                <p className="text-sm text-gray-300">Search Teams</p>
              </div>
              <div className="text-center">
                <ChartBarIcon className="h-8 w-8 text-purple-400 mx-auto mb-2" />
                <p className="text-sm text-gray-300">View Analytics</p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* Charts and Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Activity Chart */}
              <div className="card">
                <h2 className="text-xl font-semibold text-white mb-4">Activity Overview</h2>
                <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <ArrowTrendingUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-300">Activity chart coming soon</p>
                    <p className="text-sm text-gray-400 mt-2">
                      {analytics.total_searches} searches • {analytics.total_summaries} summaries
                    </p>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="card">
                <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
                <div className="space-y-4">
                  {analytics.recent_activity.length > 0 ? (
                    analytics.recent_activity.slice(0, 5).map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-gray-700 rounded-lg">
                        <div className="flex-shrink-0">
                          {activity.type === 'search' && <MagnifyingGlassIcon className="h-5 w-5 text-blue-400" />}
                          {activity.type === 'summary' && <DocumentTextIcon className="h-5 w-5 text-green-400" />}
                          {activity.type === 'team_view' && <ChartBarIcon className="h-5 w-5 text-purple-400" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-white">{activity.details}</p>
                          <p className="text-xs text-gray-300">{formatTimestamp(activity.timestamp)}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <ClockIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-300">No recent activity</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Popular Pokemon */}
            {popularPokemon.length > 0 && (
              <div className="mt-8">
                <div className="card">
                  <h2 className="text-xl font-semibold text-white mb-4">Popular Pokemon</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {popularPokemon.map(([pokemon, count]) => (
                      <div key={pokemon} className="bg-gray-700 rounded-lg p-4 text-center">
                        <p className="text-white font-medium">{pokemon}</p>
                        <p className="text-sm text-gray-300">{count} team{count !== 1 ? 's' : ''}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Recent Teams */}
            {translatedTeams.length > 0 && (
              <div className="mt-8">
                <div className="card">
                  <h2 className="text-xl font-semibold text-white mb-4">Recent Teams</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {translatedTeams.slice(0, 6).map((team) => (
                      <div key={team.id} className="bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-white font-medium">{team.pokemon}</h3>
                          <span className="text-xs text-gray-400">Lv. {team.level}</span>
                        </div>
                        <p className="text-sm text-gray-300 mb-2 truncate">{team.articleTitle}</p>
                        <div className="flex flex-wrap gap-1 mb-2">
                          {team.types.slice(0, 2).map((type) => (
                            <span key={type} className="px-2 py-1 bg-gray-600 text-white text-xs rounded">
                              {type}
                            </span>
                          ))}
                        </div>
                        <p className="text-xs text-gray-400">
                          {formatTimestamp(team.translatedDate)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Analytics; 