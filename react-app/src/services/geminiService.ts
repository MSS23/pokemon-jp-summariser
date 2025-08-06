/**
 * Google Gemini integration service for Pokemon VGC article summarization
 * Direct integration without FastAPI middleman
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

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

// Enhanced prompt template (updated from Streamlit app)
const PROMPT_TEMPLATE = `
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

**Restricted Pokémon Reference List:**
{restrict_poke}

**Input Content:**
#{text}#
   - If the title is already in English, write: TITLE: [English Title]
   - If there is no title or it's unclear, write: TITLE: Not specified

2. **Translate** all non-English text into English, using official Pokémon names, moves, abilities, and items.

3. **Analyse** the team strictly based on the provided content:
   - List exactly **six Pokémon**.
   - If any Pokémon is missing or cannot be identified, write: **"Pokémon not identifiable in the article."**
   - Only include reasoning, synergy, or strategy if explicitly described.
   - Avoid all speculation or inference.

4. **Individual Pokémon Breakdown** (for each of the six slots):
   Format each Pokémon exactly as follows:
   
   **Pokémon 1: [English Name]**
- Ability: [English Ability Name]
- Held Item: [English Item Name]
- Tera Type: [English Tera Type Name]
- Moves: [Move 1] / [Move 2] / [Move 3] / [Move 4]
- EV Spread: [HP EVs] [Atk EVs] [Def EVs] [SpA EVs] [SpD EVs] [Spe EVs]
- Nature: [English Nature Name]
- EV Explanation: [Provide detailed breakdown including:
  • Specific EV investment reasoning and key calculations
  • Survival benchmarks with exact percentages (e.g., "252 HP EVs to survive 2 hits from X")
  • Speed control details and speed tier targets
  • Damage calculations against common threats
  • Team synergy considerations and role in the team
  • Item and nature interactions and their strategic purpose
  • Any specific strategies or tech mentioned by the author
  If no detailed explanation is provided, write "Not specified in the article"]
   
   Repeat this format for all 6 Pokémon.

5. **Conclusion Summary**:
   - Team strengths
   - Notable weaknesses or counters
   - Meta relevance and effectiveness (if discussed)

---

**Strict Instructions:**
- Do **not** infer or assume anything that is not clearly visible or mentioned.
- All missing data must be marked with: **"Not specified in the article."**
- Use only **standard ASCII characters**.
- Write in clear, formal **English** only.
- **ALWAYS use official English Pokémon names, moves, abilities, and items.**
- **Format consistently**: Use the exact format specified for each Pokémon breakdown.

**Input Content:**
#{text}#

**Note:** Supplementary team images will follow. Use them where available to support the analysis.
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
`;

class GeminiService {
  private genAI: GoogleGenerativeAI | null = null;
  private model: any = null;

  constructor() {
    this.initialize();
  }

  private initialize() {
    const apiKey = import.meta.env.VITE_GOOGLE_API_KEY;
    if (!apiKey) {
      console.warn('Google API key not found. Set VITE_GOOGLE_API_KEY in your .env file');
      return;
    }

    try {
      this.genAI = new GoogleGenerativeAI(apiKey);
      this.model = this.genAI.getGenerativeModel({ 
        model: "gemini-2.0-flash",
        generationConfig: {
          temperature: 0.0,
          maxOutputTokens: 6000,
        }
      });
    } catch (error) {
      console.error('Failed to initialize Gemini:', error);
    }
  }

  public isAvailable(): boolean {
    return this.genAI !== null && this.model !== null;
  }

  public async summarizeArticle(url: string): Promise<GeminiResponse> {
    const startTime = Date.now();
    const maxRetries = 3;
    let lastError: any = null;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`Starting Gemini summarization for: ${url} (attempt ${attempt}/${maxRetries})`);
        
        if (!this.isAvailable()) {
          return {
            success: false,
            error: 'Gemini service not available. Please check your API key.'
          };
        }

        // Fetch article content
        const { articleText, imageUrls } = await this.fetchArticleContent(url);

        // Create prompt
        const prompt = PROMPT_TEMPLATE
          .replace('{restrict_poke}', RESTRICTED_POKEMON)
          .replace('#{text}#', articleText);

        // Prepare content with images
        const contentParts = await this.wrapPromptAndImages(prompt, imageUrls);

        // Generate response
        console.log('Calling Gemini API...');
        const result = await this.model.generateContent(contentParts);
        const response = await result.response;
        const summaryText = response.text();

        console.log('Gemini response received, parsing...');
        // Parse the response
        const analysis = this.parseResponse(summaryText, url);
        const processingTime = Date.now() - startTime;

        return {
          success: true,
          data: {
            ...analysis,
            meta: {
              processingTime: processingTime / 1000,
              source: 'gemini',
              language: 'en'
            }
          }
        };

      } catch (error: any) {
        lastError = error;
        console.error(`Gemini summarization failed (attempt ${attempt}/${maxRetries}):`, error instanceof Error ? error.message : 'Unknown error');
        
        // Check if it's a retryable error
        const isRetryable = this.isRetryableError(error);
        
        if (attempt < maxRetries && isRetryable) {
          const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000); // Exponential backoff, max 5s
          console.log(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        } else if (!isRetryable) {
          // Non-retryable error, break immediately
          break;
        }
      }
    }

    // All retries failed
    const errorMessage = this.getErrorMessage(lastError);
    console.error('All retry attempts failed:', errorMessage);
    return {
      success: false,
      error: errorMessage
    };
  }

  private isRetryableError(error: any): boolean {
    // Check for specific error types that are retryable
    if (error.message?.includes('503') || error.message?.includes('overloaded')) {
      return true;
    }
    if (error.message?.includes('429') || error.message?.includes('rate limit')) {
      return true;
    }
    if (error.message?.includes('500') || error.message?.includes('502')) {
      return true;
    }
    if (error.message?.includes('network') || error.message?.includes('timeout')) {
      return true;
    }
    return false;
  }

  private getErrorMessage(error: any): string {
    if (error.message?.includes('503') || error.message?.includes('overloaded')) {
      return 'Gemini service is temporarily overloaded. Please wait a moment and try again.';
    }
    if (error.message?.includes('429') || error.message?.includes('rate limit')) {
      return 'Rate limit exceeded. Please wait a moment before trying again.';
    }
    if (error.message?.includes('API key')) {
      return 'Invalid API key. Please check your Google API key configuration.';
    }
    if (error.message?.includes('network') || error.message?.includes('timeout')) {
      return 'Network error. Please check your internet connection and try again.';
    }
    return error.message || 'An unexpected error occurred. Please try again.';
  }

  private async fetchArticleContent(url: string): Promise<{ articleText: string; imageUrls: string[] }> {
    try {
      // Try multiple CORS proxies in case one fails
      const proxies = [
        `https://corsproxy.io/?${encodeURIComponent(url)}`,
        `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`,
        `https://cors.bridged.cc/${url}`,
        `https://thingproxy.freeboard.io/fetch/${url}`
      ];

      let htmlContent = '';
      let lastError = null;

      for (const proxyUrl of proxies) {
        try {
          console.log(`Trying proxy: ${proxyUrl}`);
          
          // Create AbortController for timeout
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout for images
          
          const response = await fetch(proxyUrl, {
            method: 'GET',
            headers: {
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'Accept-Language': 'en-US,en;q=0.5',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          if (!response.ok) {
            throw new Error(`Proxy failed with status: ${response.status}`);
          }

          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            // Handle JSON response (like allorigins.win)
            const data = await response.json();
            htmlContent = data.contents || data;
          } else {
            // Handle direct HTML response
            htmlContent = await response.text();
          }

          console.log(`Successfully fetched content using: ${proxyUrl}`);
          break; // Success, exit the loop
        } catch (error: any) {
          if (error?.name === 'AbortError') {
            console.warn(`Proxy timeout: ${proxyUrl}`);
            lastError = new Error('Request timeout');
          } else {
            console.warn(`Proxy failed: ${proxyUrl}`, error);
            lastError = error;
          }
          continue; // Try next proxy
        }
      }

      if (!htmlContent) {
        // Fallback: Try to use the Streamlit backend for article fetching
        console.log('CORS proxies failed, trying Streamlit backend fallback...');
        try {
          const streamlitResponse = await fetch('http://localhost:8501/api/fetch-article', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
          });
          
          if (streamlitResponse.ok) {
            const streamlitData = await streamlitResponse.json();
            htmlContent = streamlitData.content || '';
            console.log('Successfully fetched content using Streamlit backend');
          } else {
            throw new Error(`Streamlit backend failed: ${streamlitResponse.statusText}`);
          }
        } catch (streamlitError) {
          console.warn('Streamlit backend fallback also failed:', streamlitError);
          const errorMessage = lastError instanceof Error ? lastError.message : 'Unknown error';
          throw new Error(`All methods failed. Please try:\n1. Check if the URL is accessible\n2. Try a different article URL\n3. Contact support if the issue persists\n\nLast CORS error: ${errorMessage}`);
        }
      }

      // Parse HTML content
      const parser = new DOMParser();
      const doc = parser.parseFromString(htmlContent, 'text/html');

      // Remove unwanted elements
      const unwantedSelectors = ['script', 'style', 'nav', 'header', 'footer', 'aside'];
      unwantedSelectors.forEach(selector => {
        doc.querySelectorAll(selector).forEach(el => el.remove());
      });

      // Extract main content
      const contentSelectors = [
        'main', 'article', '.content', '.post-content', '.entry-content',
        '.article-content', '.main-content', '#content', '#main',
        '.post', '.entry', '.blog-post', '.article'
      ];

      let mainContent = null;
      for (const selector of contentSelectors) {
        mainContent = doc.querySelector(selector);
        if (mainContent) break;
      }

      if (!mainContent) {
        mainContent = doc.body || doc;
      }

      // Extract text content
      const paragraphs = Array.from(mainContent.querySelectorAll('p'))
        .map(p => p.textContent?.trim())
        .filter(text => text && text.length > 0);

      const headings = Array.from(mainContent.querySelectorAll('h1, h2, h3, h4, h5, h6'))
        .map(h => h.textContent?.trim())
        .filter(text => text && text.length > 0);

      // Combine content
      let articleText = '';
      if (headings.length > 0) {
        articleText += 'HEADINGS:\n' + headings.join('\n') + '\n\n';
      }
      if (paragraphs.length > 0) {
        articleText += 'CONTENT:\n' + paragraphs.join('\n');
      }

      // Extract images - more comprehensive approach
      const imageUrls = Array.from(mainContent.querySelectorAll('img'))
        .map(img => {
          let src = img.getAttribute('src') || img.getAttribute('data-src');
          if (!src) return null;

          // Handle relative URLs
          if (src.startsWith('//')) {
            src = 'https:' + src;
          } else if (src.startsWith('/')) {
            const baseUrl = new URL(url).origin;
            src = baseUrl + src;
          } else if (!src.startsWith('http')) {
            src = new URL(src, url).href;
          }

          return src;
        })
        .filter((src): src is string => 
          src !== null && 
          !src.toLowerCase().includes('logo') &&
          !src.toLowerCase().includes('icon') &&
          !src.toLowerCase().includes('avatar') &&
          !src.toLowerCase().includes('banner') &&
          !src.toLowerCase().includes('ad') &&
          (src.toLowerCase().includes('.jpg') || 
           src.toLowerCase().includes('.jpeg') || 
           src.toLowerCase().includes('.png') || 
           src.toLowerCase().includes('.webp') ||
           src.toLowerCase().includes('.gif'))
        );

      console.log(`Extracted ${imageUrls.length} images from article`);
      imageUrls.forEach((url, index) => {
        console.log(`Image ${index + 1}: ${url}`);
      });

      return { articleText, imageUrls };

    } catch (error) {
      throw new Error(`Failed to fetch article content: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async wrapPromptAndImages(prompt: string, imageUrls: string[]): Promise<any[]> {
    const content: any[] = [{ text: prompt }];
    
    // Add images (limit to first 8 for better EV detection)
    const imagePromises = imageUrls.slice(0, 8).map(async (url) => {
      if (url.match(/\.(png|jpg|jpeg|webp)$/i)) {
        try {
          // Fetch image and convert to base64
          const response = await fetch(url);
          if (!response.ok) {
            console.warn(`Failed to fetch image: ${url}`);
            return null;
          }
          
          const arrayBuffer = await response.arrayBuffer();
          const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
          
          return {
            inlineData: {
              mimeType: this.getMimeType(url),
              data: base64
            }
          };
        } catch (error) {
          console.warn(`Error processing image ${url}:`, error);
          return null;
        }
      }
      return null;
    });

    const imageData = await Promise.all(imagePromises);
    const validImages = imageData.filter(img => img !== null);
    
    console.log(`Successfully processed ${validImages.length} images for analysis`);
    content.push(...validImages);

    return content;
  }

  private getMimeType(url: string): string {
    const extension = url.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'png': return 'image/png';
      case 'jpg':
      case 'jpeg': return 'image/jpeg';
      case 'webp': return 'image/webp';
      default: return 'image/jpeg';
    }
  }

  private parseResponse(summaryText: string, sourceUrl: string): Omit<ArticleAnalysis, 'meta'> {
    // Extract title
    const titleMatch = summaryText.match(/TITLE:\s*(.+)/i);
    const title = titleMatch ? titleMatch[1].trim() : `Article from ${new URL(sourceUrl).hostname}`;

    // Extract Pokemon names
    const pokemonNames = this.extractPokemonNames(summaryText);

    // Parse team members with detailed information
    const team = this.parseDetailedTeamMembers(summaryText);

    // Extract conclusion summary
    const conclusionMatch = summaryText.match(/Conclusion Summary:(.+?)(?=\n\n|$)/is);
    const conclusion = conclusionMatch ? conclusionMatch[1].trim() : '';

    return {
      title,
      summary: summaryText,
      team,
      pokemonNames,
      strengths: this.extractStrengths(summaryText),
      weaknesses: this.extractWeaknesses(summaryText)
    };
  }

  private extractPokemonNames(summary: string): string[] {
    const pokemonMatches = summary.match(/Pokémon \d+:\s*([^\n]+)/g);
    if (!pokemonMatches) return [];

    return pokemonMatches
      .map(match => {
        const nameMatch = match.match(/Pokémon \d+:\s*([^\n]+)/);
        return nameMatch ? nameMatch[1].trim() : '';
      })
      .filter(name => name.length > 0)
      .slice(0, 6); // Limit to 6 Pokemon
  }

  private parseTeamMembers(summary: string): PokemonTeamMember[] {
    // This is a simplified parser - you might want to enhance this based on your specific needs
    const pokemonNames = this.extractPokemonNames(summary);
    
    return pokemonNames.map(name => ({
      name,
      moves: [],
      teraType: 'Not specified'
    }));
  }

  private parseDetailedTeamMembers(summary: string): PokemonTeamMember[] {
    const pokemonSections = summary.split(/Pokémon \d+:/);
    const team: PokemonTeamMember[] = [];

    for (let i = 1; i < pokemonSections.length && i <= 6; i++) {
      const section = pokemonSections[i];
      const lines = section.split('\n');

      // Extract Pokemon name (first line after "Pokémon X:")
      const name = lines[0]?.trim() || `Pokemon ${i}`;

      // Extract ability
      const abilityMatch = section.match(/- Ability:\s*([^\n]+)/);
      const ability = abilityMatch ? abilityMatch[1].trim() : 'Not specified';

      // Extract held item
      const itemMatch = section.match(/- Held Item:\s*([^\n]+)/);
      const item = itemMatch ? itemMatch[1].trim() : 'Not specified';

      // Extract Tera type
      const teraMatch = section.match(/- Tera Type:\s*([^\n]+)/);
      const teraType = teraMatch ? teraMatch[1].trim() : 'Not specified';

      // Extract nature
      const natureMatch = section.match(/- Nature:\s*([^\n]+)/);
      const nature = natureMatch ? natureMatch[1].trim() : 'Not specified';

      // Extract moves with enhanced filtering
      const movesMatch = section.match(/- Moves:\s*([^\n]+)/);
      let moves: string[] = [];
      if (movesMatch) {
        const movesText = movesMatch[1].trim();
        // Handle different separators
        if (movesText.includes('/')) {
          moves = movesText.split('/').map(move => move.trim()).filter(move => move.length > 0);
        } else if (movesText.includes(',')) {
          moves = movesText.split(',').map(move => move.trim()).filter(move => move.length > 0);
        } else {
          moves = [movesText];
        }
        
        // Filter out abilities that might be incorrectly included in moves
        const abilityKeywords = ['as one', 'unseen fist', 'grassy surge', 'regenerator', 'quark drive', 'drizzle'];
        moves = moves.filter(move => !abilityKeywords.includes(move.toLowerCase()));
      }

      // Extract EV spread
      const evMatch = section.match(/- EV Spread:\s*([^\n]+)/);
      const evSpread = evMatch ? evMatch[1].trim() : 'Not specified';

      // Extract EV explanation
      const evExplanationMatch = section.match(/- EV Explanation:\s*([\s\S]*?)(?=\n\n|\*\*Pokémon|\n- |$)/);
      const evExplanation = evExplanationMatch ? evExplanationMatch[1].trim() : 'Not specified';

      team.push({
        name,
        ability,
        item,
        teraType,
        moves,
        nature,
        evs: this.parseEVSpread(evSpread),
        evExplanation
      });
    }

    return team;
  }

  private extractStrengths(summary: string): string[] {
    const strengthsMatch = summary.match(/TEAM STRENGTHS[:\s]*([\s\S]*?)(?=TEAM WEAKNESSES|CONCLUSION|FINAL ARTICLE SUMMARY|$)/i);
    if (!strengthsMatch) return [];

    const strengthsText = strengthsMatch[1].trim();
    // Split by common separators and clean up
    const strengths = strengthsText
      .split(/[•\-\*;]/)
      .map(s => s.trim())
      .filter(s => s.length > 0 && s !== 'TEAM STRENGTHS')
      .map(s => s.replace(/^\d+\.\s*/, '')) // Remove numbered lists
      .filter(s => s.length > 10); // Only keep substantial strengths

    return strengths;
  }

  private extractWeaknesses(summary: string): string[] {
    const weaknessesMatch = summary.match(/TEAM WEAKNESSES[:\s]*([\s\S]*?)(?=CONCLUSION|FINAL ARTICLE SUMMARY|$)/i);
    if (!weaknessesMatch) return [];

    const weaknessesText = weaknessesMatch[1].trim();
    // Split by common separators and clean up
    const weaknesses = weaknessesText
      .split(/[•\-\*;]/)
      .map(s => s.trim())
      .filter(s => s.length > 0 && s !== 'TEAM WEAKNESSES')
      .map(s => s.replace(/^\d+\.\s*/, '')) // Remove numbered lists
      .filter(s => s.length > 10); // Only keep substantial weaknesses

    return weaknesses;
  }

  private parseEVSpread(evSpread: string): Record<string, number> | undefined {
    if (evSpread === 'Not specified' || evSpread === 'EVs not specified in the article or image.') {
      return undefined;
    }

    // Try different EV parsing patterns
    const evParsePatterns = [
      // Japanese format: H244 A252 B4 D4 S4
      /H(\d+)\s+A(\d+)\s+B(\d+)\s+C(\d+)\s+D(\d+)\s+S(\d+)/,
      /H(\d+)\s+A(\d+)\s+B(\d+)\s+D(\d+)\s+S(\d+)/,  // Missing C (SpA)
      // Standard format: 244 252 4 4 4 4 (space separated)
      /^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$/,
      /(\d+)\s*\/\s*(\d+)\s*\/\s*(\d+)\s*\/\s*(\d+)\s*\/\s*(\d+)\s*\/\s*(\d+)/,
      /(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/,
      /HP:\s*(\d+).*?Atk:\s*(\d+).*?Def:\s*(\d+).*?SpA:\s*(\d+).*?SpD:\s*(\d+).*?Spe:\s*(\d+)/
    ];

    for (const pattern of evParsePatterns) {
      const evMatch = evSpread.match(pattern);
      if (evMatch) {
        // Handle Japanese format (H=HP, A=Attack, B=Defense, C=SpA, D=SpD, S=Speed)
        if (pattern.source.startsWith('H(\\d+)')) {
          // Japanese format
          if (evMatch.length === 7) {
            // Full format: H244 A252 B4 C4 D4 S4
            return {
              hp: parseInt(evMatch[1]),
              attack: parseInt(evMatch[2]),
              defense: parseInt(evMatch[3]),
              spAtk: parseInt(evMatch[4]),
              spDef: parseInt(evMatch[5]),
              speed: parseInt(evMatch[6])
            };
          } else if (evMatch.length === 6) {
            // Missing C (SpA): H244 A252 B4 D4 S4
            return {
              hp: parseInt(evMatch[1]),
              attack: parseInt(evMatch[2]),
              defense: parseInt(evMatch[3]),
              spAtk: 0,  // Missing C
              spDef: parseInt(evMatch[4]),
              speed: parseInt(evMatch[5])
            };
          }
        } else {
          // Standard format
          const stats = ['hp', 'attack', 'defense', 'spAtk', 'spDef', 'speed'];
          const evs: Record<string, number> = {};
          for (let j = 0; j < stats.length; j++) {
            try {
              evs[stats[j]] = parseInt(evMatch[j + 1]);
            } catch (error) {
              evs[stats[j]] = 0;
            }
          }
          return evs;
        }
      }
    }

    return undefined;
  }
}

// Export singleton instance
export const geminiService = new GeminiService();
export default geminiService;

