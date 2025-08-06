"""
Shared Pokemon constants for both Streamlit and React applications.
"""

# Pokemon generation constants
POKEMON_GENERATIONS = {
    1: "Red/Blue/Yellow",
    2: "Gold/Silver/Crystal", 
    3: "Ruby/Sapphire/Emerald",
    4: "Diamond/Pearl/Platinum",
    5: "Black/White",
    6: "X/Y",
    7: "Sun/Moon",
    8: "Sword/Shield",
    9: "Scarlet/Violet"
}

# VGC format constants
VGC_FORMATS = {
    "VGC2024": "Regulation F",
    "VGC2023": "Regulation E", 
    "VGC2022": "Regulation D",
    "VGC2021": "Series 10",
    "VGC2020": "Series 6"
}

# Pokemon types
POKEMON_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

# Common Pokemon names for validation
COMMON_POKEMON_NAMES = [
    "Charizard", "Blastoise", "Venusaur", "Pikachu", "Raichu",
    "Gyarados", "Dragonite", "Garchomp", "Tyranitar", "Metagross",
    "Salamence", "Rayquaza", "Groudon", "Kyogre", "Mewtwo",
    "Lugia", "Ho-Oh", "Dialga", "Palkia", "Giratina",
    "Reshiram", "Zekrom", "Kyurem", "Xerneas", "Yveltal",
    "Zygarde", "Solgaleo", "Lunala", "Necrozma", "Zacian",
    "Zamazenta", "Calyrex", "Koraidon", "Miraidon", "Ogerpon"
]

# Tera types
TERA_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

# Common abilities
COMMON_ABILITIES = [
    "Intimidate", "Levitate", "Pressure", "Serene Grace", "Technician",
    "Adaptability", "Arena Trap", "Battle Armor", "Clear Body", "Cloud Nine",
    "Drizzle", "Drought", "Early Bird", "Flame Body", "Flash Fire",
    "Guts", "Huge Power", "Hustle", "Inner Focus", "Insomnia",
    "Keen Eye", "Limber", "Liquid Ooze", "Magma Armor", "Magnet Pull",
    "Marvel Scale", "Minus", "Natural Cure", "Oblivious", "Overgrow",
    "Own Tempo", "Pickup", "Plus", "Poison Point", "Poison Touch",
    "Prankster", "Pressure", "Pure Power", "Rain Dish", "Reckless",
    "Rock Head", "Rough Skin", "Run Away", "Sand Veil", "Serene Grace",
    "Shadow Tag", "Shed Skin", "Shell Armor", "Shield Dust", "Simple",
    "Skill Link", "Slow Start", "Sniper", "Snow Cloak", "Snow Warning",
    "Solid Rock", "Soundproof", "Speed Boost", "Static", "Stench",
    "Sticky Hold", "Storm Drain", "Sturdy", "Suction Cups", "Super Luck",
    "Swarm", "Swift Swim", "Synchronize", "Tangled Feet", "Technician",
    "Thick Fat", "Tinted Lens", "Torrent", "Trace", "Truant",
    "Unaware", "Unburden", "Vital Spirit", "Volt Absorb", "Water Absorb",
    "Water Veil", "White Smoke", "Wonder Guard", "Wonder Skin"
]

# Common moves
COMMON_MOVES = [
    "Thunderbolt", "Flamethrower", "Ice Beam", "Surf", "Earthquake",
    "Psychic", "Shadow Ball", "Sludge Bomb", "Giga Drain", "Thunder",
    "Fire Blast", "Blizzard", "Hydro Pump", "Focus Blast", "Energy Ball",
    "Dark Pulse", "Dragon Pulse", "Flash Cannon", "Aura Sphere", "Vacuum Wave",
    "Close Combat", "Superpower", "Brick Break", "Cross Chop", "Dynamic Punch",
    "Fire Punch", "Ice Punch", "Thunder Punch", "Drain Punch", "Mach Punch",
    "Bullet Punch", "Aqua Jet", "Extreme Speed", "Quick Attack", "Fake Out",
    "Protect", "Detect", "Endure", "Substitute", "Rest",
    "Sleep Talk", "Snore", "Roar", "Whirlwind", "Dragon Tail",
    "U-turn", "Volt Switch", "Parting Shot", "Teleport", "Baton Pass",
    "Swords Dance", "Nasty Plot", "Calm Mind", "Bulk Up", "Dragon Dance",
    "Quiver Dance", "Tail Glow", "Growth", "Hone Claws", "Coil",
    "Shell Smash", "Belly Drum", "Agility", "Rock Polish", "Autotomize",
    "Flame Charge", "Flame Burst", "Flare Blitz", "Overheat", "Eruption",
    "Heat Wave", "Magma Storm", "Blue Flare", "Sacred Fire", "V-create",
    "Water Gun", "Water Pulse", "Aqua Tail", "Liquidation", "Origin Pulse",
    "Hydro Cannon", "Water Spout", "Crabhammer", "Aqua Jet", "Bubble Beam",
    "Thunder Shock", "Thunder Fang", "Wild Charge", "Volt Tackle", "Bolt Strike",
    "Thunder Wave", "Discharge", "Thunderbolt", "Thunder", "Zap Cannon",
    "Vine Whip", "Razor Leaf", "Leaf Blade", "Solar Blade", "Frenzy Plant",
    "Giga Drain", "Energy Ball", "Leaf Storm", "Seed Flare", "Wood Hammer",
    "Powder Snow", "Ice Shard", "Icicle Crash", "Ice Hammer", "Glaciate",
    "Freeze-Dry", "Blizzard", "Sheer Cold", "Ice Burn", "Subzero Slammer"
]

# Export formats
EXPORT_FORMATS = {
    "text": "Plain Text",
    "json": "JSON Data", 
    "csv": "CSV Spreadsheet",
    "compact": "Compact Summary"
}

# Cache settings
CACHE_SETTINGS = {
    "max_age_hours": 24,
    "max_entries": 1000,
    "cleanup_interval": 3600  # 1 hour in seconds
}

# API endpoints (for React app)
API_ENDPOINTS = {
    "summarize": "/api/summarize",
    "search": "/api/search", 
    "analytics": "/api/analytics",
    "auth": "/api/auth",
    "user": "/api/user"
}

# Error messages
ERROR_MESSAGES = {
    "invalid_url": "Please enter a valid URL",
    "api_error": "Error connecting to AI service",
    "no_content": "No content found at the provided URL",
    "rate_limit": "Rate limit exceeded. Please try again later",
    "authentication": "Authentication required",
    "permission": "Permission denied"
} 