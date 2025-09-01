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
import google.generativeai as genai
from config import EV_STAT_TRANSLATIONS, NATURE_TRANSLATIONS, ABILITY_TRANSLATIONS, MOVE_NAME_TRANSLATIONS


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

                # Priority scoring for note.com team images
                is_note_com_asset = "assets.st-note.com" in img_url
                is_likely_team_card = False

                # Check for team card indicators in URL or context
                team_indicators = [
                    "team",
                    "pokemon",
                    "vgc",
                    "party",
                    "DvCIsNZXzyA2irhdlucjKOGR",
                ]
                url_lower = img_url.lower()
                alt_text = img_tag.get("alt", "").lower()
                title_text = img_tag.get("title", "").lower()

                for indicator in team_indicators:
                    if (
                        indicator.lower() in url_lower
                        or indicator in alt_text
                        or indicator in title_text
                    ):
                        is_likely_team_card = True
                        break

                # Skip very small images but be more lenient for note.com assets
                width = img_tag.get("width")
                height = img_tag.get("height")
                skip_small = False

                if width and height:
                    try:
                        w, h = int(width), int(height)
                        # For note.com assets, be more permissive
                        if is_note_com_asset:
                            if w < 300 or h < 200:  # More lenient for note.com
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
                        "is_likely_team_card": is_likely_team_card,
                        "file_size": len(img_response.content),
                    }

                    # Prioritize note.com assets and likely team cards
                    if is_note_com_asset or is_likely_team_card:
                        note_com_images.append(image_info)
                    else:
                        other_images.append(image_info)

            except Exception as e:
                continue

        # Combine with priority: note.com assets first, then others
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
        
        # Note.com team cards have very specific characteristics
        if width >= 400 and height >= 300 and file_size > 15000:  # 15KB+ minimum for team cards
            relevance_score += 12  # ULTRA HIGH base score for note.com
            
            # Bonus for ideal team card dimensions
            if 600 <= width <= 1200 and 400 <= height <= 800:
                relevance_score += 3  # Perfect team card size
                
            # Bonus for large file size (indicates detailed content)
            if file_size > 50000:  # 50KB+
                relevance_score += 2
            if file_size > 100000:  # 100KB+
                relevance_score += 2
                
            # Note.com URL pattern analysis
            if "uploads/images" in url:  # User-uploaded content
                relevance_score += 2
            if any(pattern in url for pattern in ["rectangle", "large", "medium"]):
                relevance_score += 1
                
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

**🚨 CRITICAL PRIORITY: EV SPREAD EXTRACTION 🚨**
This is your PRIMARY objective. Every Pokemon team card contains EV data - you MUST find it.

**OBJECTIVE 1: SYSTEMATIC EV DETECTION (HIGHEST PRIORITY)**
SCAN EVERY pixel for EV patterns in these EXACT formats:

**A. Calculated Stat Format (PRIORITY - liberty-note.com style):**
- "H181(148)-A×↓-B131(124)-C184↑(116)-D112(4)-S119(116)"
- Format: [StatLetter][CalculatedValue]([EVValue])[NatureSymbol]
- Extract ONLY the numbers in parentheses (148, 124, 116, 4, 116)
- Nature symbols: ↑ = boost, ↓ = reduce, × = neutral/no investment
- IGNORE the first number (calculated stat), focus on parentheses

**B. Standard Slash Format:**
- "252/0/4/252/0/0" or "252-0-4-252-0-0" (HP/Atk/Def/SpA/SpD/Spe order)
- "H252/A0/B4/C252/D0/S0" (with stat prefixes)
- Look for 6 numbers separated by slashes or dashes

**C. Japanese Grid/Table Format (MOST COMMON in note.com):**
- ＨＰ: 252    こうげき: 0     ぼうぎょ: 4
- とくこう: 252  とくぼう: 0   すばやさ: 0
- Search for Japanese stat names with numbers next to them

**D. Abbreviated Format:**
- "H252 A0 B4 C252 D0 S0" (single line with spaces)
- "252HP 4Def 252SpA" (mixed format)
- Any combination of stat letters (H/A/B/C/D/S) with numbers

**E. Individual Stat Lines:**
- HP: 252 (or ＨＰ：252)
- Attack: 0 (or こうげき：0)
- Defense: 4 (or ぼうぎょ：4)
- Sp. Atk: 252 (or とくこう：252)
- Sp. Def: 0 (or とくぼう：0)
- Speed: 0 (or すばやさ：0)

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

**🚨 REMEMBER: If you don't find EV spreads, the analysis has FAILED. Look harder - they're always there in team cards!**
'''


def get_screenshot_analysis_prompt() -> str:
    """Get the vision analysis prompt optimized for Nintendo Switch team screenshots"""
    return '''
