"""
Pokemon Damage Calculator for Gen 9 VGC
Based on official Pokemon damage formula
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PokemonStats:
    """Pokemon stats at level 50"""

    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    level: int = 50


@dataclass
class Move:
    """Move data for damage calculation"""

    name: str
    power: int
    type: str
    category: str  # 'Physical', 'Special', 'Status'
    accuracy: int = 100
    pp: int = 8
    description: str = ""


@dataclass
class DamageModifiers:
    """Modifiers for damage calculation"""

    weather: float = 1.0  # Rain/Sun boosts
    terrain: float = 1.0  # Electric/Psychic/Grassy/Misty Terrain
    ability_attacker: float = 1.0  # Attacker ability modifier
    ability_defender: float = 1.0  # Defender ability modifier
    item_attacker: float = 1.0  # Life Orb, Choice items, etc.
    item_defender: float = 1.0  # Assault Vest, berries, etc.
    crit: bool = False
    burn: bool = False  # Burn reduces physical attack by 50%
    screens: bool = False  # Light Screen/Reflect
    friend_guard: bool = False  # Friend Guard reduces damage by 25%
    multi_target: bool = False  # Spread moves in doubles


class DamageCalculator:
    """Gen 9 VGC Damage Calculator"""

    # Type effectiveness chart
    TYPE_CHART = {
        "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
        "Fire": {
            "Fire": 0.5,
            "Water": 0.5,
            "Grass": 2,
            "Ice": 2,
            "Bug": 2,
            "Rock": 0.5,
            "Dragon": 0.5,
            "Steel": 2,
        },
        "Water": {
            "Fire": 2,
            "Water": 0.5,
            "Grass": 0.5,
            "Ground": 2,
            "Rock": 2,
            "Dragon": 0.5,
        },
        "Electric": {
            "Water": 2,
            "Electric": 0.5,
            "Grass": 0.5,
            "Ground": 0,
            "Flying": 2,
            "Dragon": 0.5,
        },
        "Grass": {
            "Fire": 0.5,
            "Water": 2,
            "Grass": 0.5,
            "Poison": 0.5,
            "Ground": 2,
            "Flying": 0.5,
            "Bug": 0.5,
            "Rock": 2,
            "Dragon": 0.5,
            "Steel": 0.5,
        },
        "Ice": {
            "Fire": 0.5,
            "Water": 0.5,
            "Grass": 2,
            "Ice": 0.5,
            "Ground": 2,
            "Flying": 2,
            "Dragon": 2,
            "Steel": 0.5,
        },
        "Fighting": {
            "Normal": 2,
            "Ice": 2,
            "Poison": 0.5,
            "Flying": 0.5,
            "Psychic": 0.5,
            "Bug": 0.5,
            "Rock": 2,
            "Ghost": 0,
            "Dark": 2,
            "Steel": 2,
            "Fairy": 0.5,
        },
        "Poison": {
            "Grass": 2,
            "Poison": 0.5,
            "Ground": 0.5,
            "Rock": 0.5,
            "Ghost": 0.5,
            "Steel": 0,
            "Fairy": 2,
        },
        "Ground": {
            "Fire": 2,
            "Electric": 2,
            "Grass": 0.5,
            "Poison": 2,
            "Flying": 0,
            "Bug": 0.5,
            "Rock": 2,
            "Steel": 2,
        },
        "Flying": {
            "Electric": 0.5,
            "Grass": 2,
            "Ice": 0.5,
            "Fighting": 2,
            "Bug": 2,
            "Rock": 0.5,
            "Steel": 0.5,
        },
        "Psychic": {
            "Fighting": 2,
            "Poison": 2,
            "Psychic": 0.5,
            "Dark": 0,
            "Steel": 0.5,
        },
        "Bug": {
            "Fire": 0.5,
            "Grass": 2,
            "Fighting": 0.5,
            "Poison": 0.5,
            "Flying": 0.5,
            "Psychic": 2,
            "Ghost": 0.5,
            "Dark": 2,
            "Steel": 0.5,
            "Fairy": 0.5,
        },
        "Rock": {
            "Fire": 2,
            "Ice": 2,
            "Fighting": 0.5,
            "Ground": 0.5,
            "Flying": 2,
            "Bug": 2,
            "Steel": 0.5,
        },
        "Ghost": {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
        "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
        "Dark": {
            "Fighting": 0.5,
            "Psychic": 2,
            "Bug": 0.5,
            "Rock": 0.5,
            "Ghost": 2,
            "Dark": 0.5,
            "Fairy": 0.5,
        },
        "Steel": {
            "Fire": 0.5,
            "Water": 0.5,
            "Electric": 0.5,
            "Ice": 2,
            "Rock": 2,
            "Steel": 0.5,
            "Fairy": 2,
        },
        "Fairy": {
            "Fire": 0.5,
            "Fighting": 2,
            "Poison": 0.5,
            "Dragon": 2,
            "Dark": 2,
            "Steel": 0.5,
        },
    }

    @classmethod
    def get_type_effectiveness(
        cls, move_type: str, defender_type1: str, defender_type2: str = None
    ) -> float:
        """Calculate type effectiveness"""
        effectiveness = 1.0

        # Check against first type
        if move_type in cls.TYPE_CHART and defender_type1 in cls.TYPE_CHART[move_type]:
            effectiveness *= cls.TYPE_CHART[move_type][defender_type1]

        # Check against second type if exists
        if (
            defender_type2
            and move_type in cls.TYPE_CHART
            and defender_type2 in cls.TYPE_CHART[move_type]
        ):
            effectiveness *= cls.TYPE_CHART[move_type][defender_type2]

        return effectiveness

    @classmethod
    def calculate_stat(
        cls, base: int, iv: int, ev: int, level: int, nature_modifier: float = 1.0
    ) -> int:
        """Calculate actual stat from base/IV/EV"""
        if base == 1:  # HP calculation
            return (
                math.floor((2 * base + iv + math.floor(ev / 4)) * level / 100)
                + level
                + 10
            )
        else:
            return math.floor(
                (math.floor((2 * base + iv + math.floor(ev / 4)) * level / 100) + 5)
                * nature_modifier
            )

    @classmethod
    def calculate_damage_range(
        cls,
        attacker_stats: PokemonStats,
        defender_stats: PokemonStats,
        move: Move,
        attacker_types: List[str],
        defender_types: List[str],
        modifiers: DamageModifiers = DamageModifiers(),
    ) -> Tuple[int, int, float]:
        """
        Calculate damage range for a move
        Returns (min_damage, max_damage, ko_chance)
        """
        if move.category == "Status":
            return (0, 0, 0.0)

        # Base damage calculation
        level = attacker_stats.level
        power = move.power

        # Get attack and defense stats
        if move.category == "Physical":
            attack = attacker_stats.attack
            defense = defender_stats.defense
            if modifiers.burn and move.category == "Physical":
                attack = math.floor(attack * 0.5)  # Burn reduces physical attack
        else:  # Special
            attack = attacker_stats.sp_attack
            defense = defender_stats.sp_defense

        # Apply modifiers
        attack = math.floor(
            attack * modifiers.ability_attacker * modifiers.item_attacker
        )
        defense = math.floor(
            defense * modifiers.ability_defender * modifiers.item_defender
        )

        # Light Screen / Reflect
        if modifiers.screens:
            if move.category == "Physical":
                defense = math.floor(defense * 1.5)  # Reflect
            else:
                defense = math.floor(defense * 1.5)  # Light Screen

        # Base damage formula
        base_damage = (
            math.floor(
                math.floor(math.floor(2 * level / 5 + 2) * power * attack / defense)
                / 50
            )
            + 2
        )

        # Type effectiveness
        type_effectiveness = cls.get_type_effectiveness(
            move.type,
            defender_types[0],
            defender_types[1] if len(defender_types) > 1 else None,
        )

        # STAB (Same Type Attack Bonus)
        stab = 1.5 if move.type in attacker_types else 1.0

        # Weather/terrain modifiers
        final_modifier = (
            modifiers.weather * modifiers.terrain * stab * type_effectiveness
        )

        # Multi-target modifier (spread moves in doubles)
        if modifiers.multi_target:
            final_modifier *= 0.75

        # Friend Guard
        if modifiers.friend_guard:
            final_modifier *= 0.75

        # Critical hit
        crit_modifier = 1.5 if modifiers.crit else 1.0

        # Random factor range (85-100)
        min_damage = math.floor(base_damage * final_modifier * crit_modifier * 0.85)
        max_damage = math.floor(base_damage * final_modifier * crit_modifier * 1.0)

        # Calculate KO chance
        ko_chance = 1.0 if min_damage >= defender_stats.hp else 0.0
        if max_damage >= defender_stats.hp > min_damage:
            # Approximate KO chance based on damage range
            total_range = max_damage - min_damage + 1
            ko_range = max_damage - defender_stats.hp + 1
            ko_chance = max(0.0, ko_range / total_range)

        return (min_damage, max_damage, ko_chance)

    @classmethod
    def calculate_damage_percentage(cls, damage: int, defender_hp: int) -> float:
        """Calculate damage as percentage of HP"""
        return (damage / defender_hp) * 100 if defender_hp > 0 else 0

    @classmethod
    def bulk_calculation(
        cls, attacker: Dict, defenders: List[Dict], move_name: str, move_data: Dict
    ) -> List[Dict]:
        """Calculate damage against multiple defenders"""
        results = []

        attacker_stats = PokemonStats(**attacker["stats"])
        attacker_types = attacker.get("types", ["Normal"])

        move = Move(
            name=move_name,
            power=move_data.get("power", 80),
            type=move_data.get("type", "Normal"),
            category=move_data.get("category", "Physical"),
        )

        for defender in defenders:
            defender_stats = PokemonStats(**defender["stats"])
            defender_types = defender.get("types", ["Normal"])

            min_dmg, max_dmg, ko_chance = cls.calculate_damage_range(
                attacker_stats, defender_stats, move, attacker_types, defender_types
            )

            min_pct = cls.calculate_damage_percentage(min_dmg, defender_stats.hp)
            max_pct = cls.calculate_damage_percentage(max_dmg, defender_stats.hp)

            results.append(
                {
                    "defender": defender["name"],
                    "min_damage": min_dmg,
                    "max_damage": max_dmg,
                    "min_percentage": round(min_pct, 1),
                    "max_percentage": round(max_pct, 1),
                    "ko_chance": round(ko_chance * 100, 1),
                    "damage_range": f"{min_dmg}-{max_dmg} ({min_pct:.1f}-{max_pct:.1f}%)",
                }
            )

        return results


# Common VGC Pokemon base stats
COMMON_POKEMON_STATS = {
    "Miraidon": {
        "hp": 100,
        "attack": 85,
        "defense": 100,
        "sp_attack": 135,
        "sp_defense": 115,
        "speed": 135,
    },
    "Koraidon": {
        "hp": 100,
        "attack": 135,
        "defense": 115,
        "sp_attack": 85,
        "sp_defense": 100,
        "speed": 135,
    },
    "Flutter Mane": {
        "hp": 55,
        "attack": 55,
        "defense": 55,
        "sp_attack": 135,
        "sp_defense": 135,
        "speed": 135,
    },
    "Iron Valiant": {
        "hp": 74,
        "attack": 130,
        "defense": 90,
        "sp_attack": 120,
        "sp_defense": 60,
        "speed": 116,
    },
    "Dragapult": {
        "hp": 88,
        "attack": 120,
        "defense": 75,
        "sp_attack": 100,
        "sp_defense": 75,
        "speed": 142,
    },
    "Landorus-Therian": {
        "hp": 89,
        "attack": 145,
        "defense": 90,
        "sp_attack": 105,
        "sp_defense": 80,
        "speed": 91,
    },
    "Incineroar": {
        "hp": 95,
        "attack": 115,
        "defense": 90,
        "sp_attack": 80,
        "sp_defense": 90,
        "speed": 60,
    },
    "Raging Bolt": {
        "hp": 125,
        "attack": 73,
        "defense": 91,
        "sp_attack": 137,
        "sp_defense": 89,
        "speed": 75,
    },
    "Chien-Pao": {
        "hp": 80,
        "attack": 120,
        "defense": 80,
        "sp_attack": 90,
        "sp_defense": 65,
        "speed": 135,
    },
    "Urshifu-Rapid": {
        "hp": 100,
        "attack": 130,
        "defense": 100,
        "sp_attack": 63,
        "sp_defense": 60,
        "speed": 97,
    },
}

# Common moves data
COMMON_MOVES = {
    "Thunderbolt": {"power": 90, "type": "Electric", "category": "Special"},
    "Flamethrower": {"power": 90, "type": "Fire", "category": "Special"},
    "Ice Beam": {"power": 90, "type": "Ice", "category": "Special"},
    "Earthquake": {"power": 100, "type": "Ground", "category": "Physical"},
    "Close Combat": {"power": 120, "type": "Fighting", "category": "Physical"},
    "Dragon Pulse": {"power": 85, "type": "Dragon", "category": "Special"},
    "Shadow Ball": {"power": 80, "type": "Ghost", "category": "Special"},
    "U-turn": {"power": 70, "type": "Bug", "category": "Physical"},
    "Moonblast": {"power": 95, "type": "Fairy", "category": "Special"},
    "Stone Edge": {"power": 100, "type": "Rock", "category": "Physical"},
}
