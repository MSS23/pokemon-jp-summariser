"""
Shared Pokemon data constants
Used by both Streamlit and React applications for consistent Pokemon information
"""

# Restricted Pokemon list for VGC Regulation I
RESTRICTED_POKEMON = """
Restricted Pokémon in VGC Regulation I
Mewtwo – ミュウツー (Myuutsuu)
Lugia – ルギア (Rugia)
Ho-Oh – ホウオウ (Houou)
Kyogre – カイオーガ (Kaiōga)
Groudon – グラードン (Gurādon)
Ryquaza – レックウザ (Rekkūza)
Dialga – ディアルガ (Diaruga)
Dialga (Origin) – オリジンディアルガ (Orijin Diaruga)
Palkia – パルキア (Parukia)
Palkia (Origin) – オリジンパルキア (Orijin Parukia)
Giratina (Altered) – ギラティナ (Giratina)
Giratina (Origin) – オリジンギラティナ (Orijin Giratina)
Reshiram – レシラム (Reshiramu)
Zekrom – ゼクロム (Zekuromu)
Kyurem – キュレム (Kyuremu)
White Kyurem – ホワイトキュレム (Howaito Kyuremu)
Black Kyurem – ブラックキュレム (Burakku Kyuremu)
Cosmog – コスモッグ (Kosumoggu)
Cosmoem – コスモウム (Kosumōmu)
Solgaleo – ソルガレオ (Sorugareo)
Lunala – ルナアーラ (Runaāra)
Necrozma – ネクロズマ (Nekuromazuma)
Dusk Mane Necrozma – たそがれのたてがみネクロズマ (Tasogare no Tategami Nekuromazuma)
Dawn Wings Necrozma – あかつきのつばさネクロズマ (Akatsuki no Tsubasa Nekuromazuma)
Zacian – ザシアン (Zashian)
Zamazenta – ザマゼンタ (Zamazenta)
Eternatus – ムゲンダイナ (Mugendaina)
Calyrex – バドレックス (Badorekkusu)
Calyrex Ice Rider – バドレックス（はくばじょうのすがた）(Hakubajō no Sugata)
Calyrex Shadow Rider – バドレックス（こくばじょうのすがた）(Kokubajō no Sugata)
Koraidon – コライドン (Koraidon)
Miraidon – ミライドン (Miraidon)
Terapagos – テラパゴス (Terapagos)

Banned Pokémon in VGC Regulation I
Mew
Deoxys (All Forms)
Phione
Manaphy
Darkrai
Shaymin
Arceus
Keldeo
Diancie
Hoopa
Volcanion
Magearna
Zarude
Pecharunt
"""

# Pokemon type mappings (Japanese to English)
POKEMON_TYPES = {
    "ノーマル": "Normal",
    "ほのお": "Fire",
    "みず": "Water",
    "でんき": "Electric",
    "くさ": "Grass",
    "こおり": "Ice",
    "かくとう": "Fighting",
    "どく": "Poison",
    "じめん": "Ground",
    "ひこう": "Flying",
    "エスパー": "Psychic",
    "むし": "Bug",
    "いわ": "Rock",
    "ゴースト": "Ghost",
    "ドラゴン": "Dragon",
    "あく": "Dark",
    "はがね": "Steel",
    "フェアリー": "Fairy"
}

