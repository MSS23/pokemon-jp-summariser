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
                for move in pokemon['moves']:
                    st.markdown(f"""
                    <div style="
                        background: #3b82f6;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-size: 1rem;
                        font-weight: 600;
                        display: inline-block;
                        margin: 2px;
                        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
                    ">{move}</div>
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
                # Capitalize first letter
                if text:
                    text = text[0].upper() + text[1:]
                
                # Fix common issues
                text = text.replace('evs', 'EVs')
                text = text.replace('hp', 'HP')
                text = text.replace('atk', 'Attack')
                text = text.replace('def', 'Defense')
                text = text.replace('spa', 'Special Attack')
                text = text.replace('spd', 'Special Defense')
                text = text.replace('spe', 'Speed')
                text = text.replace('ko', 'KO')
                text = text.replace('ohko', 'OHKO')
                text = text.replace('2hko', '2HKO')
                
                # Fix sentence structure
                text = text.replace('the author', 'The author')
                text = text.replace('they considered', 'They considered')
                text = text.replace('they decided', 'They decided')
                text = text.replace('they mention', 'They mention')
                text = text.replace('they state', 'They state')
                text = text.replace('they note', 'They note')
                
                return text
            
            explanation = clean_explanation(explanation)
            
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
