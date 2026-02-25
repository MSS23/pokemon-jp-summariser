"""
VGC Image Analysis module for Pokemon team analysis from screenshots and team cards
"""

import base64
import re
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from google.genai import types
from .config import EV_STAT_TRANSLATIONS, NATURE_TRANSLATIONS, ABILITY_TRANSLATIONS, MOVE_NAME_TRANSLATIONS


def extract_images_from_url(url: str, max_images: int = 10) -> List[Dict[str, Any]]:
    """Extract images from webpage that might contain VGC data with note.com optimization"""
    images = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all images
        img_tags = soup.find_all("img")

        # Prioritize note.com team card images
        note_com_images = []
        other_images = []

        for img_tag in img_tags[: max_images * 2]:  # Check more images initially
            try:
                img_src = img_tag.get("src")
                if not img_src:
                    continue

                # Convert relative URLs to absolute
                img_url = urljoin(url, img_src)

                # ULTRA-ENHANCED priority scoring for note.com and hatenablog team images
                is_note_com_asset = "assets.st-note.com" in img_url
                is_hatenablog_asset = any(domain in img_url for domain in ["hatenablog.jp", "hatena.ne.jp", "hatenablog.com"])
                is_likely_team_card = False

                # COMPREHENSIVE team card indicators for Japanese VGC sites
                team_indicators = [
                    # Core VGC terms
                    "team", "pokemon", "vgc", "party", "チーム", "ポケモン", "構築",
                    
                    # Note.com specific patterns
                    "DvCIsNZXzyA2irhdlucjKOGR",  # Known note.com team card pattern
                    "rental", "レンタル", "build", "lineup", "note", "st-note",
                    
                    # Hatenablog specific patterns
                    "hatenablog", "hatena", "blog", "entry", "ブログ", "記事",
                    
                    # Japanese VGC terms and EV indicators
                    "ダブルバトル", "ダブル", "バトル", "調整", "努力値", "実数値",
                    "とくこう", "すばやさ", "こうげき", "ぼうぎょ", "とくぼう",
                    "最速", "準速", "4振り", "252", "244", "236", # Common EV values
                    "乱数1発", "確定1発", "耐え", "抜き", # Calc terms
                    
                    # Pokemon names that frequently appear in team cards
                    "ガブリアス", "ランドロス", "ガオガエン", "エルフーン", "パオジアン",
                    "テツノ", "ザマゼンタ", "ザシアン", "コライドン", "ミライドン",
                    "ハバタクカミ", "サーフゴー", "ドラパルト", "イエッサン", "ウインディ",
                    
                    # Items and moves that indicate team cards
                    "こだわりメガネ", "きあいのタスキ", "とつげきチョッキ", "たべのこし",
                    "まもる", "ねこだまし", "じしん", "10まんボルト"
                ]
                
                url_lower = img_url.lower()
                alt_text = img_tag.get("alt", "").lower()
                title_text = img_tag.get("title", "").lower()
                combined_text = f"{url_lower} {alt_text} {title_text}"

                # Enhanced team card detection with scoring
                team_card_score = 0
                for indicator in team_indicators:
                    if indicator.lower() in combined_text:
                        team_card_score += 1
                        # Extra weight for core VGC terms
                        if indicator in ["team", "pokemon", "vgc", "チーム", "ポケモン", "構築"]:
                            team_card_score += 2
                        # Extra weight for EV indicators (high priority for our goal)
                        if indicator in ["努力値", "実数値", "調整", "252", "244", "236"]:
                            team_card_score += 3
                
                # Domain-specific scoring bonuses
                if is_note_com_asset:
                    team_card_score += 2  # Note.com assets get priority
                if is_hatenablog_asset:
                    team_card_score += 2  # Hatenablog assets get priority
                
                is_likely_team_card = team_card_score >= 1

                # Skip very small images but be more lenient for Japanese VGC sites
                width = img_tag.get("width")
                height = img_tag.get("height")
                skip_small = False

                if width and height:
                    try:
                        w, h = int(width), int(height)
                        # More lenient for Japanese VGC sites
                        if is_note_com_asset or is_hatenablog_asset:
                            if w < 300 or h < 200:  # Lenient for Japanese sites
                                skip_small = True
                        else:
                            if w < 100 or h < 100:
                                skip_small = True
                    except:
                        pass

                if skip_small:
                    continue

                # Download and process image
                img_response = requests.get(img_url, headers=headers, timeout=15)
                if img_response.status_code == 200:
                    # Skip if too small in bytes (likely not a team card)
                    if len(img_response.content) < 5000:  # Less than 5KB
                        continue

                    # Convert to base64 for Gemini Vision
                    img_data = base64.b64encode(img_response.content).decode("utf-8")

                    # Get image info
                    try:
                        pil_img = Image.open(BytesIO(img_response.content))
                        img_format = pil_img.format
                        img_size = pil_img.size
                    except:
                        img_format = "unknown"
                        img_size = (0, 0)

                    image_info = {
                        "url": img_url,
                        "data": img_data,
                        "format": img_format,
                        "size": img_size,
                        "alt_text": img_tag.get("alt", ""),
                        "title": img_tag.get("title", ""),
                        "content_type": img_response.headers.get("content-type", ""),
                        "is_note_com_asset": is_note_com_asset,
                        "is_hatenablog_asset": is_hatenablog_asset,
                        "is_likely_team_card": is_likely_team_card,
                        "team_card_score": team_card_score,
                        "file_size": len(img_response.content),
                    }

                    # Prioritize Japanese VGC site assets and likely team cards
                    if is_note_com_asset or is_hatenablog_asset or is_likely_team_card:
                        note_com_images.append(image_info)
                    else:
                        other_images.append(image_info)

            except Exception as e:
                continue

        # Sort priority images by team card score (highest first)
        note_com_images.sort(key=lambda x: x["team_card_score"], reverse=True)
        other_images.sort(key=lambda x: x["team_card_score"], reverse=True)
        
        # Combine with priority: Japanese VGC site assets first, then others
        priority_images = note_com_images + other_images
        images = priority_images[:max_images]

    except Exception as e:
        raise ValueError(f"Could not extract images: {str(e)}")

    return images