# Common Pokemon name translations (Japanese to English)
POKEMON_NAMES = {
    # Legendary Pokemon
    "ミュウツー": "Mewtwo",
    "ルギア": "Lugia",
    "ホウオウ": "Ho-Oh",
    "カイオーガ": "Kyogre",
    "グラードン": "Groudon",
    "レックウザ": "Rayquaza",
    "ディアルガ": "Dialga",
    "パルキア": "Palkia",
    "ギラティナ": "Giratina",
    "レシラム": "Reshiram",
    "ゼクロム": "Zekrom",
    "キュレム": "Kyurem",
    "ソルガレオ": "Solgaleo",
    "ルナアーラ": "Lunala",
    "ネクロズマ": "Necrozma",
    "ザシアン": "Zacian",
    "ザマゼンタ": "Zamazenta",
    "ムゲンダイナ": "Eternatus",
    "バドレックス": "Calyrex",
    "コライドン": "Koraidon",
    "ミライドン": "Miraidon",
    "テラパゴス": "Terapagos",
    
    # Important VGC Pokemon
    "ハイドレイゴン": "Hydreigon",
    "リラボーム": "Rillaboom",
    "ガオガエン": "Incineroar",
    "テツノワダチ": "Iron Treads",
    "ハバタクカミ": "Flutter Mane",
    "チオンジェン": "Chien-Pao",
    "チェンパオ": "Chien-Pao",
    "チエンパオ": "Chien-Pao",
    "パオジアン": "Chi-Yu",
    "パオ": "Chi-Yu",
    "テツノブジン": "Iron Valiant",
    "テツノカイナ": "Iron Hands",
    "テツノツツミ": "Iron Bundle",
    "テツノドクガ": "Iron Moth",
    "テツノコウベ": "Iron Crown",
    "テツノカシラ": "Iron Boulder",
    "ウネルミナモ": "Milotic",
    "タケルライコ": "Thundurus",
    "オニシズクモ": "Grimmsnarl",
    "チャブルガ": "Charizard",
    "チグマ": "Typhlosion",
    "ヒスイウインディ": "Hisuian Arcanine",
    "ヤミカラス": "Honchkrow",
    "ドドゲザン": "Dodrio",
    "ヘイラッシャ": "Clodsire",
    "シャリタツ": "Garchomp",
    "パーモット": "Perrserker",
    "フローゼル": "Floatzel",
    "ハラバリー": "Hariyama",
    "セグレイブ": "Sceptile",
    "グレンアル": "Glalie",
    "マイッカネズミ": "Maushold",
    "サーフゴー": "Surfing Pikachu",
    "キョジオーン": "Gyarados",
    "パルデアケンタロス": "Paldean Tauros",
    "水エルレイド": "Water-type Gallade",
    "ビビヨン": "Vivillon",
    "リキキリン": "Rillaboom",
    "ムクホーク": "Staraptor",
    "ハカドッグ": "Houndoom",
    "トドロクツキ": "Togekiss",
    "サケブシッポイ": "Sceptile",
    "ダイナキバ": "Tyrantrum",
    "ワタッコイ": "Swellow",
    "イーユイ": "Flutter Mane",
    "ディンルー": "Ting-Lu",
    "キラフロル": "Florges",
    "イルカマン": "Inteleon",
    "コノヨザル": "Rillaboom",
    "シャワーズ": "Vaporeon",
    "アーマーガア": "Corviknight",
    "アイアント": "Durant",
    "アクジキング": "Kingdra",
    "アグノム": "Aggron",
    "アシレーヌ": "Azumarill",
    "アマージョ": "Amoonguss",
    "アローラガラガラ": "Alolan Dugtrio",
    "アローラキュウコン": "Alolan Ninetales",
    "アローラペルシアン": "Alolan Persian",
    "イエッサン♀": "Indeedee (Female)",
    "イエッサン♂": "Indeedee (Male)",
    "イシヘンジン": "Stonjourner",
    "イベルタル": "Hydreigon",
    "インテレオン": "Inteleon",
    "ウインディ": "Arcanine",
    "ウーラオス": "Urshifu",
    "ウォーグル": "Braviary",
    "ウォッシュロトム": "Rotom (Wash)",
    "ウオノラゴン": "Garchomp",
    "ウツロイド": "Ditto",
    "エースバーン": "Cinderace",
    "エムリット": "Emolga",
    "エルフーン": "Altaria",
    "エレザード": "Charizard",
    "エンテイ": "Entei",
    "オーロット": "Decidueye",
    "オリジンギラティナ": "Giratina (Origin)",
    "オンバーン": "Talonflame",
    "カイオーガ": "Kyogre",
    "カジリガメ": "Blastoise",
    "カットロトム": "Rotom (Mow)",
    "カバルドン": "Hippowdon",
    "カビゴン": "Snorlax",
    "カプ・コケコ": "Tapu Koko",
    "カプ・テテフ": "Tapu Lele",
    "カプ・ブルル": "Tapu Bulu",
    "カプ・レヒレ": "Tapu Fini",
    "ガブリアス": "Garchomp",
    "カポエラー": "Hawlucha",
    "ガマゲロゲ": "Seismitoad",
    "カマスジョー": "Kingdra",
    "カミツルギ": "Aegislash",
    "カメックス": "Blastoise",
    "ガラガラ": "Dugtrio",
    "ガラルサンダー": "Galarian Zapdos",
    "ガラルヒヒダルマ": "Galarian Darmanitan",
    "ガラルファイヤー": "Galarian Moltres",
    "ガラルフリーザー": "Galarian Articuno",
    "ガラルマタドガス": "Galarian Weezing",
    "ガルーラ": "Kangaskhan",
    "ギガイアス": "Golem",
    "ギギギアル": "Gigalith",
    "ギャラドス": "Gyarados",
    "キュウコン": "Ninetales",
    "キュワワー": "Lucario",
    "キリキザン": "Bisharp",
    "キングドラ": "Kingdra",
    "グラードン": "Groudon",
    "グレイシア": "Glalie",
    "クレセリア": "Cresselia",
    "クレッフィ": "Clefable",
    "クロバット": "Crobat",
    "ゲンガー": "Gengar",
    "コータス": "Torkoal",
    "コジョンド": "Mienshao",
    "ゴチルゼル": "Gothitelle",
    "コバルオン": "Cobalion",
    "ゴリランダー": "Rillaboom",
    "サイドン": "Rhydon",
    "サザンドラ": "Hydreigon",
    "サンダージ": "Jolteon",
    "ガルデジバ": "Gardevoir",
    "コイル": "Magneton",
    "シャンデラ": "Chandelure",
    "ジュカイン": "Sceptile",
    "シュバルゴ": "Escavalier",
    "ジュラルドン": "Duraludon",
    "シルヴァディ": "Sylveon",
    "スイクン": "Suicune",
    "ズガドーン": "Rhyperior",
    "ストリンダー": "Jolteon",
    "ズルズキン": "Scrafty",
    "セキタンザン": "Gigalith",
    "ゼクロム": "Zekrom",
    "ゼルネアス": "Xerneas",
    "ソルガレオ": "Solgaleo",
    "タイプ：ヌル": "Type: Null",
    "ダダリン": "Lickitung",
    "タルップル": "Togepi",
    "ツンデツンデ": "Vanilluxe",
    "ディアルガ": "Dialga",
    "デスバーン": "Houndoom",
    "テッカグヤ": "Volcarona",
    "デデンネ": "Dedenne",
    "テラキオン": "Terrakion",
    "デンジュモク": "Ferrothorn",
    "ドータクン": "Conkeldurr",
    "ゲキッスト": "Conkeldurr",
    "ゲデマルド": "Gigalith",
    "ドラパルト": "Dragapult",
    "ドラミドロ": "Dragonite",
    "トリトドン": "Gastrodon",
    "ドリュウズ": "Excadrill",
    "ナゲツケサル": "Rillaboom",
    "ナットレイ": "Ferrothorn",
    "ニンフィア": "Sylveon",
    "ヌケニン": "Greninja",
    "ヌメルゴン": "Goodra",
    "ネクロズマ": "Necrozma",
    "ネンドール": "Claydol",
    "バイバニラ": "Vanilluxe",
    "バクガメス": "Blastoise",
    "バシャーモ": "Blaziken",
    "バタフリー": "Butterfree",
    "バチンウニ": "Jolteon",
    "ハッサム": "Scizor",
    "パッチラゴン": "Dragonite",
    "パルキア": "Palkia",
    "バンギラス": "Tyranitar",
    "バンバドロ": "Snorlax",
    "ヒードラン": "Heatran",
    "ヒートロトム": "Rotom (Heat)",
    "ピカチュウ": "Pikachu",
    "ピッピ": "Cleffa",
    "ビリジオン": "Virizion",
    "ファイアロー": "Charizard",
    "ファイヤー": "Arcanine",
    "フーディン": "Alakazam",
    "フェローチェ": "Infernape",
    "フシギバナ": "Venusaur",
    "ブラッキー": "Umbreon",
    "フリーザー": "Articuno",
    "ブリザポス": "Abomasnow",
    "ブリムオン": "Chandelure",
    "ブルンゲル": "Tentacruel",
    "フロストロトム": "Rotom (Frost)",
    "ペリッパー": "Pelipper",
    "ぺリッパー": "Pelipper",
    "ペロリーム": "Clefable",
    "ホウオウ": "Ho-Oh",
    "ボーマンダ": "Salamence",
    "ポリゴン2": "Porygon2",
    "ポリゴンZ": "Porygon-Z",
    "ホルード": "Wailord",
    "ホワイトキュレム": "White Kyurem",
    "マタドガス": "Weezing",
    "マッシブーン": "Talonflame",
    "マニューラ": "Weavile",
    "マホイップ": "Slurpuff",
    "マリルリ": "Azumarill",
    "マルヤクデ": "Ferrothorn",
    "マンムー": "Mamoswine",
    "ミミッキュ": "Mimikyu",
    "ミロカロス": "Milotic",
    "ムゲンダイナ": "Eternatus",
    "メタグロス": "Metagross",
    "メタモン": "Ditto",
    "モジャンボ": "Sudowoodo",
    "ヤミラミ": "Sableye",
    "ユキノオー": "Abomasnow",
    "ユクシー": "Uxie",
    "ヨノワール": "Dusknoir",
    "ライコウ": "Raikou",
    "ライチュウ": "Raichu",
    "ラグラージ": "Swampert",
    "ラッキー": "Chansey",
    "ラティアス": "Latias",
    "ラティオス": "Latios",
    "ラプラス": "Lapras",
    "ラフレシア": "Vileplume",
    "ランクルス": "Reuniclus",
    "リオル": "Riolu",
    "リザードン": "Charizard",
    "ルージュラ": "Rhyperior",
    "ルカリオ": "Lucario",
    "ルガルガン": "Lycanroc",
    "黄昏ルガルガン": "Lycanroc (Dusk)",
    "ルガルガン真昼": "Lycanroc (Midday)",
    "ルギアル": "Lugia",
    "ナアーラ": "Ninetales",
    "ルンパッパ": "Rillaboom",
    "レイスポス": "Abomasnow",
    "レジアイス": "Regice",
    "レジエレキ": "Regieleki",
    "レジギガス": "Regigigas",
    "レジスチル": "Registeel",
    "レジドラゴ": "Regidrago",
    "レシラム": "Reshiram",
    "レジロック": "Regirock",
    "レックウザ": "Rayquaza",
    "レパルダス": "Liepard",
    "レントラー": "Luxray",
    "ローブシン": "Conkeldurr",
    "ワルビアル": "Hydreigon",
    "化身トルネロス": "Tornadus (Incarnate)",
    "ボルトロス化身": "Thundurus (Incarnate)",
    "ランドロス化身": "Landorus (Incarnate)",
    "月食ネクロズマ": "Necrozma (Dusk Mane)",
    "黒馬バドレックス": "Calyrex (Shadow Rider)",
    "日食ネクロズマ": "Necrozma (Dawn Wings)",
    "白馬バドレックス": "Calyrex (Ice Rider)",
    "霊獣トルネロス": "Tornadus (Therian)",
    "霊獣ボルトロス": "Thundurus (Therian)",
    "霊獣ランドロス": "Landorus (Therian)"
}

