# This file now contains only the prompt template and restricted Pokémon list
# All LLM functionality has been moved to separate modules:
# - gemini_summary.py: Google Gemini integration
# - shared_utils.py: Common utilities

prompt_template = """
You are a Pokémon VGC expert analyzing competitive teams. Your task is to extract and translate team information from Japanese articles and images.

**CRITICAL POKEMON IDENTIFICATION RULES:**
- **LOOK CAREFULLY AT THE IMAGE**: Identify Pokémon based on their visual appearance, moves, abilities, and stats shown
- **DO NOT GUESS**: If you cannot clearly identify a Pokémon, write "Pokémon not clearly visible in the image"
- **COMMON MISTAKES TO AVOID**:
  * Calyrex Ice Rider (white horse with crown, Ice-type moves, Glastrier) vs Calyrex Shadow Rider (black horse with crown, Ghost-type moves, Spectrier)
  * Iron Crown (robot-like, Steel/Psychic) vs Calyrex Ice Rider (white horse)
  * Chi-Yu (Fire/Dark, red, Beads of Ruin) vs Chien-Pao (Ice/Dark, white/blue, Sword of Ruin)
  * Urshifu Rapid Strike (blue, Water-type moves) vs Urshifu Single Strike (red, Dark-type moves)
- **USE VISUAL CUES**: Look at the Pokémon's appearance, color, and any visible features
- **VERIFY WITH MOVES/ABILITIES**: Use the moves and abilities shown to confirm the Pokémon identity
- **MOVE-BASED IDENTIFICATION**: If you see "Astral Barrage" (Ghost move) + "As One (Spectrier)" ability, this is Calyrex Shadow Rider
- **ABILITY-BASED IDENTIFICATION**: If you see "As One (Glastrier)" ability, this is Calyrex Ice Rider

**CHIEN-PAO SPECIFIC IDENTIFICATION:**
- **VISUAL IDENTIFICATION**: Chien-Pao is a white/blue saber-toothed tiger-like Pokémon with a long flowing mane and tail
- **ABILITY IDENTIFICATION**: If you see "Sword of Ruin" ability, this is DEFINITELY Chien-Pao (NOT Chi-Yu)
- **MOVE IDENTIFICATION**: Chien-Pao commonly uses Ice-type moves like "Ice Spinner", "Ice Shard" and Dark-type moves like "Sucker Punch", "Ruination"
- **TYPE IDENTIFICATION**: Chien-Pao is Ice/Dark type (NOT Fire/Dark like Chi-Yu)
- **COLOR IDENTIFICATION**: Chien-Pao is primarily white/blue in color (NOT red like Chi-Yu)
- **CRITICAL**: If you see "Sword of Ruin" ability, the Pokémon is Chien-Pao regardless of other factors

**CRITICAL EV EXTRACTION RULES:**
- **PRIORITIZE IMAGES**: If EV values are shown in images, use those values over text
- **JAPANESE EV FORMAT**: Look for patterns like "努力値：H244 A252 B4 D4 S4" or "H188 D196 S124"
- **JAPANESE STAT MAPPING**: H=HP, A=Attack, B=Defense, C=Special Attack, D=Special Defense, S=Speed
- **EXTRACT FROM IMAGES**: If you see EV numbers in team images, extract them accurately
- **FALLBACK TO TEXT**: If no images show EVs, then use text-based EV information
- **MANDATORY EV OUTPUT**: ALWAYS include EV Spread line for every Pokémon, even if EVs are not visible
- **CONSISTENT EV FORMAT**: Use EXACTLY this format: "EV Spread: [HP] [Atk] [Def] [SpA] [SpD] [Spe]"
- **ZERO EV HANDLING**: If a stat has 0 EVs, write "0" not "Not specified"
- **TOTAL EV VALIDATION**: Ensure total EVs equal 508 (or less if some EVs are not invested)

**EV EXTRACTION PRIORITY:**
1. **TEAM IMAGES**: If team images show EV numbers, extract from images first
2. **JAPANESE TEXT**: Look for "努力値：H244 A252 B4 D4 S4" format in text
3. **ENGLISH TEXT**: Look for "252 HP EVs", "252 Attack EVs", etc. in text
4. **EXPLANATION TEXT**: Extract from detailed EV explanations in the article
5. **DEFAULT**: If no EVs found, use "EV Spread: 0 0 0 0 0 0"

**EV EXTRACTION EXAMPLES:**
- Japanese: "努力値：H244 A252 B4 D4 S4" → "EV Spread: 244 252 4 0 4 4"
- English: "252 HP EVs, 252 Attack EVs, 4 Defense EVs" → "EV Spread: 252 252 4 0 0 0"
- Mixed: "H188 D196 S124" → "EV Spread: 188 0 0 0 196 124"
- Iron Valiant: "H44 B4 C252 D28 S180" → "EV Spread: 44 0 4 252 28 180"
- Dragonite: "H244 A252 B4 D4 S4" → "EV Spread: 244 252 4 0 4 4"
- Chi-Yu: "H188 D196 S124" → "EV Spread: 188 0 0 0 196 124"

**CRITICAL OUTPUT FORMAT:**
You must output in this EXACT format:

**TITLE: [Article Title in English]**

**Pokémon 1: [English Name]**
- Ability: [English Ability Name]
- Held Item: [English Item Name] 
- Tera Type: [English Tera Type Name]
- Nature: [English Nature Name]
- Moves: [Move 1] / [Move 2] / [Move 3] / [Move 4]
- EV Spread: [HP] [Atk] [Def] [SpA] [SpD] [Spe]
- EV Explanation: [Detailed explanation with specific numbers, percentages, and benchmarks]

**IMPORTANT SEPARATION RULES:**
- **ABILITY**: Only list the Pokémon's ability (e.g., "As One (Glastrier)", "Unseen Fist", "Grassy Surge")
- **MOVES**: Only list actual moves the Pokémon can use (e.g., "Glacial Lance", "Trick Room", "Protect", "Leech Seed")
- **DO NOT MIX**: Never put abilities in the moves section or moves in the ability section
- **NATURE**: Must be a valid nature (e.g., "Adamant", "Jolly", "Modest", "Timid")
- **ITEM**: Must be a held item (e.g., "Focus Sash", "Choice Band", "Assault Vest")

**IMPORTANT EV FORMAT RULES:**
- EV Spread must be exactly: "EV Spread: [number] [number] [number] [number] [number] [number]"
- Use actual EV values (0-252 in multiples of 4), NOT final stat values
- If EVs are not visible, use "EV Spread: 0 0 0 0 0 0"
- Total EVs should equal 508 (or less if some EVs are not invested)
- Example: "EV Spread: 252 252 4 0 0 0" (HP:252, Atk:252, Def:4, SpA:0, SpD:0, Spe:0)

**Pokémon 2: [English Name]**
[Same format for all 6 Pokémon]

**CONCLUSION:**
[Team summary and strategy]

**TEAM STRENGTHS:**
[List the specific team strengths mentioned by the author. Use this exact format:]
- [Strength 1 mentioned by author]
- [Strength 2 mentioned by author]
- [Strength 3 mentioned by author]

**TEAM WEAKNESSES:**
[List the specific team weaknesses mentioned by the author. Use this exact format:]
- [Weakness 1 mentioned by author]
- [Weakness 2 mentioned by author]
- [Weakness 3 mentioned by author]

**FINAL ARTICLE SUMMARY:**
[Provide a comprehensive summary of the entire article including:
- Overall team strategy and concept
- Key Pokemon roles and synergies
- Meta positioning and tournament viability
- Any unique strategies or innovations mentioned
- Author's recommendations and insights
- Team's competitive advantages and potential counters
- Lead combinations and selection strategies
- Specific matchups and counter strategies
- EV spread reasoning and benchmarks
- Item and ability choices explanation
- Move selection rationale
- Team building process and changes made]

**CRITICAL REQUIREMENTS FOR STRENGTHS AND WEAKNESSES:**
- ALWAYS include the "TEAM STRENGTHS:" and "TEAM WEAKNESSES:" sections even if the author doesn't explicitly mention them
- If the author doesn't mention specific strengths or weaknesses, analyze the team composition and provide 2-3 strengths and 2-3 weaknesses based on the Pokemon, items, and moves shown
- Use bullet points with dashes (-) for each strength and weakness
- Keep each point concise but specific (1-2 sentences maximum)
- Focus on competitive aspects like type coverage, speed control, defensive synergy, etc.

**IMPORTANT RULES:**
1. **ACCURATE POKEMON IDENTIFICATION**: Look carefully at the image and identify Pokémon correctly
2. **EV VALUES ONLY**: Use actual EV values (0-252 in multiples of 4), NOT final stat values
3. **EXACT FORMAT**: Follow the format above exactly with dashes and colons
4. **COMPLETE INFORMATION**: Include all 6 Pokémon even if some details are missing
5. **DETAILED EXPLANATIONS**: Include specific percentages, numbers, and benchmarks
6. **NO UNDEFINED**: Use "Not specified" for missing information

**CRITICAL EV SPREAD RULE**: If you see numbers like 175, 195, 222, 131, 219, 155, 180, 200, 160, 140, 120, 100, 80, 60, 40, 20 in the source material, these are FINAL STAT VALUES, not EV values. EV values are ONLY multiples of 4: 0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 152, 156, 160, 164, 168, 172, 176, 180, 184, 188, 192, 196, 200, 204, 208, 212, 216, 220, 224, 228, 232, 236, 240, 244, 248, 252. If you cannot determine the actual EV values from the source, write "EVs not specified in the article or image."

**Strict Instructions:**
- Do **not** infer or assume anything that is not clearly visible or mentioned.
- All missing data must be marked with: **"Not specified in the article or image."**
- Use only **standard ASCII characters**. Do not include Japanese script, accented characters, or emoji.
- Write in clear, formal **UK English** only.
- **Avoid undefined values**: Never output "undefined" or similar placeholder text. Use "Not specified in the article or image" instead.
- **Clean formatting**: Avoid broken bars, excessive separators, or unclear formatting. Use clear, consistent formatting throughout.
- **ALWAYS use official English Pokémon names, moves, abilities, and items.**
- **Translate Japanese text accurately using the provided reference lists above.**
- **IMPORTANT**: When translating Japanese Pokémon names, abilities, moves, and items, use ONLY the official English names provided in the reference lists above. Do not create new translations or use unofficial names.
- **Format consistently**: Use the exact format specified for each Pokémon breakdown.
- **EV Spreads**: Always use the English stat names (HP, Atk, Def, SpA, SpD, Spe) and provide the actual EV values invested (which should total 508 EVs), NOT the final stat values after EV investment. For example, write "252 Spe" not the final Speed stat number.
- **EV Explanations**: Provide extremely comprehensive and detailed explanations including:
  • **ALL specific percentages and survival rates** mentioned in the article (e.g., "93.6% survival rate", "87.5% chance to survive")
  • **Exact numerical targets and benchmarks** (e.g., "Reaches 200 Speed", "Survives 180 base power attacks")
  • **Specific speed benchmarks** with exact numbers (e.g., "Outspeeds max Speed [Pokémon] by 2 points")
  • **Detailed survival calculations** when provided (e.g., "Survives +2 [attack] from [Pokémon] with [item]")
  • **Damage output calculations** (e.g., "OHKOs [Pokémon] 100% of the time", "2HKOs [Pokémon]")
  • **Team synergy considerations** and how EVs support specific strategies
  • **Item and nature interactions** with EV calculations
  • **Meta-specific reasoning** for why these EVs are optimal
  • **Alternative spreads considered** if mentioned in the article
  • **Speed tier positioning** and what it outspeeds/underspeeds
  • **Defensive calculations** with specific benchmarks and survival rates
  • **Offensive calculations** with specific damage outputs and conditions
  • **Bulk calculations** and survival benchmarks
  • **Priority considerations** and speed control details
  • **Weather and terrain interactions** with EV calculations
  • **Status condition considerations** and their effects on EVs
  • **Critical hit scenarios** and their impact on EV calculations
  • **Multi-hit move considerations** and their effects
  • **Special mechanic interactions** (Z-moves, Terastallization, etc.)
  Include exact numerical targets, Pokémon names, and ALL specific details when mentioned in the article.
- **Tera Types**: Always include Tera Type in each Pokémon breakdown. Use official English type names (Normal, Fire, Water, etc.). If Tera Type is not visible in the image or text, write "Tera Type not specified in the article or image."
- **Calyrex Identification**: Pay special attention to distinguish between Calyrex forms:
  * **Calyrex Ice Rider**: White horse (Glastrier), Ice-type moves, "As One (Glastrier)" ability, Ice Tera Type
  * **Calyrex Shadow Rider**: Black horse (Spectrier), Ghost-type moves, "As One (Spectrier)" ability, Ghost Tera Type
  * **CRITICAL**: Look at the horse color (white vs black), moves (Ice vs Ghost), and ability name to determine the correct form
- **Chi-Yu vs Chien-Pao**: Pay special attention to distinguish between Chi-Yu (Fire/Dark, Beads of Ruin) and Chien-Pao (Ice/Dark, Sword of Ruin). Use moves, abilities, and visual appearance to identify correctly. **CRITICAL**: Chi-Yu has Fire-type moves and Beads of Ruin ability, while Chien-Pao has Ice-type moves and Sword of Ruin ability. Look carefully at the moveset and ability to determine which one it is.

**JAPANESE POKEMON NAME GUIDELINES:**
- **Common Japanese Pokemon Names**: 
  * ミュウツー = Mewtwo, カイオーガ = Kyogre, グラードン = Groudon, レックウザ = Rayquaza
  * バドレックス = Calyrex, ザシアン = Zacian, ザマゼンタ = Zamazenta
  * コライドン = Koraidon, ミライドン = Miraidon, テラパゴス = Terapagos
  * ウルシフー = Urshifu, リルガメ = Rillaboom, アマージョ = Amoonguss
  * アイアンクラウン = Iron Crown, アイアンジュグリス = Iron Jugulis
  * カイリュー = Dragonite, テツノブジン = Iron Valiant, モロバレル = Amoonguss
  * パオジアン = Chi-Yu, ウネルミナモ = Palafin, イーユイ = Chi-Yu
  * ウルガモス = Volcarona, オーロンゲ = Arboliva, ハバタクカミ = Flutter Mane
  * ウーラオス = Urshifu, トルネ = Tornadus, ワイガアスビ = Wide Guard
- **Form Indicators**: 
  * はくばじょうのすがた = Ice Rider form, こくばじょうのすがた = Shadow Rider form
  * いちげきのかた = Single Strike style, れんげきのかた = Rapid Strike style
- **Always translate to official English names** from the reference list above

**JAPANESE MOVE GUIDELINES:**
- **Common Japanese Move Names**:
  * アストラルバレッジ = Astral Barrage, サイコキネシス = Psychic, アンコール = Encore
  * まもる = Protect, ボディプレス = Body Press, ヘビースラム = Heavy Slam
  * ワイドガード = Wide Guard, じしん = Earthquake, かえんだん = Fire Blast
  * ハイドロポンプ = Hydro Pump, 10まんボルト = Thunderbolt, フリーズドライ = Freeze-Dry
  * ドラゴンクロー = Dragon Claw, りゅうのいかり = Dragon Rage, りゅうせいぐん = Draco Meteor
  * かえんだん = Fire Blast, かえんほうしゃ = Flamethrower, だいもんじ = Inferno
  * ハイドロポンプ = Hydro Pump, アクアジェット = Aqua Jet, なみのり = Surf
  * マジカルシャイン = Dazzling Gleam, サイコショック = Psyshock, サイコウェーブ = Psychic
  * かげぶんしん = Shadow Sneak, シャドーボール = Shadow Ball, シャドーパンチ = Shadow Punch
  * アイスビーム = Ice Beam, れいとうビーム = Ice Beam, こおりのつぶて = Ice Shard
  * かえんほうしゃ = Flamethrower, だいもんじ = Inferno, かえんだん = Fire Blast
  * ハイドロポンプ = Hydro Pump, アクアジェット = Aqua Jet, なみのり = Surf, しおのすい = Brine
  * 10まんボルト = Thunderbolt, かみなり = Thunder, でんげき = Thunder Shock
  * じしん = Earthquake, あなをほる = Dig, じばく = Self-Destruct
  * りゅうのいかり = Dragon Rage, りゅうせいぐん = Draco Meteor, りゅうのはどう = Dragon Pulse
  * どくどく = Toxic, どくのこな = Poison Powder, どくづき = Poison Sting
  * むしのさざめき = Bug Buzz, むしのていこう = Struggle Bug, むしのていこう = Struggle Bug
  * いわおとし = Rock Throw, いわなだれ = Rock Slide, がんせきふうじ = Rock Tomb
- **Move Type Indicators**:
  * でんこう = Electric moves, ほのお = Fire moves, みず = Water moves
  * こおり = Ice moves, じめん = Ground moves, ひこう = Flying moves
  * どく = Poison moves, むし = Bug moves, いわ = Rock moves
- **Always translate to official English move names**

**CRITICAL MOVE TRANSLATION RULES:**
- **Fairy Moves**: マジカルシャイン = Dazzling Gleam, ムーンフォース = Moonblast, ドレインパンチ = Draining Kiss
- **Psychic Moves**: サイコキネシス = Psychic, サイコショック = Psyshock, サイコウェーブ = Psychic
- **Ghost Moves**: シャドーボール = Shadow Ball, かげぶんしん = Shadow Sneak, シャドーパンチ = Shadow Punch
- **Ice Moves**: アイスビーム = Ice Beam, れいとうビーム = Ice Beam, こおりのつぶて = Ice Shard
- **Fire Moves**: かえんほうしゃ = Flamethrower, だいもんじ = Inferno, かえんだん = Fire Blast
- **Water Moves**: ハイドロポンプ = Hydro Pump, アクアジェット = Aqua Jet, なみのり = Surf
- **Electric Moves**: 10まんボルト = Thunderbolt, かみなり = Thunder, でんげき = Thunder Shock
- **Ground Moves**: じしん = Earthquake, あなをほる = Dig, じばく = Self-Destruct
- **Dragon Moves**: りゅうのいかり = Dragon Rage, りゅうせいぐん = Draco Meteor, りゅうのはどう = Dragon Pulse
- **Status Moves**: まもる = Protect, アンコール = Encore, ワイドガード = Wide Guard
- **Fighting Moves**: ボディプレス = Body Press, かくとう = Close Combat, ばくれつパンチ = Focus Punch

**JAPANESE ABILITY & ITEM GUIDELINES:**
- **Common Japanese Abilities**:
  * いっしょに = As One, あついしぼう = Thick Fat, かたやぶり = Mold Breaker
  * ふゆう = Levitate, すいすい = Swift Swim, すながくれ = Sand Veil
- **Common Japanese Items**:
  * きあいのタスキ = Focus Sash, こだわりハチマキ = Choice Band, こだわりメガネ = Choice Specs
  * こだわりスカーフ = Choice Scarf, たべのこし = Leftovers, オボンのみ = Sitrus Berry
- **Always translate to official English ability and item names**

**JAPANESE TEXT PATTERNS:**
- **EV Format Patterns**:
  * 努力値：H244 A252 B4 D4 S4 = Effort Values: HP244 Atk252 Def4 SpD4 Spe4
  * H188 D196 S124 = HP188 SpD196 Spe124
  * 努力値：H44 B4 C252 D28 S180 = Effort Values: HP44 Def4 SpA252 SpD28 Spe180
  * 実数値：175-*-101-217-120-222 = Actual Stats: HP175-Atk*-Def101-SpA217-SpD120-Spe222
- **Stat Abbreviations**: H=HP, A=Attack, B=Defense, C=Special Attack, D=Special Defense, S=Speed
- **Nature Patterns**: がんばりや = Adamant, おくびょう = Timid, いじっぱり = Jolly, 腕白 = Jolly, 陽気 = Modest, 意地 = Adamant, 臆病 = Timid, 呑気 = Relaxed
- **Type Patterns**: ノーマル = Normal, ほのお = Fire, みず = Water, でんき = Electric, 霊 = Ghost, 悪 = Dark, 無 = Normal
- **Item Patterns**: 気合の襷 = Focus Sash, 朽ちた盾 = Rusted Shield, 突撃チョッキ = Assault Vest, メンタルハーブ = Mental Herb, 拘り鉢巻 = Choice Band, ブーストエナジー = Booster Energy
- **Ability Patterns**: 人馬一体 = As One, 不屈の盾 = Dauntless Shield, 災いの剣 = Beads of Ruin, 再生力 = Regenerator, 精神力 = Inner Focus, クォークチャージ = Quark Drive
- **Move Patterns**: アストラルビット = Astral Barrage, サイコキネシス = Psychic, アンコール = Encore, 守る = Protect, ボディプレス = Body Press, ヘビーボンバー = Heavy Slam, ワイドガード = Wide Guard, カタストロフィ = Catastropika, アイススピナー = Ice Spinner, 不意打ち = Sucker Punch, 氷の礫 = Ice Shard, ヘドロ爆弾 = Sludge Bomb, 怒りの粉 = Rage Powder, キノコの胞子 = Spore, 神速 = Extreme Speed, けたぐり = Low Kick, 岩雪崩 = Rock Slide, 逆鱗 = Outrage, 波動弾 = Aura Sphere, マジシャ = Dazzling Gleam, 金縛り = Thunder Wave
- **Look for these patterns in both text and images** to extract accurate information

**TEAM STRATEGY EXTRACTION:**
- **Lead Combinations**: Look for patterns like "先発：ザマゼンタ＋パオジアン" (Lead: Zamazenta + Chi-Yu)
- **Back Pokemon**: Look for "後発：黒バドレックス＋モロバレル" (Back: Calyrex Shadow + Amoonguss)
- **Selection Plans**: Extract numbered plans like "＜①黒バド詰めプラン＞" (Plan 1: Calyrex Finish Plan)
- **Matchup Strategies**: Look for specific Pokemon counters and strategies
- **EV Reasoning**: Extract explanations like "・黒バドのC+2珠サイキネを93.6%耐える" (Survives Calyrex's +2 Psychic 93.6% of the time)
- **Benchmarks**: Look for survival rates, speed benchmarks, and damage calculations
- **Team Changes**: Note any Pokemon that were replaced and why

**SPECIFIC POKEMON EV PATTERNS:**
- **Iron Valiant (テツノブジン)**: Look for "H44 B4 C252 D28 S180" format in text
- **Dragonite (カイリュー)**: Look for "H244 A252 B4 D4 S4" format in text
- **Chi-Yu (パオジアン)**: Look for "H188 D196 S124" format in text
- **Calyrex Shadow (黒バドレックス)**: Look for "B4 C252 S252" format in text
- **Zamazenta (ザマゼンタ)**: Look for "H252 A4 B156 D68 S28" format in text
- **Amoonguss (モロバレル)**: Look for "H236 B220 D52" format in text

**Translation Reference:**
{restrict_poke}

**Input Content:**
#{text}#

**Note:** Use any provided images to verify information. Output in the exact format specified above.
"""

