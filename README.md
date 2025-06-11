# 🧠 Pokémon VGC Japanese Article Summariser

This project provides a web interface for summarising Japanese Pokémon VGC articles into English using Google Gemini and LangChain. It extracts team details and Pokémon names from the article, helping competitive players quickly analyse meta-relevant content.

## 🔧 Features

- 🔗 Accepts a Japanese article URL
- 🧠 Uses Google Gemini via LangChain to summarise article content and translate it into English
- 🧪 Extracts Pokémon names using regex logic
- 💾 Caches summaries to avoid redundant processing and hitting Gemini API constantly
- 🗑️ Cache clearing feature available via sidebar

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A Google Gemini API key
- (Optional) Streamlit Community Auth setup if extending
- - Create a `.streamlit/secrets.toml` file with the following content:
  ```toml
  google_api_key = "your-google-api-key-here"

### Installation

```bash
git clone https://github.com/mss23/pokemon-jp-summariser.git
cd pokemon-jp-summariser
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run Summarise_Article.py
```

## 📁 Project Structure

```
.
.
├── .gitignore
├── requirements.txt
├── Summarise_Article.py
├── pokemon_jp_translator.ipynb
├── storage/
│   └── cache.json
├── pages/
│   └── Pokémon_Team_and...  # Additional Streamlit pages
├── .streamlit/
├── utils/
│   ├── config_loader.py
│   ├── llm_summary.py
│   └── __pycache__/

```

## 🧠 How It Works

1. User inputs a Japanese article URL
2. If summary exists in cache, it is shown immediately
3. Otherwise, Gemini processes the article to generate a summary and translates it into English.
4. Pokémon names are extracted using pattern-matching
5. Result is displayed and cached for future reuse

To Test this yourself try this Japanese Article link!
https://note.com/bright_ixora372/n/nd5515195c993

## 🛠️ Technologies

- [Streamlit](https://streamlit.io/)
- [Google Gemini (Generative AI)](https://ai.google.dev/)
- [LangChain](https://www.langchain.com/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Pillow](https://python-pillow.org/)

## ✅ TODO

- Improve Pokémon name detection using LLM parsing
- Add Login Functionality and Users With Login Have Translated Teams Saved 

## 📜 License

MIT License
