# 🧠 Pokémon VGC Japanese Article Summariser

This project provides a web interface for summarising Japanese Pokémon VGC articles into English using Google Gemini and LangChain. It extracts team details and Pokémon names from the article, helping competitive players quickly analyse meta-relevant conten.

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
- (Optional but preferred) uv

### Installation

```bash
git clone https://github.com/mss23/pokemon-jp-summariser.git
cd pokemon-jp-summariser
```

If you have uv installed use:

```
uv install -r requirements.txt
```

Otherwise run

```bash
pip install -r requirements.txt
```

In a virtual environment.

### Secrets Setup

The application requires you to save your Google Gemini API key in a
`.streamlit/secrets.toml` file. Create the file with the following content:

```toml
google_api_key = <YOUR_SECRET_HERE>
```

### Run the App

```bash
uv run streamlit run Summarise_Article.py
```

## 📁 Project Structure

```
.
├── .gitignore
├── requirements.txt
├── Summarise_Article.py
├── pokemon_jp_translator.ipynb
├── storage/
│   └── cache.json
├── pages/
│   └── Pokémon_Team_and...
├── .streamlit/
├── utils/
│   ├── config_loader.py
│   ├── llm_summary.py
│   └── __pycache__/
```

## 🧠 How It Works

1. User inputs a Japanese article URL
2. If summary exists in cache, it is shown immediately
3. Otherwise, Gemini processes the article to generate a summary and translates it into English
4. Pokémon names are extracted using pattern-matching
5. Result is displayed and cached for future reuse

**To test it yourself, try this Japanese article link:**  
[https://note.com/bright_ixora372/n/nd5515195c993](https://note.com/bright_ixora372/n/nd5515195c993)

## ⚠️ Known Limitations & Translation Nuances

This project leverages **Google Gemini 2.0 Flash** and **LangChain** to translate Japanese VGC articles into English. However, due to the nature of language translation—especially when involving game-specific terminology—some inaccuracies can occur.

These issues include:

- **Move name discrepancies**: For example, Calyrex-Ice’s signature move *Glacial Lance* is occasionally translated as *Blizzard Lance*.
- **Incorrect ability/move associations**: Kyogre’s *Drizzle* ability has, in some instances, led to the incorrect appearance of the word "Rain" as a move rather than as a weather effect.

These are known quirks stemming from translation layers, context ambiguity, and input quality. As Gemini and other LLMs continue to evolve, we expect these issues to reduce over time.

Despite these challenges, this project serves as a demonstration of:

- Prompt engineering to contextualise Pokémon-specific content
- Practical use of the **Gemini SDK** and **LangChain** for multilingual content summarisation
- Early-stage experimentation with translation reliability in the context of competitive Pokémon

## 🛠️ Technologies

- [Streamlit](https://streamlit.io/)
- [Google Gemini (Generative AI)](https://ai.google.dev/)
- [LangChain](https://www.langchain.com/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

## ✅ TODO

- Improve Pokémon name detection using LLM parsing
- Add Login Functionality and Users With Login Have Translated Teams Saved 

## 📜 License

MIT License
