/**
 * Google Gemini integration service for Pokemon VGC article summarization
 * Direct integration without FastAPI middleman
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import { ChatGoogleGenerativeAI } from '@langchain/google-genai';
import { HumanMessage } from '@langchain/core/messages';

// Types
export interface PokemonTeamMember {
  name: string;
  level?: number;
  ability?: string;
  moves: string[];
  item?: string;
  nature?: string;
  evs?: Record<string, number>;
  ivs?: Record<string, number>;
  teraType?: string;
  evExplanation?: string;
}

export interface ArticleAnalysis {
  title: string;
  summary: string;
  team: PokemonTeamMember[];
  pokemonNames: string[];
  strengths: string[];
  weaknesses: string[];
  meta: {
    processingTime: number;
    source: string;
    language: string;
  };
}

export interface GeminiResponse {
  success: boolean;
  data?: ArticleAnalysis;
  error?: string;
}

// Exact prompt template from Streamlit app
const PROMPT_TEMPLATE = `
You are a Pokémon VGC expert analyzing competitive teams. Your task is to extract and translate team information from Japanese articles and images.

**CRITICAL POKEMON IDENTIFICATION RULES:**
- **LOOK CAREFULLY AT THE IMAGE**: Identify Pokémon based on their visual appearance, moves, abilities, and stats shown
- **DO NOT GUESS**: If you cannot clearly identify a Pokémon, write "Pokémon not clearly visible in the image"
- **COMMON MISTAKES TO AVOID**:
  * Calyrex Ice Rider (white horse with crown, Ice-type moves, Glastrier) vs Calyrex Shadow Rider (black horse with crown, Ghost-type moves, Spectrier)
  * Iron Crown (robot-like, Steel/Psychic) vs Iron Jugulis (robot-like, Dark/Flying)
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

**FINAL ARTICLE SUMMARY:**
[Provide a comprehensive summary of the entire article including:
- Overall team strategy and concept
- Key Pokemon roles and synergies
- **TEAM STRENGTHS**: Extract and list specific strengths mentioned by the author
- **TEAM WEAKNESSES**: Extract and list specific weaknesses mentioned by the author
- **AUTHOR'S ASSESSMENT**: Only include strengths/weaknesses that the author explicitly mentioned
- Meta positioning and tournament viability
- Any unique strategies or innovations mentioned
- Author's recommendations and insights
- Team's competitive advantages and potential counters
- Lead combinations and selection strategies
- Specific matchups and counter strategies
- EV spread reasoning and benchmarks
- Item and ability choices explanation
- Move selection rationale
- Team building process and changes made

**IMPORTANT**: For strengths and weaknesses, ONLY include what the author specifically stated in the article. Do not add your own analysis or speculation.]

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
`;

const RESTRICTED_POKEMON = `
Restricted Pokémon in VGC Regulation I
Mewtwo – ミュウツー (Myuutsuu)
Lugia – ルギア (Rugia)
Ho-Oh – ホウオウ (Houou)
Kyogre – カイオーガ (Kaiōga)
Groudon – グラードン (Gurādon)
Rayquaza – レックウザ (Rekkūza)
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

class GeminiService {
  private genAI: GoogleGenerativeAI | null = null;
  private langchainGemini: ChatGoogleGenerativeAI | null = null;

  constructor() {
    this.initialize();
  }

  private initialize() {
    const apiKey = import.meta.env.VITE_GOOGLE_API_KEY;
    
    if (!apiKey) {
      console.warn('Google API key not found. Please set VITE_GOOGLE_API_KEY in your .env file.');
      return;
    }

    try {
      // Initialize both GoogleGenerativeAI and LangChain versions
      this.genAI = new GoogleGenerativeAI(apiKey);
      this.langchainGemini = new ChatGoogleGenerativeAI({
        model: "gemini-2.0-flash",
        apiKey: apiKey,
        temperature: 0.0,
        maxTokens: 4000
      });
      console.log('Gemini service initialized successfully with LangChain');
    } catch (error) {
      console.error('Failed to initialize Gemini service:', error);
    }
  }

  public isAvailable(): boolean {
    return this.langchainGemini !== null;
  }

  public async summarizeArticle(url: string, directText?: string): Promise<GeminiResponse> {
    if (!this.langchainGemini) {
      return {
        success: false,
        error: 'Gemini service not available. Please check your API key configuration.'
      };
    }

    try {
      console.log('Starting article summarization for URL:', url);
      
      let articleText: string;
      let imageUrls: string[] = [];
      
      if (directText) {
        // Use direct text input
        articleText = directText;
        console.log('Using direct text input, length:', articleText.length);
      } else {
        // Fetch article content and images
        const result = await this.fetchArticleContent(url);
        articleText = result.articleText;
        imageUrls = result.imageUrls;
        
        if (!articleText) {
          return {
            success: false,
            error: 'Could not extract text from the provided URL.'
          };
        }
      }

      console.log('Article text extracted, length:', articleText.length);
      console.log('Images found:', imageUrls.length);

      // Create prompt with article text
      const prompt = PROMPT_TEMPLATE
        .replace('{restrict_poke}', RESTRICTED_POKEMON)
        .replace('{text}', articleText);

      console.log('Sending request to Gemini API via LangChain...');
      
      // Use multimodal approach with images
      const contentParts = await this.wrapPromptAndImages(prompt, imageUrls);
      const message = new HumanMessage({ content: contentParts });
      
      console.log('Sending multimodal request with', contentParts.length, 'content parts');
      
      const response = await this.langchainGemini.invoke([message]);
      const text = response.content;
      
      console.log('Gemini response received, length:', text.length);
      
      // Parse the response
      const parsedResponse = this.parseResponse(text, url);
      
      return {
        success: true,
        data: parsedResponse
      };
      
    } catch (error) {
      console.error('Error in summarizeArticle:', error);
      
      if (this.isRetryableError(error)) {
        return {
          success: false,
          error: 'Service temporarily unavailable. Please try again in a few moments.'
        };
      }
      
      return {
        success: false,
        error: this.getErrorMessage(error)
      };
    }
  }

  private isRetryableError(error: any): boolean {
    return error.message?.includes('503') || 
           error.message?.includes('overloaded') ||
           error.message?.includes('429');
  }

  private getErrorMessage(error: any): string {
    if (error.message?.includes('429')) {
      return 'API rate limit exceeded. Please wait a moment and try again.';
    }
    
    if (error.message?.includes('403')) {
      return 'API access denied. Please check your API key configuration.';
    }
    
    if (error.message?.includes('All CORS proxies failed')) {
      return 'Unable to access this website. This is due to browser security restrictions (CORS). Try these solutions:\n\n1. Use a different Pokémon article URL\n2. Copy and paste the article text directly\n3. Try a website that allows cross-origin access\n4. Contact the site administrator to enable CORS';
    }
    
    if (error.message?.includes('CORS blocked')) {
      return 'Unable to access this website due to CORS restrictions. Please try a different URL or contact the site administrator.';
    }
    
    if (error.message?.includes('Failed to fetch')) {
      return 'Unable to fetch the article. This might be due to CORS restrictions or the website being unavailable. Please try a different URL.';
    }
    
    return `Failed to process article: ${error.message || 'Unknown error'}`;
  }

  private async fetchArticleContent(url: string): Promise<{ articleText: string; imageUrls: string[] }> {
    try {
      // Try multiple CORS proxy services for better reliability
      const proxyServices = [
        `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`,
        `https://corsproxy.io/?${encodeURIComponent(url)}`,
        `https://thingproxy.freeboard.io/fetch/${url}`,
        `https://cors-anywhere.herokuapp.com/${url}`
      ];

      let lastError: Error | null = null;

      for (const proxyUrl of proxyServices) {
        try {
          console.log('Trying CORS proxy:', proxyUrl);
          
          const response = await fetch(proxyUrl, {
            method: 'GET',
            headers: {
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'Accept-Language': 'en-US,en;q=0.5',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout: 10000 // 10 second timeout
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const html = await response.text();
          
          if (!html || html.length < 100) {
            throw new Error('Empty or too short response');
          }

          // Extract text content
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, 'text/html');
          
          // Remove script, style, nav, header, footer elements
          const elementsToRemove = doc.querySelectorAll('script, style, nav, header, footer, aside');
          elementsToRemove.forEach(el => el.remove());
          
          // Extract main content
          const mainContent = doc.querySelector('main, article, .content, .post-content, .entry-content, .article-content, .main-content, #content, #main, .post, .entry, .blog-post, .article') || doc.body;
          
          const articleText = mainContent?.textContent?.trim() || '';
          
          if (!articleText) {
            console.warn('No article text extracted, trying fallback extraction');
            // Fallback: try to get any text content
            const allText = doc.body?.textContent?.trim() || '';
            if (allText.length > 100) {
              return { articleText: allText, imageUrls: [] };
            }
          }
          
          // Extract images
          const images = doc.querySelectorAll('img');
          const imageUrls: string[] = [];
          
          images.forEach(img => {
            const src = img.getAttribute('src');
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
                  !fullUrl.toLowerCase().includes('ad')) {
                imageUrls.push(fullUrl);
              }
            }
          });
          
          console.log('Article text extracted, length:', articleText.length);
          console.log('Images found:', imageUrls.length);
          
          return { articleText, imageUrls };
          
        } catch (error) {
          console.warn(`Proxy failed:`, error);
          lastError = error as Error;
          continue; // Try next proxy
        }
      }

      // If all proxies failed, throw a helpful error
      throw new Error(`All CORS proxies failed. Last error: ${lastError?.message}. This website may be blocking proxy access. Please try a different URL or contact the site administrator.`);
      
    } catch (error) {
      console.error('Error fetching article content:', error);
      throw new Error(`Failed to fetch article: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async wrapPromptAndImages(prompt: string, imageUrls: string[]): Promise<any[]> {
    const content = [{ type: "text", text: prompt }];
    
    for (const url of imageUrls) {
      if (url.toLowerCase().includes('.png') || 
          url.toLowerCase().includes('.jpg') || 
          url.toLowerCase().includes('.jpeg') || 
          url.toLowerCase().includes('.webp')) {
        try {
          console.log('Converting image to base64:', url);
          const base64Data = await this.convertImageToBase64(url);
          content.push({
            type: "image_url",
            image_url: { url: base64Data }
          });
        } catch (error) {
          console.warn('Failed to convert image to base64:', url, error);
          // Skip this image if conversion fails
        }
      }
    }
    
    return content;
  }

  private async convertImageToBase64(imageUrl: string): Promise<string> {
    try {
      // Try to fetch the image through CORS proxies first
      const corsProxies = [
        `https://api.allorigins.win/raw?url=${encodeURIComponent(imageUrl)}`,
        `https://corsproxy.io/?${encodeURIComponent(imageUrl)}`,
        `https://thingproxy.freeboard.io/fetch/${encodeURIComponent(imageUrl)}`,
        `https://cors-anywhere.herokuapp.com/${imageUrl}`
      ];

      let response: Response | null = null;
      let lastError: Error | null = null;

      for (const proxyUrl of corsProxies) {
        try {
          response = await fetch(proxyUrl, {
            headers: {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
              'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
              'Accept-Language': 'en-US,en;q=0.9'
            }
          });

          if (response.ok) {
            break;
          }
        } catch (error) {
          lastError = error as Error;
          console.warn(`CORS proxy failed: ${proxyUrl}`, error);
          continue;
        }
      }

      if (!response || !response.ok) {
        throw lastError || new Error('All CORS proxies failed for image');
      }

      const arrayBuffer = await response.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      
      // Convert to base64
      let binary = '';
      for (let i = 0; i < uint8Array.length; i++) {
        binary += String.fromCharCode(uint8Array[i]);
      }
      
      const base64 = btoa(binary);
      
      // Determine MIME type from URL
      let mimeType = 'image/jpeg'; // default
      if (imageUrl.toLowerCase().includes('.png')) {
        mimeType = 'image/png';
      } else if (imageUrl.toLowerCase().includes('.webp')) {
        mimeType = 'image/webp';
      }
      
      return `data:${mimeType};base64,${base64}`;
    } catch (error) {
      console.error('Error converting image to base64:', error);
      throw error;
    }
  }

  private parseResponse(summaryText: string, sourceUrl: string): ArticleAnalysis {
    // Extract title
    const titleMatch = summaryText.match(/TITLE:\s*(.+?)(?:\n|$)/);
    const title = titleMatch ? titleMatch[1].trim() : 'Not specified';

    // Parse team members
    const team = this.parseDetailedTeamMembers(summaryText);
    
    // Extract strengths and weaknesses
    const strengths = this.extractStrengths(summaryText);
    const weaknesses = this.extractWeaknesses(summaryText);

    return {
      title,
      summary: summaryText,
      team,
      pokemonNames: team.map(p => p.name),
      strengths,
      weaknesses,
      meta: {
        processingTime: 2.3,
        source: sourceUrl,
        language: 'en'
      }
    };
  }

  private extractPokemonNames(summary: string): string[] {
    const pokemonMatches = summary.match(/\*\*Pokémon \d+:\s*\[([^\]]+)\]/g);
    return pokemonMatches ? pokemonMatches.map(match => {
      const nameMatch = match.match(/\[([^\]]+)\]/);
      return nameMatch ? nameMatch[1].trim() : '';
    }).filter(name => name) : [];
  }

  private parseTeamMembers(summary: string): PokemonTeamMember[] {
    const pokemonSections = summary.split(/\*\*Pokémon \d+:/);
    return pokemonSections.slice(1).map(section => {
      const lines = section.split('\n');
      const nameMatch = lines[0].match(/\[([^\]]+)\]/);
      const pokemonName = nameMatch ? nameMatch[1].trim() : 'Unknown Pokemon';
      
      return {
        pokemon: pokemonName,
        level: 50,
        hp: { current: 100, max: 150 },
        status: 'Healthy',
        teraType: 'Not specified',
        types: [],
        item: 'Not specified',
        ability: 'Not specified',
        nature: 'Not specified',
        moves: [],
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
        strategy: 'Not specified',
        evSpread: 'Not specified'
      };
    });
  }

  private parseDetailedTeamMembers(summary: string): PokemonTeamMember[] {
    console.log('DEBUG: Starting parseDetailedTeamMembers');
    console.log('DEBUG: Summary starts with:', summary.substring(0, 500));
    
    const teams: PokemonTeamMember[] = [];

    // Try different ways to split Pokémon sections
    let pokemonSections: string[] = [];
    
    // Method 1: Look for numbered Pokémon entries (most common format)
    const pokemonNumbered = summary.match(/\*\*Pokémon\s*\d+[:\s]+(.*?)(?=\*\*Pokémon\s*\d+|\*\*CONCLUSION|\*\*FINAL|$)/gs);
    if (pokemonNumbered) {
      pokemonSections = pokemonNumbered;
      console.log(`DEBUG: Found ${pokemonSections.length} Pokémon using numbered method`);
    }
    
    // Method 2: Look for Pokémon with dashes
    if (!pokemonSections.length) {
      const pokemonDashed = summary.split(/\n\s*-\s*/);
      pokemonSections = pokemonDashed.filter(section => 
        /ability:|item:|moves:|ev spread:|nature:|tera:/i.test(section)
      );
      console.log(`DEBUG: Found ${pokemonSections.length} Pokémon using dash method`);
    }
    
    // Method 3: Look for specific patterns
    if (!pokemonSections.length) {
      const splitPatterns = ['**Pokémon', '**Pokemon', 'Pokémon', 'Pokemon', 'Team Member', 'Member'];
      
      for (const pattern of splitPatterns) {
        if (summary.includes(pattern)) {
          pokemonSections = summary.split(pattern).slice(1);
          console.log(`DEBUG: Found ${pokemonSections.length} Pokémon using pattern: ${pattern}`);
          break;
        }
      }
    }
    
    // Method 4: Look for any section with Pokémon data
    if (!pokemonSections.length) {
      const sections = summary.split('\n\n');
      pokemonSections = sections.filter(section => 
        /ability:|item:|moves:|ev spread:|nature:|tera:/i.test(section) && section.trim().length > 50
      );
      console.log(`DEBUG: Found ${pokemonSections.length} Pokémon using section method`);
    }
    
    // Method 5: Last resort - look for any numbered entries
    if (!pokemonSections.length) {
      const pokemonMatches = summary.match(/\d+[\.:]\s*([^\n]+)/g);
      if (pokemonMatches) {
        pokemonSections = pokemonMatches.map(match => `1: ${match.replace(/^\d+[\.:]\s*/, '')}`);
        console.log(`DEBUG: Found ${pokemonMatches.length} Pokémon using numbered matches`);
      }
    }
    
    console.log(`DEBUG: Total Pokémon sections found: ${pokemonSections.length}`);
    if (pokemonSections.length) {
      console.log(`DEBUG: First Pokémon section: ${pokemonSections[0].substring(0, 200)}...`);
    }

    for (let i = 0; i < pokemonSections.length && i < 6; i++) {
      const section = pokemonSections[i];
      console.log(`DEBUG: Processing Pokémon ${i+1}`);
      console.log(`DEBUG: Section preview: ${section.substring(0, 200)}...`);
      
      // Extract Pokemon name with multiple patterns
      let pokemonName = 'Unknown Pokemon';
      
      // Look for Pokémon name patterns
      const namePatterns = [
        /^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/,  // Capitalized words at start
        /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s*:)/,  // Before colon
        /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s*-)/,  // Before dash
        /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\n)/,    // Before newline
        /\[([^\]]+)\]/  // In brackets
      ];
      
      for (const pattern of namePatterns) {
        const nameMatch = section.match(pattern);
        if (nameMatch) {
          pokemonName = nameMatch[1] || nameMatch[0];
          break;
        }
      }
      
      // Method 2: Look for common Pokémon names in the section
      if (pokemonName === 'Unknown Pokemon') {
        const commonPokemon = [
          'Calyrex Shadow Rider', 'Calyrex Ice Rider', 'Zamazenta', 'Zacian',
          'Chien-Pao', 'Chi-Yu', 'Amoonguss', 'Dragonite', 'Iron Valiant',
          'Miraidon', 'Koraidon', 'Urshifu', 'Rillaboom', 'Volcarona', 'Iron Jugulis', 'Iron Crown'
        ];
        for (const pokemon of commonPokemon) {
          if (section.toLowerCase().includes(pokemon.toLowerCase())) {
            pokemonName = pokemon;
            break;
          }
        }
      }
      
      if (pokemonName === 'Unknown Pokemon') {
        console.log(`DEBUG: No name found for Pokémon ${i+1}`);
        continue;
      }
      
      console.log(`DEBUG: Found name: ${pokemonName}`);

      // Extract all data using comprehensive regex patterns
      const sectionLower = section.toLowerCase();
      
      // Extract Ability with multiple patterns
      const abilityPatterns = [
        /ability[:\s]+([^:\n]+)/i,
        /abilities?[:\s]+([^:\n]+)/i,
        /- ability[:\s]+([^:\n]+)/i,
        /• ability[:\s]+([^:\n]+)/i
      ];
      let ability = 'Not specified';
      for (const pattern of abilityPatterns) {
        const match = section.match(pattern);
        if (match) {
          ability = match[1].trim();
          console.log(`DEBUG: Found ability: ${ability}`);
          break;
        }
      }
      
      // Extract Item with multiple patterns
      const itemPatterns = [
        /item[:\s]+([^:\n]+)/i,
        /held item[:\s]+([^:\n]+)/i,
        /- item[:\s]+([^:\n]+)/i,
        /• item[:\s]+([^:\n]+)/i
      ];
      let item = 'Not specified';
      for (const pattern of itemPatterns) {
        const match = section.match(pattern);
        if (match) {
          item = match[1].trim();
          console.log(`DEBUG: Found item: ${item}`);
          break;
        }
      }
      
      // Extract Nature with multiple patterns
      const naturePatterns = [
        /nature[:\s]+([^:\n]+)/i,
        /natures?[:\s]+([^:\n]+)/i,
        /- nature[:\s]+([^:\n]+)/i,
        /• nature[:\s]+([^:\n]+)/i,
        /nature[:\s]*([a-z]+)/i,  // Just the nature name
        /([a-z]+)\s+nature/i  // Nature name before "nature"
      ];
      let nature = 'Not specified';
      for (const pattern of naturePatterns) {
        const match = section.match(pattern);
        if (match) {
          const natureText = match[1].trim();
          // Clean up common nature names
          const natureMapping: { [key: string]: string } = {
            'Adamant': 'Adamant', 'Jolly': 'Jolly', 'Modest': 'Modest', 'Timid': 'Timid',
            'Bold': 'Bold', 'Impish': 'Impish', 'Calm': 'Calm', 'Careful': 'Careful',
            'Naive': 'Naive', 'Hasty': 'Hasty', 'Naughty': 'Naughty', 'Lonely': 'Lonely',
            'Mild': 'Mild', 'Quiet': 'Quiet', 'Rash': 'Rash', 'Brave': 'Brave',
            'Relaxed': 'Relaxed', 'Sassy': 'Sassy', 'Gentle': 'Gentle', 'Lax': 'Lax'
          };
          nature = natureMapping[natureText] || natureText;
          console.log(`DEBUG: Found nature: ${nature}`);
          break;
        }
      }
      
      // Extract Tera Type with multiple patterns
      const teraPatterns = [
        /tera[:\s]+([^:\n]+)/i,
        /tera type[:\s]+([^:\n]+)/i,
        /- tera[:\s]+([^:\n]+)/i,
        /• tera[:\s]+([^:\n]+)/i
      ];
      let teraType = 'Not specified';
      for (const pattern of teraPatterns) {
        const match = section.match(pattern);
        if (match) {
          teraType = match[1].trim();
          console.log(`DEBUG: Found tera: ${teraType}`);
          break;
        }
      }
      
      // Extract Moves with enhanced filtering
      const movesPatterns = [
        /moves?[:\s]+([^:\n]+)/i,
        /moveset[:\s]+([^:\n]+)/i,
        /- moves?[:\s]+([^:\n]+)/i,
        /• moves?[:\s]+([^:\n]+)/i
      ];
      let moves: string[] = [];
      for (const pattern of movesPatterns) {
        const match = section.match(pattern);
        if (match) {
          const movesText = match[1].trim();
          // Handle different separators
          if (movesText.includes('/')) {
            moves = movesText.split('/').map(move => move.trim());
          } else if (movesText.includes(',')) {
            moves = movesText.split(',').map(move => move.trim());
          } else {
            moves = [movesText];
          }
          
          // Filter out abilities that might be incorrectly included in moves
          const abilityKeywords = ['as one', 'unseen fist', 'grassy surge', 'regenerator', 'quark drive', 'drizzle', 'sword of ruin', 'beads of ruin'];
          moves = moves.filter(move => 
            move && !abilityKeywords.some(keyword => move.toLowerCase().includes(keyword))
          );
          
          if (moves.length) {
            console.log(`DEBUG: Found moves: ${moves}`);
          } else {
            console.log(`DEBUG: No valid moves found after filtering`);
          }
          break;
        }
      }
      
      // Extract EV Spread with enhanced patterns
      const evPatterns = [
        /ev spread[:\s]+([^:\n]+)/i,
        /evs?[:\s]+([^:\n]+)/i,
        /effort values?[:\s]+([^:\n]+)/i,
        /- ev spread[:\s]+([^:\n]+)/i,
        /• ev spread[:\s]+([^:\n]+)/i,
        /ev spread[:\s]*(\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+)/i  // Direct number format
      ];
      let evSpread = 'Not specified';
      for (const pattern of evPatterns) {
        const match = section.match(pattern);
        if (match) {
          evSpread = match[1].trim();
          console.log(`DEBUG: Raw EV text extracted: '${evSpread}'`);
          break;
        }
      }
      
      const evs = this.parseEVSpread(evSpread);
      
      // Extract EV Explanation
      const evExplanationPatterns = [
        /ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)/i,
        /ev reasoning[:\s]+([^:\n]+(?:\n[^:\n]+)*)/i,
        /- ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)/i,
        /• ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)/i
      ];
      let evExplanation = 'Not specified';
      for (const pattern of evExplanationPatterns) {
        const match = section.match(pattern);
        if (match) {
          evExplanation = match[1].trim();
          console.log(`DEBUG: Found EV explanation: ${evExplanation.substring(0, 100)}...`);
          break;
        }
      }

      const team: PokemonTeamMember = {
        name: pokemonName,
        ability: ability,
        item: item,
        teraType: teraType,
        nature: nature,
        moves: moves,
        evs: evs,
        evExplanation: evExplanation
      };

      teams.push(team);
      console.log(`DEBUG: Added Pokémon ${i+1}: ${JSON.stringify(team, null, 2)}`);
    }

    return teams;
  }

  private extractStrengths(summary: string): string[] {
    console.log('DEBUG: Extracting strengths from summary');
    
    const strengthPatterns = [
      /strengths?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweaknesses?|$)/i,
      /team strengths?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweaknesses?|$)/i,
      /advantages?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\ndisadvantages?|$)/i,
      /positive[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nnegative|$)/i,
      /strong[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweak|$)/i,
      /TEAM STRENGTHS[:\s]*([\s\S]*?)(?=TEAM WEAKNESSES|CONCLUSION|$)/i,
      /Strengths[:\s]*([\s\S]*?)(?=Weaknesses|Conclusion|$)/i,
      /Team strengths[:\s]*([\s\S]*?)(?=Team weaknesses|Conclusion|$)/i
    ];

    for (const pattern of strengthPatterns) {
      const match = summary.match(pattern);
      if (match) {
        console.log('DEBUG: Found strengths with pattern:', pattern);
        return this.cleanTextAndSplit(match[1]);
      }
    }

    // Fallback to conclusion section
    const conclusionMatch = summary.match(/conclusion[:\s]+(.*?)(?=\n\n|\Z)/i);
    if (conclusionMatch) {
      console.log('DEBUG: Extracting strengths from conclusion');
      const conclusion = conclusionMatch[1].toLowerCase();
      
      // Extract positive statements
      const positiveKeywords = ['strong', 'advantage', 'effective', 'powerful', 'successful', 'good', 'excellent', 'outstanding'];
      const positiveSentences: string[] = [];
      const sentences = conclusion.split(/[.!?]+/);
      
      for (const sentence of sentences) {
        if (positiveKeywords.some(keyword => sentence.includes(keyword))) {
          positiveSentences.push(sentence.trim());
        }
      }
      
      if (positiveSentences.length) {
        return positiveSentences.slice(0, 3); // Limit to 3 sentences
      }
    }

    return [];
  }

  private extractWeaknesses(summary: string): string[] {
    console.log('DEBUG: Extracting weaknesses from summary');
    
    const weaknessPatterns = [
      /weaknesses?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrengths?|$)/i,
      /team weaknesses?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrengths?|$)/i,
      /disadvantages?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nadvantages?|$)/i,
      /negative[:\s]+(.*?)(?=\n\n|\n[A-Z]|\npositive|$)/i,
      /weak[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrong|$)/i,
      /TEAM WEAKNESSES[:\s]*([\s\S]*?)(?=TEAM STRENGTHS|CONCLUSION|$)/i,
      /Weaknesses[:\s]*([\s\S]*?)(?=Strengths|Conclusion|$)/i,
      /Team weaknesses[:\s]*([\s\S]*?)(?=Team strengths|Conclusion|$)/i
    ];

    for (const pattern of weaknessPatterns) {
      const match = summary.match(pattern);
      if (match) {
        console.log('DEBUG: Found weaknesses with pattern:', pattern);
        return this.cleanTextAndSplit(match[1]);
      }
    }

    // Fallback to conclusion section
    const conclusionMatch = summary.match(/conclusion[:\s]+(.*?)(?=\n\n|\Z)/i);
    if (conclusionMatch) {
      console.log('DEBUG: Extracting weaknesses from conclusion');
      const conclusion = conclusionMatch[1].toLowerCase();
      
      // Extract negative statements
      const negativeKeywords = ['weak', 'disadvantage', 'problem', 'issue', 'difficult', 'challenge', 'vulnerable'];
      const negativeSentences: string[] = [];
      const sentences = conclusion.split(/[.!?]+/);
      
      for (const sentence of sentences) {
        if (negativeKeywords.some(keyword => sentence.includes(keyword))) {
          negativeSentences.push(sentence.trim());
        }
      }
      
      if (negativeSentences.length) {
        return negativeSentences.slice(0, 3); // Limit to 3 sentences
      }
    }

    return [];
  }

  private cleanTextAndSplit(text: string): string[] {
    console.log('DEBUG: Cleaning and splitting text:', text.substring(0, 100) + '...');
    
    if (!text) {
      return [];
    }
    
    // Clean the text using Streamlit app's approach
    let cleaned = text
      // Remove markdown formatting
      .replace(/\*\*(.*?)\*\*/g, '$1')  // Remove bold
      .replace(/\*(.*?)\*/g, '$1')      // Remove italic
      .replace(/`(.*?)`/g, '$1')        // Remove code
      // Clean up bullet points and formatting
      .replace(/^\s*[-*•]\s*/gm, '')  // Remove bullet points
      .replace(/^\s*\d+\.\s*/gm, '')  // Remove numbered lists
      // Clean up extra whitespace and newlines
      .replace(/\n+/g, ' ') // Replace multiple newlines with space
      .replace(/\s+/g, ' ') // Replace multiple spaces with single space
      .trim();
    
    // Capitalize first letter
    if (cleaned) {
      cleaned = cleaned[0].toUpperCase() + cleaned.slice(1);
    }
    
    console.log('DEBUG: Cleaned text:', cleaned.substring(0, 100) + '...');

    // Split by common separators
    const separators = [';', ' and ', ' but ', '. '];
    for (const separator of separators) {
      if (cleaned.includes(separator)) {
        const split = cleaned.split(separator)
          .map(item => item.trim())
          .filter(item => item.length > 10) // Filter out very short items
          .slice(0, 5); // Limit to 5 items
        
        console.log('DEBUG: Split by separator:', separator, 'Result:', split);
        return split;
      }
    }

    // If no separators found, return as single item
    const result = cleaned.length > 10 ? [cleaned] : [];
    console.log('DEBUG: No separators found, returning single item:', result);
    return result;
  }

  private parseEVSpread(evSpread: string): Record<string, number> | undefined {
    if (!evSpread || evSpread === 'Not specified' || evSpread.includes('not specified')) {
      return undefined;
    }

    console.log(`DEBUG: Parsing EV spread: '${evSpread}'`);

    // Enhanced EV parsing patterns from Streamlit app
    const evParsePatterns = [
      // Japanese format: H244 A252 B4 C4 D4 S4
      /H(\d+)\s+A(\d+)\s+B(\d+)\s+C(\d+)\s+D(\d+)\s+S(\d+)/,
      // Japanese format: H244 A252 B4 D4 S4 (missing C/SpA)
      /H(\d+)\s+A(\d+)\s+B(\d+)\s+D(\d+)\s+S(\d+)/,
      // Japanese format: H188 D196 S124
      /H(\d+)\s+D(\d+)\s+S(\d+)/,
      // Standard format: 244 252 4 4 4 4 (space separated)
      /^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$/,
      // Slash format: 244/252/4/4/4/4
      /(\d+)\s*\/\s*(\d+)\s*\/\s*(\d+)\s*\/\s*(\d+)\s*\/\s*(\d+)\s*\/\s*(\d+)/,
      // Mixed format: 244 252 4 4 4 4
      /(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/,
      // Labeled format: HP:244 Atk:252 Def:4 SpA:4 SpD:4 Spe:4
      /HP:\s*(\d+).*?Atk:\s*(\d+).*?Def:\s*(\d+).*?SpA:\s*(\d+).*?SpD:\s*(\d+).*?Spe:\s*(\d+)/,
      // Mixed format: HP252 Atk252 Def4 SpA4 SpD4 Spe4
      /HP(\d+)\s+Atk(\d+)\s+Def(\d+)\s+SpA(\d+)\s+SpD(\d+)\s+Spe(\d+)/,
      // EV Spread format: 252 252 4 0 0 0
      /EV Spread:\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/
    ];

    for (let i = 0; i < evParsePatterns.length; i++) {
      const pattern = evParsePatterns[i];
      const match = evSpread.match(pattern);
      if (match) {
        console.log(`DEBUG: EV pattern ${i} matched: ${pattern}`);
        console.log(`DEBUG: EV match groups:`, match.groups || match.slice(1));
        
        const values = match.slice(1).map(v => parseInt(v) || 0);
        
        // Handle Japanese format (H=HP, A=Attack, B=Defense, C=SpA, D=SpD, S=Speed)
        if (pattern.source.includes('H(\\d+)')) {
          // Japanese format
          if (values.length === 6) {
            // Full format: H244 A252 B4 C4 D4 S4
            const evs = {
              hp: values[0],
              attack: values[1],
              defense: values[2],
              spAtk: values[3],
              spDef: values[4],
              speed: values[5]
            };
            console.log(`DEBUG: Japanese 6-value format - HP:${evs.hp}, Atk:${evs.attack}, Def:${evs.defense}, SpA:${evs.spAtk}, SpD:${evs.spDef}, Spe:${evs.speed}`);
            return evs;
          } else if (values.length === 5) {
            // Missing C (SpA): H244 A252 B4 D4 S4
            const evs = {
              hp: values[0],
              attack: values[1],
              defense: values[2],
              spAtk: 0,  // Missing C
              spDef: values[3],
              speed: values[4]
            };
            console.log(`DEBUG: Japanese 5-value format - HP:${evs.hp}, Atk:${evs.attack}, Def:${evs.defense}, SpA:${evs.spAtk}, SpD:${evs.spDef}, Spe:${evs.speed}`);
            return evs;
          } else if (values.length === 3) {
            // Partial format: H188 D196 S124
            const evs = {
              hp: values[0],
              attack: 0,
              defense: 0,
              spAtk: 0,
              spDef: values[1],
              speed: values[2]
            };
            console.log(`DEBUG: Japanese 3-value format - HP:${evs.hp}, Atk:${evs.attack}, Def:${evs.defense}, SpA:${evs.spAtk}, SpD:${evs.spDef}, Spe:${evs.speed}`);
            return evs;
          }
        } else {
          // Standard format
          if (values.length === 6) {
            const evs = {
              hp: values[0],
              attack: values[1],
              defense: values[2],
              spAtk: values[3],
              spDef: values[4],
              speed: values[5]
            };
            console.log(`DEBUG: Standard 6-value format - HP:${evs.hp}, Atk:${evs.attack}, Def:${evs.defense}, SpA:${evs.spAtk}, SpD:${evs.spDef}, Spe:${evs.speed}`);
            return evs;
          }
        }
      }
    }

    console.log(`DEBUG: No EV pattern matched for: '${evSpread}'`);
    return undefined;
  }
}

export default new GeminiService();

// Also export as named export for compatibility
export const geminiService = new GeminiService(); 