restricted_poke = """
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


# Note: fetch_article_text_and_images and wrap_prompt_and_image_urls functions
# have been moved to shared_utils.py and gemini_summary.py respectively


# Legacy compatibility function
def llm_summary(url):
    """
    Legacy function for backward compatibility
    Uses Gemini by default
    """
    try:
        from .gemini_summary import llm_summary_gemini

        return llm_summary_gemini(url)
    except ImportError:
        raise Exception(
            "Gemini module not available. Please use llm_summary_gemini() directly."
        )


def fallback_basic_parsing(article_text: str) -> str:
    """
    Basic fallback parsing when AI API is not available or quota exceeded
    Extracts Pokemon names and basic information using regex patterns

    Args:
        article_text: Raw article text to parse

    Returns:
        str: Basic parsed summary with Pokemon information
    """
    import re

    # Basic Pokemon name patterns (Japanese and English)
    pokemon_patterns = [
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # English names like "Charizard"
        r"([ァ-ヶー]+)",  # Japanese katakana
        r"([一-龯]+)",  # Japanese kanji
    ]

    # Find potential Pokemon names
    pokemon_names = set()
    for pattern in pokemon_patterns:
        matches = re.findall(pattern, article_text)
        for match in matches:
            # Filter out common non-Pokemon words
            if len(match) > 2 and match not in [
                "The",
                "And",
                "For",
                "With",
                "From",
                "This",
                "That",
            ]:
                pokemon_names.add(match)

    # Look for common Pokemon-related patterns
    ev_pattern = r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
    ev_matches = re.findall(ev_pattern, article_text)

    # Look for move patterns
    move_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    move_matches = re.findall(move_pattern, article_text)

    # Create basic summary
    summary_parts = [
        "**BASIC PARSING RESULTS (AI API Unavailable)**",
        "",
        "**Pokemon Detected:**",
    ]

    if pokemon_names:
        for i, name in enumerate(list(pokemon_names)[:10], 1):  # Limit to 10
            summary_parts.append(f"{i}. {name}")
    else:
        summary_parts.append("No Pokemon names detected")

    summary_parts.extend(
        [
            "",
            "**EV Spreads Found:**",
        ]
    )

    if ev_matches:
        for i, evs in enumerate(ev_matches[:6], 1):  # Limit to 6
            summary_parts.append(f"Pokemon {i}: {' '.join(evs)}")
    else:
        summary_parts.append("No EV spreads detected")

    summary_parts.extend(
        [
            "",
            "**Note:** This is a basic analysis without AI translation.",
            "For full analysis, please wait for your limit to reset or upgrade your plan.",
            "",
            "**Original Text Preview:**",
            article_text[:500] + "..." if len(article_text) > 500 else article_text,
        ]
    )

    return "\n".join(summary_parts)
