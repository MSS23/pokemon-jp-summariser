# summarise_article.py
import streamlit as st
import json
import os
import re
from utils.llm_summary import llm_summary

st.title("🧠 Pokémon VGC Japanese Article Summariser")
st.write("Paste the URL of a Japanese article you'd like summarised:")

# Initialise session state
if "summarising" not in st.session_state:
    st.session_state["summarising"] = False

# --- URL Input ---
url = st.text_input("Enter your URL:")
valid_url = url.strip().startswith("http")
summarise_button = st.button("Summarise my article!", disabled=not valid_url or st.session_state["summarising"])

# --- Cache setup ---
CACHE_PATH = "storage/cache.json"
os.makedirs("storage", exist_ok=True)

try:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)
    else:
        cache = {}
except json.JSONDecodeError:
    st.warning("⚠️ Cache file was corrupted or empty. Reinitialising it.")
    cache = {}

# --- Summarisation logic ---
if summarise_button:
    if not valid_url:
        st.error("❌ Please enter a valid URL starting with http or https.")
    else:
        st.session_state["summarising"] = True
        try:
            if url in cache:
                st.success("Loaded from cache ✅")
                st.write(cache[url]["summary"])
            else:
                with st.spinner("Summarising with Gemini... Please wait."):
                    summary = llm_summary(url)
                    if not isinstance(summary, str):
                        summary = str(summary)

                    # Extract Pokémon names
                    lines = summary.splitlines()
                    pokemon_names = []

                    # Method 1: Try 1. to 6. pattern
                    numbered = [
                        re.sub(r"^\d+\.\s+", "", line).strip()
                        for line in lines if re.match(r"^\d+\.\s+", line)
                    ]
                    if len(numbered) == 6:
                        pokemon_names = numbered

                    # Method 2: Name: entries
                    if not pokemon_names:
                        pokemon_names = [
                            line.replace("Name:", "").strip()
                            for line in lines if line.strip().startswith("Name:")
                        ]

                    cache[url] = {
                        "summary": summary,
                        "pokemon": pokemon_names
                    }

                    with open(CACHE_PATH, "w") as f:
                        json.dump(cache, f)

                    st.success("Summary completed!")
                    st.write(summary)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
        finally:
            st.session_state["summarising"] = False

# --- Optional: Clear cache ---
if st.sidebar.button("🗑️ Clear All Cached Summaries"):
    cache = {}
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f)
    st.success("Cache cleared.")

st.sidebar.markdown("---")
st.sidebar.info("🔎 Want to search or browse summaries?\nGo to the **Team Search** page.")