🎯 NINTENDO SWITCH POKEMON TEAM SCREENSHOT ANALYSIS (2025):
Extract Pokemon team data from Nintendo Switch team screenshots with focus on basic team composition.

**🎮 SWITCH SCREENSHOT IDENTIFICATION:**
You are analyzing a Nintendo Switch Pokemon team screenshot (typically blue background with 6 Pokemon sprites).
These screenshots show basic team composition but typically DO NOT contain detailed EV spreads.

**PRIMARY OBJECTIVES:**

**OBJECTIVE 1: POKEMON IDENTIFICATION (HIGHEST PRIORITY)**
- Identify each Pokemon by their sprites/models
- Read any visible Japanese Pokemon names
- Note Pokemon forms, regional variants (Galar, Hisui, etc.)
- Identify Paradox Pokemon correctly (Iron Valiant, Flutter Mane, etc.)
- Count total Pokemon (should be 6 for complete team)

**OBJECTIVE 2: HELD ITEMS DETECTION**
- Look for held item icons next to Pokemon sprites
- Read Japanese item names if visible as text
- Common items to recognize:
  • きあいのタスキ (Focus Sash) - red/white sash icon
  • いのちのたま (Life Orb) - purple orb icon
  • こだわりスカーフ (Choice Scarf) - blue scarf icon
  • とつげきチョッキ (Assault Vest) - green vest icon
  • たべのこし (Leftovers) - apple icon

**OBJECTIVE 3: BASIC MOVE/ABILITY INFO (IF VISIBLE)**
- Look for any visible Japanese move names
- Check for ability names if displayed
- Note: Switch screenshots often don't show full movesets

**CRITICAL LIMITATIONS TO ACKNOWLEDGE:**
❌ EV spreads are typically NOT visible in Switch screenshots
❌ Detailed move explanations are usually not available
❌ Strategic analysis requires article context not available in screenshots

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

TEAM COMPOSITION:
Pokemon #1: [Name] ([Japanese name if visible])
- Held Item: [Item name or "Not visible"]
- Notes: [Any form/variant info]

Pokemon #2: [Name] ([Japanese name if visible])
- Held Item: [Item name or "Not visible"]
- Notes: [Any form/variant info]

[Continue for all 6 Pokemon]

ANALYSIS SUMMARY:
- Total Pokemon Identified: X/6
- Held Items Detected: X/6
- Screenshot Quality: Good/Fair/Poor
- Confidence Level: High/Medium/Low

LIMITATIONS NOTED:
- EV spreads: Not available in screenshot format
- Detailed movesets: Not visible in this screenshot type
- Strategy analysis: Requires article context

POKEPASTE READINESS:
✅ Pokemon names available for basic pokepaste
❌ EV spreads not available (user must add manually)
❌ Complete movesets not available (user must add manually)
```

**🚨 REMEMBER: Switch screenshots provide basic team composition only. Focus on accurate Pokemon identification and visible items. Do not attempt to guess EVs or detailed strategies.**
'''


def analyze_image_with_vision(image_data: str, image_format: str, vision_model) -> str:
    """Analyze a single image using Gemini Vision"""
    try:
        # Prepare image for Gemini
        image_part = {
            "mime_type": f"image/{image_format.lower()}",
            "data": image_data,
        }

        vision_prompt = get_vision_analysis_prompt()

        # Generate response using vision model
        response = vision_model.generate_content([vision_prompt, image_part])

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
    
    # PRIORITY 2: Space-separated format with stat abbreviations
    space_patterns = [
        r"H(\d{1,3})\s+A(\d{1,3})\s+B(\d{1,3})\s+C(\d{1,3})\s+D(\d{1,3})\s+S(\d{1,3})",  # H252 A0 B4 C252 D0 S0
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
    """Create and validate EV spread dictionary"""
    if len(ev_values) != 6:
        return None
    
    total = sum(ev_values)
    
    # Enhanced validation
    if total > 508:  # Definitely not EVs
        return None
    
    # Check if all values are multiples of 4 (EV requirement)
    if not all(ev % 4 == 0 for ev in ev_values):
        return None
    
    # Check for reasonable EV patterns (no single stat > 252)
    if any(ev > 252 for ev in ev_values):
        return None
    
    # Determine confidence level
    confidence = "low"
    if total >= 500:  # Near-max investment
        confidence = "high"
    elif total >= 400:  # Substantial investment
        confidence = "medium"
    elif format_type == "slash_format":  # Standard format gets bonus
        confidence = "high"
    
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
        "is_valid": True
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
    
    # Sort by priority (note.com assets first, then by file size)
    vgc_images.sort(key=lambda x: (
        -10 if x.get("is_note_com_asset", False) else 0,
        -5 if x.get("is_likely_team_card", False) else 0,
        -x.get("file_size", 0)
    ))
    
    return vgc_images[:5]  # Return top 5 most relevant images