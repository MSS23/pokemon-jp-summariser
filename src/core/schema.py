"""Response schema for the Gemini analysis call (passed as response_schema)."""

from typing import Any, Dict, List

from pydantic import BaseModel


class EVSpread(BaseModel):
    hp: int = 0
    attack: int = 0
    defense: int = 0
    special_attack: int = 0
    special_defense: int = 0
    speed: int = 0


class Pokemon(BaseModel):
    name: str
    ability: str
    held_item: str
    tera_type: str
    nature: str
    ev_spread: EVSpread
    evs: str
    moves: List[str]
    ev_explanation: str
    role_in_team: str


class TeamAnalysis(BaseModel):
    title: str
    author: str
    regulation: str
    pokemon_team: List[Pokemon]
    overall_strategy: str
    team_strengths: str
    team_weaknesses: str
    team_synergies: str
    meta_analysis: str
    tournament_context: str
    full_translation: str
    translation_notes: str
    content_summary: str


# The rest of the app reads EVs under these display keys.
_EV_KEYS = {
    "hp": "HP", "attack": "Attack", "defense": "Defense",
    "special_attack": "Special Attack", "special_defense": "Special Defense", "speed": "Speed",
}


def to_result_dict(analysis: TeamAnalysis) -> Dict[str, Any]:
    """Convert the parsed model into the dict shape the UI and validators expect."""
    result = analysis.model_dump()
    for mon in result["pokemon_team"]:
        spread = {_EV_KEYS[k]: v for k, v in mon["ev_spread"].items()}
        spread["total"] = sum(spread.values())
        mon["ev_spread"] = spread
    return result