def is_potentially_vgc_image(image_info: Dict[str, Any]) -> bool:
    """Ultra-enhanced VGC image detection optimized for note.com team cards"""

    # Advanced scoring system with note.com specialization
    relevance_score = 0
    confidence_multipliers = 1.0

    # PRIORITY 1: Note.com assets (ULTRA HIGH PRIORITY - these are almost always team cards)
    if image_info.get("is_note_com_asset", False):
        width, height = image_info.get("size", (0, 0))
        file_size = image_info.get("file_size", 0)
        url = image_info.get("url", "").lower()
        team_score = image_info.get("team_card_score", 0)
        
        # Note.com team cards have very specific characteristics
        if width >= 400 and height >= 300 and file_size > 15000:  # 15KB+ minimum for team cards
            relevance_score += 12  # ULTRA HIGH base score for note.com
            
            # MAJOR bonus for high team card score
            relevance_score += min(team_score * 2, 8)  # Up to +8 points for team indicators
            
            # Bonus for ideal team card dimensions (note.com standard sizes)
            if 600 <= width <= 1200 and 400 <= height <= 800:
                relevance_score += 4  # Perfect team card size
            elif 800 <= width <= 1600 and 500 <= height <= 1000:
                relevance_score += 3  # Large team card format
                
            # Enhanced file size analysis for note.com
            if file_size > 50000:  # 50KB+ indicates detailed team card
                relevance_score += 3
            if file_size > 100000:  # 100KB+ premium content
                relevance_score += 3
            if file_size > 200000:  # 200KB+ ultra-detailed 
                relevance_score += 2
                
            # Note.com URL pattern analysis (enhanced)
            if "uploads/images" in url:  # User-uploaded content
                relevance_score += 3  # Higher weight for user content
            if any(pattern in url for pattern in ["rectangle", "large", "medium", "wide"]):
                relevance_score += 2
            if "note-common-styles" in url or "team" in url:
                relevance_score += 2
                
    # PRIORITY 2: Advanced dimension analysis for VGC content
    width, height = image_info.get("size", (0, 0))
    aspect_ratio = width / height if height > 0 else 0
    
    # Team card optimal dimensions
    if 0.8 <= aspect_ratio <= 2.0:  # Reasonable aspect ratios for team cards
        if width >= 600 and height >= 400:
            relevance_score += 4  # Good team card dimensions
        if width >= 800 and height >= 600:
            relevance_score += 5  # Excellent screenshot/team card size
        if width >= 1000 and height >= 600:
            relevance_score += 6  # Premium team display size
            
    # Wide format detection (rental team screenshots)
    if aspect_ratio >= 1.5 and width >= 1200:
        relevance_score += 5  # Wide rental team format
        
    # PRIORITY 3: Enhanced file size intelligence
    file_size = image_info.get("file_size", 0)
    if file_size > 20000:  # 20KB+ likely has meaningful content
        relevance_score += 2
    if file_size > 60000:  # 60KB+ definitely has detailed data
        relevance_score += 3
    if file_size > 150000:  # 150KB+ premium content
        relevance_score += 4
        confidence_multipliers *= 1.2
        
    # PRIORITY 4: Team card indicators
    if image_info.get("is_likely_team_card", False):
        relevance_score += 8  # High confidence team card flag
        confidence_multipliers *= 1.3

    # PRIORITY 5: Advanced text analysis with Japanese specialization
    text_content = (
        image_info.get("alt_text", "") + " " +
        image_info.get("title", "") + " " + 
        image_info.get("url", "")
    ).lower()

    # Ultra-comprehensive VGC keywords with scoring
    ultra_high_value_keywords = [
        "pokemon", "ポケモン", "vgc", "team", "チーム", 
        "rental", "レンタル", "party", "パーティ"
    ]
    
    high_value_keywords = [
        "構築", "調整", "努力値", "個体値", "battle", "バトル",
        "competitive", "tournament", "大会", "doubles", "ダブル"
    ]
    
    medium_value_keywords = [
        "ev", "iv", "stats", "movesets", "nature", "性格",
        "ability", "特性", "item", "持ち物", "tera", "テラス"
    ]
    
    # Legendary/popular Pokemon names (strong indicators)
    pokemon_indicators = [
        "ガブリアス", "ガオガエン", "ウインディ", "モロバレル", "エルフーン",
        "ランドロス", "カイリュー", "ハリテヤマ", "クレッフィ", "トリトドン",
        "ニンフィア", "リザードン", "フラッター", "テツノ", "パオジアン",
        "チオンジェン", "ディンルー", "イーユイ", "コライドン", "ミライドン"
    ]
    
    # Score keywords
    for keyword in ultra_high_value_keywords:
        if keyword in text_content:
            relevance_score += 4
            confidence_multipliers *= 1.1
            
    for keyword in high_value_keywords:
        if keyword in text_content:
            relevance_score += 3
            
    for keyword in medium_value_keywords:
        if keyword in text_content:
            relevance_score += 2
            
    # Pokemon name bonus
    pokemon_count = sum(1 for pokemon in pokemon_indicators if pokemon in text_content)
    if pokemon_count >= 2:  # Multiple Pokemon names = likely team content
        relevance_score += pokemon_count * 2
        confidence_multipliers *= 1.2

    # PRIORITY 6: Enhanced URL pattern analysis
    src_url = image_info.get("url", "").lower()
    
    # Domain-based scoring
    if "assets.st-note.com" in src_url:
        relevance_score += 4  # Note.com assets are premium
    elif "note.com" in src_url:
        relevance_score += 3
    elif "pbs.twimg.com" in src_url:
        relevance_score += 2  # Twitter images often have team cards
    elif "gyazo.com" in src_url or "imgur.com" in src_url:
        relevance_score += 1  # Screenshot hosting services

    # File format preferences with quality indicators
    if src_url.endswith(".png"):
        relevance_score += 2  # PNG often used for high-quality team cards
    elif src_url.endswith((".jpg", ".jpeg")):
        relevance_score += 1

    # Apply confidence multipliers
    final_score = int(relevance_score * confidence_multipliers)
    
    # PRIORITY 7: Special note.com override
    # If it's a note.com asset with reasonable size, prioritize it heavily
    if (image_info.get("is_note_com_asset", False) and 
        width >= 400 and height >= 300 and file_size > 10000):
        return True  # Force inclusion for note.com assets
    
    # Standard threshold with dynamic adjustment
    base_threshold = 8
    
    # Lower threshold for note.com content
    if "note.com" in src_url:
        base_threshold = 6
        
    # Lower threshold if multiple Pokemon indicators
    if pokemon_count >= 2:
        base_threshold = 7
    
    return final_score >= base_threshold


