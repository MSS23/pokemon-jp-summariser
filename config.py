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
            # Try to get from Streamlit secrets first
            cls.GOOGLE_API_KEY = st.secrets.get("google_api_key")
        except (KeyError, FileNotFoundError):
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
    def get_database_url(cls) -> str:
        """Get database URL"""
        return "sqlite:///vgc_analyzer.db"

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
    
    # Flutter Mane and Paradox Pokemon (common errors)
    "ハバタクカミ": "Flutter Mane",
    "Flutter-Mane": "Flutter Mane",
    "テツノドクガ": "Iron Moth",
    "Iron-Moth": "Iron Moth",
    "テツノブジン": "Iron Valiant",
    "Iron-Valiant": "Iron Valiant", 
    "Iron-Valian": "Iron Valiant",
    "Iron Valian": "Iron Valiant",
    "Iron-Valiant-Therian": "Iron Valiant",
    "Iron-Valian-Therian": "Iron Valiant",
    "Iron Valiant-Therian": "Iron Valiant",
    "Iron Valian-Therian": "Iron Valiant",
    "スナノケガワ": "Sandy Shocks",
    "Sandy-Shocks": "Sandy Shocks",
    "アラブルタケ": "Brute Bonnet",
    "Brute-Bonnet": "Brute Bonnet",
    "サケブシッポ": "Roaring Moon",
    "Roaring-Moon": "Roaring Moon",
    "トドロクツキ": "Roaring Moon",
    
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

# Move name translations (add more as needed)
MOVE_NAME_TRANSLATIONS = {
    "10まんボルト": "Thunderbolt",
    "かえんほうしゃ": "Flamethrower",
    "なみのり": "Surf",
    # Add more as needed...
}
