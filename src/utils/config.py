"""
Configuration management for Pokemon VGC Analysis application
"""

import os
import streamlit as st


class Config:
    """Application configuration management"""

    # API Configuration
    GOOGLE_API_KEY = None

    # Application Settings
    PAGE_TITLE = "Pokemon VGC Analysis"
    PAGE_ICON = "⚔️"
    LAYOUT = "wide"

    # Cache Settings
    CACHE_ENABLED = True
    CACHE_TTL_HOURS = 24

    # Logging Settings
    LOG_LEVEL = "INFO"
    LOG_DIR = "streamlit-app/logs"

    @classmethod
    def init_config(cls):
        """Initialize configuration from environment and Streamlit secrets"""
        try:
            # Try to get from Streamlit secrets first (check both cases)
            cls.GOOGLE_API_KEY = st.secrets.get("google_api_key") or st.secrets.get("GOOGLE_API_KEY")
        except (KeyError, FileNotFoundError, AttributeError):
            # Fall back to environment variable
            cls.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

        if not cls.GOOGLE_API_KEY:
            st.error(
                "❌ Google API key not found. "
                "Please set it in .streamlit/secrets.toml or environment variable."
            )
            st.stop()

    @classmethod
    def get_google_api_key(cls) -> str:
        """Get Google API key, initializing if needed"""
        if cls.GOOGLE_API_KEY is None:
            cls.init_config()
        return cls.GOOGLE_API_KEY

    @classmethod
    def ensure_log_directory(cls):
        """Ensure log directory exists"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)


# Translation mappings
ITEM_TRANSLATIONS = {
    # English to Japanese
    "leftovers": "たべのこし",
    "focus-sash": "きあいのタスキ",
    "mystic-water": "しんぴのしずく",
    "life-orb": "いのちのたま",
    "choice-band": "こだわりハチマキ",
    "choice-specs": "こだわりメガネ",
    "choice-scarf": "こだわりスカーフ",
    "assault-vest": "とつげきチョッキ",
    "sitrus-berry": "オボンのみ",
    "lum-berry": "ラムのみ",
    "safety-goggles": "ぼうじんゴーグル",
    "booster-energy": "ブーストエナジー",
    "clear-amulet": "クリアチャーム",
    "covert-cloak": "しんしょくオーブ",
    "rocky-helmet": "ゴツゴツメット",
    "mental-herb": "メンタルハーブ",
    "wide-lens": "こうかくレンズ",
    "mirror-herb": "ものまねハーブ",
    # Japanese to English (reverse mapping)
    "たべのこし": "leftovers",
    "きあいのタスキ": "focus-sash",
    "しんぴのしずく": "mystic-water",
    "いのちのたま": "life-orb",
    "こだわりハチマキ": "choice-band",
    "こだわりメガネ": "choice-specs",
    "こだわりスカーフ": "choice-scarf",
    "とつげきチョッキ": "assault-vest",
    "オボンのみ": "sitrus-berry",
    "ラムのみ": "lum-berry",
    "ぼうじんゴーグル": "safety-goggles",
    "ブーストエナジー": "booster-energy",
    "クリアチャーム": "clear-amulet",
    "しんしょくオーブ": "covert-cloak",
    "ゴツゴツメット": "rocky-helmet",
    "メンタルハーブ": "mental-herb",
    "こうかくレンズ": "wide-lens",
    "ものまねハーブ": "mirror-herb",
}

# Comprehensive Pokemon name translations for VGC
POKEMON_NAME_TRANSLATIONS = {
    # Treasures of Ruin (Comprehensive fixes)
    "パオジアン": "Chien-Pao",
    "パオ・ジアン": "Chien-Pao", 
    "Pao Kai": "Chien-Pao",
    "Pao-Kai": "Chien-Pao",
    "kai pao": "Chien-Pao",
    "Kai Pao": "Chien-Pao",
    "Kai-Pao": "Chien-Pao",
    "KaiPao": "Chien-Pao",
    "Chien Pao": "Chien-Pao",
    "Chienpao": "Chien-Pao",
    "チオンジェン": "Chi-Yu",
    "Chi Yu": "Chi-Yu",
    "ChiYu": "Chi-Yu",
    "ディンルー": "Ting-Lu",
    "Ting Lu": "Ting-Lu",
    "TingLu": "Ting-Lu",
    "イーユイ": "Wo-Chien",
    "Wo Chien": "Wo-Chien",
    "WoChien": "Wo-Chien",
    
    # Zamazenta/Zacian (Fix common confusion)
    "ザマゼンタ": "Zamazenta",
    "ザシアン": "Zacian",
    "Zacian-C": "Zacian-Crowned",
    "Zacian-Hero": "Zacian",
    "Zamazenta-C": "Zamazenta-Crowned", 
    "Zamazenta-Hero": "Zamazenta",
    "ザシアン王": "Zacian-Crowned",
    "ザマゼンタ王": "Zamazenta-Crowned",
    
    # Calyrex forms (Common errors)
    "カルネクス": "Calyrex-Shadow",
    "Calyrex Shadow": "Calyrex-Shadow",
    "Calyrex Ice": "Calyrex-Ice",
    "Calyrex-Shadow Rider": "Calyrex-Shadow",
    "Calyrex-Ice Rider": "Calyrex-Ice",
    "Shadow Calyrex": "Calyrex-Shadow",
    "Ice Calyrex": "Calyrex-Ice",
    "白バドレックス": "Calyrex-Ice",
    "黒バドレックス": "Calyrex-Shadow",
    
    # Urshifu forms (Common confusion)
    "ウーラオス": "Urshifu",
    "Urshifu Rapid": "Urshifu-Rapid-Strike",
    "Urshifu Single": "Urshifu-Single-Strike",
    "Urshifu-R": "Urshifu-Rapid-Strike",
    "Urshifu-S": "Urshifu-Single-Strike",
    "Rapid Strike Urshifu": "Urshifu-Rapid-Strike",
    "Single Strike Urshifu": "Urshifu-Single-Strike",
    "連撃ウーラオス": "Urshifu-Rapid-Strike",
    "一撃ウーラオス": "Urshifu-Single-Strike",
    
    # Genie forms (Therian confusion)
    "ランドロス": "Landorus-Therian",
    "Landorus T": "Landorus-Therian",
    "Landorus-T": "Landorus-Therian", 
    "Landorus Therian": "Landorus-Therian",
    "Lando-T": "Landorus-Therian",
    "ボルトロス": "Thundurus-Therian",
    "Thundurus T": "Thundurus-Therian",
    "Thundurus-T": "Thundurus-Therian",
    "Thundurus Therian": "Thundurus-Therian",
    "トルネロス": "Tornadus-Therian",
    "Tornadus T": "Tornadus-Therian", 
    "Tornadus-T": "Tornadus-Therian",
    "Tornadus Therian": "Tornadus-Therian",
    
    # Popular VGC Pokemon (Gen 9 comprehensive)
    "ガブリアス": "Garchomp",
    "ガオガエン": "Incineroar", 
    "ウインディ": "Arcanine",
    "ヒスイウインディ": "Arcanine-Hisui",
    "Arcanine-H": "Arcanine-Hisui",
    "モロバレル": "Amoonguss",
    "エルフーン": "Whimsicott",
    
    # Hoppip evolution line (missing translation fix)
    "ハネッコ": "Hoppip",
    "ポポッコ": "Skiploom", 
    "ワタッコ": "Jumpluff",
    "Watakko": "Jumpluff",  # Romanized variant
    
    # Cottonee evolution line (add missing Cottonee)
    "モンメン": "Cottonee",
    
    "カイリュー": "Dragonite",
    "ハリテヤマ": "Hariyama",
    "クレッフィ": "Klefki",
    "トリトドン": "Gastrodon",
    "ニンフィア": "Sylveon",
    "リザードン": "Charizard",
    "カメックス": "Blastoise",
    "フシギバナ": "Venusaur",
    
    # Legendary/Restricted Pokemon
    "コライドン": "Koraidon",
    "ミライドン": "Miraidon", 
    "レジエレキ": "Regieleki",
    "レジドラゴ": "Regidrago",
    "グラードン": "Groudon",
    "カイオーガ": "Kyogre",
    "レックウザ": "Rayquaza",
    "ディアルガ": "Dialga",
    "パルキア": "Palkia",
    "ギラティナ": "Giratina",
    
    # Legendary Birds
    "サンダー": "Zapdos",
    "ファイヤー": "Moltres",
    "フリーザー": "Articuno",
    "ガラルサンダー": "Zapdos-Galar",
    "ガラルファイヤー": "Moltres-Galar", 
    "ガラルフリーザー": "Articuno-Galar",
    "Galarian Zapdos": "Zapdos-Galar",
    "Galarian Moltres": "Moltres-Galar",
    "Galarian Articuno": "Articuno-Galar",
    
    # Common VGC Support Pokemon
    "イエッサン": "Indeedee",
    "イエッサン♀": "Indeedee-Female",
    "イエッサン♂": "Indeedee-Male",
    "Indeedee-F": "Indeedee-Female",
    "Indeedee-M": "Indeedee-Male",
    "オーロンゲ": "Grimmsnarl",
    "ドラパルト": "Dragapult",
    "ミミッキュ": "Mimikyu",
    "コータス": "Torkoal",
    "ナットレイ": "Ferrothorn",
    "バンギラス": "Tyranitar",
    
    # Missing Pokemon from takoyaki-games article
    "ジュペッタ": "Banette",
    "エルレイド": "Gallade",
    
    # Ogerpon forms (from validator to main config)
    "オーガポン": "Ogerpon",
    "オーガポン-いしずえのめん": "Ogerpon-Cornerstone",
    "オーガポン-いどのめん": "Ogerpon-Wellspring", 
    "オーガポン-かまどのめん": "Ogerpon-Hearthflame",
    "オーガポン-みどりのめん": "Ogerpon",
    "いしずえのめん": "Ogerpon-Cornerstone",  # Short form
    
    # Calyrex shorthand (from validator to main config)
    "白馬": "Calyrex-Ice",      # Short form meaning "White Horse"
    "黒馬": "Calyrex-Shadow",   # Short form meaning "Black Horse"
    
    # Flutter Mane and Paradox Pokemon (ULTRA COMPREHENSIVE Iron Valiant fixes)
    "ハバタクカミ": "Flutter Mane",
    "Flutter-Mane": "Flutter Mane",
    "テツノドクガ": "Iron Moth",
    "Iron-Moth": "Iron Moth",
    
    # IRON VALIANT - Ultra comprehensive mapping (catch every possible variant)
    "テツノブジン": "Iron Valiant",
    "Iron-Valiant": "Iron Valiant", 
    "Iron-Valian": "Iron Valiant",
    "Iron Valian": "Iron Valiant",
    "Iron-Valien": "Iron Valiant",
    "Iron Valien": "Iron Valiant",
    "Iron-Valliant": "Iron Valiant",  # Common typo
    "Iron Valliant": "Iron Valiant",
    "Iron-Valient": "Iron Valiant",   # Common typo
    "Iron Valient": "Iron Valiant",
    
    # WITH THERIAN (the main error pattern)
    "Iron-Valiant-Therian": "Iron Valiant",
    "Iron-Valian-Therian": "Iron Valiant",
    "Iron Valiant-Therian": "Iron Valiant",
    "Iron Valian-Therian": "Iron Valiant",
    "Iron-Valien-Therian": "Iron Valiant",
    "Iron Valien-Therian": "Iron Valiant",
    "Iron-Valliant-Therian": "Iron Valiant",
    "Iron Valliant-Therian": "Iron Valiant",
    "Iron-Valient-Therian": "Iron Valiant",
    "Iron Valient-Therian": "Iron Valiant",
    
    # PARTIAL MATCHES (just the wrong part)
    "Valian-Therian": "Iron Valiant",
    "Valien-Therian": "Iron Valiant",
    "Valliant-Therian": "Iron Valiant",
    "Valient-Therian": "Iron Valiant",
    "Valiant-Therian": "Iron Valiant",  # In case someone removes "Iron" but keeps wrong form
    
    # WITH OTHER INCORRECT FORMS
    "Iron-Valiant-Forme": "Iron Valiant",
    "Iron-Valiant-Form": "Iron Valiant",
    "Iron-Valian-Forme": "Iron Valiant",
    "Iron-Valian-Form": "Iron Valiant",
    "Iron Valiant-Forme": "Iron Valiant",
    "Iron Valiant-Form": "Iron Valiant",
    "スナノケガワ": "Sandy Shocks",
    "Sandy-Shocks": "Sandy Shocks",
    "アラブルタケ": "Brute Bonnet",
    "Brute-Bonnet": "Brute Bonnet",
    "サケブシッポ": "Roaring Moon",
    "Roaring-Moon": "Roaring Moon",
    "トドロクツキ": "Roaring Moon",
    
    # Missing Paradox Pokemon (Ancient forms)
    "ウガツホムラ": "Gouging Fire",
    
    # Missing Paradox Pokemon (Future/Iron forms) 
    "テツノツツミ": "Iron Bundle",
    "テツノカイナ": "Iron Hands",
    "テツノワダチ": "Iron Treads",
    "テツノイバラ": "Iron Thorns",
    "テツノコウベ": "Iron Crown",
    "テツノイサハ": "Iron Boulder",
    
    # Romanization variants for Gouging Fire
    "Ugatsuhomura": "Gouging Fire",
    "Ugatsu Homura": "Gouging Fire",
    "ugatsu homura": "Gouging Fire",
    
    # Popular Gen 9 Pokemon
    "ドオー": "Dondozo",
    "シャリタツ": "Tatsugiri",
    "カラミンゴ": "Flamigo",
    "オリーヴァ": "Arboliva", 
    "マフィティフ": "Maschiff",
    "マスカーニャ": "Meowscarada",
    "ラウドボーン": "Skeledirge",
    "ウェーニバル": "Quaquaval",
    "ドラミドロ": "Dragalge",
    "クエスパトラ": "Espathra",
    
    # Regional forms and variants
    "アローラガラガラ": "Marowak-Alola",
    "Alolan Marowak": "Marowak-Alola",
    "ガラルヤドキング": "Slowking-Galar",
    "Galarian Slowking": "Slowking-Galar",
    "ヒスイゾロアーク": "Zoroark-Hisui",
    "Hisuian Zoroark": "Zoroark-Hisui",
    "ヒスイダイケンキ": "Samurott-Hisui", 
    "Hisuian Samurott": "Samurott-Hisui",
    
    # Rotom forms (common in VGC)
    "ロトム": "Rotom",
    "ヒートロトム": "Rotom-Heat",
    "ウォッシュロトム": "Rotom-Wash",
    "フロストロトム": "Rotom-Frost",
    "スピンロトム": "Rotom-Fan",
    "カットロトム": "Rotom-Mow",
    "Rotom-H": "Rotom-Heat",
    "Rotom-W": "Rotom-Wash",
    "Rotom-F": "Rotom-Frost",
    "Rotom-S": "Rotom-Fan",
    "Rotom-C": "Rotom-Mow",
    
    # Common abbreviations and nicknames
    "Lando": "Landorus-Therian",
    "Thundy": "Thundurus-Therian", 
    "Torn": "Tornadus-Therian",
    "Incin": "Incineroar",
    "Amoon": "Amoonguss",
    "Whimsi": "Whimsicott",
    "Grimm": "Grimmsnarl",
    "Pult": "Dragapult",
    "Ferro": "Ferrothorn",
    "TTar": "Tyranitar",
    "Chomp": "Garchomp",
    
    # Other common translations and variants
    "テラ": "Tera",
    "ダイマックス": "Dynamax",
    "キョダイマックス": "Gigantamax",
    "メガ": "Mega",
    "プリズム": "Prism",
}

# Japanese EV and stat terminology translations
EV_STAT_TRANSLATIONS = {
    # Primary Japanese stat names
    "ＨＰ": "HP",
    "HP": "HP",
    "ヒットポイント": "HP",
    "体力": "HP",
    
    "こうげき": "Attack",
    "攻撃": "Attack", 
    "アタック": "Attack",
    "物理攻撃": "Attack",
    "A": "Attack",
    
    "ぼうぎょ": "Defense",
    "防御": "Defense",
    "ディフェンス": "Defense", 
    "物理防御": "Defense",
    "B": "Defense",
    
    "とくこう": "Special Attack",
    "特攻": "Special Attack",
    "特殊攻撃": "Special Attack",
    "とくしゅこうげき": "Special Attack", 
    "C": "Special Attack",
    
    "とくぼう": "Special Defense",
    "特防": "Special Defense",
    "特殊防御": "Special Defense",
    "とくしゅぼうぎょ": "Special Defense",
    "D": "Special Defense",
    
    "すばやさ": "Speed",
    "素早さ": "Speed",
    "素早": "Speed",
    "スピード": "Speed",
    "速さ": "Speed",
    "S": "Speed",
    
    # EV-specific terminology
    "努力値": "EVs",
    "個体値": "IVs", 
    "調整": "EV training/tuning",
    "振り": "EV distribution",
    "努力": "effort",
    "極振り": "max investment",
    "無振り": "no investment",
}

# Japanese Pokemon nature translations
NATURE_TRANSLATIONS = {
    # Attack-boosting natures
    "いじっぱり": "Adamant",
    "やんちゃ": "Naughty",
    "ゆうかん": "Brave", 
    "さみしがり": "Lonely",
    
    # Defense-boosting natures  
    "ずぶとい": "Bold",
    "わんぱく": "Impish",
    "のうてんき": "Lax",
    "のんき": "Relaxed",
    
    # Special Attack-boosting natures
    "ひかえめ": "Modest",
    "おっとり": "Mild",
    "れいせい": "Quiet", 
    "うっかりや": "Rash",
    
    # Special Defense-boosting natures
    "おだやか": "Calm",
    "おとなしい": "Gentle",
    "しんちょう": "Careful",
    "なまいき": "Sassy",
    
    # Speed-boosting natures
    "おくびょう": "Timid",
    "せっかち": "Hasty",
    "ようき": "Jolly",
    "むじゃき": "Naive",
    
    # Neutral natures
    "がんばりや": "Hardy",
    "すなお": "Docile",
    "てれや": "Bashful",
    "きまぐれ": "Quirky",
    "まじめ": "Serious",
}

# Japanese ability translations (common VGC abilities)
ABILITY_TRANSLATIONS = {
    "いかく": "Intimidate",
    "もうか": "Blaze",
    "しんりょく": "Overgrow", 
    "げきりゅう": "Torrent",
    "かそく": "Speed Boost",
    "テクニシャン": "Technician",
    "てんのめぐみ": "Serene Grace",
    "プレッシャー": "Pressure",
    "マルチスケイル": "Multiscale",
    "ふゆう": "Levitate",
    "ばけのかわ": "Disguise",
    "ビーストブースト": "Beast Boost",
    "クリアボディ": "Clear Body",
    "しろのいななき": "White Smoke",
    "マジックガード": "Magic Guard",
    "さいせいりょく": "Regenerator",
    "しぜんかいふく": "Natural Cure",
    "いたずらごころ": "Prankster",
    "すなおこし": "Sand Stream",
    "ひでり": "Drought",
    "あめふらし": "Drizzle",
    "ゆきふらし": "Snow Warning",
    "でんきエンジン": "Motor Drive",
    "もらいび": "Flash Fire",
    "ちょすい": "Water Absorb",
    "かんそうはだ": "Dry Skin",
    "ハドロンエンジン": "Hadron Engine",
    "オリハルコンエンジン": "Orichalcum Pulse",
    "こだいかっせい": "Protosynthesis",
    "クォークチャージ": "Quark Drive",
    "でんきにかえる": "Electromorphosis",
    "じんばいったい": "Unity",
    "ふかしのこぶし": "Unseen Fist",
    "りゅうのあぎと": "Dragon's Maw",
    "トランジスタ": "Transistor",
    "りゅうのいかり": "Dragon's Wrath",
}

# Move name translations (expanded)
MOVE_NAME_TRANSLATIONS = {
    "10まんボルト": "Thunderbolt",
    "かえんほうしゃ": "Flamethrower", 
    "なみのり": "Surf",
    "じしん": "Earthquake",
    "かみなり": "Thunder",
    "ふぶき": "Blizzard",
    "だいもんじ": "Fire Blast",
    "ハイドロポンプ": "Hydro Pump",
    "りゅうのはどう": "Dragon Pulse",
    "きあいだま": "Focus Blast",
    "エアスラッシュ": "Air Slash",
    "いわなだれ": "Rock Slide",
    "アイアンヘッド": "Iron Head",
    "とんぼがえり": "U-turn",
    "ボルトチェンジ": "Volt Switch",
    "ねこだまし": "Fake Out",
    "まもる": "Protect",
    "みがわり": "Substitute",
    "はねやすめ": "Roost",
    "おにび": "Will-O-Wisp",
    "でんじは": "Thunder Wave",
    "どくどく": "Toxic",
    "ステルスロック": "Stealth Rock",
    "みずしゅりけん": "Water Shuriken",
    "かげうち": "Shadow Sneak",
    "しんそく": "Extreme Speed",
    "でんこうせっか": "Quick Attack",
    "マッハパンチ": "Mach Punch",
    "バレットパンチ": "Bullet Punch",
    "こおりのつぶて": "Ice Shard",
    "かみくだく": "Crunch",
    "じゃれつく": "Play Rough",
    "ムーンフォース": "Moonblast",
    "マジカルシャイン": "Dazzling Gleam",
    "テラバースト": "Tera Blast",
    "ワイドフォース": "Expanding Force",
    "ライジングボルト": "Rising Voltage",
    "オーラウィング": "Aura Wing",
    "ダブルウィング": "Dual Wingbeat",
    "グラススライダー": "Grassy Glide",
    "ウェーブタックル": "Wave Crash",
    "イナズマドライブ": "Electro Drift",
    "流星群": "Draco Meteor",
    "りゅうせいぐん": "Draco Meteor",
    "つららおとし": "Icicle Crash",
    "つららばり": "Icicle Spear",
    "ブリザードランス": "Glacial Lance",
    "アストラルビット": "Astral Barrage",
    "ワイルドボルト": "Wild Charge",
    "クロスサンダー": "Cross Thunder",
    "らいげき": "Thunder Strike",
    "しんぴのつるぎ": "Sacred Sword",
    "あんこくきょうだ": "Darkest Lariat",
    "DDラリアット": "Darkest Lariat",
    "フレアドライブ": "Flare Blitz",
    "インファイト": "Close Combat",
    "きしかいせい": "Reversal",
    "じだんだ": "Stomping Tantrum",
    "ヘビーボンバー": "Heavy Slam",
    "アイアンローラー": "Iron Roller",
    "サイコフィールド": "Psychic Terrain",
    "エレキフィールド": "Electric Terrain",
    "グラスフィールド": "Grassy Terrain",
    "ミストフィールド": "Misty Terrain",
    "トリックルーム": "Trick Room",
    "おいかぜ": "Tailwind",
    "ひかりのかべ": "Light Screen",
    "リフレクター": "Reflect",
    "オーロラベール": "Aurora Veil",
    # Pokemon Move Translation Updates
    "ニトロチャージ": "Flame Charge",  # Flame Charge (also known as Accel Break in some contexts)
    "フレイムチャージ": "Flame Charge",  # Alternative Japanese name for Flame Charge
    "アクセルブレイク": "Flame Charge",  # Accel Break -> Flame Charge
    "カタストロフィ": "Ruination",  # Catastrophe -> Ruination
    "ワイドブレイカー": "Breaking Swipe",  # Wide Breaker -> Breaking Swipe
    # Add more as needed...
}