def encode_image_for_gemini(
    image_data: str, format_type: str = "jpeg"
) -> Dict[str, Any]:
    """Prepare image data for Gemini Vision API"""
    return {"mime_type": f"image/{format_type.lower()}", "data": image_data}


def get_vision_analysis_prompt() -> str:
    """Get the comprehensive vision analysis prompt optimized for Japanese Pokemon team cards"""
    return '''
🎯 ULTRA-ENHANCED JAPANESE POKEMON TEAM CARD ANALYSIS (2025):
Extract complete Pokemon team data from Japanese VGC team cards with maximum precision on EV spreads.

**🚨 CRITICAL PRIORITY: EV SPREAD EXTRACTION - VISUAL ONLY, NO GENERATION 🚨**
This is your PRIMARY objective. ONLY extract EV data that is VISUALLY PRESENT and READABLE in the image.
**CRITICAL RULE: If you cannot see clear, readable EV numbers in the image, return "EV data not visible" - DO NOT generate or guess spreads.**

**OBJECTIVE 1: SYSTEMATIC EV DETECTION (HIGHEST PRIORITY)**
SCAN EVERY pixel for EV patterns in these EXACT formats:

**A. Calculated Stat Format (PRIORITY - hatenablog.jp & note.com style):**
- "H181(148)-A×↓-B131(124)-C184↑(116)-D112(4)-S119(116)"
- Format: [StatLetter][CalculatedValue]([EVValue])[NatureSymbol]
- Extract ONLY the numbers in parentheses (148, 124, 116, 4, 116)
- Nature symbols: ↑ = boost, ↓ = reduce, × = neutral/no investment
- IGNORE the first number (calculated stat), focus on parentheses
- 🎯 EXACT EXAMPLES from problem articles:
  * "実数値:205-x-125-198-136-160" + "努力値:236-0-36-196-4-36"
  * "H205(236)-A×↓-B125(36)-C198↑(196)-D136(4)-S160(36)"

**B. Direct Japanese EV Format (ULTRA-PRIORITY for yunu.hatenablog.jp):**
- "努力値:236-0-36-196-4-36" (EXACT pattern from Miraidon example)
- "努力値: 252-0-4-252-0-0" (standard format)
- "個体値調整: 244-0-12-252-0-0" (alternative format)
- Structure: [keyword]: [HP]-[Atk]-[Def]-[SpA]-[SpD]-[Spe]
- 🚨 CRITICAL: This is the MOST COMMON format in Japanese VGC articles

**C. Standard Slash Format:**
- "252/0/4/252/0/0" or "252-0-4-252-0-0" (HP/Atk/Def/SpA/SpD/Spe order)
- "H252/A0/B4/C252/D0/S0" (with stat prefixes)
- Look for 6 numbers separated by slashes or dashes

**D. Japanese Grid/Table Format (MOST COMMON in note.com):**
- ＨＰ: 252    こうげき: 0     ぼうぎょ: 4
- とくこう: 252  とくぼう: 0   すばやさ: 0
- Search for Japanese stat names with numbers next to them
- 🎯 Look for this in team card layouts and Pokemon description boxes

**E. Abbreviated Format (ENHANCED FOR USER'S HYBRID FORMAT):**
- "H252 A0 B4 C252 D0 S0" (single line with spaces)
- "252HP 4Def 252SpA" (mixed format)
- 🚨 **CRITICAL HYBRID FORMAT**: "努力値：H252 A4 B156 D68 S28" (Japanese prefix + abbreviated stats)
- 🔥 **ULTRA-PRIORITY EXAMPLES**:
  * "努力値：B4 C252 S252" (Defense 4, Special Attack 252, Speed 252)
  * "努力値：H252 A4 B156 D68 S28" (HP 252, Attack 4, Defense 156, Special Defense 68, Speed 28)
  * "個体値調整：H244 B12 C252 S4" (alternative Japanese prefix)
- Any combination of stat letters (H/A/B/C/D/S) with numbers, with or without Japanese prefixes

**F. Individual Stat Lines:**
- HP: 252 (or ＨＰ：252)
- Attack: 0 (or こうげき：0)
- Defense: 4 (or ぼうぎょ：4)
- Sp. Atk: 252 (or とくこう：252)
- Sp. Def: 0 (or とくぼう：0)
- Speed: 0 (or すばやさ：0)

**G. Technical Context Format (From actual VGC analysis):**
- Damage calculations near EVs: "H-B:白馬A220のブリランダブルダメ乱数1発(12.5%)"
- Speed tier context: "S:最速90族＋4" indicates specific EV allocation
- Nature context: "控え目(C↑A↓)" = Modest nature

**🔍 ADVANCED JAPANESE EV DETECTION:**

**COMPREHENSIVE JAPANESE STAT VOCABULARY:**
- HP: ＨＰ, HP, H, ヒットポイント, 体力
- Attack: こうげき, 攻撃, A, アタック, 物理攻撃
- Defense: ぼうぎょ, 防御, B, ディフェンス, 物理防御
- Sp.Attack: とくこう, 特攻, 特殊攻撃, C, 特攻, とくしゅこうげき
- Sp.Defense: とくぼう, 特防, 特殊防御, D, 特防, とくしゅぼうぎょ
- Speed: すばやさ, 素早さ, S, スピード, 速さ

**JAPANESE LAYOUT PATTERNS TO CHECK:**
1. **Vertical stat lists** (most common in note.com team cards)
2. **Horizontal stat rows** with numbers aligned
3. **Grid format** with stat names on left, values on right
4. **Compact format** within Pokemon description boxes
5. **Small text** overlaid on Pokemon sprites/cards
6. **Side panel** information areas

**EV VALIDATION (CRITICAL):**
- Total must be ≤508 (if >508, these are likely battle stats, not EVs)
- Valid EV values: 0, 4, 12, 20, 28, 36, 44, 52, 60, 68, 76, 84, 92, 100, 108, 116, 124, 132, 140, 148, 156, 164, 172, 180, 188, 196, 204, 212, 220, 228, 236, 244, 252
- Common competitive patterns: 252/252/4, 252/0/0/252/4/0, 244/0/12/252/0/0

**OBJECTIVE 2: POKEMON IDENTIFICATION & VALIDATION**
- Identify Pokemon by sprites/artwork
- Read Japanese Pokemon names in text
- Cross-reference visual and textual identification
- Note forms, regional variants, shiny status

**OBJECTIVE 3: ADDITIONAL DATA EXTRACTION**
- Nature (look for ↑↓ arrows or Japanese nature names)
- Held Items (icons + Japanese item names)
- Abilities (Japanese ability names)
- Moves (4 moves listed in Japanese)
- Tera Types (type icons or テラス text)

**🗾 JAPANESE ITEM TRANSLATIONS:**
- たべのこし=Leftovers, きあいのタスキ=Focus Sash, いのちのたま=Life Orb
- こだわりハチマキ=Choice Band, こだわりメガネ=Choice Specs, こだわりスカーフ=Choice Scarf
- とつげきチョッキ=Assault Vest, オボンのみ=Sitrus Berry, ラムのみ=Lum Berry
- ヨプのみ=Yache Berry, カムラのみ=Salac Berry, ひかりのこな=BrightPowder

**🌟 JAPANESE NATURE TRANSLATIONS:**
- いじっぱり=Adamant, ようき=Jolly, おくびょう=Timid, ひかえめ=Modest
- ずぶとい=Bold, わんぱく=Impish, おだやか=Calm, しんちょう=Careful

**REQUIRED OUTPUT FORMAT:**
For EACH Pokemon found, provide:
```
POKEMON #[X]: [Name]
- Japanese Name: [Japanese text if visible]
- EV Spread: [EXACT format found] → Validated: [HP/Atk/Def/SpA/SpD/Spe]
- EV Total: [number] (Valid: Yes/No)
- EV Confidence: High/Medium/Low
- Nature: [nature name]
- Item: [item name]
- Ability: [ability name]
- Moves: [move1, move2, move3, move4]
- Additional Notes: [any issues or observations]
```

**FINAL SUMMARY:**
```
=== EV EXTRACTION RESULTS ===
Total Pokemon: [X]
EVs Successfully Extracted: [X/X]
High Confidence EVs: [X]
Medium/Low Confidence: [X]
Failed Extractions: [X] (reasons)

CRITICAL ISSUES: [List any major problems]
```

**🚨 CRITICAL VALIDATION RULES:**
1. **NEVER generate EV spreads** - only extract what is clearly visible as text/numbers in the image
2. **If EV data is blurry, cut off, or unclear** - return "EV data not readable" rather than guessing
3. **Do not assume standard competitive spreads** (like 252/252/4) unless you can clearly read those exact numbers
4. **If you see Pokemon sprites but no EV data** - this is normal for many team cards, return "EVs not displayed"
5. **Multiple Pokemon with identical EV spreads indicates generation** - recheck your extraction carefully
6. **Prefer "no data found" over potentially wrong data** - accuracy is more important than completeness
'''


