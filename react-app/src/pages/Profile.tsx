import { useAuth } from '../context/AuthContext';
import { useAnalytics } from '../context/AnalyticsContext';
import { 
  UserCircleIcon, 
  ChartBarIcon, 
  ClockIcon,
  CalendarIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline';

const Profile = () => {
  const { user } = useAuth();
  const { analytics } = useAnalytics();

  const stats = [
    {
      name: 'Total Searches',
      value: analytics.totalSearches,
      icon: ChartBarIcon,
      color: 'text-blue-400'
    },
    {
      name: 'Teams Viewed',
      value: analytics.teamsViewed,
      icon: ChartBarIcon,
      color: 'text-green-400'
    },
    {
      name: 'Summaries Generated',
      value: analytics.summariesGenerated,
      icon: ChartBarIcon,
      color: 'text-purple-400'
    }
  ];

  const recentActivity = [
    {
      id: 1,
      action: 'Generated summary',
      details: 'Japanese VGC article analysis',
      time: '2 hours ago'
    },
    {
      id: 2,
      action: 'Viewed team',
      details: 'Hydreigon + Rillaboom composition',
      time: '1 day ago'
    },
    {
      id: 3,
      action: 'Searched for',
      details: 'Incineroar strategies',
      time: '2 days ago'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <div className="card mb-8">
          <div className="flex items-center space-x-6">
            <div className="flex-shrink-0">
              <UserCircleIcon className="h-20 w-20 text-purple-400" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-white">{user?.username}</h1>
              <div className="flex items-center space-x-4 mt-2 text-gray-200">
                <div className="flex items-center">
                  <CalendarIcon className="h-4 w-4 mr-1" />
                  <span className="text-sm">Member since {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Recently'}</span>
                </div>
                {user?.email && (
                  <div className="flex items-center">
                    <EnvelopeIcon className="h-4 w-4 mr-1" />
                    <span className="text-sm">{user.email}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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

        {/* Personal Stats */}
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Personal Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-gray-200 mb-3">Activity Overview</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">This Week</span>
                  <span className="text-white font-medium">{analytics.totalSearches} searches</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">This Month</span>
                  <span className="text-white font-medium">{analytics.teamsViewed} teams viewed</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Total Time</span>
                  <span className="text-white font-medium">~{Math.floor(analytics.totalSearches * 2.5)} minutes</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-200 mb-3">Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Accuracy Rate</span>
                  <span className="text-purple-400 font-medium">95%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Avg. Processing</span>
                  <span className="text-white font-medium">2.3s</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Success Rate</span>
                  <span className="text-blue-400 font-medium">98%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ClockIcon className="h-5 w-5 text-purple-400" />
                  <div>
                    <p className="text-white font-medium">{activity.action}</p>
                    <p className="text-sm text-gray-300">{activity.details}</p>
                  </div>
                </div>
                <span className="text-sm text-gray-300">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Account Settings */}
        <div className="mt-8">
          <div className="card">
            <h2 className="text-xl font-semibold text-white mb-4">Account Settings</h2>
            <div className="space-y-4">
              <button className="btn-secondary w-full sm:w-auto">
                Change Password
              </button>
              <button className="btn-secondary w-full sm:w-auto">
                Update Email
              </button>
              <button className="btn-secondary w-full sm:w-auto">
                Export Data
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile; 