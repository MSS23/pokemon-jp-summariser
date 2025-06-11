import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from streamlit import secrets
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

prompt_template = """
Act as a Pokémon VGC (Video Game Championships) expert analysing teams for Pokémon Scarlet and Violet's current competitive format.

**Current Format: Regulation I**
- Two restricted Pokémon are allowed per team.
- You may refer to the restricted Pokémon list below to assist with translations and identifications from Japanese text or image content.

**Restricted Pokémon Reference List:**
{restrict_poke}

**Your Task:**

You are provided with a combination of article text and team images. These images may include screenshots showing Pokémon names, abilities, held items, moves, EV spreads, or stat indicators. Use both the text and image content to extract accurate team information.

Your response must be strictly based on the visible and written content. If anything is unclear, partial, or missing, mark it as such. **Do not make assumptions.**

**Use the images included in the prompt to cross-reference and validate information from the article text. If any details appear more clearly in the images, prioritise that content and ensure it is reflected accurately in your output.**

---

**Key Image Interpretation Rule:**
Some images include a row of stat labels and numbers like:

H A B C D S followed by 252 0 100 0 156 0

This mapping represents the Pokémon’s EV spread:
- H = HP
- A = Attack
- B = Defence
- C = Special Attack
- D = Special Defence
- S = Speed

If you see this layout in the image, interpret the values accordingly and include the EVs in your breakdown. If the layout is not present or values are unclear, write: **“EVs not specified in the article or image.”**

---

1. **Extract the title** of the article or blog post.
   - If there is a clear blog or article title (e.g. a headline at the top), write it as:

     TITLE: [insert title here]

   - If there is no title or it's unclear, write: TITLE: Not specified

2. **Translate** all non-English text (e.g. Pokémon names, moves, or EV labels in Japanese) into English, using the restricted Pokémon list where helpful.

3. **Analyse** the team strictly based on the provided content (text and images):
   - List exactly **six Pokémon**.
   - If any Pokémon is missing or cannot be identified from the source, write: **“Pokémon not identifiable in the article or image.”**
   - Only include reasoning, synergy, or strategy if explicitly described.
   - Avoid all speculation or inference.

4. **Individual Pokémon Breakdown** (for each of the six slots):
   - Name
   - Ability (if mentioned)
   - Held Item (if mentioned)
   - Moves (if available)
   - EV Spread (if available, based on either text or image): Please ensure you use the mapping specified above (i.e HP instead of H)
   - Nature (if mentioned or implied via stat indicators)
   - **EV Explanation**: If the article or image provides reasoning for the EV spread, include that reasoning exactly. Otherwise, write “Not specified in the article or image.”

5. **Conclusion Summary**:
   - Team strengths
   - Notable weaknesses or counters
   - Meta relevance and effectiveness (if discussed)

---

**Strict Instructions:**
- Do **not** infer or assume anything that is not clearly visible or mentioned.
- All missing data must be marked with: **“Not specified in the article or image.”**
- Use only **standard ASCII characters**. Do not include Japanese script, accented characters, or emoji.
- Write in clear, formal **UK English** only.

**Input Content:**
#{text}#

**Note:** Supplementary team images will follow. Use them where available to support the analysis.
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


def fetch_article_text_and_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract paragraph text (multilingual safe)
    paragraphs = [p.get_text(separator="", strip=True) for p in soup.find_all("p")]
    full_text = "\n".join(paragraphs)

    # Optional: clean up invisible characters and excessive spacing
    clean_text = re.sub(r"[\u200b\xa0]", " ", full_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    # Extract image URLs
    image_tags = soup.find_all("img")
    image_urls = []
    for img in image_tags:
        src = img.get("src")
        if src:
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                base_url = url.split("//")[0] + "//" + url.split("/")[2]
                src = base_url + src
            image_urls.append(src)

    return clean_text, image_urls


def wrap_prompt_and_image_urls(prompt, image_urls):
    content = [{"type": "text", "text": prompt}]
    for url in image_urls:
        if "png" in url:  # Same filter logic
            content.append({
                "type": "image_url",
                "image_url": {"url": url}
            })
    return content


def llm_summary(url):
    article_text, image_urls = fetch_article_text_and_images(url)
    
    # Fill in the prompt
    prompt = prompt_template.format(restrict_poke=restricted_poke, text=article_text)


    chat = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=secrets["google_api_key"],
        temperature=0.0
    )

    # Usage
    content_parts = wrap_prompt_and_image_urls(prompt, image_urls)
    message = HumanMessage(content=content_parts)
    #print(message)
        
    response = chat.invoke([message])
    return str(response.content)  # Or `response.content` if already a string

