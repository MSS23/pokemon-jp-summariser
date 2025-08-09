"""
Test script for experimental prompting features
Run this to test the advanced prompting techniques
"""

import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from experimental_prompts import ExperimentalPromptManager, test_experimental_prompts
from gemini_summary import llm_summary_gemini

def main():
    print("🧪 Testing Experimental Prompting System")
    print("=" * 50)
    
    # Sample article text for testing
    sample_article = """
    VGC Team Analysis: Calyrex Ice Rider Team
    
    1. Calyrex Ice Rider
    Ability: As One (Glastrier)
    Item: Leftovers
    Tera Type: Ice
    Nature: Adamant
    Moves: Glacial Lance / High Horsepower / Swords Dance / Protect
    EV Spread: 252 HP / 252 Atk / 4 Def
    EV Explanation: Max HP and Attack for bulk and damage output
    
    2. Iron Jugulis
    Ability: Quark Drive
    Item: Booster Energy
    Tera Type: Dark
    Nature: Timid
    Moves: Aura Sphere / Dazzling Gleam / Thunder Wave / Protect
    EV Spread: 44 HP / 4 Def / 252 SpA / 28 SpD / 180 Spe
    EV Explanation: Optimized for speed and special attack
    
    3. Rillaboom
    Ability: Grassy Surge
    Item: Assault Vest
    Tera Type: Grass
    Nature: Adamant
    Moves: Grassy Glide / Wood Hammer / U-turn / Snarl
    EV Spread: 252 HP / 252 Atk / 4 SpD
    EV Explanation: Max HP and Attack for bulk and damage
    """
    
    print("📝 Sample Article:")
    print(sample_article)
    print("\n" + "=" * 50)
    
    try:
        # Initialize the experimental prompt manager
        print("🔧 Initializing Experimental Prompt Manager...")
        prompt_manager = ExperimentalPromptManager(llm_summary_gemini)
        
        # Test the experimental analysis with text
        print("🚀 Running Experimental Analysis with text...")
        result = prompt_manager.analyze_team_with_chain_of_thought(sample_article)
        
        # Test URL-based analysis (optional)
        test_url = input("\n🔗 Enter a test URL (or press Enter to skip): ").strip()
        if test_url:
            print(f"🚀 Testing URL-based analysis for: {test_url}")
            url_result = prompt_manager.analyze_team_with_chain_of_thought_from_url(test_url)
            
            print(f"\n📊 URL Analysis Results:")
            print(f"Success: {url_result.success}")
            print(f"Confidence: {url_result.confidence:.2f}")
            print(f"Pokemon Found: {len(url_result.data.get('pokemon', []))}")
            print(f"Missing Fields: {url_result.missing_fields}")
            print(f"Corrections Applied: {url_result.corrections_applied}")
            
            # Display parsed Pokemon data from URL
            if url_result.data.get('pokemon'):
                print("\n📋 Parsed Pokemon Data (from URL):")
                for i, pokemon in enumerate(url_result.data['pokemon']):
                    print(f"\nPokemon {i+1}:")
                    print(f"  Name: {pokemon.get('name', 'N/A')}")
                    print(f"  Ability: {pokemon.get('ability', 'N/A')}")
                    print(f"  Item: {pokemon.get('item', 'N/A')}")
                    print(f"  Nature: {pokemon.get('nature', 'N/A')}")
                    print(f"  Tera: {pokemon.get('tera', 'N/A')}")
                    print(f"  Moves: {pokemon.get('moves', 'N/A')}")
                    print(f"  EV Spread: {pokemon.get('ev_spread', 'N/A')}")
                    print(f"  EV Explanation: {pokemon.get('ev_explanation', 'N/A')}")
        
        print("\n📊 Results:")
        print(f"Success: {result.success}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Pokemon Found: {len(result.data.get('pokemon', []))}")
        print(f"Missing Fields: {result.missing_fields}")
        print(f"Corrections Applied: {result.corrections_applied}")
        
        # Display parsed Pokemon data
        if result.data.get('pokemon'):
            print("\n📋 Parsed Pokemon Data:")
            for i, pokemon in enumerate(result.data['pokemon']):
                print(f"\nPokemon {i+1}:")
                print(f"  Name: {pokemon.get('name', 'N/A')}")
                print(f"  Ability: {pokemon.get('ability', 'N/A')}")
                print(f"  Item: {pokemon.get('item', 'N/A')}")
                print(f"  Nature: {pokemon.get('nature', 'N/A')}")
                print(f"  Tera: {pokemon.get('tera', 'N/A')}")
                print(f"  Moves: {pokemon.get('moves', 'N/A')}")
                print(f"  EV Spread: {pokemon.get('ev_spread', 'N/A')}")
                print(f"  EV Explanation: {pokemon.get('ev_explanation', 'N/A')}")
        
        # Test user feedback system
        print("\n💬 Testing User Feedback System...")
        prompt_manager.submit_user_feedback(
            team_id="test_team_001",
            field_name="name",
            original_value="Iron Crown",
            corrected_value="Iron Jugulis",
            confidence_rating=5,
            feedback_notes="Common mistake in parsing"
        )
        
        prompt_manager.submit_user_feedback(
            team_id="test_team_001",
            field_name="moves",
            original_value="Bark Out",
            corrected_value="Snarl",
            confidence_rating=4,
            feedback_notes="Move name variation"
        )
        
        # Get feedback statistics
        stats = prompt_manager.get_feedback_statistics()
        print(f"\n📊 Feedback Statistics:")
        print(f"Total Feedback: {stats['total_feedback']}")
        print(f"Average Confidence: {stats['average_confidence']:.2f}")
        print(f"Most Common Corrections: {stats['most_common_corrections']}")
        
        # Export feedback data
        prompt_manager.export_feedback_data("test_feedback.json")
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
