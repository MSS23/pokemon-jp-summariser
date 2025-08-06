import { useState, useCallback, useMemo, useEffect } from 'react';
import { useAnalytics } from '../context/AnalyticsContext';
import { useTheme } from '../context/ThemeContext';
import { useDebounce, usePerformanceMonitor } from '../utils/performance';
import { useGemini } from '../hooks/useGemini';
import toast from 'react-hot-toast';
import { 
  DocumentTextIcon, 
  ArrowDownTrayIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  ShareIcon
} from '@heroicons/react/24/outline';

interface SummaryData {
  articleTitle: string;
  summary: string;
  teams: any[];
  processingTime: number;
  metadata?: {
    url: string;
    processedAt: string;
    version: string;
  };
}

const Summarizer = () => {
  // Performance monitoring
  usePerformanceMonitor('Summarizer');

  const [url, setUrl] = useState('');
  const { trackSummary } = useAnalytics();
  const { isDark } = useTheme();
  
  // Use Gemini hook for direct integration
  const { summarizeArticle, isLoading, result, error, isAvailable, reset } = useGemini();

  // Handle article summarization with Gemini
  const handleSummarization = useCallback(async (urlToProcess: string) => {
    const loadingToast = toast.loading('Analyzing article with Gemini...', {
      icon: '⚡',
    });

    try {
      await summarizeArticle(urlToProcess);
      trackSummary();
      toast.success('Team analysis completed successfully!', { id: loadingToast });
    } catch (err: any) {
      let errorMessage = err.message || 'Failed to process article. Please check the URL and try again.';
      
      // Handle specific Gemini errors
      if (err.message?.includes('overloaded')) {
        errorMessage = 'Gemini service is temporarily busy. Please wait a moment and try again.';
      } else if (err.message?.includes('rate limit')) {
        errorMessage = 'Rate limit exceeded. Please wait a moment before trying again.';
      }
      
      toast.error(errorMessage, { id: loadingToast });
      console.error('Error:', err);
    }
  }, [summarizeArticle, trackSummary]);

  // Debounced URL validation
  const debouncedUrlValidation = useDebounce((urlToValidate: string) => {
    // Validation is now handled by the Gemini service
    // Just check basic URL format here
    if (urlToValidate && !urlToValidate.match(/^https?:\/\/.+/)) {
      // Error will be shown in the UI from the Gemini hook
    }
  }, 300);

  const handleUrlChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);
    debouncedUrlValidation(newUrl);
  }, [debouncedUrlValidation]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      toast.error('Please enter a valid URL');
      return;
    }

    if (!isAvailable) {
      toast.error('Gemini service is not available. Please check your API key.');
      return;
    }

    reset(); // Clear previous results
    await handleSummarization(url);
  }, [url, handleSummarization, isAvailable, reset]);

  const handleRetry = useCallback(() => {
    if (url.trim()) {
      handleSubmit(new Event('submit') as any);
    }
  }, [url, handleSubmit]);

  const handleDownload = useCallback(() => {
    if (!result) return;

    const data = {
      title: result.articleTitle,
      summary: result.summary,
      teams: result.teams,
      processingTime: result.processingTime,
      url: url,
      generatedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url_download = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url_download;
    a.download = `pokemon-team-analysis-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url_download);
  }, [result, url]);

  const handleShare = useCallback(() => {
    if (result) {
      const shareData = {
        title: result.articleTitle,
        text: `Check out this translated Pokemon VGC article: ${result.articleTitle}`,
        url: window.location.href
      };
      
      if (navigator.share) {
        navigator.share(shareData);
      } else {
        navigator.clipboard.writeText(shareData.url);
        toast.success('Link copied to clipboard!');
      }
    }
  }, [result]);

  // Memoized utility functions
  const getHpPercentage = useCallback((current: number, max: number) => {
    return (current / max) * 100;
  }, []);

  const getHpColor = useCallback((percentage: number) => {
    if (percentage > 60) return 'bg-green-500';
    if (percentage > 30) return 'bg-yellow-500';
    return 'bg-red-500';
  }, []);

  const getTypeColor = useCallback((type: string) => {
    const typeMap: { [key: string]: string } = {
      'DARK': 'bg-gray-800 text-white',
      'DRAGON': 'bg-purple-600 text-white',
      'GRASS': 'bg-green-500 text-white',
      'FIRE': 'bg-red-500 text-white',
      'GHOST': 'bg-purple-500 text-white',
      'WATER': 'bg-blue-500 text-white',
      'ELECTRIC': 'bg-yellow-400 text-black',
      'ICE': 'bg-blue-200 text-black',
      'FIGHTING': 'bg-red-700 text-white',
      'POISON': 'bg-purple-500 text-white',
      'GROUND': 'bg-yellow-600 text-white',
      'FLYING': 'bg-indigo-400 text-white',
      'PSYCHIC': 'bg-pink-500 text-white',
      'BUG': 'bg-green-600 text-white',
      'ROCK': 'bg-yellow-800 text-white',
      'STEEL': 'bg-gray-500 text-white',
      'FAIRY': 'bg-pink-300 text-black',
      'NORMAL': 'bg-gray-400 text-black'
    };
    return typeMap[type] || 'bg-gray-100 text-gray-800';
  }, []);

  // Memoized computed values
  const isFormValid = useMemo(() => {
    return url.trim() && !error && !isLoading;
  }, [url, error, isLoading]);

  const hasTeams = useMemo(() => {
    return result?.teams && result.teams.length > 0;
  }, [result]);

  // Save teams to localStorage when analysis is complete
  useEffect(() => {
    if (result?.teams && result.teams.length > 0) {
      try {
        // Get existing teams from localStorage
        const existingTeams = localStorage.getItem('translatedTeams');
        const teams = existingTeams ? JSON.parse(existingTeams) : [];
        
        // Create new team entries with proper structure
        const newTeams = result.teams.map((pokemon: any, index: number) => ({
          id: `${Date.now()}-${index}`,
          pokemon: pokemon.name,
          level: 50, // Default level for VGC
          hp: { current: 100, max: 100 },
          status: 'Healthy',
          teraType: pokemon.teraType || 'Not specified',
          item: pokemon.item || 'Not specified',
          ability: pokemon.ability || 'Not specified',
          types: pokemon.types || [],
          moves: pokemon.moves ? pokemon.moves.map((move: string) => ({
            name: move,
            bp: 0, // Base power not available from analysis
            checked: true
          })) : [],
          stats: {
            hp: { base: 0, evs: pokemon.evs?.hp || 0, ivs: 31, final: 0 },
            attack: { base: 0, evs: pokemon.evs?.attack || 0, ivs: 31, final: 0 },
            defense: { base: 0, evs: pokemon.evs?.defense || 0, ivs: 31, final: 0 },
            spAtk: { base: 0, evs: pokemon.evs?.spAtk || 0, ivs: 31, final: 0 },
            spDef: { base: 0, evs: pokemon.evs?.spDef || 0, ivs: 31, final: 0 },
            speed: { base: 0, evs: pokemon.evs?.speed || 0, ivs: 31, final: 0 }
          },
          bst: 0, // Base stat total not calculated
          remainingEvs: 0, // Not calculated
          nature: pokemon.nature || 'Not specified',
          articleTitle: result.articleTitle,
          translatedDate: new Date().toISOString(),
          articleUrl: url
        }));
        
        // Add new teams to existing ones
        const updatedTeams = [...teams, ...newTeams];
        
        // Save back to localStorage
        localStorage.setItem('translatedTeams', JSON.stringify(updatedTeams));
        
        console.log(`Saved ${newTeams.length} teams to localStorage`);
      } catch (error) {
        console.error('Error saving teams to localStorage:', error);
      }
    }
  }, [result, url]);



  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center mr-4">
              <DocumentTextIcon className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Pokemon Team Analyzer
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-300 text-lg max-w-2xl mx-auto">
              Analyze Japanese VGC articles and extract detailed team compositions with AI-powered accuracy
          </p>
        </div>

        {/* URL Input Form */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-8 border border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Pokemon VGC Article URL
              </label>
              <div className="relative">
                <input
                  type="url"
                  id="url"
                  value={url}
                  onChange={handleUrlChange}
                  placeholder="https://pokemon.co.jp/vgc/article..."
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-colors"
                  required
                  disabled={isLoading}
                />
                {isLoading && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
                  </div>
                )}
              </div>
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={!isFormValid}
                className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
              >
                                            {isLoading ? (
                              <>
                                <ArrowPathIcon className="h-5 w-5 mr-2 animate-spin" />
                                Analyzing...
                              </>
                            ) : (
                              <>
                                <DocumentTextIcon className="h-5 w-5 mr-2" />
                                Analyze Article
                              </>
                            )}
              </button>
              {error && (
                <button
                  type="button"
                  onClick={handleRetry}
                  className="px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  <ArrowPathIcon className="h-5 w-5" />
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Translation Error</h3>
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-8">
            {/* Article Header */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-2" />
                  Team Analysis Complete
                </h2>
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center text-gray-600 dark:text-gray-300">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    Processed in: <span className="text-purple-600 dark:text-purple-400 font-medium ml-1">{result.processingTime || 2.3}s</span>
                  </div>
                  <button
                    onClick={handleDownload}
                    className="flex items-center text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                    Download
                  </button>
                  <button
                    onClick={handleShare}
                    className="flex items-center text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
                  >
                    <ShareIcon className="h-4 w-4 mr-1" />
                    Share
                  </button>
                </div>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {result.articleTitle}
              </h3>
            </div>



                                      {/* Pokemon Team Summary */}
                          {hasTeams && (
                            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                                <ChartBarIcon className="h-6 w-6 mr-2 text-blue-500" />
                                Pokemon Team ({result.teams.length} Pokemon)
                              </h3>
                              
                              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
                                {result.teams.map((pokemon, index) => (
                                  <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-center border border-gray-200 dark:border-gray-600">
                                    <div className="font-semibold text-gray-900 dark:text-white text-sm mb-1">
                                      {pokemon.name}
                                    </div>
                                    {pokemon.teraType && pokemon.teraType !== 'Not specified' && (
                                      <div className="text-xs text-gray-600 dark:text-gray-300">
                                        Tera: {pokemon.teraType}
                                      </div>
                                    )}
                                    {pokemon.item && pokemon.item !== 'Not specified' && (
                                      <div className="text-xs text-gray-600 dark:text-gray-300 truncate">
                                        {pokemon.item}
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Detailed Pokemon Analysis */}
                          {hasTeams && (
                            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                                <ChartBarIcon className="h-6 w-6 mr-2 text-blue-500" />
                                Detailed Pokemon Analysis
                              </h3>
                
                <div className="space-y-6">
                  {result.teams.map((pokemon, index) => (
                                                       <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 border border-gray-200 dark:border-gray-600">
                                     {/* Pokemon Header */}
                                     <div className="flex items-center justify-between mb-4">
                                       <h4 className="text-lg font-bold text-gray-900 dark:text-white">
                                         {pokemon.name}
                                       </h4>
                                       {pokemon.teraType && pokemon.teraType !== 'Not specified' && (
                                         <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTypeColor(pokemon.teraType)}`}>
                                           Tera: {pokemon.teraType}
                                         </span>
                                       )}
                                     </div>

                                     {/* Pokemon Details Grid */}
                                     <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                       <div className="space-y-2">
                                         {pokemon.ability && pokemon.ability !== 'Not specified' && (
                                           <div className="flex items-center">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-300 w-16">Ability:</span>
                                             <span className="text-sm text-gray-900 dark:text-white">{pokemon.ability}</span>
                                           </div>
                                         )}
                                         
                                         {pokemon.item && pokemon.item !== 'Not specified' && (
                                           <div className="flex items-center">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-300 w-16">Item:</span>
                                             <span className="text-sm text-gray-900 dark:text-white">{pokemon.item}</span>
                                           </div>
                                         )}
                                         
                                         {pokemon.nature && pokemon.nature !== 'Not specified' && (
                                           <div className="flex items-center">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-300 w-16">Nature:</span>
                                             <span className="text-sm text-gray-900 dark:text-white">{pokemon.nature}</span>
                                           </div>
                                         )}
                                       </div>

                                       <div className="space-y-2">
                                         {pokemon.moves && pokemon.moves.length > 0 && (
                                           <div>
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Moves:</span>
                                             <div className="flex flex-wrap gap-1 mt-1">
                                               {pokemon.moves.map((move: string, moveIndex: number) => (
                                                 <span key={moveIndex} className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded">
                                                   {move}
                                                 </span>
                                               ))}
                                             </div>
                                           </div>
                                         )}
                                       </div>
                                     </div>

                                     {/* EV Spread - Similar to the image format */}
                                     {pokemon.evs && (
                                       <div className="mb-4">
                                         <h5 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Stats:</h5>
                                         <div className="space-y-2">
                                           <div className="flex items-center justify-between">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-8">HP:</span>
                                             <div className="flex items-center flex-1 ml-2">
                                               <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                                                 <div 
                                                   className="bg-yellow-400 h-2 rounded-full" 
                                                   style={{ width: `${(pokemon.evs.hp || 0) / 252 * 100}%` }}
                                                 ></div>
                                               </div>
                                               <span className="text-sm text-gray-900 dark:text-white w-8 text-right">{pokemon.evs.hp || 0}</span>
                                             </div>
                                           </div>
                                           <div className="flex items-center justify-between">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-8">Atk:</span>
                                             <div className="flex items-center flex-1 ml-2">
                                               <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                                                 <div 
                                                   className="bg-pink-400 h-2 rounded-full" 
                                                   style={{ width: `${(pokemon.evs.attack || 0) / 252 * 100}%` }}
                                                 ></div>
                                               </div>
                                               <span className="text-sm text-gray-900 dark:text-white w-8 text-right">{pokemon.evs.attack || 0}</span>
                                             </div>
                                           </div>
                                           <div className="flex items-center justify-between">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-8">Def:</span>
                                             <div className="flex items-center flex-1 ml-2">
                                               <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                                                 <div 
                                                   className="bg-yellow-400 h-2 rounded-full" 
                                                   style={{ width: `${(pokemon.evs.defense || 0) / 252 * 100}%` }}
                                                 ></div>
                                               </div>
                                               <span className="text-sm text-gray-900 dark:text-white w-8 text-right">{pokemon.evs.defense || 0}</span>
                                             </div>
                                           </div>
                                           <div className="flex items-center justify-between">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-8">SpA:</span>
                                             <div className="flex items-center flex-1 ml-2">
                                               <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                                                 <div 
                                                   className="bg-yellow-400 h-2 rounded-full" 
                                                   style={{ width: `${(pokemon.evs.spAtk || 0) / 252 * 100}%` }}
                                                 ></div>
                                               </div>
                                               <span className="text-sm text-gray-900 dark:text-white w-8 text-right">{pokemon.evs.spAtk || 0}</span>
                                             </div>
                                           </div>
                                           <div className="flex items-center justify-between">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-8">SpD:</span>
                                             <div className="flex items-center flex-1 ml-2">
                                               <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                                                 <div 
                                                   className="bg-yellow-400 h-2 rounded-full" 
                                                   style={{ width: `${(pokemon.evs.spDef || 0) / 252 * 100}%` }}
                                                 ></div>
                                               </div>
                                               <span className="text-sm text-gray-900 dark:text-white w-8 text-right">{pokemon.evs.spDef || 0}</span>
                                             </div>
                                           </div>
                                           <div className="flex items-center justify-between">
                                             <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-8">Spe:</span>
                                             <div className="flex items-center flex-1 ml-2">
                                               <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                                                 <div 
                                                   className="bg-yellow-400 h-2 rounded-full" 
                                                   style={{ width: `${(pokemon.evs.speed || 0) / 252 * 100}%` }}
                                                 ></div>
                                               </div>
                                               <span className="text-sm text-gray-900 dark:text-white w-8 text-right">{pokemon.evs.speed || 0}</span>
                                             </div>
                                           </div>
                                         </div>
                                       </div>
                                     )}

                                     {/* EV Explanation */}
                                     {pokemon.evExplanation && pokemon.evExplanation !== 'Not specified' && (
                                       <div className="bg-white dark:bg-gray-600 rounded-lg p-4 border border-gray-200 dark:border-gray-500">
                                         <h5 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">EV Explanation & Key Calculations:</h5>
                                         <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                                           {pokemon.evExplanation}
                                         </p>
                                       </div>
                                     )}
                                   </div>
                  ))}
                </div>
              </div>
            )}

            {/* Conclusion Summary */}
            {result.summary && (
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <DocumentTextIcon className="h-6 w-6 mr-2 text-purple-500" />
                  Article Summary & Analysis
                </h3>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                    {result.summary}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Summarizer; 