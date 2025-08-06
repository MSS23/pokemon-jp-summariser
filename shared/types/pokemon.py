"""
Shared type definitions for Pokemon data structures.
"""

from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Pokemon:
    """Pokemon data structure"""
    name: str
    ability: Optional[str] = None
    moves: List[str] = None
    tera_type: Optional[str] = None
    item: Optional[str] = None
    nature: Optional[str] = None
    evs: Optional[Dict[str, int]] = None
    ivs: Optional[Dict[str, int]] = None
    
    def __post_init__(self):
        if self.moves is None:
            self.moves = []

@dataclass
class Team:
    """Pokemon team data structure"""
    pokemon: List[Pokemon]
    format: Optional[str] = None
    source_url: Optional[str] = None
    created_at: Optional[datetime] = None
    author: Optional[str] = None
    
    def __post_init__(self):
        if self.pokemon is None:
            self.pokemon = []

@dataclass
class Summary:
    """Article summary data structure"""
    title: str
    content: str
    teams: List[Team]
    pokemon_mentioned: List[str]
    source_url: str
    created_at: datetime
    model_used: str
    processing_time: float
    
    def __post_init__(self):
        if self.teams is None:
            self.teams = []
        if self.pokemon_mentioned is None:
            self.pokemon_mentioned = []

@dataclass
class User:
    """User data structure"""
    username: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, any]] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}

@dataclass
class Analytics:
    """Analytics data structure"""
    total_searches: int
    total_teams_viewed: int
    total_summaries: int
    favorite_pokemon: List[tuple]
    recent_activity: List[Dict[str, any]]
    
    def __post_init__(self):
        if self.favorite_pokemon is None:
            self.favorite_pokemon = []
        if self.recent_activity is None:
            self.recent_activity = []

# Type aliases for common use cases
PokemonList = List[Pokemon]
TeamList = List[Team]
SummaryList = List[Summary]
UserList = List[User]

# API response types
APIResponse = Dict[str, Union[str, int, bool, List, Dict]]
ErrorResponse = Dict[str, str]
SuccessResponse = Dict[str, Union[str, Dict, List]] 