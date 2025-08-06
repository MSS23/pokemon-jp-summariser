import express from 'express';
import cors from 'cors';
import { GoogleGenerativeAI } from '@google/generative-ai';
import axios from 'axios';
import * as cheerio from 'cheerio';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ChatGoogleGenerativeAI } from '@langchain/google-genai';
import { HumanMessage } from '@langchain/core/messages';
import crypto from 'crypto';

// Load API key from secrets file or environment variable
let apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  try {
    // Try to load from Streamlit secrets file
    const secretsPath = path.join(process.cwd(), '..', 'streamlit-app', '.streamlit', 'secrets.toml');
    const secretsContent = await fs.readFile(secretsPath, 'utf-8');
    const match = secretsContent.match(/google_api_key\s*=\s*"([^"]+)"/);
    if (match) {
      apiKey = match[1];
      console.log('Loaded API key from Streamlit secrets file');
    }
  } catch (error) {
    console.log('Could not load API key from secrets file:', error.message);
  }
}

if (!apiKey) {
  console.log('No API key found. Please set GEMINI_API_KEY environment variable or ensure secrets.toml exists.');
}

const app = express();
const PORT = process.env.PORT || 3001;

// Cache storage
const translationCache = new Map();
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Gemini AI
const genAI = apiKey ? new GoogleGenerativeAI(apiKey) : null;

// Initialize LangChain Gemini for better compatibility
const langchainGemini = apiKey ? new ChatGoogleGenerativeAI({
  model: "gemini-2.0-flash",
  apiKey: apiKey,
  temperature: 0.0,
  maxTokens: 4000
}) : null;

// Prompt template from Streamlit app
const promptTemplate = `
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

You are provided with article text. Use the content to extract accurate team information and identify the overall team strategy.

Your response must be strictly based on the visible and written content. If anything is unclear, partial, or missing, mark it as such. **Do not make assumptions.**

**Use the text content to cross-reference and validate information from the article. If any details appear more clearly in the text, prioritise that content and ensure it is reflected accurately in your output.**

**Strategy Detection:**
Based on the team composition, moves, items, and EV spreads, identify the overall team strategy. Common strategies include:
- **Hyper Offense**: Fast, powerful attackers with Choice items, priority moves, and offensive EV spreads
- **Balance**: Mix of offensive and defensive Pokemon with support moves like Fake Out, Parting Shot, and defensive items
- **Trick Room**: Slow Pokemon with Trick Room moves, Quiet/Brave natures, and defensive EV spreads
- **Weather**: Pokemon with weather-setting abilities and weather-boosted moves
- **Stall**: Defensive Pokemon with recovery moves, status moves, and defensive items
- **Screen Support**: Pokemon with Light Screen, Reflect, and support moves
- **Priority Spam**: Pokemon with multiple priority moves and speed control
- **Setup Sweepers**: Pokemon with boosting moves like Dragon Dance, Swords Dance, or Nasty Plot

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

**EXTREMELY IMPORTANT**: When you see numbers like 175 HP, 207 HP, 202 HP, 231 HP, 165 HP, 238 Atk, 135 Atk, 164 Atk, 111 Def, 170 Def, 110 Def, 113 Def, 112 Def, 140 Def, 202 SpA, 105 SpA, 189 SpA, 82 SpA, 160 SpD, 151 SpD, 111 SpD, 121 SpD, 126 SpD, 91 SpD, 156 Spe, 49 Spe, 123 Spe, 31 Spe, 97 Spe, 173 Spe - these are ALL FINAL STAT VALUES, NOT EV VALUES. Do NOT output these as EV spreads. If you see these types of numbers, write "EVs not specified in the article" instead.
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
`;

const restrictedPoke = `
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
`;

// Cache utility functions
function generateCacheKey(url) {
  return crypto.createHash('md5').update(url).digest('hex');
}

function getCachedTranslation(url) {
  const cacheKey = generateCacheKey(url);
  const cached = translationCache.get(cacheKey);
  
  if (cached && (Date.now() - cached.timestamp) < CACHE_DURATION) {
    console.log('Cache hit for URL:', url);
    return cached.data;
  }
  
  if (cached) {
    console.log('Cache expired for URL:', url);
    translationCache.delete(cacheKey);
  }
  
  return null;
}

