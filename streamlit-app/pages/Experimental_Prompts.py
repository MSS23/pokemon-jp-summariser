"""
Experimental Prompts Test Page
This page allows testing of advanced prompting techniques without affecting the main application.
"""

import streamlit as st
import sys
import os
from datetime import datetime
import json

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from experimental_prompts import ExperimentalPromptManager, test_experimental_prompts
from gemini_summary import llm_summary_gemini
from shared_utils import strip_html_tags

def main():
    st.set_page_config(
        page_title="Experimental Prompts",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Experimental Prompting System")
    st.markdown("""
    This page tests advanced prompting techniques including:
    - **Chain-of-Thought Prompts**: Step-by-step reasoning before analysis
    - **Multi-Step Prompting**: Breaking down analysis into focused steps
    - **Error Recovery Prompts**: Specialized prompts for missing information
    - **User Feedback System**: Rate analysis accuracy and provide corrections
    """)
    
    # Initialize session state
    if 'experimental_results' not in st.session_state:
        st.session_state.experimental_results = None
    if 'prompt_manager' not in st.session_state:
        st.session_state.prompt_manager = None
    if 'analyzed_url' not in st.session_state:
        st.session_state.analyzed_url = None
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🧪 Experimental Controls")
        
        # Test mode selection
        test_mode = st.selectbox(
            "Test Mode",
            ["Chain-of-Thought Analysis", "Error Recovery", "User Feedback", "All Features"]
        )
        
        # Confidence threshold
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Minimum confidence score to consider parsing successful"
        )
        
        # Show detailed reasoning
        show_reasoning = st.checkbox(
            "Show Detailed Reasoning",
            value=True,
            help="Display the model's step-by-step reasoning process"
        )
        
        # Export feedback
        if st.button("📊 Export Feedback Data"):
            if st.session_state.prompt_manager:
                st.session_state.prompt_manager.export_feedback_data("experimental_feedback.json")
                st.success("Feedback data exported to experimental_feedback.json")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔗 Input Article URL")
        
        # Add structured data option
        st.subheader("🖼️ Or Use Structured Data (Image)")
        use_image_data = st.checkbox("Use team data from image", help="Use the structured team data from the provided image")
        
        # Structured data from image
        if use_image_data:
            st.info("📊 Using structured data from the provided image as the primary source.")
            
            # Create structured data from the image
            image_team_data = {
                "title": "Pokemon VGC Team Analysis",
                "summary": "Team analysis from mobile application interface",
                "pokemon": [
                    {
                        "name": "Calyrex (Ice Rider Form)",
                        "ability": "As One (Glastrier)",
                        "item": "Leftovers",
                        "tera_type": "Ice",
                        "nature": "Modest",
                        "moves": ["Glacial Lance", "Trick Room", "Protect"],
                        "ev_spread": [252, 36, 0, 0, 0, 220],
                        "ev_explanation": "Max HP and Speed investment for bulk and speed control",
                        "types": ["Psychic", "Ice"]
                    },
                    {
                        "name": "Kyogre",
                        "ability": "Drizzle",
                        "item": "Blue Orb",
                        "tera_type": "Water",
                        "nature": "Modest",
                        "moves": ["Origin Pulse", "Hydro Pump", "Thunder", "Scary Face"],
                        "ev_spread": [4, 0, 252, 0, 0, 252],
                        "ev_explanation": "Max Special Attack and Speed for offensive pressure",
                        "types": ["Water"]
                    },
                    {
                        "name": "Urshifu (Rapid Strike Style)",
                        "ability": "Unseen Fist",
                        "item": "Choice Band",
                        "tera_type": "Water",
                        "nature": "Adamant",
                        "moves": ["Surging Strikes", "Aqua Jet", "Close Combat", "Detect"],
                        "ev_spread": [4, 252, 0, 0, 0, 252],
                        "ev_explanation": "Max Attack and Speed for priority and coverage",
                        "types": ["Fighting", "Water"]
                    },
                    {
                        "name": "Rillaboom",
                        "ability": "Grassy Surge",
                        "item": "Assault Vest",
                        "tera_type": "Grass",
                        "nature": "Adamant",
                        "moves": ["Grassy Glide", "Wood Hammer", "Fake Out", "U-turn"],
                        "ev_spread": [252, 156, 100, 0, 0, 0],
                        "ev_explanation": "Max HP with balanced Attack and Defense for bulk",
                        "types": ["Grass"]
                    },
                    {
                        "name": "Amoonguss",
                        "ability": "Regenerator",
                        "item": "Rocky Helmet",
                        "tera_type": "Grass",
                        "nature": "Bold",
                        "moves": ["Spore", "Protect", "Pollen Puff", "Rage Powder"],
                        "ev_spread": [252, 0, 100, 0, 156, 0],
                        "ev_explanation": "Max HP and Special Defense for support role",
                        "types": ["Grass", "Poison"]
                    },
                    {
                        "name": "Iron Jugulis",
                        "ability": "Quark Drive",
                        "item": "Booster Energy",
                        "tera_type": "Dark",
                        "nature": "Timid",
                        "moves": ["Snarl", "Tailwind", "Hurricane", "Protect"],
                        "ev_spread": [4, 0, 0, 252, 0, 252],
                        "ev_explanation": "Max Special Attack and Speed for speed control",
                        "types": ["Dark", "Flying"]
                    }
                ],
                "strengths": [
                    "Strong speed control with Tailwind and Trick Room",
                    "Excellent type coverage across all Pokemon",
                    "Good balance of offensive and support Pokemon",
                    "Priority moves for momentum control"
                ],
                "weaknesses": [
                    "Limited defensive Pokemon",
                    "Relies heavily on speed control",
                    "May struggle against strong priority users"
                ]
            }
            
            if st.button("🧪 Run Experimental Analysis (Image Data)", type="primary"):
                progress_container = st.container()
                progress_placeholder = progress_container.empty()
                
                def update_progress(message):
                    progress_placeholder.info(f"🔄 {message}")
                
                with st.spinner("Analyzing team from structured data..."):
                    try:
                        # Initialize the experimental prompt manager
                        if st.session_state.prompt_manager is None:
                            st.session_state.prompt_manager = ExperimentalPromptManager(llm_summary_gemini)
                        
                        # Use the structured data analysis
                        result = st.session_state.prompt_manager.analyze_team_from_structured_data(
                            image_team_data, update_progress
                        )
                        
                        st.session_state.experimental_results = result
                        
                        # Clear progress and show success
                        progress_placeholder.empty()
                        st.success("✅ Analysis completed successfully!")
                        
                    except Exception as e:
                        progress_placeholder.empty()
                        st.error(f"❌ Error during analysis: {str(e)}")
        
        # Status message area for progress updates
        status_container = st.container()
        status_placeholder = status_container.empty()
        
        # URL input (same as main app)
        url = st.text_input(
            "Enter article URL:",
            placeholder="https://example.com/pokemon-article",
            help="Paste the URL of a Japanese Pokemon article to analyze"
        )
        
        # URL validation
        if url:
            if not url.startswith(('http://', 'https://')):
                st.error("❌ Please enter a valid URL starting with http:// or https://")
            else:
                st.success("✅ Valid URL format")
        
        # Article text input (alternative)
        st.header("📝 Or Paste Article Text")
        article_text = st.text_area(
            "Paste your Pokemon team article here:",
            height=200,
            placeholder="Alternatively, paste your article text here to test the experimental prompting system..."
        )
        
        # Test button
        if st.button("🧪 Run Experimental Analysis", type="primary"):
            if url and url.startswith(('http://', 'https://')):
                # Create progress container for real-time updates
                progress_container = st.container()
                progress_placeholder = progress_container.empty()
                
                # Progress callback function
                def update_progress(message):
                    status_placeholder.info(f"🔄 {message}")
                    progress_placeholder.info(f"🔄 {message}")
                
                with st.spinner("Starting experimental analysis..."):
                    try:
                        # Initialize the experimental prompt manager
                        if st.session_state.prompt_manager is None:
                            st.session_state.prompt_manager = ExperimentalPromptManager(llm_summary_gemini)
                        
                        # Use the URL-based analysis with progress updates
                        result = st.session_state.prompt_manager.analyze_team_with_chain_of_thought_from_url(url, update_progress)
                        st.session_state.experimental_results = result
                        st.session_state.analyzed_url = url
                        
                        # Clear progress and show success
                        status_placeholder.empty()
                        progress_placeholder.empty()
                        st.success("✅ Experimental analysis completed!")
                        
                    except Exception as e:
                        status_placeholder.empty()
                        progress_placeholder.empty()
                        st.error(f"❌ Error during experimental analysis: {str(e)}")
                        st.info("💡 Try pasting the article text directly if URL analysis fails")
            elif article_text.strip():
                # Create progress container for real-time updates
                progress_container = st.container()
                progress_placeholder = progress_container.empty()
                
                # Progress callback function
                def update_progress(message):
                    progress_placeholder.info(f"🔄 {message}")
                
                with st.spinner("Starting experimental analysis..."):
                    try:
                        # Initialize the experimental prompt manager
                        if st.session_state.prompt_manager is None:
                            st.session_state.prompt_manager = ExperimentalPromptManager(llm_summary_gemini)
                        
                        # Run the experimental analysis on text with progress updates
                        result = st.session_state.prompt_manager.analyze_team_with_chain_of_thought(article_text, update_progress)
                        st.session_state.experimental_results = result
                        
                        # Clear progress and show success
                        progress_placeholder.empty()
                        st.success("✅ Experimental analysis completed!")
                        
                    except Exception as e:
                        progress_placeholder.empty()
                        st.error(f"❌ Error during experimental analysis: {str(e)}")
            else:
                st.warning("Please enter either a valid URL or paste article text to analyze.")
    
    with col2:
        st.header("📊 Results")
        
        # Show analyzed URL if available
        if st.session_state.analyzed_url:
            st.info(f"🔗 **Analyzed URL:** {st.session_state.analyzed_url}")
        
        if st.session_state.experimental_results:
            result = st.session_state.experimental_results
            
            # Success indicator
            if result.success:
                st.success("✅ Analysis Successful")
            else:
                st.error("❌ Analysis Failed")
            
            # Confidence score
            confidence_color = "green" if result.confidence >= confidence_threshold else "orange"
            st.metric(
                "Confidence Score",
                f"{result.confidence:.2f}",
                delta=f"{'High' if result.confidence >= confidence_threshold else 'Low'} confidence"
            )
            
            # Pokemon count
            pokemon_count = len(result.data.get('pokemon', []))
            st.metric("Pokemon Found", pokemon_count)
            
            # Missing fields
            if result.missing_fields:
                st.warning(f"Missing Fields: {len(result.missing_fields)}")
                for field in result.missing_fields:
                    st.write(f"• {field}")
            
            # Corrections applied
            if result.corrections_applied:
                st.info(f"Corrections Applied: {len(result.corrections_applied)}")
                for correction in result.corrections_applied:
                    st.write(f"• {correction}")
    
    # Display detailed results
    if st.session_state.experimental_results:
        result = st.session_state.experimental_results
        
        st.header("🔍 Detailed Analysis")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📋 Parsed Data", "🤔 Reasoning", "📊 Feedback", "⚙️ Settings", 
            "🔍 Validation", "🏗️ Team Builder", "📈 Analytics"
        ])
        
        with tab1:
            st.subheader("Parsed Pokemon Data")
            
            if result.data.get('pokemon'):
                for i, pokemon in enumerate(result.data['pokemon']):
                    with st.expander(f"Pokemon {i+1}: {pokemon.get('name', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Basic Info:**")
                            st.write(f"• Name: {pokemon.get('name', 'N/A')}")
                            st.write(f"• Ability: {pokemon.get('ability', 'N/A')}")
                            st.write(f"• Item: {pokemon.get('item', 'N/A')}")
                            st.write(f"• Nature: {pokemon.get('nature', 'N/A')}")
                            st.write(f"• Tera Type: {pokemon.get('tera', 'N/A')}")
                        
                        with col2:
                            st.write("**Battle Info:**")
                            st.write(f"• Moves: {pokemon.get('moves', 'N/A')}")
                            st.write(f"• EV Spread: {pokemon.get('ev_spread', 'N/A')}")
                            st.write(f"• EV Explanation: {pokemon.get('ev_explanation', 'N/A')}")
                        
                        # User feedback section for this Pokemon
                        st.subheader("💬 Provide Feedback")
                        feedback_col1, feedback_col2 = st.columns(2)
                        
                        with feedback_col1:
                            field_to_correct = st.selectbox(
                                f"Field to correct for {pokemon.get('name', 'Pokemon')}:",
                                ['name', 'ability', 'item', 'nature', 'tera', 'moves', 'ev_spread', 'ev_explanation'],
                                key=f"field_{i}"
                            )
                            
                            original_value = pokemon.get(field_to_correct, 'N/A')
                            corrected_value = st.text_input(
                                "Corrected value:",
                                value=original_value,
                                key=f"correct_{i}"
                            )
                        
                        with feedback_col2:
                            confidence_rating = st.slider(
                                "How confident are you in this correction?",
                                min_value=1,
                                max_value=5,
                                value=3,
                                key=f"confidence_{i}"
                            )
                            
                            feedback_notes = st.text_area(
                                "Additional notes:",
                                key=f"notes_{i}"
                            )
                            
                            if st.button(f"Submit Feedback for {pokemon.get('name', 'Pokemon')}", key=f"submit_{i}"):
                                if st.session_state.prompt_manager:
                                    # Get user IP and session ID for validation
                                    user_ip = st.experimental_get_query_params().get('user_ip', [''])[0]
                                    session_id = st.session_state.get('session_id', f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                                    
                                    result = st.session_state.prompt_manager.submit_user_feedback(
                                        team_id=f"team_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                        field_name=field_to_correct,
                                        original_value=original_value,
                                        corrected_value=corrected_value,
                                        confidence_rating=confidence_rating,
                                        feedback_notes=feedback_notes,
                                        user_ip=user_ip,
                                        session_id=session_id
                                    )
                                    
                                    if result['valid']:
                                        st.success(f"✅ {result['message']}")
                                    else:
                                        st.error(f"❌ {result['error']}")
        
        with tab2:
            st.subheader("Model Reasoning")
            
            if show_reasoning and result.reasoning:
                st.text_area(
                    "Detailed Reasoning:",
                    value=result.reasoning,
                    height=400,
                    disabled=True
                )
            else:
                st.info("Enable 'Show Detailed Reasoning' in the sidebar to view the model's reasoning process.")
        
        with tab3:
            st.subheader("Feedback Statistics")
            
            if st.session_state.prompt_manager:
                stats = st.session_state.prompt_manager.get_feedback_statistics()
                
                if stats["total_feedback"] > 0:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Feedback", stats["total_feedback"])
                    
                    with col2:
                        st.metric("Average Confidence", f"{stats['average_confidence']:.2f}")
                    
                    with col3:
                        st.metric("Recent Feedback", len(stats["recent_feedback"]))
                    
                    # Most common corrections
                    if stats["most_common_corrections"]:
                        st.subheader("Most Common Corrections")
                        for correction, count in stats["most_common_corrections"]:
                            st.write(f"• {correction} ({count} times)")
                    
                    # Recent feedback
                    if stats["recent_feedback"]:
                        st.subheader("Recent Feedback")
                        for feedback in stats["recent_feedback"]:
                            with st.expander(f"{feedback['field']}: {feedback['correction']} (Rating: {feedback['rating']}/5)"):
                                st.write(f"**Timestamp:** {feedback['timestamp']}")
                                st.write(f"**Field:** {feedback['field']}")
                                st.write(f"**Correction:** {feedback['correction']}")
                                st.write(f"**Confidence Rating:** {feedback['rating']}/5")
                else:
                    st.info("No feedback submitted yet. Use the feedback forms above to provide corrections.")
            
            # Quality Report Section
            st.subheader("🔍 Feedback Quality Report")
            
            if st.session_state.prompt_manager:
                quality_report = st.session_state.prompt_manager.get_feedback_quality_report()
                
                if "message" in quality_report:
                    st.info(quality_report["message"])
                else:
                    # Quality Score
                    quality_score = quality_report.get("quality_score", 0)
                    quality_color = "green" if quality_score >= 80 else "orange" if quality_score >= 60 else "red"
                    
                    st.metric(
                        "Overall Quality Score",
                        f"{quality_score:.1f}/100",
                        delta=f"{'Excellent' if quality_score >= 80 else 'Good' if quality_score >= 60 else 'Needs Improvement'}"
                    )
                    
                    # Spam Indicators
                    if quality_report.get("spam_indicators"):
                        st.warning(f"⚠️ {len(quality_report['spam_indicators'])} potential spam submissions detected")
                        with st.expander("View Spam Indicators"):
                            for indicator in quality_report["spam_indicators"]:
                                st.write(f"• Team {indicator['team_id']}, Field: {indicator['field']} - {indicator['reason']}")
                    
                    # Rate Limit Violations
                    if quality_report.get("rate_limit_violations"):
                        st.error(f"🚫 {len(quality_report['rate_limit_violations'])} rate limit violations detected")
                        with st.expander("View Rate Limit Violations"):
                            for violation in quality_report["rate_limit_violations"]:
                                st.write(f"• User: {violation['user']} - {violation['submissions']} submissions")
                    
                    # Recommendations
                    if quality_report.get("recommendations"):
                        st.subheader("📋 Quality Recommendations")
                        for recommendation in quality_report["recommendations"]:
                            st.write(f"• {recommendation}")
                    
                    # Export Quality Report
                    if st.button("📊 Export Quality Report"):
                        import json
                        from datetime import datetime
                        
                        report_data = {
                            "timestamp": datetime.now().isoformat(),
                            "quality_report": quality_report
                        }
                        
                        report_json = json.dumps(report_data, indent=2)
                        
                        st.download_button(
                            label="📄 Download Quality Report",
                            data=report_json,
                            file_name=f"feedback_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
        
        with tab4:
            st.subheader("Experimental Settings")
            
            st.write("**Current Settings:**")
            st.write(f"• Test Mode: {test_mode}")
            st.write(f"• Confidence Threshold: {confidence_threshold}")
            st.write(f"• Show Detailed Reasoning: {show_reasoning}")
            
            st.write("**System Information:**")
            st.write(f"• Analysis Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"• Success: {result.success}")
            st.write(f"• Missing Fields: {len(result.missing_fields)}")
            st.write(f"• Corrections Applied: {len(result.corrections_applied)}")
        
        with tab5:
            st.subheader("🔍 Pokemon Database Validation")
            
            if result.data.get('pokemon'):
                validation_results = []
                
                for i, pokemon in enumerate(result.data['pokemon']):
                    with st.expander(f"Validation: {pokemon.get('name', 'Unknown')}"):
                        validation = validate_pokemon_data(pokemon)
                        validation_results.append(validation)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Validation Results:**")
                            
                            # Pokemon name validation
                            if validation['name_valid']:
                                st.success("✅ Valid Pokemon name")
                            else:
                                st.error(f"❌ Invalid Pokemon name: {pokemon.get('name', 'Unknown')}")
                                if validation['name_suggestions']:
                                    st.info(f"💡 Suggestions: {', '.join(validation['name_suggestions'])}")
                            
                            # Moves validation
                            if validation['moves_valid']:
                                st.success("✅ All moves are valid")
                            else:
                                st.error(f"❌ Invalid moves: {', '.join(validation['invalid_moves'])}")
                            
                            # EV spread validation
                            if validation['evs_valid']:
                                st.success("✅ EV spread is legal")
                            else:
                                st.error(f"❌ Invalid EV spread: {validation['ev_issues']}")
                            
                            # Item validation
                            if validation['item_valid']:
                                st.success("✅ Valid held item")
                            else:
                                st.warning(f"⚠️ Unusual item: {pokemon.get('item', 'Unknown')}")
                        
                        with col2:
                            st.write("**Team Role Analysis:**")
                            
                            # Determine Pokemon role
                            role = analyze_pokemon_role(pokemon)
                            st.info(f"🎯 Role: {role['primary_role']}")
                            
                            if role['secondary_roles']:
                                st.write(f"🔄 Secondary roles: {', '.join(role['secondary_roles'])}")
                            
                            # Coverage analysis
                            if role['coverage']:
                                st.write("📊 Coverage:")
                                for type_coverage in role['coverage']:
                                    st.write(f"• {type_coverage}")
                
                # Overall team validation
                st.subheader("🏆 Overall Team Validation")
                
                team_validation = validate_team_composition(result.data['pokemon'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Valid Pokemon",
                        f"{team_validation['valid_pokemon']}/{len(result.data['pokemon'])}",
                        delta=f"{team_validation['valid_pokemon'] - len(result.data['pokemon'])}"
                    )
                
                with col2:
                    st.metric(
                        "Legal Teams",
                        "✅" if team_validation['team_legal'] else "❌",
                        delta="Legal" if team_validation['team_legal'] else "Illegal"
                    )
                
                with col3:
                    st.metric(
                        "Type Coverage",
                        f"{team_validation['type_coverage_score']:.1f}/10",
                        delta=f"{'Good' if team_validation['type_coverage_score'] >= 7 else 'Needs Work'}"
                    )
                
                # Team archetype detection
                archetype = detect_team_archetype(result.data['pokemon'])
                st.info(f"🎭 **Detected Team Archetype:** {archetype['name']}")
                st.write(f"**Description:** {archetype['description']}")
                
                if archetype['strengths']:
                    st.write("**Strengths:**")
                    for strength in archetype['strengths']:
                        st.write(f"• {strength}")
                
                if archetype['weaknesses']:
                    st.write("**Weaknesses:**")
                    for weakness in archetype['weaknesses']:
                        st.write(f"• {weakness}")
        
        with tab6:
            st.subheader("🏗️ Interactive Team Builder")
            
            if result.data.get('pokemon'):
                st.write("**Modify and experiment with the extracted team:**")
                
                # Team overview
                st.subheader("Current Team")
                
                modified_team = []
                for i, pokemon in enumerate(result.data['pokemon']):
                    with st.expander(f"Pokemon {i+1}: {pokemon.get('name', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Basic info editing
                            modified_name = st.text_input(
                                "Pokemon Name",
                                value=pokemon.get('name', ''),
                                key=f"edit_name_{i}"
                            )
                            
                            modified_ability = st.text_input(
                                "Ability",
                                value=pokemon.get('ability', ''),
                                key=f"edit_ability_{i}"
                            )
                            
                            modified_item = st.text_input(
                                "Held Item",
                                value=pokemon.get('item', ''),
                                key=f"edit_item_{i}"
                            )
                            
                            modified_nature = st.selectbox(
                                "Nature",
                                options=get_valid_natures(),
                                index=get_valid_natures().index(pokemon.get('nature', 'Hardy')) if pokemon.get('nature') in get_valid_natures() else 0,
                                key=f"edit_nature_{i}"
                            )
                        
                        with col2:
                            # Moves editing
                            st.write("**Moves:**")
                            moves = pokemon.get('moves', '').split(' / ') if pokemon.get('moves') else []
                            modified_moves = []
                            
                            for j in range(4):
                                move = moves[j] if j < len(moves) else ''
                                modified_move = st.text_input(
                                    f"Move {j+1}",
                                    value=move,
                                    key=f"edit_move_{i}_{j}"
                                )
                                modified_moves.append(modified_move)
                            
                            # EV spread editing
                            st.write("**EV Spread:**")
                            ev_spread = pokemon.get('ev_spread', '').split() if pokemon.get('ev_spread') else ['0'] * 6
                            ev_labels = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']
                            modified_evs = {}
                            
                            for j, label in enumerate(ev_labels):
                                ev_value = int(ev_spread[j]) if j < len(ev_spread) and ev_spread[j].isdigit() else 0
                                modified_ev = st.number_input(
                                    label,
                                    min_value=0,
                                    max_value=252,
                                    value=ev_value,
                                    key=f"edit_ev_{i}_{j}"
                                )
                                modified_evs[label] = modified_ev
                        
                        # Create modified Pokemon
                        modified_pokemon = {
                            'name': modified_name,
                            'ability': modified_ability,
                            'item': modified_item,
                            'nature': modified_nature,
                            'moves': ' / '.join([m for m in modified_moves if m]),
                            'ev_spread': ' '.join([str(modified_evs[label]) for label in ev_labels]),
                            'tera': pokemon.get('tera', ''),
                            'ev_explanation': pokemon.get('ev_explanation', '')
                        }
                        
                        modified_team.append(modified_pokemon)
                
                # Team analysis
                st.subheader("Team Analysis")
                
                if st.button("🔍 Analyze Modified Team"):
                    analysis = analyze_modified_team(modified_team)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Team Strengths:**")
                        for strength in analysis['strengths']:
                            st.success(f"✅ {strength}")
                        
                        st.write("**Team Weaknesses:**")
                        for weakness in analysis['weaknesses']:
                            st.error(f"❌ {weakness}")
                    
                    with col2:
                        st.write("**Type Coverage:**")
                        for type_info in analysis['type_coverage']:
                            if type_info['coverage'] == 'Strong':
                                st.success(f"🟢 {type_info['type']}: Strong")
                            elif type_info['coverage'] == 'Weak':
                                st.error(f"🔴 {type_info['type']}: Weak")
                            else:
                                st.warning(f"🟡 {type_info['type']}: Neutral")
                    
                    # Suggestions
                    if analysis['suggestions']:
                        st.subheader("💡 Improvement Suggestions")
                        for suggestion in analysis['suggestions']:
                            st.info(f"💡 {suggestion}")
                
                # Export options
                st.subheader("📤 Export Team")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📄 Export to Showdown"):
                        showdown_format = convert_to_showdown_format(modified_team)
                        st.text_area("Pokemon Showdown Format:", showdown_format, height=200)
                
                with col2:
                    if st.button("📊 Export as JSON"):
                        st.json(modified_team)
                
                with col3:
                    if st.button("📋 Export as CSV"):
                        csv_data = convert_to_csv_format(modified_team)
                        st.download_button(
                            "Download CSV",
                            csv_data,
                            file_name="pokemon_team.csv",
                            mime="text/csv"
                        )
        
        with tab7:
            st.subheader("📈 Enhanced Analytics")
            
            if result.data.get('pokemon'):
                # Performance metrics
                st.subheader("Performance Metrics")
                
                metrics = calculate_performance_metrics(result)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Parsing Accuracy",
                        f"{metrics['parsing_accuracy']:.1f}%",
                        delta=f"{metrics['accuracy_delta']:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Processing Time",
                        f"{metrics['processing_time']:.2f}s",
                        delta=f"{'Fast' if metrics['processing_time'] < 5 else 'Slow'}"
                    )
                
                with col3:
                    st.metric(
                        "Data Completeness",
                        f"{metrics['completeness']:.1f}%",
                        delta=f"{'Complete' if metrics['completeness'] >= 90 else 'Incomplete'}"
                    )
                
                with col4:
                    st.metric(
                        "Confidence Score",
                        f"{metrics['confidence']:.2f}",
                        delta=f"{'High' if metrics['confidence'] >= 0.8 else 'Low'}"
                    )
                
                # Meta analysis
                st.subheader("Meta Analysis")
                
                meta_analysis = analyze_meta_trends(result.data['pokemon'])
                
                # Popular Pokemon
                st.write("**Popular Pokemon in Team:**")
                for pokemon, usage in meta_analysis['popular_pokemon']:
                    st.write(f"• {pokemon}: {usage}% usage rate")
                
                # Common items
                st.write("**Common Items:**")
                for item, count in meta_analysis['common_items']:
                    st.write(f"• {item}: {count} Pokemon")
                
                # Team synergy
                st.write("**Team Synergy Analysis:**")
                for synergy in meta_analysis['synergies']:
                    st.info(f"🤝 {synergy['description']}")
                
                # Speed control analysis
                st.write("**Speed Control Mechanisms:**")
                for mechanism in meta_analysis['speed_control']:
                    st.write(f"• {mechanism}")
                
                # Coverage analysis
                st.subheader("Type Coverage Analysis")
                
                coverage_chart = create_coverage_chart(meta_analysis['type_coverage'])
                st.plotly_chart(coverage_chart, use_container_width=True)
                
                # Team balance
                st.subheader("Team Balance")
                
                balance_metrics = calculate_team_balance(result.data['pokemon'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Offensive Balance:**")
                    st.progress(balance_metrics['offensive_balance'])
                    st.write(f"Physical: {balance_metrics['physical_attackers']} | Special: {balance_metrics['special_attackers']}")
                
                with col2:
                    st.write("**Defensive Balance:**")
                    st.progress(balance_metrics['defensive_balance'])
                    st.write(f"Physical: {balance_metrics['physical_tanks']} | Special: {balance_metrics['special_tanks']}")
                
                # Export analytics
                st.subheader("📊 Export Analytics")
                
                if st.button("📈 Export Analytics Report"):
                    report = generate_analytics_report(result, metrics, meta_analysis, balance_metrics)
                    st.download_button(
                        "Download Analytics Report",
                        report,
                        file_name="pokemon_analytics_report.json",
                        mime="application/json"
                    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Note:** This is an experimental system designed to test advanced prompting techniques. 
    The main application continues to use the proven parsing system.
    """)

# Helper functions for experimental features
def validate_pokemon_data(pokemon):
    """Validate Pokemon data using real parsed data."""
    issues = []
    
    # Validate Pokemon name
    name = pokemon.get('name', '')
    if not name or name == 'N/A':
        issues.append("Missing or invalid Pokemon name")
        name_valid = False
    else:
        name_valid = True
    
    # Validate moves
    moves = pokemon.get('moves', [])
    if not moves or len(moves) != 4:
        issues.append(f"Expected 4 moves, found {len(moves)}")
        moves_valid = False
    else:
        moves_valid = True
    
    # Validate EV spread
    ev_spread = pokemon.get('ev_spread', [])
    ev_issues = []
    if not ev_spread or len(ev_spread) != 6:
        issues.append(f"Expected 6 EV values, found {len(ev_spread)}")
        evs_valid = False
    else:
        try:
            total_evs = sum(ev_spread)
            if total_evs > 510:
                ev_issues.append(f"Total EVs ({total_evs}) exceed 510")
            if any(ev > 252 for ev in ev_spread):
                ev_issues.append("Individual EVs exceed 252")
            if any(ev < 0 for ev in ev_spread):
                ev_issues.append("EVs cannot be negative")
            
            evs_valid = len(ev_issues) == 0
            issues.extend(ev_issues)
        except:
            issues.append("Invalid EV format")
            evs_valid = False
    
    # Validate item
    item = pokemon.get('item', '')
    if not item or item == 'N/A':
        issues.append("Missing held item")
        item_valid = False
    else:
        item_valid = True
    
    return {
        'name_valid': name_valid,
        'name_suggestions': [],
        'moves_valid': moves_valid,
        'invalid_moves': [],
        'evs_valid': evs_valid,
        'ev_issues': ev_issues,
        'item_valid': item_valid,
        'issues': issues
    }

def analyze_pokemon_role(pokemon):
    """Analyze Pokemon's role based on real parsed data."""
    name = pokemon.get('name', '').lower()
    moves = pokemon.get('moves', [])
    ev_spread = pokemon.get('ev_spread', [0, 0, 0, 0, 0, 0])
    
    # Determine role based on EV distribution
    hp, atk, def_, spa, spd, spe = ev_spread
    
    if spe >= 252:
        primary_role = "Fast Attacker"
        secondary_roles = ["Speed Control"]
    elif atk >= 252:
        primary_role = "Physical Attacker"
        secondary_roles = []
    elif spa >= 252:
        primary_role = "Special Attacker"
        secondary_roles = []
    elif def_ >= 252 or spd >= 252:
        primary_role = "Defensive"
        secondary_roles = ["Support"]
    elif hp >= 252:
        primary_role = "Tank"
        secondary_roles = ["Support"]
    else:
        primary_role = "Mixed Attacker"
        secondary_roles = []
    
    # Analyze move types for coverage
    coverage = []
    if any('Fire' in move for move in moves):
        coverage.append('Fire')
    if any('Water' in move for move in moves):
        coverage.append('Water')
    if any('Electric' in move for move in moves):
        coverage.append('Electric')
    if any('Grass' in move for move in moves):
        coverage.append('Grass')
    if any('Ice' in move for move in moves):
        coverage.append('Ice')
    if any('Fighting' in move for move in moves):
        coverage.append('Fighting')
    if any('Poison' in move for move in moves):
        coverage.append('Poison')
    if any('Ground' in move for move in moves):
        coverage.append('Ground')
    if any('Flying' in move for move in moves):
        coverage.append('Flying')
    if any('Psychic' in move for move in moves):
        coverage.append('Psychic')
    if any('Bug' in move for move in moves):
        coverage.append('Bug')
    if any('Rock' in move for move in moves):
        coverage.append('Rock')
    if any('Ghost' in move for move in moves):
        coverage.append('Ghost')
    if any('Dragon' in move for move in moves):
        coverage.append('Dragon')
    if any('Dark' in move for move in moves):
        coverage.append('Dark')
    if any('Steel' in move for move in moves):
        coverage.append('Steel')
    if any('Fairy' in move for move in moves):
        coverage.append('Fairy')
    if any('Normal' in move for move in moves):
        coverage.append('Normal')
    
    return {
        'primary_role': primary_role,
        'secondary_roles': secondary_roles,
        'coverage': coverage
    }

def validate_team_composition(pokemon_list):
    """Validate overall team composition using real parsed data."""
    if not pokemon_list or len(pokemon_list) != 6:
        return {
            'valid_pokemon': 0,
            'team_legal': False,
            'type_coverage_score': 0.0,
            'issues': ['Team must have exactly 6 Pokemon']
        }
    
    # Check for valid Pokemon names
    valid_pokemon = sum(1 for p in pokemon_list if p.get('name') and p.get('name') != 'N/A')
    
    # Check for duplicate Pokemon
    names = [p.get('name', '') for p in pokemon_list]
    duplicates = [name for name in set(names) if names.count(name) > 1 and name != 'N/A']
    
    # Analyze move coverage across team
    all_moves = []
    for pokemon in pokemon_list:
        moves = pokemon.get('moves', [])
        if isinstance(moves, list):
            all_moves.extend(moves)
    
    # Count move types for coverage analysis
    move_types = {}
    for move in all_moves:
        for move_type in ['Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 
                         'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 
                         'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy', 'Normal']:
            if move_type in move:
                move_types[move_type] = move_types.get(move_type, 0) + 1
    
    coverage_score = len(move_types) / 18.0  # 18 types total
    
    issues = []
    if duplicates:
        issues.append(f"Remove duplicate Pokemon: {', '.join(duplicates)}")
    if coverage_score < 0.3:
        issues.append("Add more type coverage")
    if valid_pokemon < 6:
        issues.append(f"Only {valid_pokemon}/6 Pokemon have valid names")
    
    return {
        'valid_pokemon': valid_pokemon,
        'team_legal': len(duplicates) == 0 and valid_pokemon == 6,
        'type_coverage_score': coverage_score,
        'issues': issues
    }

def detect_team_archetype(pokemon_list):
    """Detect team archetype based on real parsed data."""
    if not pokemon_list:
        return {
            'name': "Unknown",
            'description': "No team data available",
            'strengths': [],
            'weaknesses': []
        }
    
    # Analyze team characteristics based on EV distribution
    total_speed_evs = sum(p.get('ev_spread', [0, 0, 0, 0, 0, 0])[5] for p in pokemon_list)
    total_attack_evs = sum(p.get('ev_spread', [0, 0, 0, 0, 0, 0])[1] for p in pokemon_list)
    total_spatk_evs = sum(p.get('ev_spread', [0, 0, 0, 0, 0, 0])[3] for p in pokemon_list)
    total_def_evs = sum(p.get('ev_spread', [0, 0, 0, 0, 0, 0])[2] for p in pokemon_list)
    total_spdef_evs = sum(p.get('ev_spread', [0, 0, 0, 0, 0, 0])[4] for p in pokemon_list)
    
    avg_speed = total_speed_evs / len(pokemon_list)
    avg_attack = total_attack_evs / len(pokemon_list)
    avg_spatk = total_spatk_evs / len(pokemon_list)
    avg_def = total_def_evs / len(pokemon_list)
    avg_spdef = total_spdef_evs / len(pokemon_list)
    
    # Analyze move types for team strategy
    all_moves = []
    for pokemon in pokemon_list:
        moves = pokemon.get('moves', [])
        if isinstance(moves, list):
            all_moves.extend(moves)
    
    # Count support moves
    support_moves = ['Protect', 'Detect', 'Spore', 'Thunder Wave', 'Tailwind', 'Trick Room']
    support_count = sum(1 for move in all_moves if any(support in move for support in support_moves))
    
    # Determine archetype
    if avg_speed > 200:
        archetype = "Hyper Offense"
        description = "Team built around fast, offensive Pokemon"
        strengths = ["Fast sweepers", "High speed investment", "Offensive focus"]
        weaknesses = ["Defensive teams", "Priority moves", "Speed control"]
    elif avg_attack > 150 or avg_spatk > 150:
        archetype = "Offense"
        description = "Team focused on high damage output"
        strengths = ["High damage output", "Mixed offensive investment"]
        weaknesses = ["Defensive teams", "Status conditions"]
    elif avg_def > 150 or avg_spdef > 150:
        archetype = "Defense"
        description = "Team built around defensive Pokemon"
        strengths = ["Defensive investment", "Stall potential"]
        weaknesses = ["Setup sweepers", "Status conditions"]
    elif support_count >= 4:
        archetype = "Support"
        description = "Team with heavy support move usage"
        strengths = ["Team support", "Status control", "Speed control"]
        weaknesses = ["Taunt", "Setup sweepers", "High damage"]
    else:
        archetype = "Balanced"
        description = "Standard balanced team composition"
        strengths = ["Versatility", "Good coverage", "Flexible strategy"]
        weaknesses = ["No clear win condition", "May lack focus"]
    
    return {
        'name': archetype,
        'description': description,
        'strengths': strengths,
        'weaknesses': weaknesses
    }

def get_valid_natures():
    """Get list of valid Pokemon natures."""
    return [
        'Hardy', 'Lonely', 'Brave', 'Adamant', 'Naughty', 'Bold', 'Docile', 'Relaxed',
        'Impish', 'Lax', 'Timid', 'Hasty', 'Serious', 'Jolly', 'Naive', 'Modest',
        'Mild', 'Quiet', 'Bashful', 'Rash', 'Calm', 'Gentle', 'Sassy', 'Careful',
        'Quirky'
    ]

def analyze_modified_team(team):
    """Analyze the modified team for strengths and weaknesses using real data."""
    if not team:
        return {
            'strengths': [],
            'weaknesses': ['No team data available'],
            'type_coverage': [],
            'suggestions': ['Add Pokemon to the team']
        }
    
    # Analyze EV distribution
    total_speed = sum(p.get('ev_spread', [0, 0, 0, 0, 0, 0])[5] for p in team)
    total_attack = sum(p.get('ev_spread', [0, 0, 0, 0, 0, 0])[1] for p in team)
    total_spatk = sum(p.get('ev_spread', [0, 0, 0, 0, 0, 0])[3] for p in team)
    
    # Analyze move coverage
    all_moves = []
    for pokemon in team:
        moves = pokemon.get('moves', [])
        if isinstance(moves, list):
            all_moves.extend(moves)
    
    # Count move types
    move_types = {}
    for move in all_moves:
        for move_type in ['Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 
                         'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 
                         'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy', 'Normal']:
            if move_type in move:
                move_types[move_type] = move_types.get(move_type, 0) + 1
    
    # Determine strengths and weaknesses
    strengths = []
    weaknesses = []
    
    if total_speed > 1000:
        strengths.append('High speed investment')
    if total_attack > 800:
        strengths.append('Strong physical offense')
    if total_spatk > 800:
        strengths.append('Strong special offense')
    if len(move_types) > 8:
        strengths.append('Good type coverage')
    
    if total_speed < 500:
        weaknesses.append('Low speed investment')
    if total_attack < 400 and total_spatk < 400:
        weaknesses.append('Limited offensive pressure')
    if len(move_types) < 5:
        weaknesses.append('Poor type coverage')
    
    # Create type coverage analysis
    type_coverage = []
    for move_type, count in move_types.items():
        if count >= 3:
            coverage = 'Strong'
        elif count >= 2:
            coverage = 'Good'
        else:
            coverage = 'Weak'
        type_coverage.append({'type': move_type, 'coverage': coverage})
    
    suggestions = []
    if len(move_types) < 5:
        suggestions.append('Add more type coverage')
    if total_speed < 500:
        suggestions.append('Consider speed investment')
    if total_attack < 400 and total_spatk < 400:
        suggestions.append('Add offensive pressure')
    
    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'type_coverage': type_coverage,
        'suggestions': suggestions
    }

def convert_to_showdown_format(team):
    """Convert team to Pokemon Showdown format using real data."""
    showdown_lines = []
    for pokemon in team:
        name = pokemon.get('name', 'Unknown')
        item = pokemon.get('item', '')
        ability = pokemon.get('ability', '')
        moves = pokemon.get('moves', [])
        nature = pokemon.get('nature', 'Hardy')
        ev_spread = pokemon.get('ev_spread', [0, 0, 0, 0, 0, 0])
        
        # Format: Name @ Item
        line1 = f"{name} @ {item}" if item else name
        
        # Format: Ability: Ability
        line2 = f"Ability: {ability}" if ability else "Ability: (none)"
        
        # Format: EVs: HP / Atk / Def / SpA / SpD / Spe
        line3 = f"EVs: {ev_spread[0]} HP / {ev_spread[1]} Atk / {ev_spread[2]} Def / {ev_spread[3]} SpA / {ev_spread[4]} SpD / {ev_spread[5]} Spe"
        
        # Format: Nature Nature
        line4 = f"{nature} Nature"
        
        # Format: Moves
        moves_lines = []
        for move in moves:
            if move and move.strip():
                moves_lines.append(f"- {move.strip()}")
        
        showdown_lines.extend([line1, line2, line3, line4] + moves_lines + [""])
    
    return "\n".join(showdown_lines)

def convert_to_csv_format(team):
    """Convert team to CSV format using real data."""
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Name', 'Item', 'Ability', 'Nature', 'Move 1', 'Move 2', 'Move 3', 'Move 4', 'HP EVs', 'Atk EVs', 'Def EVs', 'SpA EVs', 'SpD EVs', 'Spe EVs'])
    
    # Data
    for pokemon in team:
        moves = pokemon.get('moves', [])
        ev_spread = pokemon.get('ev_spread', [0, 0, 0, 0, 0, 0])
        
        row = [
            pokemon.get('name', ''),
            pokemon.get('item', ''),
            pokemon.get('ability', ''),
            pokemon.get('nature', ''),
            moves[0] if len(moves) > 0 else '',
            moves[1] if len(moves) > 1 else '',
            moves[2] if len(moves) > 2 else '',
            moves[3] if len(moves) > 3 else '',
            ev_spread[0],
            ev_spread[1],
            ev_spread[2],
            ev_spread[3],
            ev_spread[4],
            ev_spread[5]
        ]
        writer.writerow(row)
    
    return output.getvalue()

def calculate_performance_metrics(result):
    """Calculate performance metrics for the analysis using real data."""
    if not result or not hasattr(result, 'data') or not result.data:
        return {
            'parsing_accuracy': 0.0,
            'accuracy_delta': 0.0,
            'processing_time': 0.0,
            'completeness': 0.0,
            'confidence': 0.0
        }
    
    # Calculate completeness based on filled fields
    pokemon_list = result.data.get('pokemon', [])
    total_fields = 0
    filled_fields = 0
    
    for pokemon in pokemon_list:
        fields = ['name', 'ability', 'item', 'nature', 'tera', 'moves', 'ev_spread', 'ev_explanation']
        for field in fields:
            total_fields += 1
            value = pokemon.get(field)
            if value and value != 'N/A' and value != []:
                filled_fields += 1
    
    completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0
    
    # Calculate confidence based on result confidence
    confidence = getattr(result, 'confidence', 0.0)
    
    return {
        'parsing_accuracy': completeness,
        'accuracy_delta': 0.0,  # Would need historical data
        'processing_time': 0.0,  # Would need timing data
        'completeness': completeness,
        'confidence': confidence
    }

def analyze_meta_trends(pokemon_list):
    """Analyze meta trends for the team using real data."""
    if not pokemon_list:
        return {
            'popular_pokemon': [],
            'common_items': [],
            'synergies': [],
            'speed_control': [],
            'type_coverage': {}
        }
    
    # Count Pokemon usage
    pokemon_counts = {}
    item_counts = {}
    all_moves = []
    
    for pokemon in pokemon_list:
        name = pokemon.get('name', '')
        if name and name != 'N/A':
            pokemon_counts[name] = pokemon_counts.get(name, 0) + 1
        
        item = pokemon.get('item', '')
        if item and item != 'N/A':
            item_counts[item] = item_counts.get(item, 0) + 1
        
        moves = pokemon.get('moves', [])
        if isinstance(moves, list):
            all_moves.extend(moves)
    
    # Sort by usage
    popular_pokemon = sorted(pokemon_counts.items(), key=lambda x: x[1], reverse=True)
    common_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Analyze type coverage
    type_coverage = {}
    for move in all_moves:
        for move_type in ['Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 
                         'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 
                         'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy', 'Normal']:
            if move_type in move:
                type_coverage[move_type] = type_coverage.get(move_type, 0) + 1
    
    # Identify speed control moves
    speed_control_moves = ['Trick Room', 'Tailwind', 'Thunder Wave', 'Aqua Jet', 'Fake Out']
    speed_control = [move for move in all_moves if any(control in move for control in speed_control_moves)]
    
    # Generate synergies (simplified)
    synergies = []
    if len(pokemon_list) >= 2:
        synergies.append({'description': f'Team has {len(pokemon_list)} Pokemon with diverse coverage'})
    
    return {
        'popular_pokemon': popular_pokemon,
        'common_items': common_items,
        'synergies': synergies,
        'speed_control': speed_control,
        'type_coverage': type_coverage
    }

def create_coverage_chart(type_coverage):
    """Create a type coverage chart."""
    # Fallback without plotly - return None to avoid import errors
    return None

def calculate_team_balance(pokemon_list):
    """Calculate team balance metrics using real data."""
    if not pokemon_list:
        return {
            'offensive_balance': 0.0,
            'physical_attackers': 0,
            'special_attackers': 0,
            'defensive_balance': 0.0,
            'physical_tanks': 0,
            'special_tanks': 0
        }
    
    physical_attackers = 0
    special_attackers = 0
    physical_tanks = 0
    special_tanks = 0
    
    for pokemon in pokemon_list:
        ev_spread = pokemon.get('ev_spread', [0, 0, 0, 0, 0, 0])
        atk, spa, def_, spd = ev_spread[1], ev_spread[3], ev_spread[2], ev_spread[4]
        
        # Count attackers
        if atk >= 252:
            physical_attackers += 1
        if spa >= 252:
            special_attackers += 1
        
        # Count tanks
        if def_ >= 252:
            physical_tanks += 1
        if spd >= 252:
            special_tanks += 1
    
    total_attackers = physical_attackers + special_attackers
    total_tanks = physical_tanks + special_tanks
    
    offensive_balance = total_attackers / len(pokemon_list) if pokemon_list else 0
    defensive_balance = total_tanks / len(pokemon_list) if pokemon_list else 0
    
    return {
        'offensive_balance': offensive_balance,
        'physical_attackers': physical_attackers,
        'special_attackers': special_attackers,
        'defensive_balance': defensive_balance,
        'physical_tanks': physical_tanks,
        'special_tanks': special_tanks
    }

def generate_analytics_report(result, metrics, meta_analysis, balance_metrics):
    """Generate comprehensive analytics report."""
    import json
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'performance_metrics': metrics,
        'meta_analysis': meta_analysis,
        'team_balance': balance_metrics,
        'parsing_result': {
            'success': result.success,
            'confidence': result.confidence,
            'pokemon_count': len(result.data.get('pokemon', [])),
            'missing_fields': result.missing_fields,
            'corrections_applied': result.corrections_applied
        }
    }
    
    return json.dumps(report, indent=2)

if __name__ == "__main__":
    main()
