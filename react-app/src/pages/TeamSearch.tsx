import { useState, useEffect } from 'react';
import { useAnalytics } from '../context/AnalyticsContext';
import { MagnifyingGlassIcon, FunnelIcon, CalendarIcon, TagIcon } from '@heroicons/react/24/outline';

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

const TeamSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [teams, setTeams] = useState<TranslatedTeam[]>([]);
  const [allTeams, setAllTeams] = useState<TranslatedTeam[]>([]);
  const [filteredTeams, setFilteredTeams] = useState<TranslatedTeam[]>([]);
  const [selectedDateRange, setSelectedDateRange] = useState('All Dates');
  const [selectedPokemon, setSelectedPokemon] = useState<string[]>([]);
  const [selectedMoves, setSelectedMoves] = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const { trackSearch } = useAnalytics();




  

  useEffect(() => {
    // Filter teams based on search query and filters
    let filtered = allTeams;

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(team =>
        team.pokemon.toLowerCase().includes(searchQuery.toLowerCase()) ||
        team.articleTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
        team.moves.some(move => move.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
        team.ability.toLowerCase().includes(searchQuery.toLowerCase()) ||
        team.item.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by Pokemon (multiple selection)
    if (selectedPokemon.length > 0) {
      filtered = filtered.filter(team => selectedPokemon.includes(team.pokemon));
    }

    // Filter by moves (multiple selection)
    if (selectedMoves.length > 0) {
      filtered = filtered.filter(team => 
        selectedMoves.some(move => 
          team.moves.some(teamMove => teamMove.name.toLowerCase() === move.toLowerCase())
        )
      );
    }

    // Filter by types (multiple selection)
    if (selectedTypes.length > 0) {
      filtered = filtered.filter(team => 
        selectedTypes.some(type => 
          team.types.some(teamType => teamType.toLowerCase() === type.toLowerCase())
        )
      );
    }

    // Filter by date range
    if (selectedDateRange !== 'All Dates') {
      const now = new Date();
      const teamDate = new Date();
      
      switch (selectedDateRange) {
        case 'Last 7 days':
          teamDate.setDate(now.getDate() - 7);
          break;
        case 'Last 30 days':
          teamDate.setDate(now.getDate() - 30);
          break;
        case 'Last 3 months':
          teamDate.setMonth(now.getMonth() - 3);
          break;
      }
      
      filtered = filtered.filter(team => new Date(team.translatedDate) >= teamDate);
    }

    setFilteredTeams(filtered);
  }, [allTeams, searchQuery, selectedPokemon, selectedMoves, selectedTypes, selectedDateRange]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    trackSearch(query);
  };

  const getTypeColor = (type: string) => {
    const typeMap: { [key: string]: string } = {
      'DARK': 'type-dark',
      'DRAGON': 'type-dragon',
      'GRASS': 'type-grass',
      'FIRE': 'type-fire',
      'GHOST': 'type-ghost',
      'WATER': 'type-water',
      'ELECTRIC': 'type-electric',
      'ICE': 'type-ice',
      'FIGHTING': 'type-fighting',
      'POISON': 'type-poison',
      'GROUND': 'type-ground',
      'FLYING': 'type-flying',
      'PSYCHIC': 'type-psychic',
      'BUG': 'type-bug',
      'ROCK': 'type-rock',
      'STEEL': 'type-steel',
      'FAIRY': 'type-fairy',
      'NORMAL': 'type-normal'
    };
    return typeMap[type] || 'bg-gray-100 text-gray-800';
  };

  const getUniquePokemon = () => {
    const pokemon = allTeams.map(team => team.pokemon);
    return Array.from(new Set(pokemon)).sort();
  };

  const getUniqueMoves = () => {
    const moves = allTeams.flatMap(team => team.moves.map(move => move.name));
    return Array.from(new Set(moves)).sort();
  };

  const getUniqueTypes = () => {
    const types = allTeams.flatMap(team => team.types);
    return Array.from(new Set(types)).sort();
  };

  const handlePokemonToggle = (pokemon: string) => {
    setSelectedPokemon(prev => 
      prev.includes(pokemon) 
        ? prev.filter(p => p !== pokemon)
        : [...prev, pokemon]
    );
  };

  const handleMoveToggle = (move: string) => {
    setSelectedMoves(prev => 
      prev.includes(move) 
        ? prev.filter(m => m !== move)
        : [...prev, move]
    );
  };

  const handleTypeToggle = (type: string) => {
    setSelectedTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">
            Translated Team Search
          </h1>
          <p className="text-gray-200 text-lg">
            Search through your translated Japanese VGC articles and extracted teams
          </p>
        </div>

        {/* Search Form */}
        <div className="card mb-8">
          <form className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <label htmlFor="search" className="block text-sm font-medium text-gray-200 mb-2">
                  Search Teams
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="search"
                    value={searchQuery}
                    onChange={handleSearch}
                    placeholder="Search by Pokemon, strategy, or article title..."
                    className="input-field pl-10"
                  />
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>
              
            </div>
          </form>
        </div>

        {/* Filters */}
        <div className="card mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center">
              <FunnelIcon className="h-5 w-5 mr-2" />
              Filters
            </h2>
            <div className="text-sm text-gray-300">
              {filteredTeams.length} of {allTeams.length} teams
            </div>
          </div>
          
          {/* Date Range Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-200 mb-2 flex items-center">
              <CalendarIcon className="h-4 w-4 mr-1" />
              Date Range
            </label>
            <select 
              value={selectedDateRange} 
              onChange={(e) => setSelectedDateRange(e.target.value)}
              className="input-field w-full md:w-64"
            >
              <option>All Dates</option>
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Last 3 months</option>
            </select>
          </div>

          {/* Pokemon Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Pokemon
            </label>
            <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
              {getUniquePokemon().map(pokemon => (
                <button
                  key={pokemon}
                  onClick={() => handlePokemonToggle(pokemon)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedPokemon.includes(pokemon)
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {pokemon}
                </button>
              ))}
            </div>
          </div>

          {/* Moves Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Moves
            </label>
            <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
              {getUniqueMoves().map(move => (
                <button
                  key={move}
                  onClick={() => handleMoveToggle(move)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedMoves.includes(move)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {move}
                </button>
              ))}
            </div>
          </div>

          {/* Types Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Types
            </label>
            <div className="flex flex-wrap gap-2">
              {getUniqueTypes().map(type => (
                <button
                  key={type}
                  onClick={() => handleTypeToggle(type)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedTypes.includes(type)
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Clear Filters Button */}
          <div className="flex justify-end">
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedPokemon([]);
                setSelectedMoves([]);
                setSelectedTypes([]);
                setSelectedDateRange('All Dates');
              }}
              className="btn-secondary"
            >
              Clear All Filters
            </button>
          </div>
        </div>

        {/* Search Results */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              Translated Teams
            </h2>
            <p className="text-gray-300">
              {filteredTeams.length > 0 ? `${filteredTeams.length} teams found` : 'No teams found'}
            </p>
          </div>

          {/* Team Results */}
          {filteredTeams.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredTeams.map((team) => (
                <div key={team.id} className="card hover:bg-gray-750 transition-all duration-300">
                  {/* Pokemon Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-white">{team.pokemon}</h3>
                      <p className="text-sm text-gray-300">Lv. {team.level}</p>
                    </div>
                  </div>

                  {/* Article Info */}
                  <div className="mb-4 p-3 bg-gray-700 rounded-lg">
                    <p className="text-sm text-gray-200 font-medium">{team.articleTitle}</p>
                    <p className="text-xs text-gray-400">Translated: {new Date(team.translatedDate).toLocaleDateString()}</p>
                  </div>

                  {/* Pokemon Details */}
                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div>
                      <span className="text-gray-300">Item:</span>
                      <span className="text-white ml-2">{team.item}</span>
                    </div>
                    <div>
                      <span className="text-gray-300">Ability:</span>
                      <span className="text-white ml-2">{team.ability}</span>
                    </div>
                    <div>
                      <span className="text-gray-300">Tera:</span>
                      <span className="text-white ml-2">{team.teraType}</span>
                    </div>
                    <div>
                      <span className="text-gray-300">Nature:</span>
                      <span className="text-white ml-2">{team.nature}</span>
                    </div>
                  </div>

                  {/* Types */}
                  {team.types && team.types.length > 0 && (
                    <div className="mb-4">
                      <div className="flex gap-2">
                        {team.types.map((type) => (
                          <span key={type} className={`pokemon-type ${getTypeColor(type)}`}>
                            {type}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Moves */}
                  {team.moves && team.moves.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-200 mb-2">Moves</h4>
                      <div className="space-y-1">
                        {team.moves.map((move, moveIndex) => (
                          <div key={moveIndex} className={`move-item ${move.checked ? 'move-checked' : ''}`}>
                            <span className="text-white">{move.name}</span>
                            <span className="text-gray-300">BP {move.bp}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* EV Spread */}
                  <div className="text-sm text-gray-300">
                    <div>EVs: {team.stats.hp.evs} HP / {team.stats.attack.evs} Atk / {team.stats.defense.evs} Def / {team.stats.spAtk.evs} SpA / {team.stats.spDef.evs} SpD / {team.stats.speed.evs} Spe</div>
                    <div>BST: {team.bst}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card text-center py-12">
              <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No teams found</h3>
              <p className="text-gray-300">
                Try adjusting your search terms or filters to find translated teams
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamSearch; 