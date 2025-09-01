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
    """Enhanced VGC image detection with 2025 improvements"""

    # Enhanced scoring system for better accuracy
    relevance_score = 0

    # Priority 1: note.com assets (highest priority)
    if image_info.get("is_note_com_asset", False):
        width, height = image_info.get("size", (0, 0))
        file_size = image_info.get("file_size", 0)
        if width > 300 and height > 200 and file_size > 10000:  # 10KB+
            relevance_score += 8  # Very high score for note.com assets

    # Priority 2: Image dimensions analysis
    width, height = image_info.get("size", (0, 0))
    if width > 600 and height > 400:  # Team card likely dimensions
        relevance_score += 3
    elif width > 800 and height > 600:  # Screenshot dimensions
        relevance_score += 4
    elif width > 1200:  # Wide format (rental team screenshots)
        relevance_score += 5

    # Priority 3: File size indicators
    file_size = image_info.get("file_size", 0)
    if file_size > 50000:  # Large images likely contain detailed data
        relevance_score += 2
    elif file_size > 100000:  # Very large images
        relevance_score += 3

    # Priority 4: Already flagged as likely team card
    if image_info.get("is_likely_team_card", False):
        relevance_score += 6

    # Priority 5: Text content analysis (enhanced keywords)
    text_content = (
        image_info.get("alt_text", "")
        + " "
        + image_info.get("title", "")
        + " "
        + image_info.get("url", "")
    ).lower()

    enhanced_vgc_keywords = [
        # English keywords
        "pokemon",
        "vgc",
        "team",
        "ev",
        "iv",
        "stats",
        "competitive",
        "doubles",
        "battle",
        "rental",
        "pokepaste",
        "regulation",
        "tournament",
        "worlds",
        "regional",
        "championship",
        "movesets",
        "nature",
        "ability",
        "item",
        "tera",
        "sprite",
        "showdown",
        # Japanese keywords
        "ポケモン",
        "チーム",
        "ダブル",
        "バトル",
        "大会",
        "構築",
        "調整",
        "技構成",
        "持ち物",
        "性格",
        "特性",
        "テラス",
        "ランクマ",
        "レンタル",
        "努力値",
        "個体値",
        # Common Pokemon names that indicate team content
        "ガブリアス",
        "ガオガエン",
        "ウインディ",
        "モロバレル",
        "エルフーン",
        "ランドロス",
        "カイリュー",
        "ハリテヤマ",
        "クレッフィ",
        "トリトドン",
        "ニンフィア",
        "リザードン",
    ]

    # Enhanced keyword scoring
    high_value_keywords = [
        "pokemon",
        "ポケモン",
        "vgc",
        "team",
        "チーム",
        "rental",
        "レンタル",
    ]
    medium_value_keywords = [
        "ev",
        "努力値",
        "battle",
        "バトル",
        "regulation",
        "tournament",
    ]

    for keyword in enhanced_vgc_keywords:
        if keyword in text_content:
            if keyword in high_value_keywords:
                relevance_score += 3
            elif keyword in medium_value_keywords:
                relevance_score += 2
            else:
                relevance_score += 1

    # Priority 6: URL-based detection
    src_url = image_info.get("url", "").lower()
    if any(
        domain in src_url
        for domain in ["note.com", "assets.st-note.com", "pbs.twimg.com"]
    ):
        relevance_score += 2

    # Priority 7: File format preferences
    if src_url.endswith((".png", ".jpg", ".jpeg")):
        relevance_score += 1

    # Return True if score meets threshold (adjustable based on testing)
    return relevance_score >= 5  # Threshold for "potentially VGC-relevant"


def encode_image_for_gemini(
    image_data: str, format_type: str = "jpeg"
) -> Dict[str, Any]:
    """Prepare image data for Gemini Vision API"""
    return {"mime_type": f"image/{format_type.lower()}", "data": image_data}


