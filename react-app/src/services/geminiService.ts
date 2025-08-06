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

// Prompt template (from your Streamlit app)
const PROMPT_TEMPLATE = `
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
- Chien-Pao (チオンジェン/チエンパオ/チェンパオ) is the Ice/Dark legendary with Sword of Ruin ability
- When in doubt, look at the moves, abilities, and visual appearance in images to distinguish them

**Your Task:**

You are provided with article text and team images. Your response must be strictly based on the visible and written content. If anything is unclear, partial, or missing, mark it as such. **Do not make assumptions.**

**CRITICAL IMAGE ANALYSIS FOR EV EXTRACTION:**
When analyzing team images, prioritize these elements:

1. **EV Spreads (HIGHEST PRIORITY):**
   - Look for stat displays with format: H### A### B### C### D### S### (e.g., H244 A252 B4 C0 D4 S4)
   - Search for "努力値" (Japanese for "Effort Values") followed by numbers
   - Look for EV bars, stat distributions, or numerical displays
   - Check for patterns like "252/252/4" or "244/252/12"
   - Examine Pokemon summary screens, team builders, or stat calculators

2. **Pokemon Identification:**
   - Japanese names (e.g., バドレックス=Calyrex, カイオーガ=Kyogre, ウーラオス=Urshifu)
   - Visual sprites/models to confirm identity
   - Type icons and color schemes

3. **Additional Data:**
   - Move names in Japanese with type icons
   - Held items (icons: red apple, blue orb, etc.)
   - Nature indicators (up/down arrows, red/blue text)
   - Ability names in Japanese
   - Tera type indicators

**ENHANCED IMAGE ANALYSIS INSTRUCTIONS:**
- **SCAN EVERY IMAGE** for EV-related information first
- **LOOK FOR MULTIPLE EV FORMATS**: H/A/B/C/D/S, HP/Atk/Def/SpA/SpD/Spe, numerical spreads
- **EXAMINE POKEMON SUMMARY SCREENS** - these often show detailed EV information
- **CHECK TEAM BUILDING TOOLS** - Showdown, Pikalytics, or similar interfaces
- **CROSS-REFERENCE** image EV data with any text mentions
- **PRIORITIZE IMAGE DATA** - if image shows EVs but text doesn't, use image data
- **EXTRACT EXACT VALUES** - don't approximate, get precise EV numbers from images
- **DO NOT make assumptions** about moves - only use what's clearly visible in images or explicitly stated in text
- **Pay special attention** to move type icons and their corresponding move names

---

1. **Extract the title** of the article or blog post.
   - If there is a clear blog or article title, write it as:
     TITLE: [Japanese Title]（[English Translation]）
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
      pokemonNames
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

      // Extract moves
      const movesMatch = section.match(/- Moves:\s*([^\n]+)/);
      const moves = movesMatch 
        ? movesMatch[1].split('/').map(move => move.trim()).filter(move => move.length > 0)
        : [];

      // Extract EV spread
      const evMatch = section.match(/- EV Spread:\s*([^\n]+)/);
      const evSpread = evMatch ? evMatch[1].trim() : 'Not specified';

      // Extract nature
      const natureMatch = section.match(/- Nature:\s*([^\n]+)/);
      const nature = natureMatch ? natureMatch[1].trim() : 'Not specified';

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

  private parseEVSpread(evSpread: string): Record<string, number> | undefined {
    if (evSpread === 'Not specified') return undefined;

    const evMatch = evSpread.match(/(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/);
    if (!evMatch) return undefined;

    return {
      hp: parseInt(evMatch[1]),
      attack: parseInt(evMatch[2]),
      defense: parseInt(evMatch[3]),
      spAtk: parseInt(evMatch[4]),
      spDef: parseInt(evMatch[5]),
      speed: parseInt(evMatch[6])
    };
  }
}

// Export singleton instance
export const geminiService = new GeminiService();
export default geminiService;