# Common ability translations (Japanese to English)
ABILITIES = {
    "人馬一体": "As One",
    "不屈の盾": "Dauntless Shield",
    "災いの剣": "Beads of Ruin",
    "再生力": "Regenerator",
    "精神力": "Inner Focus",
    "クォークチャージ": "Quark Drive",
    "すいすい": "Swift Swim",
    "かたやぶり": "Mold Breaker",
    "てんのめぐみ": "Serene Grace",
    "ふしぎなまもり": "Wonder Guard",
    "かげふみ": "Shadow Tag",
    "プレッシャー": "Pressure",
    "がんじょう": "Sturdy",
    "きもったま": "Guts",
    "しんりょく": "Overgrow",
    "もうか": "Blaze",
    "げきりゅう": "Torrent",
    "むしのしらせ": "Swarm",
    "いかく": "Intimidate",
    "ふゆう": "Levitate",
    "てつのこころ": "Clear Body",
    "すいほう": "Water Absorb",
    "ひでり": "Drought",
    "あめふらし": "Drizzle",
    "すなあらし": "Sand Stream",
    "ゆきふらし": "Snow Warning",
    "エアロック": "Air Lock",
    "きずなへんげ": "Battle Bond",
    "ビーストブースト": "Beast Boost",
    "フェアリーオーラ": "Fairy Aura",
    "ダークオーラ": "Dark Aura",
    "オーラブレイク": "Aura Break",
    "フラワーベール": "Flower Veil",
    "スイートベール": "Sweet Veil",
    "チェックベール": "Check Veil",
    "ミストベール": "Mist Veil",
    "サイコサーフ": "Psychic Surge",
    "エレクトリックサーフ": "Electric Surge",
    "グラスサーフ": "Grassy Surge",
    "ミストサーフ": "Misty Surge",
    "サイコシフト": "Psychic Shift",
    "エレクトリックシフト": "Electric Shift",
    "グラスシフト": "Grassy Shift",
    "ミストシフト": "Misty Shift"
}

