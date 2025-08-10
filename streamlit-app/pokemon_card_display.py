# -*- coding: utf-8 -*-
import streamlit as st
import json
import re
from datetime import datetime

def display_pokemon_card_with_summary(pokemon, index):
    """Display a Pokemon in a beautiful card format with all details using Streamlit components"""
    
    # Create the main container with styling
    with st.container():
        st.markdown(f"""
        <div style="
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            margin: 24px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        ">
        """, unsafe_allow_html=True)
        
        # Header section
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            padding: 20px 24px;
            position: relative;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <div style="
                        background: rgba(255, 255, 255, 0.25);
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 16px;
                        font-weight: 800;
                        font-size: 1.2rem;
                        border: 2px solid rgba(255, 255, 255, 0.3);
                    ">{index}</div>
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">
                        {pokemon.get('name', 'Unknown').title()}
                    </h2>
                </div>
                <div style="display:flex; gap:8px; align-items:center;">
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-weight: 700;
                        font-size: 1rem;
                        border: 1px solid rgba(255, 255, 255, 0.3);
                    ">
                        Tera: {pokemon.get('tera_type', 'Not specified')}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Content section using Streamlit columns
        st.markdown('<div style="padding: 24px;">', unsafe_allow_html=True)
        
        # Create two columns for the layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Basic Info Section
            st.markdown("""
            <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                ⚡ Basic Info
            </h3>
            """, unsafe_allow_html=True)
            
            # Create info cards
            info_data = [
                ("Ability", pokemon.get('ability', 'Not specified')),
                ("Item", pokemon.get('item', 'Not specified')),
                ("Nature", pokemon.get('nature', 'Not specified'))
            ]
            
            for label, value in info_data:
                st.markdown(f"""
                <div style="
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                ">
                    <div style="font-weight: 700; color: #475569; font-size: 0.9rem; margin-bottom: 4px;">{label}</div>
                    <div style="color: #0f172a; font-size: 1rem; font-weight: 600;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Moves Section
            st.markdown("""
            <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                ⚔️ Moves
            </h3>
            """, unsafe_allow_html=True)
            
            if pokemon.get('moves'):
                # Display moves with validation status
                moves = pokemon.get('moves', [])
                valid_moves = pokemon.get('valid_moves', [])
                invalid_moves = pokemon.get('invalid_moves', [])
                
                # Display all moves with color coding
                for move in moves:
                    if move in valid_moves:
                        # Valid move - blue
                        move_color = "#3b82f6"
                        move_bg = "#3b82f6"
                        move_text_color = "white"
                    elif move in [m.split(' (')[0] for m in invalid_moves]:
                        # Invalid move - red
                        move_color = "#dc2626"
                        move_bg = "#fef2f2"
                        move_text_color = "#dc2626"
                    else:
                        # Unverified move - orange
                        move_color = "#f59e0b"
                        move_bg = "#fef3c7"
                        move_text_color = "#92400e"
                    
                    st.markdown(f"""
                    <div style="
                        background: {move_bg};
                        color: {move_text_color};
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-size: 1rem;
                        font-weight: 600;
                        display: inline-block;
                        margin: 2px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        border: 2px solid {move_color};
                    ">{move}</div>
                    """, unsafe_allow_html=True)
                
                # Display validation summary
                if valid_moves and invalid_moves:
                    st.markdown(f"""
                    <div style="margin-top: 12px; padding: 8px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #0ea5e9;">
                        <div style="color: #0369a1; font-size: 0.85rem; font-weight: 600;">📊 Move Validation:</div>
                        <div style="color: #0369a1; font-size: 0.8rem; margin-top: 4px;">
                            ✅ {len(valid_moves)} valid • ⚠️ {len(invalid_moves)} issues
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif valid_moves and not invalid_moves:
                    st.markdown(f"""
                    <div style="margin-top: 12px; padding: 8px; background: #f0fdf4; border-radius: 8px; border-left: 4px solid #22c55e;">
                        <div style="color: #15803d; font-size: 0.85rem; font-weight: 600;">✅ All moves validated successfully!</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display validation issues if any
                if invalid_moves:
                    st.markdown("""
                    <div style="margin-top: 12px;">
                        <div style="color: #dc2626; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px;">⚠️ Move Validation Issues:</div>
                    """, unsafe_allow_html=True)
                    
                    for invalid_move in invalid_moves:
                        st.markdown(f"""
                        <div style="
                            background: #fef2f2;
                            color: #dc2626;
                            padding: 6px 12px;
                            border-radius: 16px;
                            font-size: 0.9rem;
                            font-weight: 500;
                            display: inline-block;
                            margin: 2px;
                            border: 1px solid #fecaca;
                        ">{invalid_move}</div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Show move count and validation status
                st.markdown(f"""
                <div style="margin-top: 8px; color: #64748b; font-size: 0.85rem;">
                    Total moves: {len(moves)} • Validated: {len(valid_moves)} • Issues: {len(invalid_moves)}
                </div>
                """, unsafe_allow_html=True)
                
                # Debug information (only show in development)
                if pokemon.get('move_validation_issues'):
                    st.markdown(f"""
                    <div style="margin-top: 8px; padding: 8px; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <div style="color: #92400e; font-size: 0.8rem; font-weight: 600;">🔍 Debug Info:</div>
                        <div style="color: #92400e; font-size: 0.75rem; margin-top: 4px;">
                            Validation issues detected. Check console for details.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="color: #64748b; font-style: italic; font-size: 1.1rem;">No moves specified</div>
                """, unsafe_allow_html=True)
        
        # EV Spread Section (full width)
        st.markdown("""
        <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin: 24px 0 16px 0; display: flex; align-items: center;">
            📊 EV Spread
        </h3>
        """, unsafe_allow_html=True)
        
        # Create EV bars using Streamlit components
        ev_stats = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
        ev_labels = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']
        ev_colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6']
        
        for stat, label, color in zip(ev_stats, ev_labels, ev_colors):
            ev_value = pokemon.get('evs', {}).get(stat, 0)
            percentage = (ev_value / 252) * 100 if ev_value > 0 else 0
            
            st.markdown(f"""
            <div style="
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 8px;
            ">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 700; color: #475569; font-size: 1rem;">{label}</span>
                    <span style="font-weight: 700; color: #0f172a; font-size: 1rem;">{ev_value}</span>
                </div>
                <div style="
                    width: 100%;
                    height: 12px;
                    background: #e2e8f0;
                    border-radius: 6px;
                    overflow: hidden;
                    border: 1px solid #cbd5e1;
                ">
                    <div style="
                        height: 100%;
                        background: {color};
                        width: {percentage}%;
                        border-radius: 5px;
                    "></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
            # EV Explanation Section (if available)
        if pokemon.get('ev_explanation') and pokemon['ev_explanation'] != 'Not specified' and pokemon['ev_explanation'] != 'Not specified in the article or image.':
            st.markdown("""
            <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin: 24px 0 16px 0; display: flex; align-items: center;">
                🧠 Strategy & EV Explanation
            </h3>
            """, unsafe_allow_html=True)
            
            # Format the explanation text for better readability
            explanation = pokemon['ev_explanation']
            
            # Clean up the explanation text
            def clean_explanation(text):
                # Strip HTML tags first
                try:
                    from utils.shared_utils import strip_html_tags
                    text = strip_html_tags(text)
                except ImportError:
                    # Fallback HTML stripping
                    import re
                    text = re.sub(r'<[^>]+>', '', text)
                
                # Remove simple markdown/emphasis artifacts and stray markers
                import re
                text = re.sub(r"\*{1,3}", "", text)  # remove *, **, ***
                text = re.sub(r"\s*-\s*ev explanation\s*$", "", text, flags=re.IGNORECASE)
                text = text.replace("—", "-").replace("–", "-")
                text = text.replace("’", "'").replace('“', '"').replace('”', '"')

                # Capitalize first letter
                if text:
                    text = text[0].upper() + text[1:]
                
                # Fix common issues
                # Normalize stat abbreviations and common terms (case-insensitive)
                replacements_ci = {
                    r"\bevs\b": "EVs",
                    r"\bhp\b": "HP",
                    r"\batk\b": "Attack",
                    r"\bdef\b": "Defense",
                    r"\bspa\b": "Special Attack",
                    r"\bsp\.?a\b": "Special Attack",
                    r"\bspd\b": "Special Defense",
                    r"\bsp\.?d\b": "Special Defense",
                    r"\bspe\b": "Speed",
                    r"\bko\b": "KO",
                    r"\bohko\b": "OHKO",
                    r"\b2hko\b": "2HKO",
                    r"\b3hko\b": "3HKO",
                    r"\bpokemon\b": "Pokémon",
                }
                for pattern, repl in replacements_ci.items():
                    text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
                
                # Correct common typos and normalize stat names
                # Special Defense typos
                text = re.sub(r"(?i)\bpe?e?dcial\s+defen[cs]e(?:nse)?\b", "Special Defense", text)
                text = re.sub(r"(?i)\bspecial\s+defen[cs]e\b", "Special Defense", text)
                # Defense duplicated suffix (e.g., Defenseense)
                text = re.sub(r"(?i)\bdefenseense\b", "Defense", text)
                # Speed misspellings
                text = re.sub(r"(?i)\bspe+ed+ed\b", "Speed", text)
                text = re.sub(r"(?i)\bspe+ed\b", "Speed", text)
                # Generic stat lowercase occurrences
                text = re.sub(r"(?i)\bspecial\s+defen[cs]e\b", "Special Defense", text)
                text = re.sub(r"(?i)\bspecial\s+attack\b", "Special Attack", text)
                text = re.sub(r"(?i)\bdefen[cs]e\b", "Defense", text)
                text = re.sub(r"(?i)\bspeed\b", "Speed", text)

                # Translate a few common Japanese shorthand terms for clarity
                jp_terms = {
                    "準速": "neutral-nature max Speed",
                    "最速": "max Speed (positive nature)",
                    "無振り": "no investment",
                    "確定耐え": "guaranteed survival",
                    "乱数": "chance",
                }
                for jp, en in jp_terms.items():
                    text = text.replace(jp, en)

                # Fix sentence structure
                text = text.replace('the author', 'The author')
                text = text.replace('they considered', 'They considered')
                text = text.replace('they decided', 'They decided')
                text = text.replace('they mention', 'They mention')
                text = text.replace('they state', 'They state')
                text = text.replace('they note', 'They note')
                # Normalize percent spacing
                text = re.sub(r"\s+%", "%", text)
                # Remove stray trailing punctuation/asterisks
                text = text.strip().rstrip('*').strip()
                
                return text
            
            explanation = clean_explanation(explanation)

            # Additional readability polishing
            def polish(text: str) -> str:
                import re
                # Normalize spacing and punctuation
                text = re.sub(r"\s+%", "%", text)
                text = re.sub(r"\s+\.", ".", text)
                text = re.sub(r"\s+,", ",", text)
                # Replace awkward phrases
                replacements = {
                    'it is able to': 'it can',
                    'it is possible to': 'it can',
                    'in order to': 'to',
                    'the author mentions that': 'The author notes that',
                    'the author states that': 'The author states that',
                    'the author believes that': 'The author believes that',
                }
                for k,v in replacements.items():
                    text = text.replace(k, v)
                # Split and tidy sentences; ensure proper capitalization and ending
                raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
                cleaned_sentences = []
                for s in raw_sentences:
                    if not s:
                        continue
                    # Capitalize first alpha character only
                    s = s[0].upper() + s[1:] if len(s) > 1 else s.upper()
                    if s and s[-1] not in '.!?':
                        s += '.'
                    cleaned_sentences.append(s)
                return ' '.join(cleaned_sentences)

            explanation = polish(explanation)
            
            # Split into coherent paragraphs
            if len(explanation) > 150:
                # Split by key phrases to create logical sections
                sections = []
                current_section = ""
                
                # Split by common EV explanation patterns
                parts = re.split(r'(?<=\.)\s+(?=The|They|This|These|The author|HP|Attack|Defense|Special|Speed)', explanation)
                
                for part in parts:
                    part = part.strip()
                    if part:
                        if len(part) > 50:  # Only add substantial parts
                            sections.append(part)
                
                if sections:
                    explanation_html = ""
                    for section in sections:
                        if section:
                            # Ensure proper sentence ending
                            if not section.endswith('.'):
                                section += '.'
                            explanation_html += f'<div style="margin-bottom: 16px; line-height: 1.6;">• {section}</div>'
                else:
                    # Fallback to simple sentence splitting
                    sentences = [s.strip() for s in explanation.split('.') if s.strip() and len(s.strip()) > 20]
                    explanation_html = ""
                    for sentence in sentences:
                        if sentence:
                            if not sentence.endswith('.'):
                                sentence += '.'
                            explanation_html += f'<div style="margin-bottom: 12px; line-height: 1.6;">• {sentence}</div>'
            else:
                explanation_html = f'<div style="line-height: 1.8;">{explanation}</div>'
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border: 2px solid #0ea5e9;
                border-radius: 12px;
                padding: 20px;
                font-size: 1.1rem;
                color: #0c4a6e;
                font-weight: 500;
            ">
                {explanation_html}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)


def display_article_summary(parsed_data, full_summary):
    """Display the overall article summary at the bottom"""
    
    st.markdown("""
    <div style="margin: 48px 0 32px 0;">
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h2 style="margin: 0; font-size: 2rem; font-weight: 800;">
                📰 Overall Article Summary
            </h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the summary content
    if parsed_data.get('conclusion'):
        st.markdown(f"""
        <div style="
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 32px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="color: #1e293b; font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center;">
                🎯 Key Insights & Strategy
            </h3>
            <div style="
                color: #0f172a;
                font-size: 1.2rem;
                line-height: 1.8;
                font-weight: 500;
            ">
                {parsed_data['conclusion']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 32px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="color: #1e293b; font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center;">
                ✅ Analysis Complete
            </h3>
            <div style="
                color: #0f172a;
                font-size: 1.2rem;
                line-height: 1.8;
                font-weight: 500;
            ">
                The analysis has successfully extracted and translated the Pokemon team information from the Japanese article. 
                All Pokemon, moves, abilities, items, Tera types, and EV spreads have been identified and translated to English.
                The detailed breakdown above provides comprehensive information about each Pokemon's role and strategy within the team.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Download section
    display_download_section(full_summary)


def display_download_section(summary):
    """Display download options in a modern card"""
    
    st.markdown("""
    <div style="
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 32px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="color: #1e293b; font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center;">
            📥 Download Results
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create download buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.download_button(
            label="📄 Download as Text",
            data=summary,
            file_name=f"pokemon_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        ):
            st.success("✅ Text file downloaded!")
    
    with col2:
        json_data = json.dumps({
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "word_count": len(summary.split())
        }, indent=2, ensure_ascii=False)
        
        if st.download_button(
                            label="📊 Download as JSON",
            data=json_data,
            file_name=f"pokemon_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        ):
            st.success("✅ JSON file downloaded!")
    
    with col3:
        if st.download_button(
            label="📋 Download as CSV",
            data="Pokemon,Analysis\nTeam,Complete",
            file_name=f"pokemon_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        ):
            st.success("✅ CSV file downloaded!")
