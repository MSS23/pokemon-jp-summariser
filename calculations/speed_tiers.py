"""
Pokemon Speed Tier Analyzer for Gen 9 VGC
Automatic speed benchmark identification and tier analysis
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpeedTierEntry:
    """Speed tier entry for a Pokemon"""

    pokemon_name: str
    base_speed: int
    level: int = 50
    speed_stat_positive: int = 0  # +Speed nature with max EVs
    speed_stat_neutral: int = 0  # Neutral nature with max EVs
    speed_stat_negative: int = 0  # -Speed nature with no EVs
    common_builds: List[int] = None  # Common speed values in meta
    usage_tier: str = "C"  # S, A, B, C, D tier
    regulation: str = "A"

    def __post_init__(self):
        if self.common_builds is None:
            self.common_builds = []


class SpeedTierAnalyzer:
    """Gen 9 VGC Speed Tier Analysis"""

    # Common VGC Pokemon base stats
    VGC_POKEMON_BASE_SPEEDS = {
        "Dragapult": 142,
        "Miraidon": 135,
        "Koraidon": 135,
        "Flutter Mane": 135,
        "Chien-Pao": 135,
        "Iron Valiant": 116,
        "Urshifu-Rapid": 97,
        "Landorus-Therian": 91,
        "Raging Bolt": 75,
        "Incineroar": 60,
        "Torkoal": 20,
        "Amoonguss": 30,
        "Hatterene": 29,
        "Oranguru": 60,
        "Indeedee-Female": 95,
        "Calyrex-Shadow": 150,
        "Calyrex-Ice": 50,
        "Iron Hands": 50,
        "Gholdengo": 84,
        "Annihilape": 90,
        "Garchomp": 102,
        "Chi-Yu": 100,
        "Walking Wake": 109,
        "Iron Bundle": 136,
        "Great Tusk": 87,
        "Ogerpon-Wellspring": 110,
        "Ogerpon-Hearthflame": 110,
        "Ogerpon-Cornerstone": 110,
        "Ogerpon": 110,
    }

    # Speed tier rankings for common meta Pokemon
    SPEED_TIER_RANKINGS = {
        "S": [
            "Calyrex-Shadow",
            "Dragapult",
            "Miraidon",
            "Koraidon",
            "Flutter Mane",
            "Chien-Pao",
            "Iron Bundle",
        ],
        "A": [
            "Iron Valiant",
            "Ogerpon-Wellspring",
            "Ogerpon-Hearthflame",
            "Ogerpon-Cornerstone",
            "Ogerpon",
            "Walking Wake",
            "Garchomp",
            "Chi-Yu",
        ],
        "B": [
            "Urshifu-Rapid",
            "Indeedee-Female",
            "Landorus-Therian",
            "Annihilape",
            "Great Tusk",
            "Gholdengo",
        ],
        "C": ["Raging Bolt", "Oranguru", "Incineroar", "Iron Hands", "Calyrex-Ice"],
        "D": ["Amoonguss", "Hatterene", "Torkoal"],
    }

    @classmethod
    def calculate_speed_stat(
        cls,
        base_speed: int,
        iv: int = 31,
        ev: int = 0,
        level: int = 50,
        nature_modifier: float = 1.0,
    ) -> int:
        """Calculate speed stat from base/IV/EV/nature"""
        return math.floor(
            (math.floor((2 * base_speed + iv + math.floor(ev / 4)) * level / 100) + 5)
            * nature_modifier
        )

    @classmethod
    def get_speed_tier_entry(
        cls, pokemon_name: str, regulation: str = "A"
    ) -> SpeedTierEntry:
        """Generate speed tier entry for a Pokemon"""
        base_speed = cls.VGC_POKEMON_BASE_SPEEDS.get(pokemon_name, 80)

        # Calculate common speed values
        speed_positive = cls.calculate_speed_stat(
            base_speed, ev=252, nature_modifier=1.1
        )  # +Speed nature
        speed_neutral = cls.calculate_speed_stat(
            base_speed, ev=252, nature_modifier=1.0
        )  # Neutral nature
        speed_negative = cls.calculate_speed_stat(
            base_speed, ev=0, nature_modifier=0.9
        )  # -Speed nature

        # Determine usage tier
        usage_tier = "C"  # Default
        for tier, pokemon_list in cls.SPEED_TIER_RANKINGS.items():
            if pokemon_name in pokemon_list:
                usage_tier = tier
                break

        # Common builds - generate typical speed values seen in tournament play
        common_builds = []
        if usage_tier in ["S", "A"]:
            # High tier Pokemon usually invest in speed
            common_builds = [speed_positive, speed_neutral]
            if base_speed >= 100:
                # Also include some mid-investment builds
                speed_mid = cls.calculate_speed_stat(
                    base_speed, ev=156, nature_modifier=1.1
                )
                common_builds.append(speed_mid)
        elif usage_tier == "B":
            # Mid tier Pokemon have varied builds
            common_builds = [speed_positive, speed_neutral]
            speed_mid = cls.calculate_speed_stat(
                base_speed, ev=100, nature_modifier=1.0
            )
            common_builds.append(speed_mid)
        else:
            # Lower tier Pokemon often don't invest in speed
            common_builds = [speed_neutral, speed_negative]
            speed_min = cls.calculate_speed_stat(base_speed, ev=0, nature_modifier=1.0)
            common_builds.append(speed_min)

        return SpeedTierEntry(
            pokemon_name=pokemon_name,
            base_speed=base_speed,
            speed_stat_positive=speed_positive,
            speed_stat_neutral=speed_neutral,
            speed_stat_negative=speed_negative,
            common_builds=sorted(set(common_builds), reverse=True),
            usage_tier=usage_tier,
            regulation=regulation,
        )

    @classmethod
    def analyze_speed_benchmark(cls, target_speed: int, regulation: str = "A") -> Dict:
        """Analyze what a target speed value accomplishes"""
        benchmarks = []
        outspeed_count = 0
        total_relevant_pokemon = 0

        for pokemon_name in cls.VGC_POKEMON_BASE_SPEEDS.keys():
            tier_entry = cls.get_speed_tier_entry(pokemon_name, regulation)

            # Only consider relevant Pokemon for meta analysis
            if tier_entry.usage_tier in ["S", "A", "B"]:
                total_relevant_pokemon += 1

                # Check what builds this speed outspeeds
                outspeeds = []
                for build_speed in tier_entry.common_builds:
                    if target_speed > build_speed:
                        outspeeds.append(f"{pokemon_name} ({build_speed})")
                        outspeed_count += 1

                if outspeeds:
                    benchmarks.extend(outspeeds)

        # Find specific tier cutoffs
        tier_analysis = cls._analyze_tier_cutoffs(target_speed, regulation)

        return {
            "target_speed": target_speed,
            "outspeeds": benchmarks[:10],  # Top 10 most relevant
            "outspeed_percentage": round(
                (outspeed_count / max(total_relevant_pokemon * 2, 1)) * 100, 1
            ),
            "tier_position": tier_analysis["position"],
            "speed_tier": tier_analysis["tier"],
            "recommendations": cls._get_speed_recommendations(
                target_speed, tier_analysis
            ),
        }

    @classmethod
    def _analyze_tier_cutoffs(cls, target_speed: int, regulation: str = "A") -> Dict:
        """Analyze which speed tier a target speed falls into"""
        all_speeds = []

        for pokemon_name in cls.VGC_POKEMON_BASE_SPEEDS.keys():
            tier_entry = cls.get_speed_tier_entry(pokemon_name, regulation)
            if tier_entry.usage_tier in ["S", "A"]:
                all_speeds.extend(tier_entry.common_builds)

        all_speeds = sorted(set(all_speeds), reverse=True)

        position = "Unknown"
        tier = "C"

        if target_speed >= 200:
            position = "Elite"
            tier = "S+"
        elif target_speed >= 180:
            position = "Very Fast"
            tier = "S"
        elif target_speed >= 160:
            position = "Fast"
            tier = "A"
        elif target_speed >= 140:
            position = "Above Average"
            tier = "B+"
        elif target_speed >= 120:
            position = "Average"
            tier = "B"
        elif target_speed >= 100:
            position = "Below Average"
            tier = "C+"
        else:
            position = "Slow"
            tier = "C"

        return {"position": position, "tier": tier}

    @classmethod
    def _get_speed_recommendations(
        cls, target_speed: int, tier_analysis: Dict
    ) -> List[str]:
        """Get recommendations based on speed tier analysis"""
        recommendations = []

        if tier_analysis["tier"] in ["S+", "S"]:
            recommendations.append("Excellent speed tier - outspeeds most threats")
            recommendations.append(
                "Consider this for offensive Pokemon requiring speed control"
            )
        elif tier_analysis["tier"] in ["A", "B+"]:
            recommendations.append("Good speed tier - outspeeds common threats")
            recommendations.append("Suitable for most offensive builds")
        elif tier_analysis["tier"] in ["B", "C+"]:
            recommendations.append("Moderate speed tier - may need priority moves")
            recommendations.append("Consider Trick Room or speed control support")
        else:
            recommendations.append("Low speed tier - ideal for Trick Room")
            recommendations.append("Focus on bulk and priority moves")

        return recommendations

    @classmethod
    def generate_team_speed_analysis(
        cls, team_speeds: List[Tuple[str, int]], regulation: str = "A"
    ) -> Dict:
        """Analyze speed distribution of an entire team"""
        team_analysis = []
        speed_coverage = {"S": 0, "A": 0, "B": 0, "C": 0}

        for pokemon_name, speed in team_speeds:
            analysis = cls.analyze_speed_benchmark(speed, regulation)
            team_analysis.append(
                {
                    "pokemon": pokemon_name,
                    "speed": speed,
                    "tier": analysis["tier_position"],
                    "outspeed_percentage": analysis["outspeed_percentage"],
                }
            )

            # Count tier coverage
            tier = analysis["speed_tier"]
            if tier in ["S+", "S"]:
                speed_coverage["S"] += 1
            elif tier in ["A", "B+"]:
                speed_coverage["A"] += 1
            elif tier in ["B", "C+"]:
                speed_coverage["B"] += 1
            else:
                speed_coverage["C"] += 1

        # Generate team recommendations
        team_recommendations = []
        if speed_coverage["S"] == 0 and speed_coverage["A"] == 0:
            team_recommendations.append(
                "Consider adding faster Pokemon for speed control"
            )
        if speed_coverage["C"] >= 4:
            team_recommendations.append("Excellent Trick Room team composition")
        if speed_coverage["S"] >= 3:
            team_recommendations.append("Strong offensive speed control team")

        return {
            "team_analysis": team_analysis,
            "speed_coverage": speed_coverage,
            "recommendations": team_recommendations,
            "average_outspeed": round(
                sum(p["outspeed_percentage"] for p in team_analysis)
                / len(team_analysis),
                1,
            ),
        }

    @classmethod
    def suggest_speed_evs(
        cls, pokemon_name: str, target_benchmark: str = "auto", regulation: str = "A"
    ) -> Dict:
        """Suggest optimal speed EV investment for a Pokemon"""
        base_speed = cls.VGC_POKEMON_BASE_SPEEDS.get(pokemon_name, 80)
        tier_entry = cls.get_speed_tier_entry(pokemon_name, regulation)

        suggestions = []

        if target_benchmark == "auto":
            # Auto-suggest based on usage tier
            if tier_entry.usage_tier in ["S", "A"]:
                suggestions.append(
                    {
                        "description": "Max Speed (+Speed nature)",
                        "evs": 252,
                        "nature": "Positive",
                        "resulting_speed": tier_entry.speed_stat_positive,
                        "justification": "Outspeeds most threats in current meta",
                    }
                )

                suggestions.append(
                    {
                        "description": "Max Speed (Neutral nature)",
                        "evs": 252,
                        "nature": "Neutral",
                        "resulting_speed": tier_entry.speed_stat_neutral,
                        "justification": "Good speed while preserving other stats",
                    }
                )

            elif tier_entry.usage_tier == "B":
                suggestions.append(
                    {
                        "description": "Moderate Speed Investment",
                        "evs": 156,
                        "nature": "Positive",
                        "resulting_speed": cls.calculate_speed_stat(
                            base_speed, ev=156, nature_modifier=1.1
                        ),
                        "justification": "Outspeed specific threats while investing elsewhere",
                    }
                )

                suggestions.append(
                    {
                        "description": "Minimal Speed",
                        "evs": 4,
                        "nature": "Neutral",
                        "resulting_speed": cls.calculate_speed_stat(
                            base_speed, ev=4, nature_modifier=1.0
                        ),
                        "justification": "Focus on bulk/offense, rely on priority/support",
                    }
                )

            else:  # C, D tier
                suggestions.append(
                    {
                        "description": "Trick Room Build",
                        "evs": 0,
                        "nature": "Negative",
                        "resulting_speed": tier_entry.speed_stat_negative,
                        "justification": "Optimized for Trick Room environments",
                    }
                )

        return {
            "pokemon": pokemon_name,
            "base_speed": base_speed,
            "usage_tier": tier_entry.usage_tier,
            "suggestions": suggestions,
        }


# Pre-calculated speed tiers for quick reference
COMMON_SPEED_BENCHMARKS = {
    "Dragapult Max": 216,
    "Miraidon/Koraidon Max": 209,
    "Flutter Mane Max": 209,
    "Chien-Pao Max": 209,
    "Iron Bundle Max": 210,
    "Iron Valiant Max": 184,
    "Ogerpon Max": 178,
    "Walking Wake Max": 173,
    "Garchomp Max": 169,
    "Chi-Yu Max": 167,
    "Urshifu-R Max": 161,
    "Indeedee-F Max": 161,
    "Landorus-T Max": 155,
    "Annihilape Max": 156,
    "Great Tusk Max": 154,
    "Gholdengo Max": 147,
    "Raging Bolt Max": 139,
    "Incineroar Max": 124,
    "Iron Hands Max": 117,
    "Calyrex-Ice Max": 117,
}