function setCachedTranslation(url, data) {
  const cacheKey = generateCacheKey(url);
  translationCache.set(cacheKey, {
    data: data,
    timestamp: Date.now()
  });
  console.log('Cached translation for URL:', url);
}

// Function to extract text from URL (real implementation) - Updated to match Streamlit
async function extractArticleText(url) {
  try {
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate',
      'Connection': 'keep-alive',
    };
    
    const response = await axios.get(url, { timeout: 15000, headers });
    
    if (response.encoding === 'ISO-8859-1') {
      response.encoding = 'utf-8';
    }
    
    const $ = cheerio.load(response.data);

    // Remove script, style, nav, header, footer, aside elements
    $('script, style, nav, header, footer, aside').remove();

    let mainContent = null;
    const contentSelectors = [
      'main', 'article', '.content', '.post-content', '.entry-content',
      '.article-content', '.main-content', '#content', '#main',
      '.post', '.entry', '.blog-post', '.article'
    ];
    
    for (const selector of contentSelectors) {
      mainContent = $(selector);
      if (mainContent.length > 0) {
        break;
      }
    }
    
    if (!mainContent || mainContent.length === 0) {
      mainContent = $('body').length > 0 ? $('body') : $;
    }

    const paragraphs = mainContent.find('p').map((i, el) => $(el).text().trim()).get();
    const headings = mainContent.find('h1, h2, h3, h4, h5, h6').map((i, el) => $(el).text().trim()).get();
    
    const divTexts = [];
    mainContent.find('div').each((i, el) => {
      const text = $(el).text().trim();
      if (text.length > 50 && !text.toLowerCase().includes('menu') && 
          !text.toLowerCase().includes('navigation') && !text.toLowerCase().includes('sidebar') && 
          !text.toLowerCase().includes('footer') && !text.toLowerCase().includes('header') && 
          !text.toLowerCase().includes('advertisement')) {
        divTexts.push(text);
      }
    });
    
    const allTextParts = [];
    if (headings.length > 0) {
      allTextParts.push("HEADINGS:\n" + headings.join('\n'));
    }
    if (paragraphs.length > 0) {
      allTextParts.push("CONTENT:\n" + paragraphs.join('\n'));
    }
    if (divTexts.length > 0) {
      allTextParts.push("ADDITIONAL CONTENT:\n" + divTexts.slice(0, 5).join('\n'));
    }
    
    let allText = allTextParts.join('\n\n');

    // Clean the text - match Streamlit implementation exactly
    allText = allText.replace(/[\u200b\xa0\u200e\u200f]/g, ' ');
    allText = allText.replace(/\s+/g, ' ');
    allText = allText.replace(/[^\w\s\-\.\,\!\?\:\;\(\)\[\]\{\}\/\@\#\$\%\&\*\+\=\|\~\`\'\"]/g, '');
    allText = allText.trim();

    return allText;
  } catch (error) {
    console.error('Error fetching URL:', error);
    throw new Error(`Failed to fetch article: ${error.message}`);
  }
}

// Function to extract images from URL (matching Streamlit implementation)
async function extractImages(url) {
  try {
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate',
      'Connection': 'keep-alive',
    };
    
    const response = await axios.get(url, { timeout: 15000, headers });
    const $ = cheerio.load(response.data);
    
    const imageTags = $('img');
    const imageUrls = [];
    
    imageTags.each((i, el) => {
      const src = $(el).attr('src');
      if (src) {
        let fullUrl = src;
        if (src.startsWith('//')) {
          fullUrl = 'https:' + src;
        } else if (src.startsWith('/')) {
          const baseUrl = url.split('//')[0] + '//' + url.split('/')[2];
          fullUrl = baseUrl + src;
        } else if (!src.startsWith('http')) {
          const baseUrl = url.split('/').slice(0, -1).join('/') + '/';
          fullUrl = baseUrl + src;
        }
        
        if (!fullUrl.toLowerCase().includes('logo') && 
            !fullUrl.toLowerCase().includes('icon') && 
            !fullUrl.toLowerCase().includes('avatar') && 
            !fullUrl.toLowerCase().includes('banner') && 
            !fullUrl.toLowerCase().includes('ad') && 
            !fullUrl.toLowerCase().includes('ads')) {
          imageUrls.push(fullUrl);
        }
      }
    });
    
    return imageUrls;
  } catch (error) {
    console.error('Error extracting images:', error);
    return [];
  }
}