# Common move translations (Japanese to English)
MOVES = {
    "アストラルビット": "Astral Barrage",
    "サイコキネシス": "Psychic",
    "アンコール": "Encore",
    "守る": "Protect",
    "ボディプレス": "Body Press",
    "ヘビーボンバー": "Heavy Slam",
    "ワイドガード": "Wide Guard",
    "カタストロフィ": "Ruination",
    "アイススピナー": "Ice Spinner",
    "不意打ち": "Sucker Punch",
    "氷の礫": "Ice Shard",
    "ヘドロ爆弾": "Sludge Bomb",
    "怒りの粉": "Rage Powder",
    "キノコの胞子": "Spore",
    "神速": "Extreme Speed",
    "けたぐり": "Low Kick",
    "岩雪崩": "Rock Slide",
    "逆鱗": "Outrage",
    "波動弾": "Aura Sphere",
    "マジシャ": "Magical Shine",
    "金縛り": "Imprison",
    "でんこうせっか": "Thunderbolt",
    "かえんだん": "Fire Blast",
    "れいとうビーム": "Ice Beam",
    "サイコウェーブ": "Psyshock",
    "りゅうのいかり": "Dragon Claw",
    "かげうち": "Shadow Sneak",
    "つばめがえし": "Aerial Ace",
    "いわなだれ": "Rock Slide",
    "じしん": "Earthquake",
    "ほのおのうず": "Fire Spin",
    "みずでっぽう": "Water Gun",
    "でんげき": "Thunder Shock",
    "つるぎのまい": "Sacred Sword",
    "きあいだま": "Focus Blast",
    "りゅうせいぐん": "Draco Meteor",
    "ふぶき": "Blizzard",
    "かみなり": "Thunder",
    "だいもんじ": "Fire Blast",
    "ハイドロポンプ": "Hydro Pump",
    "ギガインパクト": "Giga Impact",
    "ハイパービーム": "Hyper Beam",
    "ソーラービーム": "Solar Beam",
    "フリーズドライ": "Freeze-Dry",
    "パワージェム": "Power Gem",
    "ダークパルス": "Dark Pulse",
    "ドラゴンパルス": "Dragon Pulse",
    "フラッシュキャノン": "Flash Cannon",
    "エナジーボール": "Energy Ball",
    "サイコブースト": "Psycho Boost",
    "ブレイズキック": "Blaze Kick",
    "スカイアッパー": "Sky Uppercut",
    "クロスチョップ": "Cross Chop",
    "ドレインパンチ": "Drain Punch",
    "マッハパンチ": "Mach Punch",
    "バレットパンチ": "Bullet Punch",
    "メタルクロー": "Metal Claw",
    "アイアンテール": "Iron Tail",
    "ドラゴンテール": "Dragon Tail",
    "アクアテール": "Aqua Tail",
    "ポイズンテール": "Poison Tail",
    "しっぽをふる": "Tail Whip",
    "かみくだく": "Crunch",
    "かみつく": "Bite",
    "つつく": "Peck",
    "つばさでうつ": "Wing Attack",
    "つめでひっかく": "Scratch",
    "パンチ": "Punch",
    "キック": "Kick",
    "ヘッドバット": "Headbutt",
    "ボディスラム": "Body Slam",
    "とっしん": "Tackle",
    "でんこう": "Quick Attack",
    "でんこうがえし": "Volt Switch",
    "とんぼがえり": "U-turn",
    "ふきとばし": "Gust",
    "かぜおこし": "Whirlwind",
    "つむじかぜ": "Twister",
    "りゅうのまい": "Dragon Dance",
    "つるぎのまい": "Sacred Sword",
    "かげぶんしん": "Double Team",
    "かげふみ": "Shadow Sneak",
    "かげうち": "Shadow Sneak",
    "かげのボール": "Shadow Ball",
    "かげのつめ": "Shadow Claw",
    "かげのパンチ": "Shadow Punch",
    "かげのキック": "Shadow Kick",
    "かげのテール": "Shadow Tail",
    "かげのビーム": "Shadow Beam",
    "かげのウェーブ": "Shadow Wave",
    "かげのパルス": "Shadow Pulse",
    "かげのブースト": "Shadow Boost",
    "かげのキャノン": "Shadow Cannon"
}

