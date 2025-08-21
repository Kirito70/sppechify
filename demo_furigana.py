#!/usr/bin/env python3
"""
Furigana Generation Demo Script

This script demonstrates the furigana generation functionality
for Japanese language learning applications.

Usage:
    python demo_furigana.py

The script will test various Japanese sentences and show:
- Original Japanese text
- Generated furigana (hiragana readings)
- Romanization
- Text analysis (kanji detection, difficulty estimation, etc.)
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def demo_furigana_generation():
    """Demonstrate furigana generation with sample sentences."""
    
    print("🌸 Japanese Furigana Generation Demo 🌸")
    print("="*50)
    
    # Test sentences with various complexity levels
    test_sentences = [
        "今日は晴れです",           # Today is sunny
        "私の名前は田中です",       # My name is Tanaka
        "学校へ行きます",           # I go to school
        "本を読んでいます",         # I am reading a book
        "日本語を勉強しています",   # I am studying Japanese
        "こんにちは",              # Hello (hiragana only)
        "お元気ですか？",           # How are you?
        "ありがとうございます",     # Thank you (hiragana only)
    ]
    
    try:
        # Try to import and use the Japanese processor
        from app.services.japanese_processor import get_japanese_processor
        
        processor = get_japanese_processor()
        
        if not processor.furigana_generator:
            print("⚠️  Japanese processing dependencies not available.")
            print("To enable furigana generation, install:")
            print("  pip install pykakasi jaconv")
            print("\nFalling back to basic text analysis...")
            print()
            
            for i, sentence in enumerate(test_sentences, 1):
                print(f"{i}. Original: {sentence}")
                print(f"   Status: Dependencies not available for processing")
                print()
            return
        
        print("✅ Japanese processing system initialized successfully!")
        print()
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"{i}. Processing: {sentence}")
            print("-" * 40)
            
            # Process the sentence
            result = processor.process_japanese_sentence(sentence)
            
            # Display results
            print(f"   Original Text: {result.get('original_text', sentence)}")
            
            if result.get('furigana'):
                print(f"   Furigana:      {result['furigana']}")
            else:
                print(f"   Furigana:      [Could not generate]")
            
            if result.get('romanization'):
                print(f"   Romanization:  {result['romanization']}")
            else:
                print(f"   Romanization:  [Could not generate]")
            
            print(f"   Has Kanji:     {result.get('has_kanji', 'Unknown')}")
            print(f"   Kanji Count:   {result.get('kanji_count', 0)}")
            
            if result.get('kanji_characters'):
                print(f"   Kanji Found:   {', '.join(result['kanji_characters'])}")
            
            print(f"   Difficulty:    {result.get('difficulty_estimate', 'Unknown')}/5")
            
            # Estimate JLPT level
            jlpt_level = processor.estimate_jlpt_level(sentence)
            print(f"   JLPT Level:    {jlpt_level or 'Unknown'}")
            
            print(f"   Sentence Type: {result.get('sentence_type', 'Unknown')}")
            
            if result.get('character_composition'):
                comp = result['character_composition']
                print(f"   Composition:   Kanji:{comp.get('kanji',0)}, "
                      f"Hiragana:{comp.get('hiragana',0)}, "
                      f"Katakana:{comp.get('katakana',0)}, "
                      f"ASCII:{comp.get('ascii',0)}")
            
            if result.get('error'):
                print(f"   Error:         {result['error']}")
            
            print()
    
    except ImportError as e:
        print("❌ Could not import Japanese processing modules.")
        print(f"Error: {e}")
        print("\nThis is expected if you haven't installed the Japanese processing dependencies.")
        print("To test the furigana functionality, please install:")
        print("  pip install pykakasi jaconv")
        print()
        
        # Show what the system would look like with dependencies
        print("📋 Expected output format (example):")
        print("-" * 40)
        print("1. Processing: 今日は晴れです")
        print("   Original Text: 今日は晴れです")
        print("   Furigana:      きょうははれです")
        print("   Romanization:  kyou wa hare desu")
        print("   Has Kanji:     True")
        print("   Kanji Count:   2")
        print("   Kanji Found:   今, 日, 晴")
        print("   Difficulty:    3/5")
        print("   JLPT Level:    N4")
        print("   Sentence Type: statement")
        print()

def test_api_schemas():
    """Test the API request/response schemas."""
    print("🔧 Testing API Schemas")
    print("="*25)
    
    try:
        from app.schemas.japanese_sentence import (
            JapaneseTextProcessingRequest,
            JapaneseTextProcessingResponse,
            FuriganaGenerationRequest,
            FuriganaGenerationResponse
        )
        
        # Test request schemas
        print("✅ Testing request schemas...")
        
        process_request = JapaneseTextProcessingRequest(japanese_text="今日は晴れです")
        print(f"   Process request: {process_request.japanese_text}")
        
        furigana_request = FuriganaGenerationRequest(
            japanese_text="今日は晴れです", 
            include_markup=True
        )
        print(f"   Furigana request: {furigana_request.japanese_text} (markup: {furigana_request.include_markup})")
        
        # Test response schemas
        print("✅ Testing response schemas...")
        
        process_response = JapaneseTextProcessingResponse(
            original_text="今日は晴れです",
            furigana="きょうははれです",
            has_kanji=True,
            kanji_count=2
        )
        print(f"   Process response: {process_response.original_text} -> {process_response.furigana}")
        
        furigana_response = FuriganaGenerationResponse(
            original_text="今日は晴れです",
            furigana="きょうははれです",
            has_kanji=True
        )
        print(f"   Furigana response: {furigana_response.original_text} -> {furigana_response.furigana}")
        
        print("✅ All schemas working correctly!")
        print()
        
    except ImportError as e:
        print(f"❌ Could not import schema modules: {e}")
        print()

def show_feature_summary():
    """Show a summary of implemented features."""
    print("📋 Furigana Generation System - Feature Summary")
    print("="*50)
    
    features = [
        "✅ Furigana Generation (hiragana readings for kanji)",
        "✅ Romanization (Japanese to Roman alphabet)",
        "✅ Kanji Detection and Extraction",
        "✅ Text Composition Analysis (kanji/hiragana/katakana/ascii)",
        "✅ Difficulty Level Estimation (1-5 scale)",
        "✅ JLPT Level Estimation (N5-N1)",
        "✅ Sentence Type Detection (statement/question/command)",
        "✅ RESTful API Endpoints",
        "✅ Request/Response Schemas",
        "✅ Error Handling for Missing Dependencies",
        "✅ Comprehensive Test Suite",
        "✅ Database Model Integration",
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print()
    print("🚀 API Endpoints Available:")
    endpoints = [
        "POST /api/v1/process-text - Full Japanese text processing",
        "POST /api/v1/generate-furigana - Furigana generation only", 
        "PUT /api/v1/sentences/{id}/auto-process - Auto-process existing sentences"
    ]
    
    for endpoint in endpoints:
        print(f"  • {endpoint}")
    
    print()
    
    print("📚 Dependencies Required:")
    deps = [
        "pykakasi>=2.3.0 - Japanese text processing engine",
        "jaconv>=0.3.4 - Japanese text conversion utilities"
    ]
    
    for dep in deps:
        print(f"  • {dep}")
    
    print()
    print("💡 Installation command:")
    print("  pip install pykakasi jaconv")
    print()

def main():
    """Main demo function."""
    print()
    show_feature_summary()
    test_api_schemas()
    demo_furigana_generation()
    
    print("🎉 Furigana generation system demo completed!")
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install pykakasi jaconv")
    print("2. Start the backend server")
    print("3. Test the API endpoints with actual Japanese text")
    print("4. Integrate with the frontend for user-facing features")
    print()

if __name__ == "__main__":
    main()