// Function to wrap prompt with image URLs for multimodal processing (matching Streamlit)
function wrapPromptAndImageUrls(prompt, imageUrls) {
  console.log('wrapPromptAndImageUrls called with:');
  console.log('- prompt length:', prompt ? prompt.length : 'undefined');
  console.log('- prompt preview:', prompt ? prompt.substring(0, 100) : 'undefined');
  console.log('- imageUrls count:', imageUrls ? imageUrls.length : 'undefined');
  
  const content = [{ type: "text", text: prompt }];
  
  for (const url of imageUrls) {
    if (url.toLowerCase().includes('.png') || 
        url.toLowerCase().includes('.jpg') || 
        url.toLowerCase().includes('.jpeg') || 
        url.toLowerCase().includes('.webp')) {
      content.push({
        type: "image_url",
        image_url: { url: url }
      });
    }
  }
  
  console.log('Content parts created:', content.length);
  console.log('First content part type:', content[0] ? content[0].type : 'undefined');
  console.log('First content part text length:', content[0] && content[0].text ? content[0].text.length : 'undefined');
  
  return content;
}

// Function to validate and fix EV spreads
function validateAndFixEVSpread(evSpread) {
  if (!evSpread || evSpread === 'Not specified in the article') {
    return 'EVs not specified in the article';
  }
  
  // Check if the spread contains typical final stat values (3-digit numbers)
  const statPattern = /\b(1[0-9][0-9]|2[0-9][0-9]|3[0-9][0-9])\b/;
  if (statPattern.test(evSpread)) {
    return 'EVs not specified in the article (final stat values detected)';
  }
  
  // Check if the spread contains valid EV values (multiples of 4, 0-252)
  const evValues = evSpread.match(/\b(\d+)\b/g);
  if (evValues) {
    for (const value of evValues) {
      const num = parseInt(value);
      if (num < 0 || num > 252 || num % 4 !== 0) {
        return 'EVs not specified in the article (invalid EV values detected)';
      }
    }
  }
  
  return evSpread;
}