def get_screenshot_analysis_prompt() -> str:
    """Get the vision analysis prompt optimized for Nintendo Switch team screenshots"""
    return '''
🎯 NINTENDO SWITCH POKEMON TEAM SCREENSHOT ANALYSIS (2025):
Extract Pokemon team data from Nintendo Switch team screenshots with focus on basic team composition.

**🎮 SWITCH SCREENSHOT IDENTIFICATION:**
You are analyzing a Nintendo Switch Pokemon team screenshot (typically blue background with 6 Pokemon sprites).
These screenshots show basic team composition but typically DO NOT contain detailed EV spreads.

🔍 **SYSTEMATIC POKEMON IDENTIFICATION PROCESS:**

**STEP 1: SCREENSHOT ANALYSIS & SETUP**
1. **Identify Screenshot Type**: Team builder, battle box, rental team, or battle screen
2. **Count Pokemon Positions**: Locate all 6 Pokemon slots (even if some empty)
3. **Assess Image Quality**: Note if sprites are clear, blurry, or partially obscured
4. **UI Language Detection**: Identify if interface shows Japanese text

**STEP 2: INDIVIDUAL POKEMON ANALYSIS (Repeat for each Pokemon)**
For Pokemon Position #1, #2, #3, #4, #5, #6:

**A. VISUAL SPRITE EXAMINATION:**
- **Primary Colors**: What are the dominant colors? (e.g., golden = Gholdengo, brown/tan = Ursaluna)
- **Body Shape**: Humanoid, quadruped, bird-like, fish-like, etc.
- **Size Relative**: Large, medium, small compared to other Pokemon
- **Distinctive Features**: Wings, tails, weapons, special appendages, unique silhouette
- **Posture/Stance**: Standing, flying, swimming, fighting pose

**B. DETAILED FEATURE ANALYSIS:**
- **Head Shape**: Round, angular, elongated, crowned, etc.
- **Eyes**: Visible eye color, size, expression
- **Body Texture**: Smooth, furry, scaled, metallic, ghostly
- **Special Elements**: Flames, water, electricity, auras, typing indicators
- **Unique Identifiers**: Specific patterns, markings, tools, or accessories

**C. JAPANESE TEXT EXTRACTION:**
- **Pokemon Name Text**: Look for Japanese characters near each Pokemon
- **Scan Systematically**: Check above, below, and beside each sprite
- **OCR Confidence**: Note if text is clear or partially obscured

**D. CROSS-REFERENCE IDENTIFICATION:**
- **Visual + Text Matching**: Compare sprite analysis with any Japanese text found
- **Database Lookup**: Match findings against comprehensive Pokemon database
- **Form Verification**: Check if this is a regional variant, paradox form, or special form
- **Confidence Assessment**: Rate identification as High/Medium/Low confidence

**STEP 3: TEAM COMPOSITION VALIDATION**
- **VGC Legality Check**: Does this team make sense for competitive play?
- **Type Balance Review**: Reasonable type distribution and synergy
- **Generation Consistency**: Mix of Pokemon from different generations is normal
- **Meta Relevance**: Are these Pokemon commonly used in VGC?

**STEP 4: HELD ITEMS & ADDITIONAL INFO**
- **Item Icon Detection**: Look for small item icons near Pokemon sprites
- **Japanese Item Names**: Extract any visible item text
- **Ability/Move Info**: Note any additional data if visible
- **Level/Stats**: Record if visible (usually not in team builders)

**🚨 CRITICAL IDENTIFICATION GUIDELINES:**

**COMMON SWITCH SCREENSHOT POKEMON BY VISUAL CUES:**
- **Golden/Yellow Metal Pokemon** = Likely Gholdengo (ゴルデンゴ)
- **Large Brown Bear** = Likely Ursaluna (ガチグマ)
- **Big Pelican/Bird** = Likely Pelipper (ペリッパー)
- **Bridge/Structure-like** = Likely Archaludon (ブリジュラス)
- **Long Fish with Red/White** = Likely Basculegion (イダイトウ)
- **Small White/Green Cotton Ball** = Likely Whimsicott (エルフーン)
- **Orange Dragon** = Likely Koraidon (コライドン)
- **Purple Electric Dragon** = Likely Miraidon (ミライドン)
- **Pink/Purple Flowing Ghost** = Likely Flutter Mane (フラッター)
- **Metallic Robot-like** = Likely Iron Paradox Pokemon (テツノ)

**ERROR PREVENTION STRATEGIES:**
- **Don't Guess**: If uncertain between 2+ Pokemon, state both possibilities
- **Use Elimination**: Rule out impossible matches based on clear visual differences
- **Context Clues**: Use team composition to validate individual identifications
- **Confidence Scoring**: Always provide confidence level for each identification

**🗾 ESSENTIAL JAPANESE TRANSLATIONS:**

**POKEMON NAMES (Key ones to recognize):**
- ガブリアス = Garchomp
- ランドロス = Landorus
- ガオガエン = Incineroar  
- ウインディ = Arcanine
- モロバレル = Amoonguss
- エルフーン = Whimsicott
- カイリュー = Dragonite
- リザードン = Charizard
- ニンフィア = Sylveon
- パオジアン = Chien-Pao
- チオンジェン = Chi-Yu
- ディンルー = Ting-Lu
- イーユイ = Wo-Chien

**CRITICAL MISSING POKEMON (Recently Misidentified):**
- ゴルデンゴ = Gholdengo (Gen 9 Steel/Ghost - golden surfboard-like Pokemon)
- ペリッパー = Pelipper (Water/Flying - large pelican Pokemon)
- ガチグマ = Ursaluna (Ground/Normal - large brown bear from Legends Arceus)
- ブリジュラス = Archaludon (Steel/Dragon - bridge-like structure Pokemon)
- イダイトウ = Basculegion (Water/Ghost - elongated fish with red/white coloring)

**ADDITIONAL COMMON VGC POKEMON:**
- フラッター = Flutter Mane (Ghost/Fairy paradox - flowing pink/purple)
- テツノ = Iron (Future Paradox prefix - various Iron Pokemon)
- ウネルミナモ = Walking Wake (Water/Dragon paradox)
- ライド = Raging Bolt (Electric/Dragon paradox)
- トリトドン = Gastrodon (Water/Ground - sea slug Pokemon)
- クレッフィ = Klefki (Steel/Fairy - key ring Pokemon)
- ハリテヤマ = Hariyama (Fighting - sumo wrestler Pokemon)
- オーロンゲ = Grimmsnarl (Dark/Fairy - long-haired troll-like)
- ドラパルト = Dragapult (Dragon/Ghost - stealth bomber-like)
- ミミッキュ = Mimikyu (Ghost/Fairy - Pikachu disguise)
- アーマーガア = Corviknight (Flying/Steel - armored raven)
- サーフゴー = Gholdengo (Steel/Ghost - same as ゴルデンゴ)
- コライドン = Koraidon (Fighting/Dragon - orange legendary)
- ミライドン = Miraidon (Electric/Dragon - purple legendary)
- カイオーガ = Kyogre (Water legendary - blue whale-like)
- グラードン = Groudon (Ground legendary - red dinosaur-like)
- レックウザ = Rayquaza (Dragon/Flying legendary - green serpent)
- ルナアーラ = Lunala (Psychic/Ghost legendary - bat-like)
- ソルガレオ = Solgaleo (Psychic/Steel legendary - lion-like)
- ネクロズマ = Necrozma (Psychic legendary - crystalline)
- ザシアン = Zacian (Fairy/Steel legendary - wolf with sword)
- ザマゼンタ = Zamazenta (Fighting/Steel legendary - wolf with shield)
- バドレックス = Calyrex (Psychic/Grass legendary - crowned)
- レジエレキ = Regieleki (Electric legendary - electrical pattern)
- レジドラゴ = Regidrago (Dragon legendary - dragon head)
- ブリザポス = Glastrier (Ice legendary horse)
- レイスポス = Spectrier (Ghost legendary horse)

**ITEM NAMES:**
- たべのこし = Leftovers
- きあいのタスキ = Focus Sash
- いのちのたま = Life Orb
- こだわりハチマキ = Choice Band
- こだわりメガネ = Choice Specs
- こだわりスカーフ = Choice Scarf
- とつげきチョッキ = Assault Vest
- オボンのみ = Sitrus Berry
- ラムのみ = Lum Berry

**FORMS AND VARIANTS:**
- テリジオン = Terrakion
- コバルオン = Cobalion  
- ビリジオン = Virizion
- ザマゼンタ = Zamazenta
- ザシアン = Zacian
- カラマネロ = Malamar
- イルカマン = Palafin

**REQUIRED OUTPUT FORMAT:**

```
=== NINTENDO SWITCH TEAM SCREENSHOT ANALYSIS ===

SCREENSHOT ASSESSMENT:
- Screenshot Type: [Team Builder/Battle Box/Rental Team/Battle Screen]
- Image Quality: [Good/Fair/Poor]
- UI Language: [Japanese/English/Mixed]
- Total Pokemon Slots Visible: [X/6]

SYSTEMATIC POKEMON IDENTIFICATION:

Pokemon Slot #1:
- Visual Analysis: [Dominant colors, body shape, distinctive features]
- Japanese Name Text: [Japanese characters if visible, or "Not visible"]
- Identified As: [Pokemon Name] 
- Confidence Level: [High/Medium/Low]
- Reasoning: [Brief explanation of identification]
- Held Item: [Item name or "Not visible"]

Pokemon Slot #2:
- Visual Analysis: [Dominant colors, body shape, distinctive features]
- Japanese Name Text: [Japanese characters if visible, or "Not visible"]
- Identified As: [Pokemon Name]
- Confidence Level: [High/Medium/Low]
- Reasoning: [Brief explanation of identification]
- Held Item: [Item name or "Not visible"]

[Continue for all 6 Pokemon slots]

TEAM COMPOSITION VALIDATION:
- VGC Legality: [Legal/Questionable - explain if issues]
- Type Balance: [Describe type distribution]
- Meta Relevance: [Common/Uncommon/Unusual team composition]
- Synergy Assessment: [Brief team synergy notes]

CONFIDENCE SUMMARY:
- High Confidence Identifications: [X/6]
- Medium Confidence Identifications: [X/6] 
- Low Confidence Identifications: [X/6]
- Failed Identifications: [X/6]

POTENTIAL IDENTIFICATION ISSUES:
[List any Pokemon you're uncertain about and why]

OVERALL ANALYSIS QUALITY:
- Screenshot Quality Impact: [How image quality affected analysis]
- Text Visibility: [How well Japanese text could be read]
- Final Confidence Rating: [High/Medium/Low]

POKEPASTE READINESS:
✅ Pokemon names available: [X/6 identified]
❌ EV spreads not available (user must add manually)
❌ Complete movesets not available (user must add manually)
⚠️ Low confidence identifications: [List any uncertain Pokemon]
```

**🚨 CRITICAL REMINDERS FOR ACCURATE IDENTIFICATION:**

1. **VISUAL ANALYSIS FIRST**: Analyze the sprite/model appearance before looking at text
2. **CROSS-VALIDATE**: Match visual analysis with any Japanese text found
3. **USE PROCESS OF ELIMINATION**: Rule out obviously wrong Pokemon based on clear differences
4. **DON'T FORCE MATCHES**: If uncertain, state multiple possibilities with confidence levels
5. **RECENT FAILURE EXAMPLE**: A team was incorrectly identified - the actual team was:
   - Whimsicott (エルフーン) - small white/green cotton Pokemon
   - Gholdengo (ゴルデンゴ) - golden metallic surfboard-like Pokemon  
   - Pelipper (ペリッパー) - large white/blue pelican Pokemon
   - Ursaluna (ガチグマ) - large brown bear Pokemon
   - Archaludon (ブリジュラス) - metallic bridge-like structure Pokemon
   - Basculegion (イダイトウ) - elongated red/white ghost fish Pokemon

6. **SYSTEMATIC APPROACH**: Follow the step-by-step process, don't skip steps
7. **CONFIDENCE HONESTY**: Better to admit uncertainty than give wrong confident answer
8. **CONTEXT VALIDATION**: Check if the identified team makes sense for VGC play

**🚨 REMEMBER: Switch screenshots provide basic team composition only. Focus on accurate Pokemon identification and visible items. Do not attempt to guess EVs or detailed strategies.**
'''


