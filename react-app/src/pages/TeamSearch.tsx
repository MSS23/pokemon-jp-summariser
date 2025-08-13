import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArticleAnalysis } from '../services/geminiService';

interface TeamSearchProps {
  // Props if needed
}

const TeamSearch: React.FC<TeamSearchProps> = () => {
  const [teams, setTeams] = useState<ArticleAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTeam, setSelectedTeam] = useState<ArticleAnalysis | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // Load teams from localStorage or API
    loadTeams();
  }, []);

  const loadTeams = () => {
    try {
      const savedTeams = localStorage.getItem('analyzedTeams');
      if (savedTeams) {
        const parsedTeams = JSON.parse(savedTeams);
        setTeams(parsedTeams);
      }
    } catch (error) {
      console.error('Error loading teams:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRowClick = (team: ArticleAnalysis) => {
    setSelectedTeam(team);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedTeam(null);
  };

  const getPokemonList = (team: ArticleAnalysis) => {
    return team.team.map(pokemon => pokemon.name).join(', ');
  };

  const getSummaryPreview = (summary: string) => {
    // Extract the conclusion or first part of the summary
    const conclusionMatch = summary.match(/CONCLUSION[:\s]*([\s\S]*?)(?=\*\*|$)/i);
    if (conclusionMatch) {
      return conclusionMatch[1].substring(0, 150) + '...';
    }
    
    // Fallback to first 150 characters
    return summary.substring(0, 150) + '...';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading teams...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Teams Analyzed</h1>
          <p className="text-gray-600">
            View all the Pokémon teams that have been analyzed. Click on any row to see detailed information.
          </p>
        </div>

        {/* Teams Table */}
        {teams.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No teams analyzed yet</h3>
            <p className="text-gray-500 mb-6">
              Start by analyzing a Pokémon team article to see it appear here.
            </p>
            <Link
              to="/"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Analyze a Team
            </Link>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Team Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pokémon
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Summary Preview
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {teams.map((team, index) => (
                    <tr
                      key={index}
                      onClick={() => handleRowClick(team)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors duration-150"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {team.title || 'Untitled Team'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {team.meta.source}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {getPokemonList(team)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-md">
                          {getSummaryPreview(team.summary)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date().toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Modal for detailed view */}
      {showModal && selectedTeam && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              {/* Header */}
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  {selectedTeam.title || 'Team Details'}
                </h3>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Source URL */}
              <div className="mb-6">
                <p className="text-sm text-gray-600">
                  <strong>Source:</strong>{' '}
                  <a
                    href={selectedTeam.meta.source}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    {selectedTeam.meta.source}
                  </a>
                </p>
              </div>

              {/* Team Members */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Team Members</h4>
                <div className="space-y-6">
                  {selectedTeam.team.map((pokemon, index) => (
                    <div key={index} className="bg-white dark:bg-gray-700 rounded-2xl shadow-lg border-2 border-gray-200 dark:border-gray-600 overflow-hidden">
                      {/* Pokemon Header with Gradient */}
                      <div className="bg-gradient-to-r from-blue-500 to-blue-700 text-white p-4 relative">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="bg-white/25 rounded-full w-8 h-8 flex items-center justify-center mr-3 font-bold text-sm border-2 border-white/30">
                              {index + 1}
                            </div>
                            <h5 className="text-xl font-bold">
                              {pokemon.name}
                            </h5>
                          </div>
                          {pokemon.teraType && pokemon.teraType !== 'Not specified' && (
                            <div className="bg-white/20 px-3 py-1 rounded-full font-bold text-xs border border-white/30">
                              Tera: {pokemon.teraType}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Content Section */}
                      <div className="p-4">
                        {/* Two Column Layout */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          {/* Basic Info Column */}
                          <div>
                            <h6 className="text-sm font-bold text-gray-900 dark:text-white mb-2 flex items-center">
                              ⚡ Basic Info
                            </h6>
                            <div className="space-y-2">
                              {pokemon.ability && pokemon.ability !== 'Not specified' && (
                                <div className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded p-2">
                                  <div className="font-bold text-gray-600 dark:text-gray-300 text-xs mb-1">Ability</div>
                                  <div className="text-gray-900 dark:text-white font-semibold text-sm">{pokemon.ability}</div>
                                </div>
                              )}
                              
                              {pokemon.item && pokemon.item !== 'Not specified' && (
                                <div className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded p-2">
                                  <div className="font-bold text-gray-600 dark:text-gray-300 text-xs mb-1">Item</div>
                                  <div className="text-gray-900 dark:text-white font-semibold text-sm">{pokemon.item}</div>
                                </div>
                              )}
                              
                              {pokemon.nature && pokemon.nature !== 'Not specified' && (
                                <div className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded p-2">
                                  <div className="font-bold text-gray-600 dark:text-gray-300 text-xs mb-1">Nature</div>
                                  <div className="text-gray-900 dark:text-white font-semibold text-sm">{pokemon.nature}</div>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Moves Column */}
                          <div>
                            <h6 className="text-sm font-bold text-gray-900 dark:text-white mb-2 flex items-center">
                              ⚔️ Moves
                            </h6>
                            {pokemon.moves && pokemon.moves.length > 0 ? (
                              <div className="flex flex-wrap gap-1">
                                {pokemon.moves.map((move: string, moveIndex: number) => (
                                  <span key={moveIndex} className="bg-blue-500 text-white px-2 py-1 rounded-full text-xs font-semibold shadow-sm">
                                    {move}
                                  </span>
                                ))}
                              </div>
                            ) : (
                              <div className="text-gray-500 dark:text-gray-400 italic text-sm">No moves specified</div>
                            )}
                          </div>
                        </div>

                        {/* EV Spread Section */}
                        {pokemon.evs && (
                          <div className="mb-4">
                            <h6 className="text-sm font-bold text-gray-900 dark:text-white mb-2 flex items-center">
                              📊 EV Spread
                            </h6>
                            <div className="space-y-2">
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
                                  <div key={stat.key} className="bg-gray-50 dark:bg-gray-600 border border-gray-200 dark:border-gray-500 rounded p-2">
                                    <div className="flex items-center justify-between mb-1">
                                      <span className="font-bold text-gray-700 dark:text-gray-300 text-xs">{stat.label}</span>
                                      <span className="font-bold text-gray-900 dark:text-white text-xs">{evValue}</span>
                                    </div>
                                    <div className="w-full h-2 bg-gray-200 dark:bg-gray-500 rounded-full overflow-hidden border border-gray-300 dark:border-gray-400">
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

                        {/* EV Explanation Section - Enhanced for better detail display */}
                        {pokemon.evExplanation && pokemon.evExplanation !== 'Not specified' && (
                          <div>
                            <h6 className="text-sm font-bold text-gray-900 dark:text-white mb-2 flex items-center">
                              📈 EV Strategy & Explanation
                            </h6>
                            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-2 border-blue-200 dark:border-blue-700 rounded-lg p-3">
                              <div className="text-blue-900 dark:text-blue-100 font-medium text-xs leading-relaxed">
                                {pokemon.evExplanation.split('\n\n').map((paragraph, idx) => {
                                  const trimmed = paragraph.trim();
                                  if (trimmed && trimmed.length > 10) {
                                    // Check for key benchmark information
                                    const isBenchmark = /survive|survival|benchmark|outspeed|damage|ohko|2hko/i.test(trimmed);
                                    // Check for strategic reasoning
                                    const isStrategic = /strategy|reasoning|consider|decide|choose|because|reason/i.test(trimmed);
                                    
                                    if (isBenchmark) {
                                      return (
                                        <div key={idx} className="mb-2 p-2 bg-amber-50 dark:bg-amber-900/20 border-l-2 border-amber-400 dark:border-amber-500 rounded-r text-xs">
                                          <span className="font-semibold text-amber-800 dark:text-amber-200">🎯 </span>
                                          {trimmed}
                                        </div>
                                      );
                                    } else if (isStrategic) {
                                      return (
                                        <div key={idx} className="mb-2 p-2 bg-blue-50 dark:bg-blue-900/20 border-l-2 border-blue-400 dark:border-blue-500 rounded-r text-xs">
                                          <span className="font-semibold text-blue-800 dark:text-blue-200">🧠 </span>
                                          {trimmed}
                                        </div>
                                      );
                                    } else {
                                      return (
                                        <div key={idx} className="mb-1 flex items-start text-xs">
                                          <span className="text-blue-600 dark:text-blue-300 mr-1 mt-0.5">•</span>
                                          <span>{trimmed}</span>
                                        </div>
                                      );
                                    }
                                  }
                                  return null;
                                })}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strengths and Weaknesses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-2 border-green-200 dark:border-green-700 rounded-xl p-4">
                  <h4 className="text-lg font-semibold text-green-700 dark:text-green-300 mb-3 flex items-center">
                    ✅ Team Strengths
                  </h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-700 dark:text-gray-300">
                    {selectedTeam.strengths.length > 0 ? (
                      selectedTeam.strengths.map((strength, index) => (
                        <li key={index}>{strength}</li>
                      ))
                    ) : (
                      <li className="text-gray-500 dark:text-gray-400">No specific strengths mentioned</li>
                    )}
                  </ul>
                </div>
                <div className="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 border-2 border-red-200 dark:border-red-700 rounded-xl p-4">
                  <h4 className="text-lg font-semibold text-red-700 dark:text-red-300 mb-3 flex items-center">
                    ⚠️ Team Weaknesses
                  </h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-700 dark:text-gray-300">
                    {selectedTeam.weaknesses.length > 0 ? (
                      selectedTeam.weaknesses.map((weakness, index) => (
                        <li key={index}>{weakness}</li>
                      ))
                    ) : (
                      <li className="text-gray-500 dark:text-gray-400">No specific weaknesses mentioned</li>
                    )}
                  </ul>
                </div>
              </div>

              {/* Full Summary */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  📰 Full Analysis
                </h4>
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-2 border-blue-200 dark:border-blue-700 rounded-xl p-4 max-h-96 overflow-y-auto">
                  <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                    {selectedTeam.summary}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="mt-6 flex justify-end">
                <button
                  onClick={closeModal}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamSearch; 