// Function to parse Gemini response into structured format
function parseGeminiResponse(text) {
  try {
    // Extract title
    const titleMatch = text.match(/TITLE:\s*(.+?)(?:\n|$)/);
    const title = titleMatch ? titleMatch[1].trim() : 'Not specified';

    // Extract Pokemon teams
    const pokemonSections = text.split(/\*\*Pokémon \d+:/);
    const teams = [];

    for (let i = 1; i < pokemonSections.length && i <= 6; i++) {
      const section = pokemonSections[i];
      const lines = section.split('\n');
      
      // Extract Pokemon name
      const nameMatch = lines[0].match(/\[([^\]]+)\]/);
      const pokemonName = nameMatch ? nameMatch[1].trim() : 'Unknown Pokemon';
      
             // Extract other details
       const abilityMatch = section.match(/Ability:\s*(.+?)(?:\n|$)/);
       const itemMatch = section.match(/Held Item:\s*(.+?)(?:\n|$)/);
       const teraMatch = section.match(/Tera Type:\s*(.+?)(?:\n|$)/);
       const movesMatch = section.match(/Moves:\s*(.+?)(?:\n|$)/);
       const evMatch = section.match(/EV Spread:\s*(.+?)(?:\n|$)/);
       const natureMatch = section.match(/Nature:\s*(.+?)(?:\n|$)/);
       const evExplanationMatch = section.match(/EV Explanation:\s*([\s\S]*?)(?:\*\*Pokémon|\*\*Conclusion|$)/);

       // Validate and fix EV spread
       const rawEVSpread = evMatch ? evMatch[1].trim() : 'Not specified';
       const validatedEVSpread = validateAndFixEVSpread(rawEVSpread);

       const team = {
         pokemon: pokemonName,
         level: 50,
         hp: { current: 100, max: 150 },
         status: 'Healthy',
         teraType: teraMatch ? teraMatch[1].trim() : 'Not specified',
         types: [], // Will be populated based on Pokemon name
         item: itemMatch ? itemMatch[1].trim() : 'Not specified',
         ability: abilityMatch ? abilityMatch[1].trim() : 'Not specified',
         nature: natureMatch ? natureMatch[1].trim() : 'Not specified',
         moves: movesMatch ? movesMatch[1].split('/').map(move => ({
           name: move.trim(),
           bp: 0,
           checked: true
         })) : [],
         stats: {
           hp: { base: 100, evs: 0, ivs: 31, final: 150 },
           attack: { base: 100, evs: 0, ivs: 31, final: 100 },
           defense: { base: 100, evs: 0, ivs: 31, final: 100 },
           spAtk: { base: 100, evs: 0, ivs: 31, final: 100 },
           spDef: { base: 100, evs: 0, ivs: 31, final: 100 },
           speed: { base: 100, evs: 0, ivs: 31, final: 100 }
         },
         bst: 600,
         remainingEvs: 508,
         strategy: evExplanationMatch ? evExplanationMatch[1].trim() : 'Not specified',
         evSpread: validatedEVSpread // Add the validated EV spread
       };

       // Parse EV spread if available and valid
       if (validatedEVSpread !== 'EVs not specified in the article' && 
           validatedEVSpread !== 'EVs not specified in the article (final stat values detected)' &&
           validatedEVSpread !== 'EVs not specified in the article (invalid EV values detected)') {
         const evValues = validatedEVSpread.split(/\s+/);
         if (evValues.length >= 6) {
           team.stats.hp.evs = parseInt(evValues[0]) || 0;
           team.stats.attack.evs = parseInt(evValues[1]) || 0;
           team.stats.defense.evs = parseInt(evValues[2]) || 0;
           team.stats.spAtk.evs = parseInt(evValues[3]) || 0;
           team.stats.spDef.evs = parseInt(evValues[4]) || 0;
           team.stats.speed.evs = parseInt(evValues[5]) || 0;
           
           // Calculate remaining EVs
           const totalEvs = team.stats.hp.evs + team.stats.attack.evs + team.stats.defense.evs + 
                           team.stats.spAtk.evs + team.stats.spDef.evs + team.stats.speed.evs;
           team.remainingEvs = 508 - totalEvs;
         }
       }

      teams.push(team);
    }

    // Extract mentioned Pokemon
    const mentionedPokemon = [];
    const pokemonNames = teams.map(team => team.pokemon);
    mentionedPokemon.push(...pokemonNames);

    // Detect overall strategy based on team composition
    let overallStrategy = 'Balance'; // Default
    const strategyIndicators = {
      'Hyper Offense': ['Choice Scarf', 'Choice Band', 'Choice Specs', 'Life Orb', 'Focus Sash'],
      'Trick Room': ['Trick Room', 'Quiet', 'Brave', 'Slow'],
      'Weather': ['Drought', 'Drizzle', 'Sand Stream', 'Snow Warning'],
      'Stall': ['Leftovers', 'Black Sludge', 'Recover', 'Wish', 'Protect'],
      'Screen Support': ['Light Screen', 'Reflect', 'Aurora Veil'],
      'Priority Spam': ['Fake Out', 'Extreme Speed', 'Aqua Jet', 'Bullet Punch'],
      'Setup Sweepers': ['Dragon Dance', 'Swords Dance', 'Nasty Plot', 'Calm Mind']
    };

    for (const [strategy, indicators] of Object.entries(strategyIndicators)) {
      const hasStrategy = teams.some(team => 
        indicators.some(indicator => 
          team.moves.some(move => move.name.includes(indicator)) ||
          team.item.includes(indicator) ||
          team.nature.includes(indicator) ||
          team.ability.includes(indicator)
        )
      );
      if (hasStrategy) {
        overallStrategy = strategy;
        break;
      }
    }

    // Check if any teams have invalid EV spreads
    const hasInvalidEVs = teams.some(team => 
      team.evSpread && team.evSpread.includes('final stat values detected')
    );

    return {
      originalText: text,
      translatedText: text, // The response is already in English
      summary: text,
      articleTitle: title,
      overallStrategy: overallStrategy,
      teams: teams,
      mentionedPokemon: mentionedPokemon,
      translationConfidence: 95,
      processingTime: 2.3,
      translatedDate: new Date().toISOString().split('T')[0],
      evWarning: hasInvalidEVs ? 'Note: Some Pokémon EV spreads were not available in the article. Final stat values were detected instead of EV investments.' : null
    };
  } catch (error) {
    console.error('Error parsing Gemini response:', error);
    throw new Error('Failed to parse AI response');
  }
}