def analyze_image_with_vision(image_data: str, image_format: str, client) -> str:
    """Analyze a single image using Gemini Vision"""
    try:
        # Prepare image for Gemini (inline_data format for new google-genai SDK)
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=f"image/{image_format.lower()}",
                data=image_data,
            )
        )

        vision_prompt = get_vision_analysis_prompt()

        # Generate response using vision client
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[vision_prompt, image_part]
        )

        if response and response.text:
            return response.text
        else:
            return "No analysis results from vision model"

    except Exception as e:
        return f"Vision analysis error: {str(e)}"


def extract_ev_spreads_from_image_analysis(image_analysis: str) -> List[Dict[str, Any]]:
    """Enhanced EV spread extraction with comprehensive Japanese pattern recognition and calculated stat format"""
    ev_spreads = []
    
    # PRIORITY 1: Calculated stat format (liberty-note.com style) - NEW!
    calc_stat_patterns = [
        r"([HABCDS])(?:\d+)?\((\d+)\)([↑↓×]?)",  # H181(148)↑ or H(148)
        r"([HABCDS])\((\d+)\)([↑↓×]?)",  # H(148)×
        r"([HABCDS])(\d+)([↑↓×])",  # H148↑ (without parentheses)
    ]
    
    for pattern in calc_stat_patterns:
        matches = re.finditer(pattern, image_analysis, re.UNICODE | re.IGNORECASE)
        stat_groups = []
        
        for match in matches:
            stat_groups.append(match.groups())
        
        # If we found multiple stat groups, try to form a complete EV spread
        if len(stat_groups) >= 4:  # Need at least 4 stats for reasonable confidence
            ev_values = [0, 0, 0, 0, 0, 0]
            stat_mapping = {'H': 0, 'A': 1, 'B': 2, 'C': 3, 'D': 4, 'S': 5}
            
            valid_stats = 0
            for stat_letter, ev_value, nature_symbol in stat_groups:
                if stat_letter.upper() in stat_mapping:
                    try:
                        ev_int = int(ev_value)
                        if 0 <= ev_int <= 252:
                            ev_values[stat_mapping[stat_letter.upper()]] = ev_int
                            valid_stats += 1
                    except (ValueError, IndexError):
                        continue
            
            if valid_stats >= 4:
                spread_dict = _create_ev_spread_dict(ev_values, "calculated_stat_format", f"calc_format_{len(stat_groups)}_stats")
                if spread_dict:
                    ev_spreads.append(spread_dict)
    
    # PRIORITY 2: Standard slash-separated format (most reliable)
    slash_patterns = [
        r"(\d{1,3})[\/\-](\d{1,3})[\/\-](\d{1,3})[\/\-](\d{1,3})[\/\-](\d{1,3})[\/\-](\d{1,3})",  # 252/0/4/252/0/0
        r"H(\d{1,3})[\/\-]A(\d{1,3})[\/\-]B(\d{1,3})[\/\-]C(\d{1,3})[\/\-]D(\d{1,3})[\/\-]S(\d{1,3})",  # H252/A0/B4...
    ]
    
    for pattern in slash_patterns:
        matches = re.finditer(pattern, image_analysis, re.IGNORECASE)
        for match in matches:
            ev_values = [int(x) for x in match.groups()]
            if len(ev_values) == 6:
                spread_dict = _create_ev_spread_dict(ev_values, "slash_format", match.group())
                if spread_dict:
                    ev_spreads.append(spread_dict)
    
    # PRIORITY 2: Space-separated format with stat abbreviations (ULTRA-ENHANCED FOR JAPANESE HYBRID FORMAT)
    space_patterns = [
        # CRITICAL: Japanese hybrid format (努力値：H252 A4 B156 format) - USER'S EXACT CASE
        r"(?:努力値|個体値調整|EV配分|調整|EV)[：:\s]\s*H(\d{1,3})\s+A(\d{1,3})\s+B(\d{1,3})\s+C(\d{1,3})\s+D(\d{1,3})\s+S(\d{1,3})",
        r"(?:努力値|個体値調整|EV配分|調整|EV)[：:\s]\s*H(\d{1,3})\s*A(\d{1,3})\s*B(\d{1,3})\s*C(\d{1,3})\s*D(\d{1,3})\s*S(\d{1,3})",  # Optional spaces
        # Enhanced Japanese variations
        r"(?:努力値振り|EV振り|振り分け)[：:\s]\s*H(\d{1,3})\s*A(\d{1,3})\s*B(\d{1,3})\s*C(\d{1,3})\s*D(\d{1,3})\s*S(\d{1,3})",
        r"(?:実数値調整|ステ振り)[：:\s]\s*H(\d{1,3})\s*A(\d{1,3})\s*B(\d{1,3})\s*C(\d{1,3})\s*D(\d{1,3})\s*S(\d{1,3})",
        # Standard abbreviated format
        r"H(\d{1,3})\s+A(\d{1,3})\s+B(\d{1,3})\s+C(\d{1,3})\s+D(\d{1,3})\s+S(\d{1,3})",  # H252 A0 B4 C252 D0 S0
        r"H(\d{1,3})\s*A(\d{1,3})\s*B(\d{1,3})\s*C(\d{1,3})\s*D(\d{1,3})\s*S(\d{1,3})",  # Flexible spacing
        # Alternative format with HP/Atk names
        r"(\d{1,3})HP\s+(\d{1,3})Atk?\s+(\d{1,3})Def?\s+(\d{1,3})SpA?\s+(\d{1,3})SpD?\s+(\d{1,3})Spe?",  # 252HP 0Atk 4Def...
    ]
    
    for pattern in space_patterns:
        matches = re.finditer(pattern, image_analysis, re.IGNORECASE)
        for match in matches:
            ev_values = [int(x) for x in match.groups()]
            if len(ev_values) == 6:
                spread_dict = _create_ev_spread_dict(ev_values, "space_format", match.group())
                if spread_dict:
                    ev_spreads.append(spread_dict)
    
    # PRIORITY 2.5: Additional Japanese format variations
    additional_japanese_patterns = [
        # Table/grid format commonly used in note.com
        r"HP[:：]\s*(\d{1,3})\s*こうげき[:：]\s*(\d{1,3})\s*ぼうぎょ[:：]\s*(\d{1,3})\s*とくこう[:：]\s*(\d{1,3})\s*とくぼう[:：]\s*(\d{1,3})\s*すばやさ[:：]\s*(\d{1,3})",
        # Bullet point format
        r"[・•]\s*HP\s*(\d{1,3})\s*[・•]\s*こうげき\s*(\d{1,3})\s*[・•]\s*ぼうぎょ\s*(\d{1,3})\s*[・•]\s*とくこう\s*(\d{1,3})\s*[・•]\s*とくぼう\s*(\d{1,3})\s*[・•]\s*すばやさ\s*(\d{1,3})",
        # Bracket format
        r"\[HP(\d{1,3})\]\s*\[A(\d{1,3})\]\s*\[B(\d{1,3})\]\s*\[C(\d{1,3})\]\s*\[D(\d{1,3})\]\s*\[S(\d{1,3})\]",
        # Line break separated with Japanese stats
        r"ＨＰ\s*[:：]?\s*(\d{1,3}).*?こうげき\s*[:：]?\s*(\d{1,3}).*?ぼうぎょ\s*[:：]?\s*(\d{1,3}).*?とくこう\s*[:：]?\s*(\d{1,3}).*?とくぼう\s*[:：]?\s*(\d{1,3}).*?すばやさ\s*[:：]?\s*(\d{1,3})",
    ]
    
    for pattern in additional_japanese_patterns:
        matches = re.finditer(pattern, image_analysis, re.IGNORECASE | re.DOTALL)
        for match in matches:
            ev_values = [int(x) for x in match.groups()]
            if len(ev_values) == 6:
                spread_dict = _create_ev_spread_dict(ev_values, "japanese_table_format", match.group())
                if spread_dict:
                    ev_spreads.append(spread_dict)
    
    # PRIORITY 3: Japanese stat name patterns (CRITICAL for note.com)
    japanese_patterns = [
        # Full Japanese stat names with colons/spaces
        r"(?:ＨＰ|HP)[:\s]*(\d{1,3}).*?(?:こうげき|攻撃)[:\s]*(\d{1,3}).*?(?:ぼうぎょ|防御)[:\s]*(\d{1,3}).*?(?:とくこう|特攻|特殊攻撃)[:\s]*(\d{1,3}).*?(?:とくぼう|特防|特殊防御)[:\s]*(\d{1,3}).*?(?:すばやさ|素早さ|素早)[:\s]*(\d{1,3})",
        
        # Compact Japanese format
        r"ＨＰ(\d{1,3})\s*こうげき(\d{1,3})\s*ぼうぎょ(\d{1,3})\s*とくこう(\d{1,3})\s*とくぼう(\d{1,3})\s*すばやさ(\d{1,3})",
        
        # Mixed Japanese/English
        r"(?:HP|ＨＰ)(\d{1,3})\s*(?:A|こうげき)(\d{1,3})\s*(?:B|ぼうぎょ)(\d{1,3})\s*(?:C|とくこう)(\d{1,3})\s*(?:D|とくぼう)(\d{1,3})\s*(?:S|すばやさ)(\d{1,3})",
    ]
    
    for pattern in japanese_patterns:
        matches = re.finditer(pattern, image_analysis, re.IGNORECASE | re.DOTALL)
        for match in matches:
            ev_values = [int(x) for x in match.groups()]
            if len(ev_values) == 6:
                spread_dict = _create_ev_spread_dict(ev_values, "japanese_format", match.group())
                if spread_dict:
                    ev_spreads.append(spread_dict)
    
    # PRIORITY 4: Individual stat line parsing (flexible order)
    individual_stats = {}
    stat_patterns = {
        'hp': [r"(?:HP|ＨＰ|ヒットポイント)[:\s]*(\d{1,3})", r"体力[:\s]*(\d{1,3})"],
        'attack': [r"(?:Attack|こうげき|攻撃|A)[:\s]*(\d{1,3})", r"(?:アタック|物理攻撃)[:\s]*(\d{1,3})"],
        'defense': [r"(?:Defense|ぼうぎょ|防御|B)[:\s]*(\d{1,3})", r"(?:ディフェンス|物理防御)[:\s]*(\d{1,3})"],
        'special_attack': [r"(?:Sp\.?\s*Attack|とくこう|特攻|特殊攻撃|C)[:\s]*(\d{1,3})", r"(?:とくしゅこうげき)[:\s]*(\d{1,3})"],
        'special_defense': [r"(?:Sp\.?\s*Defense|とくぼう|特防|特殊防御|D)[:\s]*(\d{1,3})", r"(?:とくしゅぼうぎょ)[:\s]*(\d{1,3})"],
        'speed': [r"(?:Speed|すばやさ|素早さ|素早|S)[:\s]*(\d{1,3})", r"(?:スピード|速さ)[:\s]*(\d{1,3})"]
    }
    
    for stat, patterns in stat_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, image_analysis, re.IGNORECASE)
            for match in matches:
                value = int(match.group(1))
                if 0 <= value <= 252:  # Basic validation
                    individual_stats[stat] = value
                    break  # Take first valid match for this stat
    
    # If we found all 6 individual stats, create EV spread
    if len(individual_stats) == 6:
        ev_values = [
            individual_stats['hp'],
            individual_stats['attack'], 
            individual_stats['defense'],
            individual_stats['special_attack'],
            individual_stats['special_defense'],
            individual_stats['speed']
        ]
        spread_dict = _create_ev_spread_dict(ev_values, "individual_stats", str(individual_stats))
        if spread_dict:
            ev_spreads.append(spread_dict)
    
    # Remove duplicates (keep highest confidence)
    ev_spreads = _remove_duplicate_ev_spreads(ev_spreads)
    
    return ev_spreads