# Held item translations (Japanese to English)
HELD_ITEMS = {
    "気合の襷": "Focus Sash",
    "チョッキ": "Assault Vest",
    "鉢巻": "Choice Band",
    "ブーストエナジー": "Booster Energy"
}

# EV spread mapping (Japanese to English)
EV_MAPPING = {
    "H": "HP",
    "A": "Attack",
    "B": "Defense", 
    "C": "Special Attack",
    "D": "Special Defense",
    "S": "Speed"
}

def translate_pokemon_name(japanese_name: str) -> str:
    """
    Translate Japanese Pokemon name to English
    
    Args:
        japanese_name (str): Japanese Pokemon name
    
    Returns:
        str: English Pokemon name
    """
    return POKEMON_NAMES.get(japanese_name, japanese_name)

def translate_ability(japanese_ability: str) -> str:
    """
    Translate Japanese ability to English
    
    Args:
        japanese_ability (str): Japanese ability name
    
    Returns:
        str: English ability name
    """
    return ABILITIES.get(japanese_ability, japanese_ability)

def translate_move(japanese_move: str) -> str:
    """
    Translate Japanese move to English
    
    Args:
        japanese_move (str): Japanese move name
    
    Returns:
        str: English move name
    """
    return MOVES.get(japanese_move, japanese_move)

def translate_item(japanese_item: str) -> str:
    """
    Translate Japanese held item to English
    
    Args:
        japanese_item (str): Japanese item name
    
    Returns:
        str: English item name
    """
    return HELD_ITEMS.get(japanese_item, japanese_item)

def translate_type(japanese_type: str) -> str:
    """
    Translate Japanese type to English
    
    Args:
        japanese_type (str): Japanese type name
    
    Returns:
        str: English type name
    """
    return POKEMON_TYPES.get(japanese_type, japanese_type)

def map_ev_label(japanese_label: str) -> str:
    """
    Map Japanese EV label to English
    
    Args:
        japanese_label (str): Japanese EV label (H, A, B, C, D, S)
    
    Returns:
        str: English EV label (HP, Atk, Def, SpA, SpD, Spe)
    """
    return EV_MAPPING.get(japanese_label, japanese_label) 