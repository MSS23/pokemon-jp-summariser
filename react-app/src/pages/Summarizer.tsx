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
  const [articleText, setArticleText] = useState('');
  const [inputMode, setInputMode] = useState<'url' | 'text'>('url');
  const { trackSummary } = useAnalytics();
  const { isDark } = useTheme();
  
  // Use Gemini hook for direct integration
  const { summarizeArticle, isLoading, result, error, isAvailable, reset } = useGemini();

  // Handle article summarization with Gemini
  const handleSummarization = useCallback(async (urlToProcess: string, directText?: string) => {
    const loadingToast = toast.loading('Analyzing article with Gemini...', {
      icon: '⚡',
    });

    try {
      await summarizeArticle(urlToProcess, directText);
      trackSummary();
      
      // Save the analyzed team to localStorage for the Teams searched page
      if (result) {
        try {
          const existingTeams = localStorage.getItem('analyzedTeams');
          const teams = existingTeams ? JSON.parse(existingTeams) : [];
          
          // Add the new team analysis
          const newTeam = {
            ...result,
            analyzedAt: new Date().toISOString(),
            id: Date.now().toString()
          };
          
          // Check if this URL has already been analyzed
          const existingIndex = teams.findIndex((team: any) => team.meta?.source === urlToProcess);
          if (existingIndex !== -1) {
            // Update existing entry
            teams[existingIndex] = newTeam;
          } else {
            // Add new entry
            teams.unshift(newTeam); // Add to beginning of array
          }
          
          // Keep only the last 50 analyses to prevent localStorage from getting too large
          const trimmedTeams = teams.slice(0, 50);
          
          localStorage.setItem('analyzedTeams', JSON.stringify(trimmedTeams));
          console.log('Team analysis saved to localStorage');
        } catch (storageError) {
          console.error('Error saving team to localStorage:', storageError);
        }
      }
      
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
  }, [summarizeArticle, trackSummary, result]);

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
    
    if (inputMode === 'url') {
      if (!url.trim()) {
        toast.error('Please enter a valid URL');
        return;
      }
    } else {
      if (!articleText.trim()) {
        toast.error('Please enter article text');
        return;
      }
    }

    if (!isAvailable) {
      toast.error('Gemini service is not available. Please check your API key.');
      return;
    }

    reset(); // Clear previous results
    
    if (inputMode === 'url') {
      await handleSummarization(url);
    } else {
      await handleSummarization('', articleText);
    }
  }, [url, articleText, inputMode, handleSummarization, isAvailable, reset]);

  const handleRetry = useCallback(() => {
    if (url.trim()) {
      handleSubmit(new Event('submit') as any);
    }
  }, [url, handleSubmit]);

  const handleExportJSON = useCallback(() => {
    if (!result) return;

    const data = {
      title: result.title,
      summary: result.summary,
      team: result.team,
      strengths: result.strengths,
      weaknesses: result.weaknesses,
      processingTime: result.meta?.processingTime,
      source: result.meta?.source,
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
  }, [result]);

  const formatEVsShowdown = (evs?: Record<string, number>) => {
    if (!evs) return '';
    const parts: string[] = [];
    const order: Array<[keyof typeof evs, string]> = [
      ['hp', 'HP'], ['attack', 'Atk'], ['defense', 'Def'], ['spAtk', 'SpA'], ['spDef', 'SpD'], ['speed', 'Spe']
    ];
    order.forEach(([key, label]) => {
      const val = (evs as any)[key] ?? 0;
      if (val && val > 0) parts.push(`${val} ${label}`);
    });
    return parts.length ? `EVs: ${parts.join(' / ')}` : '';
  };

  const toShowdownText = (team: any[]) => {
    const lines: string[] = [];
    team.forEach((p) => {
      const name = p.name || 'Unknown';
      const item = p.item && p.item !== 'Not specified' ? ` @ ${p.item}` : '';
      lines.push(`${name}${item}`);
      if (p.ability && p.ability !== 'Not specified') lines.push(`Ability: ${p.ability}`);
      if (p.teraType && p.teraType !== 'Not specified') lines.push(`Tera Type: ${p.teraType}`);
      const evLine = formatEVsShowdown(p.evs);
      if (evLine) lines.push(evLine);
      if (p.nature && p.nature !== 'Not specified') lines.push(`${p.nature} Nature`);
      if (Array.isArray(p.moves)) {
        p.moves.filter(Boolean).forEach((m: string) => lines.push(`- ${m.trim()}`));
      }
      lines.push('');
    });
    return lines.join('\n');
  };

  const handleExportShowdown = useCallback(() => {
    if (!result?.team?.length) return;
    const text = toShowdownText(result.team);
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url_download = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url_download;
    a.download = `team-showdown-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url_download);
  }, [result]);

  const toCSV = (team: any[]) => {
    const headers = ['Name','Ability','Item','Nature','Tera Type','EVs','Moves','EV Explanation'];
    const rows = team.map(p => {
      const evLine = formatEVsShowdown(p.evs).replace(/^EVs: /,'');
      const moves = Array.isArray(p.moves) ? p.moves.join(' | ') : '';
      const cells = [
        p.name || '',
        p.ability || '',
        p.item || '',
        p.nature || '',
        p.teraType || '',
        evLine,
        moves,
        p.evExplanation || ''
      ];
      return cells.map(c => `"${String(c).replace(/"/g,'""')}"`).join(',');
    });
    return [headers.join(','), ...rows].join('\n');
  };

  const handleExportCSV = useCallback(() => {
    if (!result?.team?.length) return;
    const csv = toCSV(result.team);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url_download = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url_download;
    a.download = `team-${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url_download);
  }, [result]);

  const handleShare = useCallback(() => {
    if (result) {
      const shareData = {
        title: result.title,
        text: `Check out this translated Pokemon VGC article: ${result.title}`,
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
    if (inputMode === 'url') {
      return url.trim() && !error && !isLoading;
    } else {
      return articleText.trim() && !error && !isLoading;
    }
  }, [url, articleText, inputMode, error, isLoading]);

  const hasTeams = useMemo(() => {
    return result?.team && result.team.length > 0;
  }, [result]);

  const archetypeTags = useMemo(() => {
    if (!result) return [] as string[];
    const tags = new Set<string>();
    const text = (result.summary || '').toLowerCase();
    const team = result.team || [];

    const hasMove = (moveName: string) => team.some(p => Array.isArray(p.moves) && p.moves.some(m => m.toLowerCase().includes(moveName)));
    const hasAnyMove = (names: string[]) => names.some(n => hasMove(n));
    const hasItem = (itemName: string) => team.some(p => (p.item||'').toLowerCase().includes(itemName));
    const hasAbility = (abilityName: string) => team.some(p => (p.ability||'').toLowerCase().includes(abilityName));

    // Trick Room
    if (text.includes('trick room') || hasMove('trick room')) tags.add('Trick Room');

    // Tailwind
    if (text.includes('tailwind') || hasMove('tailwind')) tags.add('Tailwind');

    // Stall
    const stallSignals = (
      hasAnyMove(['protect','leech seed','recover','roost','strength sap','substitute','iron defense','calm mind','toxic']) ||
      hasItem('leftovers') ||
      hasAbility('regenerator') ||
      text.includes('stall')
    );
    if (stallSignals) tags.add('Stall');

    // Hyper Offense
    const offenseSignals = (
      hasAnyMove(['swords dance','nasty plot','dragon dance','belly drum','tailwind']) ||
      hasItem('choice band') || hasItem('choice specs') || hasItem('life orb') ||
      text.includes('hyper offense')
    );
    if (offenseSignals) tags.add('Hyper Offense');

    // Balance (default iff none of the above OR explicitly mentioned)
    if (text.includes('balance') || (!tags.size)) tags.add('Balance');

    // Limit to requested archetypes
    const order = ['Trick Room','Tailwind','Balance','Hyper Offense','Stall'];
    return order.filter(t => tags.has(t));
  }, [result]);

  // Save teams to localStorage when analysis is complete
  useEffect(() => {
    if (result?.team && result.team.length > 0) {
      try {
        // Get existing teams from localStorage
        const existingTeams = localStorage.getItem('translatedTeams');
        const teams = existingTeams ? JSON.parse(existingTeams) : [];
        
        // Create new team entries with proper structure
        const newTeams = result.team.map((pokemon: any, index: number) => ({
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
          articleTitle: result.title,
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

        {/* Input Form */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-8 border border-gray-200 dark:border-gray-700">
          {/* Input Mode Toggle */}
          <div className="flex space-x-4 mb-6">
            <button
              type="button"
              onClick={() => setInputMode('url')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                inputMode === 'url'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              📄 Article URL
            </button>
            <button
              type="button"
              onClick={() => setInputMode('text')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                inputMode === 'text'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              📝 Paste Article Text
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {inputMode === 'url' ? (
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
                    required={inputMode === 'url'}
                    disabled={isLoading}
                  />
                  {isLoading && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div>
                <label htmlFor="articleText" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Paste Article Text (Japanese or English)
                </label>
                <textarea
                  id="articleText"
                  value={articleText}
                  onChange={(e) => setArticleText(e.target.value)}
                  placeholder="Paste the article text here... (Useful when CORS blocks URL access)"
                  rows={8}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-colors resize-vertical"
                  required={inputMode === 'text'}
                  disabled={isLoading}
                />
              </div>
            )}
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
                    Processed in: <span className="text-purple-600 dark:text-purple-400 font-medium ml-1">{result.meta?.processingTime || 2.3}s</span>
                  </div>
                  <button onClick={handleExportShowdown} className="flex items-center text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                    <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                    Export Showdown
                  </button>
                  <button onClick={handleExportCSV} className="flex items-center text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                    <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                    Export CSV
                  </button>
                  <button onClick={handleExportJSON} className="flex items-center text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                    <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                    Export JSON
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
                {result.title}
              </h3>

              {archetypeTags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {archetypeTags.map(tag => (
                    <span key={tag} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-200 border border-purple-200 dark:border-purple-800">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>



                                      {/* Pokemon Team Summary */}
                          {hasTeams && (
                            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                                <ChartBarIcon className="h-6 w-6 mr-2 text-blue-500" />
                                Pokemon Team ({result.team.length} Pokemon)
                              </h3>
                              
                              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
                                {result.team.map((pokemon, index) => (
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

                          {/* Detailed Pokemon Analysis - REMOVED - Using text format instead */}

            {/* Conclusion Summary */}
            {result.summary && (
              <div className="bg-gray-900 text-gray-100 rounded-2xl shadow-lg p-6 border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                  <DocumentTextIcon className="h-6 w-6 mr-2 text-purple-400" />
                  Article Summary & Analysis
                </h3>
                
                {/* Article Title */}
                <div className="mb-6">
                  <h4 className="text-lg font-bold text-white mb-2">
                    <strong>TITLE: {result.title}</strong>
                  </h4>
                </div>

                {/* Pokemon Details */}
                {hasTeams && (
                  <div className="mb-6">
                    <h4 className="text-lg font-bold text-white mb-4">
                      <strong>CONCLUSION:</strong>
                    </h4>
                    
                    {/* Pokemon Cards */}
                    <div className="space-y-6">
                      {result.team.map((pokemon, index) => {
                        console.log(`DEBUG: Pokemon ${index + 1} data:`, pokemon);
                        return (
                          <div key={index} className="bg-white dark:bg-gray-700 rounded-2xl shadow-lg border-2 border-gray-200 dark:border-gray-600 overflow-hidden">
                            {/* Pokemon Header with Gradient */}
                            <div className="bg-gradient-to-r from-blue-500 to-blue-700 text-white p-6 relative">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                  <div className="bg-white/25 rounded-full w-10 h-10 flex items-center justify-center mr-4 font-bold text-lg border-2 border-white/30">
                                    {index + 1}
                                  </div>
                                  <h5 className="text-2xl font-bold">
                                    {pokemon.name}
                                  </h5>
                                </div>
                                {pokemon.teraType && pokemon.teraType !== 'Not specified' && (
                                  <div className="bg-white/20 px-4 py-2 rounded-full font-bold text-sm border border-white/30">
                                    Tera: {pokemon.teraType}
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Content Section */}
                            <div className="p-6">
                              {/* Two Column Layout */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                {/* Basic Info Column */}
                                <div>
                                  <h6 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                                    ⚡ Basic Info
                                  </h6>
                                  <div className="space-y-3">
                                    {pokemon.ability && pokemon.ability !== 'Not specified' && (
                                      <div className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded-lg p-3">
                                        <div className="font-bold text-gray-600 dark:text-gray-300 text-sm mb-1">Ability</div>
                                        <div className="text-gray-900 dark:text-white font-semibold">{pokemon.ability}</div>
                                      </div>
                                    )}
                                    
                                    {pokemon.item && pokemon.item !== 'Not specified' && (
                                      <div className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded-lg p-3">
                                        <div className="font-bold text-gray-600 dark:text-gray-300 text-sm mb-1">Item</div>
                                        <div className="text-gray-900 dark:text-white font-semibold">{pokemon.item}</div>
                                      </div>
                                    )}
                                    
                                    {pokemon.nature && pokemon.nature !== 'Not specified' && (
                                      <div className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded-lg p-3">
                                        <div className="font-bold text-gray-600 dark:text-gray-300 text-sm mb-1">Nature</div>
                                        <div className="text-gray-900 dark:text-white font-semibold">{pokemon.nature}</div>
                                      </div>
                                    )}
                                  </div>
                                </div>

                                {/* Moves Column */}
                                <div>
                                  <h6 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                                    ⚔️ Moves
                                  </h6>
                                  {pokemon.moves && pokemon.moves.length > 0 ? (
                                    <div className="flex flex-wrap gap-2">
                                      {pokemon.moves.map((move: string, moveIndex: number) => (
                                        <span key={moveIndex} className="bg-blue-500 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-md">
                                          {move}
                                        </span>
                                      ))}
                                    </div>
                                  ) : (
                                    <div className="text-gray-500 dark:text-gray-400 italic text-lg">No moves specified</div>
                                  )}
                                </div>
                              </div>

                              {/* EV Spread Section */}
                              {pokemon.evs && (
                                <div className="mb-6">
                                  <h6 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                                    📊 EV Spread
                                  </h6>
                                  <div className="space-y-3">
                                    {[
                                      { key: 'hp', label: 'HP', color: 'bg-red-500' },
                                      { key: 'attack', label: 'Atk', color: 'bg-orange-500' },
                                      { key: 'defense', label: 'Def', color: 'bg-yellow-500' },
                                      { key: 'spAtk', label: 'SpA', color: 'bg-green-500' },
                                      { key: 'spDef', label: 'SpD', color: 'bg-cyan-500' },
                                      { key: 'speed', label: 'Spe', color: 'bg-purple-500' }
                                    ].map((stat) => {
                                      const evValue = pokemon.evs[stat.key] || 0;
                                      const percentage = (evValue / 252) * 100;
                                      return (
                                        <div key={stat.key} className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded-lg p-4">
                                          <div className="flex items-center justify-between mb-2">
                                            <span className="font-bold text-gray-700 dark:text-gray-300">{stat.label}</span>
                                            <span className="font-bold text-gray-900 dark:text-white">{evValue}</span>
                                          </div>
                                          <div className="w-full h-3 bg-gray-200 dark:bg-gray-500 rounded-full overflow-hidden border border-gray-300 dark:border-gray-400">
                                            <div 
                                              className={`h-full ${stat.color} rounded-full transition-all duration-300`}
                                              style={{ width: `${percentage}%` }}
                                            ></div>
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                              
                              {/* Fallback EV Display */}
                              {!pokemon.evs && (
                                <div className="mb-6">
                                  <h6 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                                    📊 EV Spread
                                  </h6>
                                  <div className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded-lg p-4">
                                    <div className="text-gray-500 dark:text-gray-400 italic">
                                      EV spread not available
                                    </div>
                                    {pokemon.evSpread && (
                                      <div className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                                        Raw data: {pokemon.evSpread}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}

                              {/* EV Explanation Section */}
                              {pokemon.evExplanation && pokemon.evExplanation !== 'Not specified' && (
                                <div>
                                  <h6 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                                    🧠 Strategy & EV Explanation
                                  </h6>
                                  <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-2 border-blue-200 dark:border-blue-700 rounded-xl p-5">
                                    <div className="text-blue-900 dark:text-blue-100 font-medium leading-relaxed whitespace-pre-line">
                                      {pokemon.evExplanation.split('.').map((sentence, idx) => {
                                        const trimmed = sentence.trim();
                                        if (trimmed && trimmed.length > 20) {
                                          return (
                                            <div key={idx} className="mb-3 flex items-start">
                                              <span className="text-blue-600 dark:text-blue-300 mr-2 mt-1">•</span>
                                              <span>{trimmed}{!trimmed.endsWith('.') ? '.' : ''}</span>
                                            </div>
                                          );
                                        }
                                        return null;
                                      })}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Conclusion */}
                <div className="mb-6">
                  <h4 className="text-lg font-bold text-white mb-2">
                    <strong>CONCLUSION:</strong>
                  </h4>
                  <div className="text-sm text-gray-300 ml-4">
                    {result.summary}
                  </div>
                </div>

                {/* Team Strengths */}
                {result.strengths && result.strengths.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-bold text-white mb-2">
                      <strong>TEAM STRENGTHS:</strong>
                    </h4>
                    <div className="text-sm text-gray-300 ml-4">
                      <ul className="list-disc list-inside space-y-1">
                        {result.strengths.map((strength: string, index: number) => (
                          <li key={index}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Team Weaknesses */}
                {result.weaknesses && result.weaknesses.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-bold text-white mb-2">
                      <strong>TEAM WEAKNESSES:</strong>
                    </h4>
                    <div className="text-sm text-gray-300 ml-4">
                      <ul className="list-disc list-inside space-y-1">
                        {result.weaknesses.map((weakness: string, index: number) => (
                          <li key={index}>{weakness}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Final Article Summary */}
                <div>
                  <h4 className="text-lg font-bold text-white mb-2">
                    <strong>FINAL ARTICLE SUMMARY:</strong>
                  </h4>
                  <div className="text-sm text-gray-300 ml-4">
                    The article is a reflection on the author's performance in Season 30 of Pokémon SV Double Battles. The author discusses their team composition, strategy, and key insights from their competitive experience.
                  </div>
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