def _create_ev_spread_dict(ev_values: List[int], format_type: str, raw_match: str) -> Dict[str, Any]:
    """Create and validate EV spread dictionary with ultra-strict validation"""
    if len(ev_values) != 6:
        return None
    
    total = sum(ev_values)
    
    # ULTRA-STRICT validation to prevent AI generation
    if total > 508:  # Definitely not EVs
        return None
    
    if total == 0:  # All zeros - likely no data found
        return None
    
    # Check if all values are multiples of 4 (EV requirement)
    if not all(ev % 4 == 0 for ev in ev_values):
        return None
    
    # Check for reasonable EV patterns (no single stat > 252)
    if any(ev > 252 for ev in ev_values):
        return None
    
    # BALANCED ANTI-GENERATION: Allow legitimate competitive patterns while catching obvious AI generation
    non_zero_values = [ev for ev in ev_values if ev > 0]
    
    # Only reject if ALL of these suspicious conditions are met:
    suspicious_indicators = 0
    
    # Indicator 1: Perfect 508 total with only basic competitive values
    if total == 508 and all(ev in [0, 4, 252] for ev in ev_values):
        suspicious_indicators += 1
    
    # Indicator 2: Multiple identical non-zero values (very unusual in real spreads)
    if len(non_zero_values) >= 3 and all(ev == non_zero_values[0] for ev in non_zero_values):
        suspicious_indicators += 1
    
    # Indicator 3: Exactly 6 investment stats all at 252 (impossible due to EV limit)
    if ev_values.count(252) >= 3:  # More than 2 maxed stats is very unusual
        suspicious_indicators += 1
    
    # Only reject if multiple suspicious indicators (legitimate spreads can trigger 1)
    if suspicious_indicators >= 2:
        return None
    
    # Determine confidence level (balanced approach)
    confidence = "low"
    
    # High confidence: Good format + high investment
    if total >= 500 and format_type in ["slash_format", "japanese_format"]:
        confidence = "high"
    elif total == 508 and format_type in ["slash_format", "japanese_format"]:  # Perfect competitive total
        confidence = "high"
    
    # Medium confidence: Decent format + substantial investment
    elif total >= 400 and format_type in ["japanese_format", "calculated_stat_format", "slash_format"]:
        confidence = "medium"
    elif total >= 300 and format_type == "slash_format":  # Standard format is reliable
        confidence = "medium"
    
    # Bonus for realistic spreads (common competitive patterns)
    if total in [500, 504, 508] and ev_values.count(252) <= 2:  # Common totals with reasonable distribution
        if confidence == "medium":
            confidence = "high"
        elif confidence == "low":
            confidence = "medium"
    
    return {
        "hp": ev_values[0],
        "attack": ev_values[1],
        "defense": ev_values[2],
        "special_attack": ev_values[3],
        "special_defense": ev_values[4],
        "speed": ev_values[5],
        "total": total,
        "format": "/".join(map(str, ev_values)),
        "confidence": confidence,
        "format_type": format_type,
        "raw_match": raw_match[:100],  # Store first 100 chars of original match
        "is_valid": True,
        "validation_notes": f"Total: {total}, Non-zero stats: {len(non_zero_values)}, Format: {format_type}"
    }


