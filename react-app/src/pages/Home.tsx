import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  DocumentTextIcon, 
  MagnifyingGlassIcon, 
  ChartBarIcon,
  BoltIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  LanguageIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

const Home = () => {
  const { user } = useAuth();

  const features = [
    {
      name: 'Japanese Article Translation',
      description: 'Translate Japanese VGC articles into English with AI-powered accuracy.',
      icon: LanguageIcon,
      href: '/summarizer'
    },
    {
      name: 'Team Analysis & Extraction',
      description: 'Extract and analyze Pokemon teams from Japanese articles with detailed statistics.',
      icon: DocumentTextIcon,
      href: '/summarizer'
    },
    {
      name: 'Advanced Search',
      description: 'Search through translated articles and extracted teams with powerful filters.',
      icon: MagnifyingGlassIcon,
      href: '/search'
    },
    {
      name: 'Analytics Dashboard',
      description: 'Track your translation activity and view usage insights.',
      icon: ChartBarIcon,
      href: '/analytics'
    },
    {
      name: 'Multi-Language Support',
      description: 'Support for various Japanese VGC content sources and formats.',
      icon: GlobeAltIcon,
      href: '/summarizer'
    },
    {
      name: 'Real-time Processing',
      description: 'Instant translation and analysis with optimized AI models.',
      icon: BoltIcon,
      href: '/summarizer'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Pokemon Japanese Team
              <span className="text-purple-400 block">Translator & Summariser</span>
            </h1>
            <p className="text-xl text-gray-200 mb-8 max-w-3xl mx-auto">
              Break down language barriers in competitive Pokemon. Translate Japanese VGC articles, 
              extract team compositions, and gain insights from the Japanese competitive scene.
            </p>
            
            {user ? (
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/summarizer"
                  className="btn-primary text-lg px-8 py-3"
                >
                  Start Translating
                </Link>
                <Link
                  to="/search"
                  className="btn-secondary text-lg px-8 py-3"
                >
                  Search Teams
                </Link>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/login"
                  className="btn-primary text-lg px-8 py-3"
                >
                  Get Started
                </Link>
                <Link
                  to="/register"
                  className="btn-secondary text-lg px-8 py-3"
                >
                  Create Account
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">
            Powerful Translation & Analysis Tools
          </h2>
          <p className="text-gray-200 text-lg">
            Everything you need to understand Japanese Pokemon VGC content
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <Link
              key={feature.name}
              to={feature.href}
              className="card hover:bg-gray-750 transition-all duration-300 group"
            >
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0">
                  <feature.icon className="h-8 w-8 text-purple-400 group-hover:text-purple-300 transition-colors" />
                </div>
                <h3 className="ml-3 text-lg font-semibold text-white group-hover:text-purple-300 transition-colors">
                  {feature.name}
                </h3>
              </div>
              <p className="text-gray-200 group-hover:text-gray-100 transition-colors">
                {feature.description}
              </p>
            </Link>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-gray-800 border-t border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-purple-400 mb-2">5K+</div>
              <div className="text-gray-200">Articles Translated</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-400 mb-2">2K+</div>
              <div className="text-gray-200">Teams Extracted</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-400 mb-2">98%</div>
              <div className="text-gray-200">Translation Accuracy</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Access Japanese VGC Content?
          </h2>
          <p className="text-gray-200 mb-8 text-lg">
            Join thousands of players using our translation tools to stay competitive
          </p>
          {!user && (
            <Link
              to="/register"
              className="btn-primary text-lg px-8 py-3"
            >
              Start Free Translation
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home; 