def get_vision_analysis_prompt() -> str:
    """Get the comprehensive vision analysis prompt"""
    return '''
🎯 ENHANCED 2025 POKEMON VGC IMAGE ANALYSIS MISSION:
Perform comprehensive Pokemon team identification and data extraction with confidence scoring.

**MULTI-OBJECTIVE ANALYSIS (Execute ALL):**

**OBJECTIVE 1: POKEMON SPRITE IDENTIFICATION & VALIDATION**
- Identify each Pokemon by visual appearance (sprites, artwork, models)
- Cross-reference visual identification with any text labels
- Note Pokemon forms, regional variants, shiny status if visible
- Rate identification confidence for each Pokemon (High/Medium/Low)
- Flag any Pokemon that are visually ambiguous or unclear

**OBJECTIVE 2: POKEMON NAME VALIDATION**  
- Look for Japanese Pokemon names in text labels
- Cross-reference with comprehensive name database
- Validate sprite matches expected Pokemon name
- Flag any mismatches between visual and textual identification

**OBJECTIVE 3: EV SPREAD DETECTION (Enhanced)**
SCAN METHODICALLY for numerical EV patterns in ALL these formats:
- Standard: "252/0/4/252/0/0" or "252-0-4-252-0-0" (HP/Atk/Def/SpA/SpD/Spe)
- Japanese: "H252 A0 B4 C252 D0 S0" or "ＨＰ252 こうげき0 ぼうぎょ4..."
- Grid layout: Numbers in rows/columns next to stat abbreviations
- Individual entries: "HP: 252", "Attack: 0", "Defense: 4"...
- Compact: "252HP/4Def/252SpA" or "H252/B4/C252"
- Note.com style: May use Japanese stat names with numbers

**EV VALIDATION RULES:**
- Total EVs must be ≤508 (if >508, these are likely actual stats, not EVs)
- Valid individual values: 0, 4, 12, 20, 28, 36, 44, 52, 60, 68, 76, 84, 92, 100, 108, 116, 124, 132, 140, 148, 156, 164, 172, 180, 188, 196, 204, 212, 220, 228, 236, 244, 252
- Common patterns: 252/252/4, 252/0/0/252/4/0, 252/0/4/0/0/252

**JAPANESE STAT TRANSLATIONS:**
- ＨＰ/HP/H = HP
- こうげき/攻撃/A = Attack  
- ぼうぎょ/防御/B = Defense
- とくこう/特攻/C = Special Attack
- とくぼう/特防/D = Special Defense
- すばやさ/素早/S = Speed

**TEAM LAYOUT PARSING (Note.com Format):**
1. Pokemon Name/Sprite (top of each card)
2. Pokemon Types (colored type indicators)
3. Ability (below name, before moves)
4. Held Item (icon/text near sprite)
5. Nature (stat arrows: ↑=boost, ↓=reduction)
6. MOVES (exactly 4, listed vertically)
7. **EV SPREAD** (most critical - look for number patterns)
8. Tera Type (if shown)

**EV EXTRACTION PRIORITY AREAS:**
1. Dedicated EV section/table within each Pokemon card
2. Numbers next to stat abbreviations (H/A/B/C/D/S)
3. Small text below Pokemon data
4. Side panels or secondary info areas
5. Overlaid text on Pokemon cards
6. Separate EV summary section

**NATURE DETECTION - STAT ARROW ANALYSIS:**
Look for colored arrows next to stat abbreviations:
- RED/Pink arrows (↑) = stat INCREASE (+10%)
- BLUE/Navy arrows (↓) = stat DECREASE (-10%)
- Example: Blue "A" + Red "S" = Timid nature (-Attack, +Speed)

**ITEM TRANSLATIONS (Japanese ↔ English):**
- しんぴのしずく = Mystic Water, たべのこし = Leftovers
- きあいのタスキ = Focus Sash, いのちのたま = Life Orb
- こだわりハチマキ = Choice Band, こだわりメガネ = Choice Specs
- こだわりスカーフ = Choice Scarf, とつげきチョッキ = Assault Vest
- オボンのみ = Sitrus Berry, ラムのみ = Lum Berry

**ENHANCED OUTPUT FORMAT (2025 STANDARDS):**
Provide detailed analysis for each Pokemon found:

```
=== POKEMON ANALYSIS SUMMARY ===
Total Pokemon Identified: X
Data Quality Score: X/10
Overall Confidence: High/Medium/Low

TEAM COMPOSITION:
[List each Pokemon with all available data]

EV SPREADS DETECTED:
[List EV patterns found with validation status]

ADDITIONAL NOTES:
[Any important observations or data quality issues]
```

Please analyze this image thoroughly and provide comprehensive Pokemon team data extraction.
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
    """Extract EV spread data from image analysis text"""
    ev_spreads = []
    
    # Look for various EV patterns in the analysis
    ev_patterns = [
        r"(\d{1,3})[\/\-](\d{1,3})[\/\-](\d{1,3})[\/\-](\d{1,3})[\/\-](\d{1,3})[\/\-](\d{1,3})",  # 252/0/4/252/0/0
        r"H(\d{1,3})\s*A(\d{1,3})\s*B(\d{1,3})\s*C(\d{1,3})\s*D(\d{1,3})\s*S(\d{1,3})",  # H252 A0 B4...
        r"HP:\s*(\d{1,3}).*?Attack:\s*(\d{1,3}).*?Defense:\s*(\d{1,3}).*?Sp\.?\s*Attack:\s*(\d{1,3}).*?Sp\.?\s*Defense:\s*(\d{1,3}).*?Speed:\s*(\d{1,3})",  # HP: 252, Attack: 0...
    ]
    
    for pattern in ev_patterns:
        matches = re.finditer(pattern, image_analysis, re.IGNORECASE | re.DOTALL)
        for match in matches:
            ev_values = [int(x) for x in match.groups()]
            if len(ev_values) == 6:
                total = sum(ev_values)
                # Validate EV spread
                if total <= 508 and all(ev % 4 == 0 for ev in ev_values):
                    spread_dict = {
                        "hp": ev_values[0],
                        "attack": ev_values[1],
                        "defense": ev_values[2],
                        "special_attack": ev_values[3],
                        "special_defense": ev_values[4],
                        "speed": ev_values[5],
                        "total": total,
                        "format": "/".join(map(str, ev_values)),
                        "confidence": "high" if total in [508, 504, 500, 496] else "medium"
                    }
                    ev_spreads.append(spread_dict)
    
    return ev_spreads


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