def _remove_duplicate_ev_spreads(ev_spreads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate EV spreads, keeping the highest confidence ones"""
    unique_spreads = {}
    
    for spread in ev_spreads:
        # Use the actual EV values as key to identify duplicates
        key = (spread["hp"], spread["attack"], spread["defense"], 
               spread["special_attack"], spread["special_defense"], spread["speed"])
        
        if key not in unique_spreads:
            unique_spreads[key] = spread
        else:
            # Keep the one with higher confidence
            current_confidence = {"high": 3, "medium": 2, "low": 1}[spread["confidence"]]
            existing_confidence = {"high": 3, "medium": 2, "low": 1}[unique_spreads[key]["confidence"]]
            
            if current_confidence > existing_confidence:
                unique_spreads[key] = spread
    
    return list(unique_spreads.values())


def filter_vgc_images(images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter images for VGC relevance and return sorted by priority"""
    vgc_images = []
    
    for image in images:
        if is_potentially_vgc_image(image):
            vgc_images.append(image)
    
    # ULTRA-ENHANCED sorting by priority (note.com + team score + file size)
    vgc_images.sort(key=lambda x: (
        -15 if x.get("is_note_com_asset", False) else 0,  # Note.com assets highest priority
        -x.get("team_card_score", 0) * 2,  # Team card score (higher = better)
        -10 if x.get("is_likely_team_card", False) else 0,  # General team card indicator
        -x.get("file_size", 0) // 1000,  # File size in KB (larger = more detailed)
        x.get("url", "").count("/"),  # Fewer URL segments = simpler/cleaner URLs
    ))
    
    return vgc_images[:5]  # Return top 5 most relevant images