// API endpoint for summarizing articles
app.post('/api/summarize', async (req, res) => {
  try {
    console.log('API call received:', req.body);
    const { url } = req.body;
    
    if (!url) {
      console.log('No URL provided');
      return res.status(400).json({ error: 'URL is required' });
    }

    console.log('Processing URL:', url);

    // Check cache first
    const cachedResult = getCachedTranslation(url);
    if (cachedResult) {
      console.log('Returning cached result for URL:', url);
      return res.json(cachedResult);
    }

    // Check if Gemini API key is available
    if (!langchainGemini) {
      console.log('No LangChain Gemini available');
      return res.status(400).json({ 
        error: 'Gemini API key not configured. The application will try to load it from the Streamlit secrets file or you can set GEMINI_API_KEY environment variable.' 
      });
    }

    console.log('Gemini API key is available, extracting article content...');

    // Extract text and images from the URL (matching Streamlit implementation)
    const [articleText, imageUrls] = await Promise.all([
      extractArticleText(url),
      extractImages(url)
    ]);
    
    if (!articleText) {
      console.log('Could not extract text from URL');
      return res.status(400).json({ error: 'Could not extract text from URL' });
    }

    console.log('Article text extracted, length:', articleText.length);
    console.log('Images found:', imageUrls.length);
    console.log('First 200 characters:', articleText.substring(0, 200));

    // Create prompt (matching Streamlit implementation)
    const prompt = promptTemplate
      .replace('{restrict_poke}', restrictedPoke)
      .replace('{text}', articleText);

    console.log('Sending request to Gemini API via LangChain...');
    console.log('Prompt length:', prompt.length);
    console.log('Article text length:', articleText.length);
    console.log('First 500 characters of prompt:', prompt.substring(0, 500));
    console.log('Last 500 characters of prompt:', prompt.substring(prompt.length - 500));
    
    // Validate prompt is not empty
    if (!prompt || prompt.trim().length === 0) {
      console.error('Prompt is empty!');
      return res.status(400).json({ error: 'Failed to create prompt - article text may be empty' });
    }

    try {
      // Use multimodal approach matching Streamlit implementation
      const contentParts = wrapPromptAndImageUrls(prompt, imageUrls);
      const message = new HumanMessage({ content: contentParts });
      
      console.log('Sending multimodal request with', contentParts.length, 'content parts');
      
      const response = await langchainGemini.invoke([message]);
      const text = response.content;
      
      console.log('Gemini response received, length:', text.length);
      console.log('First 200 characters of response:', text.substring(0, 200));
      
      // Parse the response into structured format
      const parsedResponse = parseGeminiResponse(text);
      
      // Cache the result
      setCachedTranslation(url, parsedResponse);
      
      console.log('Response parsed successfully, cached, and sending to client');
      res.json(parsedResponse);
      
    } catch (geminiError) {
      console.error('Gemini API Error Details:', geminiError);
      
      // Check if it's a rate limit error
      if (geminiError.message.includes('429') || geminiError.message.includes('quota')) {
        return res.status(429).json({ 
          error: 'API rate limit exceeded. The free tier has daily and per-minute limits. Please wait a few minutes and try again, or upgrade your Gemini API plan for higher limits.',
          details: 'Your API key is working correctly, but you have reached the free tier limits. Each article translation typically uses 1-2 API calls.',
          retryAfter: 'Wait 1-2 minutes before trying again'
        });
      }
      
      throw new Error(`Gemini API Error: ${geminiError.message}`);
    }

  } catch (error) {
    console.error('Error processing article:', error);
    res.status(500).json({ error: 'Failed to process article: ' + error.message });
  }
});

// Cache management endpoints
app.get('/api/cache/status', (req, res) => {
  const cacheInfo = {
    size: translationCache.size,
    entries: Array.from(translationCache.entries()).map(([key, value]) => ({
      key: key,
      timestamp: value.timestamp,
      age: Date.now() - value.timestamp,
      expiresIn: CACHE_DURATION - (Date.now() - value.timestamp)
    }))
  };
  res.json(cacheInfo);
});

app.delete('/api/cache/clear', (req, res) => {
  const clearedCount = translationCache.size;
  translationCache.clear();
  console.log('Cache cleared, removed', clearedCount, 'entries');
  res.json({ message: `Cache cleared. Removed ${clearedCount} entries.` });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 