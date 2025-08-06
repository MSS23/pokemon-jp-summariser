"""
Shared VGC analysis prompt template
Used by both Streamlit and React applications for consistent Gemini AI analysis
"""

# Main prompt template for VGC team analysis
VGC_ANALYSIS_PROMPT = """
Act as a Pokémon VGC (Video Game Championships) expert analysing teams for Pokémon Scarlet and Violet's current competitive format.

**Current Format: Regulation I**
- Two restricted Pokémon are allowed per team.
- You may refer to the restricted Pokémon list below to assist with translations and identifications from Japanese text or image content.

**Restricted Pokémon Reference List:**
{restrict_poke}

**CRITICAL TRANSLATION GUIDELINES:**

**Pokémon Names - Use Official English Names:**
**IMPORTANT: Chi-Yu vs Chien-Pao Distinction:**
- Chi-Yu (パオジアン) is the Fire/Dark legendary with Beads of Ruin ability
- Chien-Pao (チオンジェン/チェンパオ/チエンパオ) is the Ice/Dark legendary with Sword of Ruin ability
- When in doubt, look at the moves, abilities, and visual appearance in images to distinguish them

**Common Abilities - Use Official English Names:**
- 人馬一体 (Jinba Ittai) = As One
- 不屈の盾 (Fukutsu no Tate) = Dauntless Shield
- 災いの剣 (Wazawai no Ken) = Beads of Ruin
- 再生力 (Saiseiryoku) = Regenerator
- 精神力 (Seishinryoku) = Inner Focus
- クォークチャージ (Quark Charge) = Quark Drive
- すいすい (Suisui) = Swift Swim
- かたやぶり (Katayaburi) = Mold Breaker
- てんのめぐみ (Ten no Megumi) = Serene Grace
- ふしぎなまもり (Fushigi na Mamori) = Wonder Guard
- かげふみ (Kagefumi) = Shadow Tag
- プレッシャー (Pressure) = Pressure
- がんじょう (Ganjo) = Sturdy
- きもったま (Kimottama) = Guts
- しんりょく (Shinryoku) = Overgrow
- もうか (Moka) = Blaze
- げきりゅう (Gekiryuu) = Torrent
- むしのしらせ (Mushi no Shirase) = Swarm
- いかく (Ikaku) = Intimidate
- ふゆう (Fuyuu) = Levitate
- てつのこころ (Tetsu no Kokoro) = Clear Body
- すいほう (Suihou) = Water Absorb
- ひでり (Hideri) = Drought
- あめふらし (Amefurashi) = Drizzle
- すなあらし (Sunaarashi) = Sand Stream
- ゆきふらし (Yukifurashi) = Snow Warning
- エアロック (Air Lock) = Air Lock
- きずなへんげ (Kizuna Henge) = Battle Bond
- ビーストブースト (Beast Boost) = Beast Boost
- フェアリーオーラ (Fairy Aura) = Fairy Aura
- ダークオーラ (Dark Aura) = Dark Aura
- オーラブレイク (Aura Break) = Aura Break
- フラワーベール (Flower Veil) = Flower Veil
- スイートベール (Sweet Veil) = Sweet Veil
- チェックベール (Check Veil) = Check Veil
- ミストベール (Mist Veil) = Mist Veil
- サイコサーフ (Psycho Surf) = Psychic Surge
- エレクトリックサーフ (Electric Surf) = Electric Surge
- グラスサーフ (Grass Surf) = Grassy Surge
- ミストサーフ (Mist Surf) = Misty Surge
- サイコシフト (Psycho Shift) = Psychic Shift
- エレクトリックシフト (Electric Shift) = Electric Shift
- グラスシフト (Grass Shift) = Grassy Shift
- ミストシフト (Mist Shift) = Misty Shift

**Common Moves - Use Official English Names:**
- アストラルビット (Astral Barrage) = Astral Barrage
- サイコキネシス (Psychokinesis) = Psychic
- アンコール (Encore) = Encore
- 守る (Mamoru) = Protect
- ボディプレス (Body Press) = Body Press
- ヘビーボンバー (Heavy Bomber) = Heavy Slam
- ワイドガード (Wide Guard) = Wide Guard
- カタストロフィ (Catastrophe) = Ruination
- アイススピナー (Ice Spinner) = Ice Spinner
- 不意打ち (Sneak Attack) = Sucker Punch
- 氷の礫 (Ice Pebble) = Ice Shard
- ヘドロ爆弾 (Sludge Bomb) = Sludge Bomb
- 怒りの粉 (Rage Powder) = Rage Powder
- キノコの胞子 (Mushroom Spore) = Spore
- 神速 (Extreme Speed) = Extreme Speed
- けたぐり (Low Kick) = Low Kick
- 岩雪崩 (Rock Slide) = Rock Slide
- 逆鱗 (Outrage) = Outrage
- 波動弾 (Wave Ball) = Aura Sphere
- マジシャ (Magical Shine) = Magical Shine
- 金縛り (Binding) = Imprison
- でんこうせっか (Denko Sekka) = Thunderbolt
- かえんだん (Kaendan) = Fire Blast
- れいとうビーム (Reito Beam) = Ice Beam
- サイコウェーブ (Psycho Wave) = Psyshock
- りゅうのいかり (Ryu no Ikari) = Dragon Claw
- かげうち (Kageuchi) = Shadow Sneak
- つばめがえし (Tsubamegaeshi) = Aerial Ace
- いわなだれ (Iwa Nadare) = Rock Slide
- じしん (Jishin) = Earthquake
- ほのおのうず (Honoo no Uzu) = Fire Spin
- みずでっぽう (Mizu Deppou) = Water Gun
- でんげき (Dengeki) = Thunder Shock
- つるぎのまい (Tsurugi no Mai) = Sacred Sword
- きあいだま (Kiai Dama) = Focus Blast
- りゅうせいぐん (Ryuseigun) = Draco Meteor
- ふぶき (Fubuki) = Blizzard
- かみなり (Kaminari) = Thunder
- だいもんじ (Daimonji) = Fire Blast
- ハイドロポンプ (Hydro Pump) = Hydro Pump
- ギガインパクト (Giga Impact) = Giga Impact
- ハイパービーム (Hyper Beam) = Hyper Beam
- ソーラービーム (Solar Beam) = Solar Beam
- フリーズドライ (Freeze-Dry) = Freeze-Dry
- パワージェム (Power Gem) = Power Gem
- ダークパルス (Dark Pulse) = Dark Pulse
- ドラゴンパルス (Dragon Pulse) = Dragon Pulse
- フラッシュキャノン (Flash Cannon) = Flash Cannon
- エナジーボール (Energy Ball) = Energy Ball
- サイコブースト (Psycho Boost) = Psycho Boost
- ブレイズキック (Blaze Kick) = Blaze Kick
- スカイアッパー (Sky Uppercut) = Sky Uppercut
- クロスチョップ (Cross Chop) = Cross Chop
- ドレインパンチ (Drain Punch) = Drain Punch
- マッハパンチ (Mach Punch) = Mach Punch
- バレットパンチ (Bullet Punch) = Bullet Punch
- メタルクロー (Metal Claw) = Metal Claw
- アイアンテール (Iron Tail) = Iron Tail
- ドラゴンテール (Dragon Tail) = Dragon Tail
- アクアテール (Aqua Tail) = Aqua Tail
- ポイズンテール (Poison Tail) = Poison Tail
- しっぽをふる (Shippo wo Furu) = Tail Whip
- かみくだく (Kamikudaku) = Crunch
- かみつく (Kamitsuku) = Bite
- つつく (Tsutsuku) = Peck
- つばさでうつ (Tsubasa de Utsu) = Wing Attack
- つめでひっかく (Tsume de Hikkaku) = Scratch
- パンチ (Punch) = Punch
- キック (Kick) = Kick
- ヘッドバット (Headbutt) = Headbutt
- ボディスラム (Body Slam) = Body Slam
- とっしん (Tosshin) = Tackle
- でんこう (Denko) = Quick Attack
- でんこうがえし (Denkogaeshi) = Volt Switch
- とんぼがえり (Tonbogaeri) = U-turn
- ふきとばし (Fukitobashi) = Gust
- かぜおこし (Kazeokoshi) = Whirlwind
- つむじかぜ (Tsumujikaze) = Twister
- りゅうのまい (Ryu no Mai) = Dragon Dance
- つるぎのまい (Tsurugi no Mai) = Sacred Sword
- かげぶんしん (Kagebunshin) = Double Team
- かげふみ (Kagefumi) = Shadow Sneak
- かげうち (Kageuchi) = Shadow Sneak
- かげのボール (Kage no Ball) = Shadow Ball
- かげのつめ (Kage no Tsume) = Shadow Claw
- かげのパンチ (Kage no Punch) = Shadow Punch
- かげのキック (Kage no Kick) = Shadow Kick
- かげのテール (Kage no Tail) = Shadow Tail
- かげのビーム (Kage no Beam) = Shadow Beam
- かげのウェーブ (Kage no Wave) = Shadow Wave
- かげのパルス (Kage no Pulse) = Shadow Pulse
- かげのブースト (Kage no Boost) = Shadow Boost
- かげのキャノン (Kage no Cannon) = Shadow Cannon

**Held Items - Use Official English Names:**
- 気合の襷 (Fighting Spirit Sash) = Focus Sash
- チョッキ (Vest) = Assault Vest
- 鉢巻 (Headband) = Choice Band
- ブーストエナジー (Boost Energy) = Booster Energy

**Tera Types - Use Official English Names:**
- ノーマル (Normal) = Normal
- ほのお (Fire) = Fire
- みず (Water) = Water
- でんき (Electric) = Electric
- くさ (Grass) = Grass
- こおり (Ice) = Ice
- かくとう (Fighting) = Fighting
- どく (Poison) = Poison
- じめん (Ground) = Ground
- ひこう (Flying) = Flying
- エスパー (Psychic) = Psychic
- むし (Bug) = Bug
- いわ (Rock) = Rock
- ゴースト (Ghost) = Ghost
- ドラゴン (Dragon) = Dragon
- あく (Dark) = Dark
- はがね (Steel) = Steel
- フェアリー (Fairy) = Fairy

**EV Spread Mapping:**
When you see Japanese EV labels, use this mapping:
- H = HP
- A = Attack  
- B = Defense
- C = Special Attack
- D = Special Defense
- S = Speed

**Your Task:**

You are provided with article text. Use the content to extract accurate team information.

Your response must be strictly based on the visible and written content. If anything is unclear, partial, or missing, mark it as such. **Do not make assumptions.**

**Use the text content to cross-reference and validate information from the article. If any details appear more clearly in the text, prioritise that content and ensure it is reflected accurately in your output.**

---

**Key Text Interpretation Rule:**
Some text includes stat labels and numbers like:

H A B C D S followed by 252 0 100 0 156 0

This mapping represents the Pokémon's EV spread:
- H = HP
- A = Attack
- B = Defence
- C = Special Attack
- D = Special Defence
- S = Speed

If you see this layout in the text, interpret the values accordingly and include the EVs in your breakdown. **These are the actual EV values invested, not the final stat values.** If the layout is not present or values are unclear, write: **"EVs not specified in the article."**

**Tera Type Identification:**
Look for Tera Type mentions in the text. Common Tera Types include:
- Normal (grey), Fire (red), Water (blue), Electric (yellow), Grass (green)
- Ice (light blue), Fighting (orange), Poison (purple), Ground (brown)
- Flying (light blue), Psychic (pink), Bug (green), Rock (brown)
- Ghost (purple), Dragon (purple), Dark (dark purple), Steel (grey), Fairy (pink)

If Tera Type is visible in the text, include it in the breakdown. If not specified, write: **"Tera Type not specified in the article."**

---

1. **Extract the title** of the article or blog post.
   - If there is a clear blog or article title (e.g. a headline at the top), write it as:

     TITLE: [Japanese Title]（[English Translation]）

   - If the title is already in English, write: TITLE: [English Title]
   - If there is no title or it's unclear, write: TITLE: Not specified
   - **Important**: Always provide both Japanese and English versions when possible, separated by parentheses

2. **Translate** all non-English text (e.g. Pokémon names, moves, or EV labels in Japanese) into English, using the restricted Pokémon list and translation guidelines above where helpful.

3. **Analyse** the team strictly based on the provided content (text):
   - List exactly **six Pokémon**.
   - If any Pokémon is missing or cannot be identified from the source, write: **"Pokémon not identifiable in the article."**
   - Only include reasoning, synergy, or strategy if explicitly described.
   - Avoid all speculation or inference.
   - **Pay special attention to EV explanations**: Look for detailed reasoning about why specific EVs were invested, including speed benchmarks, survival calculations, damage thresholds, and team synergy considerations. Include ALL specific percentages, numerical targets, and survival rates mentioned in the article. Be extremely thorough in extracting every detail about EV reasoning. **CRITICAL**: Always include exact percentages when mentioned (e.g., "93.6% survival rate", "87.5% chance to survive"), specific numerical targets (e.g., "Reaches 200 Speed", "Survives 180 base power attacks"), and precise benchmarks (e.g., "Outspeeds max Speed [Pokémon] by 2 points").
- **Double-check EV values**: Before outputting any EV spread, verify that the numbers are actual EV values (0-252 in increments of 4) and not final stat values. If you see numbers like 175, 195, 222, these are final stats, not EVs.
- **Identify Tera Types**: Look for Tera Type mentions in the text. Include Tera Type in each Pokémon breakdown.

4. **Individual Pokémon Breakdown** (for each of the six slots):
   Format each Pokémon exactly as follows:
   
   **Pokémon 1: [English Name]**
- Ability: [English Ability Name]
- Held Item: [English Item Name]
- Tera Type: [English Tera Type Name]
- Moves: [Move 1] / [Move 2] / [Move 3] / [Move 4]
- EV Spread: [HP EVs] [Atk EVs] [Def EVs] [SpA EVs] [SpD EVs] [Spe EVs]
- Nature: [English Nature Name]
- EV Explanation: [Provide an extremely detailed and comprehensive breakdown including:
  • **Exact EV Investment Reasoning**: Specific numbers and reasoning (e.g., "252 Speed EVs to outspeed max Speed [Pokémon] by 1 point")
  • **Survival Benchmarks with Percentages**: Exact survival rates when mentioned (e.g., "Survives [specific attack] from [Pokémon] with [item] 93.6% of the time", "Survives [attack] from [Pokémon] 87.5% of the time")
  • **Speed Control Details**: Precise speed benchmarks and targets (e.g., "Outspeeds max Speed [Pokémon] by 2 points", "Faster than [Pokémon] but slower than [Pokémon]")
  • **Damage Calculations**: Specific damage outputs and OHKO chances (e.g., "OHKOs [Pokémon] with [move] 100% of the time", "2HKOs [Pokémon] with [move]")
  • **Numerical Targets**: Any specific stat numbers, damage thresholds, or benchmarks mentioned (e.g., "Reaches 200 Speed to outspeed [Pokémon]", "Survives 180 base power attacks")
  • **Team Synergy Considerations**: How EVs support specific teammates or team strategies (e.g., "Supports [teammate] by surviving [specific threat]", "Enables [specific team strategy]")
  • **Item Interactions**: How held items affect EV calculations (e.g., "With [item], survives [attack] from [Pokémon]")
  • **Nature Considerations**: How nature affects the EV spread (e.g., "Timid nature allows fewer Speed EVs to outspeed [Pokémon]")
  • **Meta-Specific Reasoning**: Why these EVs are optimal for the current meta (e.g., "Reduced Defense EVs due to decline in [Pokémon] usage")
  • **Alternative Spreads Considered**: If the article mentions alternative EV spreads that were considered
  • **Survival Calculations**: Specific damage calculations and survival percentages when provided
  • **Speed Tiers**: Exact speed tier positioning and what it outspeeds/underspeeds
  • **Defensive Calculations**: Specific defensive benchmarks (e.g., "Survives [attack] from [Pokémon] with [item] 95% of the time")
  • **Offensive Calculations**: Specific damage outputs (e.g., "OHKOs [Pokémon] with [move] after [condition]")
  • **Speed Tier Analysis**: Exact positioning in speed tiers and what it outspeeds/underspeeds
  • **Bulk Calculations**: Specific bulk benchmarks and survival rates
  • **Priority Considerations**: How EVs affect priority moves and speed control
  • **Weather Interactions**: How weather affects EV calculations
  • **Terrain Interactions**: How terrain affects EV calculations
  • **Status Condition Considerations**: How status conditions affect EV calculations
  • **Critical Hit Calculations**: How EVs affect critical hit scenarios
  • **Multi-hit Move Considerations**: How EVs affect multi-hit move scenarios
  • **Z-Move/Terastallization Interactions**: How EVs work with special mechanics
  If no detailed explanation is provided, write "Not specified in the article"]
  
  **EV EXPLANATION FORMAT**: Each EV explanation should be comprehensive and include:
  - Specific percentages when mentioned (e.g., "93.6% survival rate")
  - Exact numerical targets (e.g., "Reaches 200 Speed")
  - Precise benchmarks (e.g., "Outspeeds max Speed [Pokémon] by 2 points")
  - Detailed survival calculations when provided
  - Team synergy considerations
  - Meta-specific reasoning
  - Item and nature interactions
   
   **CRITICAL**: EV Spread should show the actual EV values invested (which should total 508 EVs), NOT the final stat values after EV investment. For example, if a Pokémon has max Speed EVs, write "252 Spe" not the final Speed stat number.
   
   **EV SPREAD VALIDATION**: Before outputting any EV spread, verify that:
   - The numbers represent EVs invested (typically 0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 152, 156, 160, 164, 168, 172, 176, 180, 184, 188, 192, 196, 200, 204, 208, 212, 216, 220, 224, 228, 232, 236, 240, 244, 248, 252)
   - NOT final stat values (which can be any number like 175, 195, 222, etc.)
   - The total EVs should equal 508 (or less if some EVs are not invested)
   - If you see numbers like 175, 195, 222 in the source, these are FINAL STATS, not EVs
   - **DOUBLE-CHECK**: If you see numbers like 131, 219, 155, 175, 195, 222, 180, 200, etc., these are FINAL STAT VALUES, not EV values
   - **EV VALUES ONLY**: Only use numbers that are multiples of 4 (0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 152, 156, 160, 164, 168, 172, 176, 180, 184, 188, 192, 196, 200, 204, 208, 212, 216, 220, 224, 228, 232, 236, 240, 244, 248, 252)
   - **WHEN IN DOUBT**: If you cannot determine the actual EV values from the source, write "EVs not specified in the article"
   
   Repeat this format for all 6 Pokémon. Use the EV mapping specified above (HP, Atk, Def, SpA, SpD, Spe instead of H, A, B, C, D, S).

5. **Conclusion Summary**:
   - Team strengths
   - Notable weaknesses or counters
   - Meta relevance and effectiveness (if discussed)

---

**Strict Instructions:**
- Do **not** infer or assume anything that is not clearly visible or mentioned.
- All missing data must be marked with: **"Not specified in the article."**
- Use only **standard ASCII characters**. Do not include Japanese script, accented characters, or emoji.
- Write in clear, formal **UK English** only.
- **Avoid undefined values**: Never output "undefined" or similar placeholder text. Use "Not specified in the article" instead.
- **Clean formatting**: Avoid broken bars, excessive separators, or unclear formatting. Use clear, consistent formatting throughout.
- **ALWAYS use official English Pokémon names, moves, abilities, and items.**
- **Translate Japanese text accurately using the provided reference lists above.**
- **IMPORTANT**: When translating Japanese Pokémon names, abilities, moves, and items, use ONLY the official English names provided in the reference lists above. Do not create new translations or use unofficial names.
- **Format consistently**: Use the exact format specified for each Pokémon breakdown.
- **EV Spreads**: Always use the English stat names (HP, Atk, Def, SpA, SpD, Spe) and provide the actual EV values invested (which should total 508 EVs), NOT the final stat values after EV investment. For example, write "252 Spe" not the final Speed stat number.
  
  **CRITICAL EV SPREAD RULE**: If you see numbers like 175, 195, 222, 131, 219, 155, 180, 200, 160, 140, 120, 100, 80, 60, 40, 20 in the source material, these are FINAL STAT VALUES, not EV values. EV values are ONLY multiples of 4: 0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 152, 156, 160, 164, 168, 172, 176, 180, 184, 188, 192, 196, 200, 204, 208, 212, 216, 220, 224, 228, 232, 236, 240, 244, 248, 252. If you cannot determine the actual EV values from the source, write "EVs not specified in the article."
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
- **Tera Types**: Always include Tera Type in each Pokémon breakdown. Use official English type names (Normal, Fire, Water, etc.). If Tera Type is not visible in the text, write "Tera Type not specified in the article."
- **Chi-Yu vs Chien-Pao**: Pay special attention to distinguish between Chi-Yu (Fire/Dark, Beads of Ruin) and Chien-Pao (Ice/Dark, Sword of Ruin). Use moves, abilities, and visual appearance to identify correctly. **CRITICAL**: Chi-Yu has Fire-type moves and Beads of Ruin ability, while Chien-Pao has Ice-type moves and Sword of Ruin ability. Look carefully at the moveset and ability to determine which one it is.

**Input Content:**
{text}

**Note:** Analyze the text content to extract team information.
"""

def get_formatted_prompt(restricted_pokemon_list: str, article_text: str) -> str:
    """
    Get formatted prompt with restricted Pokemon list and article text
    
    Args:
        restricted_pokemon_list (str): Restricted Pokemon reference list
        article_text (str): Article text to analyze
    
    Returns:
        str: Formatted prompt ready for Gemini
    """
    return VGC_ANALYSIS_PROMPT.format(
        restrict_poke=restricted_pokemon_list,
        text=article_text
    ) 