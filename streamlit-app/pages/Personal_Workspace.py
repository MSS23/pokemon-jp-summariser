# -*- coding: utf-8 -*-
import streamlit as st
from utils.workspace import (
    get_history,
    get_downloads,
    get_reading_list,
    add_to_reading_list,
    remove_from_reading_list,
    clear_reading_list,
    list_summaries,
    get_summary,
    add_to_collection,
    list_collections,
    export_workspace,
    set_reading_list_tags,
)
from utils.permalinks import compute_team_fingerprint, build_permalink
import io
import json

st.set_page_config(page_title="Personal Workspace", page_icon="🗂️", layout="wide")
st.markdown(
    """
    <style>
    /* Make workspace content span wider for a clean table look */
    .block-container { max-width: 1600px; padding-left: 24px; padding-right: 24px; }
    .ws-card { padding: 14px 16px; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 12px; background: #ffffff; box-shadow: 0 1px 2px rgba(16,24,40,0.04); }
    .ws-card:hover { box-shadow: 0 2px 8px rgba(16,24,40,0.08); }
    .ws-team-badges span { margin-right: 6px; }
    .ws-title { font-weight: 700; font-size: 1rem; color: #0f172a; margin-bottom: 6px; }
    .ws-url { color: #64748b; font-size: 0.85rem; margin-top: 2px; }
    .ws-actions .stButton>button, .ws-actions .stDownloadButton>button { height: 36px; width: 36px; padding: 0; border-radius: 10px; }
    .ws-actions .stTextInput>div>div>input { height: 36px; }
    .ws-section-title { font-size: 1.1rem; font-weight: 700; color: #334155; margin: 8px 0 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🗂️ Personal Workspace")
st.caption("Your history, downloads, reading list, and collections")

# Search bar for workspace
q = st.text_input("Search history (title, URL, Pokémon, tournament)", key="ws_search")

# Sorting & filtering controls
sort_by = st.selectbox("Sort by", ["Most recent", "Most viewed", "Alphabetical"], index=0)
collections = list_collections()
col_filter = st.selectbox("Filter by collection (optional)", ["All"] + list(collections.keys()))
tournament_filter = st.text_input("Filter by tournament keyword", key="ws_tourn")
pokemon_filter = st.text_input("Filter by Pokémon in team (comma separated)", key="ws_poke")

col1, col2 = st.columns(2)
with col1:
    st.subheader("History & Downloads")
    hist = get_history(200)
    dls = get_downloads(200)
    summaries = {s.get("summary_id"): s for s in list_summaries()}

    # Build enriched entries
    entries = []
    for h in hist:
        meta = summaries.get(h.get("summary_id"), {})
        entries.append({
            "summary_id": h.get("summary_id"),
            "title": meta.get("title") or h.get("title"),
            "url": h.get("url"),
            "team": meta.get("team_names", []),
            "views": meta.get("view_count", 1),
            "tournament": meta.get("tournament", ""),
            "ts": h.get("timestamp"),
        })

    # Filter
    if q:
        ql = q.lower()
        entries = [e for e in entries if ql in (e["title"] or "").lower() or ql in (e["url"] or "").lower() or any(ql in (p or "").lower() for p in e.get("team", []))]
    if tournament_filter:
        tl = tournament_filter.lower()
        entries = [e for e in entries if tl in (e.get("tournament") or "").lower()]
    if pokemon_filter:
        wants = [x.strip().lower() for x in pokemon_filter.split(',') if x.strip()]
        if wants:
            entries = [e for e in entries if any(w in [p.lower() for p in e.get("team",[])] for w in wants)]
    if col_filter != "All":
        ids = set(collections.get(col_filter, []))
        entries = [e for e in entries if e.get("summary_id") in ids]

    # Sort
    if sort_by == "Most recent":
        entries.sort(key=lambda e: e.get("ts",""), reverse=True)
    elif sort_by == "Most viewed":
        entries.sort(key=lambda e: e.get("views",0), reverse=True)
    elif sort_by == "Alphabetical":
        entries.sort(key=lambda e: (e.get("title") or "").lower())

    # Render with quick actions and indicators
    with st.expander("Recent Views", expanded=True):
        if not entries:
            st.write("No matching entries.")
        else:
            import re
            for idx, e in enumerate(entries[:50]):
                raw_key = f"{e.get('summary_id','')}_{e.get('ts','')}_{idx}"
                unique = re.sub(r"\W+", "", raw_key) or f"row{idx}"
                # Card container
                st.markdown("<div class='ws-card'>", unsafe_allow_html=True)
                top_l, top_r = st.columns([10,3])
                with top_l:
                    team_badges = "".join([f"<span style='padding:2px 6px;border:1px solid #e2e8f0;border-radius:10px;margin-right:6px;font-size:0.8rem;'>{p}</span>" for p in e.get("team", [])[:8]])
                    trophy = "🏆 " if e.get("tournament") else ""
                    st.markdown(f"<div class='ws-title'>{trophy}{e.get('title')}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='ws-team-badges'>{team_badges}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='ws-url'>{e.get('url')}</div>", unsafe_allow_html=True)
                with top_r:
                    with st.container():
                        st.markdown("<div class='ws-section-title'>Quick Actions</div>", unsafe_allow_html=True)
                        act1, act2, act3, act4, act5 = st.columns([1,1,2,1,1])
                        with act1:
                            if st.button("📄", help="View Summary", key=f"view_{unique}"):
                                st.session_state["prefill_url"] = e.get("url")
                                st.switch_page("Summarise_Article.py")
                        with act2:
                            fp = compute_team_fingerprint([{"name": p} for p in e.get("team", [])], e.get("title"), e.get("url"))
                            pl = build_permalink("", fp)
                            st.download_button("⬇", pl, file_name="team_link.txt", help="Download Showdown/CSV link placeholder", key=f"dl_{unique}")
                        with act3:
                            from utils.workspace import list_collections
                            col_names = list(list_collections().keys())
                            sel = st.selectbox("Collection", options=["Default"] + col_names, index=0, key=f"colsel_{unique}", label_visibility="collapsed")
                            if st.button("⭐", help="Save to Collection", key=f"save_{unique}"):
                                add_to_collection(sel or "Default", e['summary_id'])
                                st.toast(f"Saved to collection {sel or 'Default'}")
                        with act4:
                            if st.button("🔍", help="Open in Compare Teams mode", key=f"cmp_{unique}"):
                                st.info("Compare mode coming soon.")
                        with act5:
                            st.write("")
                st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Recent Downloads", expanded=False):
        if not dls:
            st.write("No downloads yet.")
        else:
            for d in dls[:50]:
                s = summaries.get(d.get("summary_id")) if d.get("summary_id") else None
                label = f"{(s or {}).get('title','Team')} — {d.get('file_type','').upper()} at {d.get('timestamp','')}"
                st.markdown(f"- {label}")

with col2:
    st.subheader("Reading List")
    new_url = st.text_input("Add article URL", key="ws_add_url")
    add_btn = st.button("Add to Reading List", disabled=not bool(new_url))
    if add_btn:
        add_to_reading_list(new_url)
        st.success("Added to reading list.")
        st.session_state["ws_add_url"] = ""
        st.experimental_rerun()

    rl = get_reading_list()
    if rl:
        for item in rl:
            c1, c2, c3 = st.columns([5,2,1])
            with c1:
                tag_val = st.text_input("Tags (comma separated)", value=", ".join(item.get("tags", [])), key=f"tags_{item.get('url')}" )
                st.write(f"{item.get('url')} — {item.get('status','queued')}")
                if st.button("Save Tags", key=f"save_tags_{item.get('url')}"):
                    set_reading_list_tags(item.get('url'), [t.strip() for t in tag_val.split(',') if t.strip()])
                    st.success("Tags saved")
            with c2:
                if st.button("Prefill & Open", key=f"open_{item.get('url')}"):
                    st.session_state["prefill_url"] = item.get('url')
                    st.switch_page("Summarise_Article.py")
            with c3:
                if st.button("✖", key=f"rm_{item.get('url')}"):
                    remove_from_reading_list(item.get('url'))
                    st.experimental_rerun()
        st.divider()
        if st.button("▶️ Batch Translate (Manual)"):
            st.info("Open each link with Prefill & Open. Automated batch can be added via a headless worker.")
        if st.button("🧹 Clear Reading List"):
            clear_reading_list()
            st.experimental_rerun()
    else:
        st.info("Your reading list is empty.")

st.divider()
st.subheader("Export Workspace Data")
colj, colc = st.columns(2)
with colj:
    data_json = export_workspace("json")
    st.download_button("Export JSON", data_json, file_name="workspace.json", mime="application/json")
with colc:
    data_csv = export_workspace("csv")
    st.download_button("Export CSV", data_csv, file_name="workspace.csv", mime="text/csv")



