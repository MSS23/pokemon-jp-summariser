# -*- coding: utf-8 -*-
import streamlit as st
import json
import re
from datetime import datetime

# Import enhanced corrections utility
try:
    from utils.corrections import (
        save_pokemon_corrections,
        get_all_team_moves,
        get_tera_types,
        format_ev_spread,
        validate_ev_total,
        validate_ev_spread,
        can_revert_correction,
        revert_correction,
        get_corrections_audit_trail,
        cleanup_session_corrections
    )
    CORRECTIONS_AVAILABLE = True
except ImportError as e:
    st.warning(f"Enhanced corrections functionality not available: {e}")
    CORRECTIONS_AVAILABLE = False

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
                    <div style="color: #64748b; font-size: 0.9rem; font-weight: 600; margin-bottom: 4px;">
                        {label}
                    </div>
                    <div style="color: #1e293b; font-size: 1rem; font-weight: 500;">
                        {value}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Moves Section
            st.markdown("""
            <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                🥊 Moves
            </h3>
            """, unsafe_allow_html=True)
            
            moves = pokemon.get('moves', [])
            if moves:
                for i, move in enumerate(moves, 1):
                    st.markdown(f"""
                    <div style="
                        background: #fef3c7;
                        border: 1px solid #f59e0b;
                        border-radius: 8px;
                        padding: 8px 12px;
                        margin-bottom: 6px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    ">
                        <span style="color: #92400e; font-weight: 600;">{i}. {move}</span>
                        <span style="
                            background: #fbbf24;
                            color: #92400e;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 0.8rem;
                            font-weight: 700;
                        ">Move</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 12px 16px;
                    color: #64748b;
                    font-style: italic;
                ">
                    No moves specified
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # EVs Section
            st.markdown("""
            <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                📊 EVs
            </h3>
            """, unsafe_allow_html=True)
            
            evs = pokemon.get('evs', {})
            if evs:
                # Calculate total EVs
                total_evs = sum(evs.values())
                ev_color = "#22c55e" if total_evs <= 508 else "#ef4444"
                
                st.markdown(f"""
                <div style="
                    background: #f0fdf4;
                    border: 1px solid {ev_color};
                    border-radius: 8px;
                    padding: 12px 16px;
                    margin-bottom: 12px;
                ">
                    <div style="color: #15803d; font-weight: 600; margin-bottom: 8px;">
                        Total EVs: <span style="color: {ev_color}; font-weight: 700;">{total_evs}/508</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display individual EV stats
                ev_stats = [
                    ('hp', 'HP'),
                    ('attack', 'Atk'),
                    ('defense', 'Def'),
                    ('sp_attack', 'SpA'),
                    ('sp_defense', 'SpD'),
                    ('speed', 'Spe')
                ]
                
                for stat, label in ev_stats:
                    value = evs.get(stat, 0)
                    if value > 0:
                        st.markdown(f"""
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding: 4px 0;
                        ">
                            <span style="color: #15803d; font-weight: 500;">{label}</span>
                            <span style="
                                background: #dcfce7;
                                color: #15803d;
                                padding: 2px 8px;
                                border-radius: 12px;
                                font-size: 0.9rem;
                                font-weight: 600;
                            ">{value}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 12px 16px;
                    color: #64748b;
                    font-style: italic;
                ">
                    No EVs specified
                </div>
                """, unsafe_allow_html=True)
            
            # Tera Type Section
            st.markdown("""
            <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                💎 Tera Type
            </h3>
            """, unsafe_allow_html=True)
            
            tera_type = pokemon.get('tera_type', 'Not specified')
            if tera_type != 'Not specified':
                st.markdown(f"""
                <div style="
                    background: #fef3c7;
                    border: 1px solid #f59e0b;
                    border-radius: 8px;
                    padding: 12px 16px;
                    text-align: center;
                ">
                    <div style="color: #92400e; font-size: 1.1rem; font-weight: 700;">
                        {tera_type}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 12px 16px;
                    color: #64748b;
                    font-style: italic;
                    text-align: center;
                ">
                    No Tera type specified
                </div>
                """, unsafe_allow_html=True)
        
        # Close the content div
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Strategy Section
        if pokemon.get('strategy'):
            st.markdown("""
            <div style="
                background: #f8fafc;
                border-top: 1px solid #e2e8f0;
                padding: 24px;
            ">
                <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                    🧠 Strategy
                </h3>
                <div style="
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 16px;
                    color: #475569;
                    line-height: 1.6;
                ">
            """, unsafe_allow_html=True)
            
            # Clean and display strategy text
            strategy_text = pokemon.get('strategy', '')
            if strategy_text:
                def clean_explanation(text):
                    # Strip HTML tags first
                    import re
                    clean_text = re.sub(r'<[^>]+>', '', text)
                    # Remove extra whitespace
                    clean_text = re.sub(r'\s+', ' ', clean_text)
                    # Clean up common formatting issues
                    clean_text = clean_text.replace('\\n', '\n').replace('\\t', '\t')
                    return clean_text.strip()
                
                cleaned_strategy = clean_explanation(strategy_text)
                st.markdown(cleaned_strategy)
            else:
                st.markdown("No strategy information available.")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # EV Explanation Section - Enhanced for better detail display
        if pokemon.get('ev_explanation'):
            ev_explanation = pokemon.get('ev_explanation', '')
            if ev_explanation and ev_explanation.strip():
                st.markdown("""
                <div style="
                    background: #f0f9ff;
                    border-top: 1px solid #e2e8f0;
                    padding: 24px;
                ">
                    <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                        📈 EV Strategy & Explanation
                    </h3>
                """, unsafe_allow_html=True)
                
                def polish(text: str) -> str:
                    # Clean up the text and preserve formatting
                    text = text.replace('\\n', '\n').replace('\\t', '\t')
                    # Preserve line breaks for better readability
                    text = re.sub(r'\n\s*\n', '\n\n', text)
                    text = re.sub(r' +', ' ', text)
                    return text.strip()
                
                cleaned_explanation = polish(str(ev_explanation))
                
                # Split into paragraphs for better display
                paragraphs = cleaned_explanation.split('\n\n')
                
                for i, paragraph in enumerate(paragraphs):
                    if paragraph.strip():
                        # Highlight key information with better formatting
                        if any(keyword in paragraph.lower() for keyword in ['survive', 'survival', 'benchmark', 'outspeed', 'damage', 'ohko', '2hko']):
                            st.markdown(f"""
                            <div style="
                                background: #fef3c7;
                                border-left: 4px solid #f59e0b;
                                padding: 12px 16px;
                                margin: 8px 0;
                                border-radius: 4px;
                            ">
                                <strong>🎯 Key Benchmark:</strong> {paragraph.strip()}
                            </div>
                            """, unsafe_allow_html=True)
                        elif any(keyword in paragraph.lower() for keyword in ['strategy', 'reasoning', 'consider', 'decide', 'choose']):
                            st.markdown(f"""
                            <div style="
                                background: #dbeafe;
                                border-left: 4px solid #3b82f6;
                                padding: 12px 16px;
                                margin: 8px 0;
                                border-radius: 4px;
                            ">
                                <strong>🧠 Strategic Reasoning:</strong> {paragraph.strip()}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(paragraph.strip())
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Enhanced Feedback & Corrections Section
        if CORRECTIONS_AVAILABLE:
            st.markdown("""
            <div style="
                background: #fefce8;
                border-top: 1px solid #e2e8f0;
                padding: 24px;
            ">
                <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                    🔧 Feedback & Corrections
                </h3>
                <div style="
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                ">
            """, unsafe_allow_html=True)
            
            # Get parsed data for corrections
            parsed_data = st.session_state.get('parsed_data', {})
            
            # Moves Correction Section
            st.markdown("**Moves Correction**")
            current_moves = pokemon.get('moves', [])
            if not current_moves:
                current_moves = []
            
            # Create move text input fields
            corrected_moves = []
            for i in range(4):  # Pokemon can have up to 4 moves
                current_move = current_moves[i] if i < len(current_moves) else ""
                
                corrected_move = st.text_input(
                    f"Move {i+1}",
                    value=current_move,
                    key=f"move_{pokemon.get('name', 'unknown')}_{i}",
                    placeholder="Enter move name"
                )
                corrected_moves.append(corrected_move)
            
            # Remove empty moves
            corrected_moves = [move for move in corrected_moves if move and move.strip()]
            
            # Show current vs corrected moves
            if corrected_moves != current_moves:
                st.info(f"**Changes detected:** {', '.join(current_moves)} → {', '.join(corrected_moves)}")
                
                if st.button(f"Confirm Move Changes for {pokemon.get('name', 'Pokemon')}", 
                           key=f"confirm_moves_{pokemon.get('name', 'unknown')}"):
                    success, message = save_pokemon_corrections(pokemon, 'moves', corrected_moves)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            st.markdown("---")
            
            # EVs Correction Section
            st.markdown("**EVs Correction**")
            current_evs = pokemon.get('evs', {})
            if not current_evs:
                current_evs = {'hp': 0, 'attack': 0, 'defense': 0, 'sp_attack': 0, 'sp_defense': 0, 'speed': 0}
            
            # Create EV input fields
            corrected_evs = {}
            ev_labels = {
                'hp': 'HP', 'attack': 'Attack', 'defense': 'Defense',
                'sp_attack': 'Special Attack', 'sp_defense': 'Special Defense', 'speed': 'Speed'
            }
            
            col1, col2 = st.columns(2)
            with col1:
                for stat in ['hp', 'attack', 'defense']:
                    corrected_evs[stat] = st.number_input(
                        ev_labels[stat],
                        min_value=0,
                        max_value=252,
                        value=current_evs.get(stat, 0),
                        key=f"ev_{pokemon.get('name', 'unknown')}_{stat}"
                    )
            
            with col2:
                for stat in ['sp_attack', 'sp_defense', 'speed']:
                    corrected_evs[stat] = st.number_input(
                        ev_labels[stat],
                        min_value=0,
                        max_value=252,
                        value=current_evs.get(stat, 0),
                        key=f"ev_{pokemon.get('name', 'unknown')}_{stat}_2"
                    )
            
            # Show EV total and validation
            total_evs = sum(corrected_evs.values())
            is_valid, validation_message = validate_ev_spread(corrected_evs)
            
            if is_valid:
                st.success(f"**Total EVs: {total_evs}/508** ✅ {validation_message}")
            else:
                st.error(f"**Total EVs: {total_evs}/508** ❌ {validation_message}")
            
            # Show current vs corrected EVs
            if corrected_evs != current_evs:
                st.info(f"**Changes detected:** {format_ev_spread(current_evs)} → {format_ev_spread(corrected_evs)}")
                
                if st.button(f"Confirm EV Changes for {pokemon.get('name', 'Pokemon')}", 
                           key=f"confirm_evs_{pokemon.get('name', 'unknown')}"):
                    success, message = save_pokemon_corrections(pokemon, 'evs', corrected_evs)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            st.markdown("---")
            
            # Tera Type Correction Section
            st.markdown("**Tera Type Correction**")
            current_tera = pokemon.get('tera_type', 'Not specified')
            tera_options = get_tera_types()
            
            if current_tera in tera_options:
                default_index = tera_options.index(current_tera)
            else:
                default_index = 0
            
            corrected_tera = st.selectbox(
                "Tera Type",
                options=tera_options,
                index=default_index,
                key=f"tera_{pokemon.get('name', 'unknown')}"
            )
            
            # Show current vs corrected Tera type
            if corrected_tera != current_tera:
                st.info(f"**Changes detected:** {current_tera} → {corrected_tera}")
                
                if st.button(f"Confirm Tera Type Change for {pokemon.get('name', 'Pokemon')}", 
                           key=f"confirm_tera_{pokemon.get('name', 'unknown')}"):
                    success, message = save_pokemon_corrections(pokemon, 'tera_type', corrected_tera)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            st.markdown("---")
            
            # Overall confirmation section
            st.markdown("**Save All Corrections**")
            st.info("Individual corrections are saved immediately when confirmed above. Use this section to review all changes.")
            
            # Show audit trail
            audit_trail = get_corrections_audit_trail()
            if audit_trail:
                st.markdown("**Recent Corrections:**")
                for correction in audit_trail[-3:]:  # Show last 3 corrections
                    if correction.get('pokemon_name') == pokemon.get('name'):
                        st.markdown(f"""
                        <div style="
                            background: #f0fdf4;
                            border: 1px solid #22c55e;
                            border-radius: 6px;
                            padding: 8px 12px;
                            margin-bottom: 8px;
                            font-size: 0.9rem;
                        ">
                            <strong>{correction['field'].title()}:</strong> {correction['old_value']} → {correction['new_value']}
                            <br><small style="color: #16a34a;">{correction['timestamp'][:19]}</small>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Cleanup old corrections
            cleanup_session_corrections()
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # EV Explanation Section
        ev_explanation = pokemon.get('ev_explanation')
        if ev_explanation:
            st.markdown(f"""
            <div style="padding: 0 24px 24px 24px;">
                <div style="background: #f0f9ff; border-top: 1px solid #e2e8f0; padding: 24px; border-radius: 12px;">
                    <h3 style="color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">📈 EV Strategy & Explanation</h3>
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; color: #475569; line-height: 1.7; font-size: 0.95rem;">
                        <p style="margin: 0;">{ev_explanation}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Close the main container
        st.markdown("</div>", unsafe_allow_html=True)

def display_article_summary(parsed_data, full_summary):
    """Display the article summary with enhanced formatting"""
    st.markdown("""
    <div style="
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        margin: 24px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    ">
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 20px 24px;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">
                📄 Article Summary
            </h2>
        </div>
        <div style="padding: 24px;">
            <div style="
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
                color: #475569;
                line-height: 1.7;
                font-size: 1rem;
            ">
    """, unsafe_allow_html=True)
    
    # Display the summary text
    if full_summary:
        st.markdown(full_summary)
    else:
        st.markdown("No summary available.")
    
    st.markdown("</div></div></div>", unsafe_allow_html=True)

def display_download_section(summary):
    """Display download options for the summary"""
    st.markdown("""
    <div style="
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        margin: 24px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    ">
        <div style="
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            padding: 20px 24px;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">
                💾 Download Options
            </h2>
        </div>
        <div style="padding: 24px;">
            <div style="
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
            ">
    """, unsafe_allow_html=True)
    
    # Download buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download as Text", key="download_text"):
            st.download_button(
                label="Click to download",
                data=summary,
                file_name="pokemon_team_summary.txt",
                mime="text/plain",
                key="download_text_btn"
            )
    
    with col2:
        if st.button("📊 Download as JSON", key="download_json"):
            # Convert summary to JSON format
            import json
            json_data = {"summary": summary, "timestamp": datetime.now().isoformat()}
            st.download_button(
                label="Click to download",
                data=json.dumps(json_data, indent=2),
                file_name="pokemon_team_summary.json",
                mime="application/json",
                key="download_json_btn"
            )
    
    st.markdown("</div></div></div>", unsafe_allow_html=True)
