# pages/2_Pokemon_Team_and_Summary_Search.py
import streamlit as st
import json
import os
import re

st.title("🔍 Pokémon Team Search & Summary Table")

CACHE_PATH = "storage/cache.json"

# --- Disable input if summarisation is ongoing ---
if st.session_state.get("summarising"):
    st.warning("🔄 Summarising in progress. Please wait before searching again.")
    st.stop()

# Load cache
try:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)
    else:
        cache = {}
except json.JSONDecodeError:
    st.warning("⚠️ Cache file was corrupted or empty.")
    cache = {}

if not cache:
    st.info("No summaries found. Please add some on the 'Summarise Article' page.")
    st.stop()

# --- Search bar ---
search_term = st.text_input("Search for a Pokémon name (partial match allowed):").lower().strip()

# --- Build table data ---
table_data = []

for cached_url, result in cache.items():
    summary = result.get("summary", "")
    lines = summary.splitlines()

    # Extract title
    title_line = next((line for line in lines if line.startswith("TITLE:")), None)
    title = title_line.replace("TITLE:", "").strip() if title_line else "Untitled"

    # Extract Pokémon names from lines like "1. Calyrex Ice Rider"
    pokemon_names = [
        re.sub(r"^\d+\.\s+(.*)", r"\1", line).strip()
        for line in lines if re.match(r"^\d+\.\s+", line)
    ]

    # Fallback: Try extracting from TITLE if 1.-6. not found
    if len(pokemon_names) < 6 and "[" in title and "]" in title:
        match = re.search(r"\[(.*?)\]", title)
        if match:
            pokemon_names = [p.strip() for p in match.group(1).split(",")]

    # Filter by Pokémon if search term is present
    if search_term:
        if not any(search_term in p.lower() for p in pokemon_names):
            continue

    table_data.append({
        "Title": title,
        "URL": f"[Link]({cached_url})",
        "Pokémon": ", ".join(pokemon_names) if pokemon_names else "Not found",
        "Team Summary": summary
    })

# --- Show results ---
if table_data:
    st.dataframe(table_data, use_container_width=True)
else:
    if search_term:
        st.warning("No teams found matching your search.")
    else:
        st.info("Enter a Pokémon name above to begin searching.")
