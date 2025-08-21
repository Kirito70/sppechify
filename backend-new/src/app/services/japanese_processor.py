"""
Japanese text processing service for language learning applications.

This module provides comprehensive Japanese text processing capabilities including
furigana generation, romanization, JLPT level detection, and text analysis.
"""

import logging
from typing import Dict, List, Optional, Tuple
import re

try:
    from .furigana_generator import FuriganaGenerator
    import jaconv
except ImportError as e:
    logging.warning(f"Japanese processing dependencies not available: {e}")
    FuriganaGenerator = None
    jaconv = None

logger = logging.getLogger(__name__)

class JapaneseProcessor:
    """
    Main service class for Japanese text processing operations.
    
    This class provides a unified interface for all Japanese text processing
    needs in the language learning application.
    """
    
    def __init__(self):
        """Initialize the Japanese processor with all required components."""
        self.furigana_generator = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all processing components."""
        try:
            if FuriganaGenerator:
                self.furigana_generator = FuriganaGenerator()
                logger.info("Japanese processor initialized successfully")
            else:
                logger.warning("FuriganaGenerator not available - some features will be disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Japanese processor: {e}")
    
    def process_japanese_sentence(self, japanese_text: str) -> Dict[str, any]:
        """
        Process a Japanese sentence and return comprehensive analysis.
        
        Args:
            japanese_text (str): The Japanese sentence to process
            
        Returns:
            Dict[str, any]: Comprehensive analysis including furigana, romanization, etc.
            
        Example:
            >>> processor = JapaneseProcessor()
            >>> result = processor.process_japanese_sentence("今日は晴れです")
            {
                'original_text': '今日は晴れです',
                'furigana': 'きょうははれです',
                'romanization': 'kyou wa hare desu',
                'has_kanji': True,
                'kanji_count': 2,
                'difficulty_estimate': 3,
                'character_composition': {...}
            }
        """
        if not japanese_text or not japanese_text.strip():
            return {
                'original_text': japanese_text,
                'error': 'Empty or invalid text provided'
            }
        
        result = {
            'original_text': japanese_text.strip()
        }
        
        try:
            # Generate furigana if available
            if self.furigana_generator:
                furigana = self.furigana_generator.generate_furigana(japanese_text)
                result['furigana'] = furigana
                
                # Generate romanization
                if furigana:
                    romanization = self._generate_romanization(furigana)
                    result['romanization'] = romanization
                
                # Analyze text composition
                composition = self.furigana_generator.analyze_text_composition(japanese_text)
                result['character_composition'] = composition
                result['has_kanji'] = composition['kanji'] > 0
                result['kanji_count'] = composition['kanji']
                
                # Extract kanji characters
                if result['has_kanji']:
                    kanji_chars = self.furigana_generator.extract_kanji(japanese_text)
                    result['kanji_characters'] = kanji_chars
                
                # Estimate difficulty level (1-5 scale)
                difficulty = self._estimate_difficulty(japanese_text, composition)
                result['difficulty_estimate'] = difficulty
                
                # Detect sentence type
                sentence_type = self._detect_sentence_type(japanese_text)
                result['sentence_type'] = sentence_type
                
            else:
                result['error'] = 'Japanese processing components not available'
                result['furigana'] = None
                result['romanization'] = None
                
        except Exception as e:
            logger.error(f"Error processing Japanese text '{japanese_text}': {e}")
            result['error'] = f"Processing failed: {str(e)}"
        
        return result
    
    def generate_furigana(self, japanese_text: str) -> Optional[str]:
        """
        Generate furigana for Japanese text.
        
        Args:
            japanese_text (str): The Japanese text
            
        Returns:
            Optional[str]: The furigana or None if generation fails
        """
        if not self.furigana_generator:
            return None
        return self.furigana_generator.generate_furigana(japanese_text)
    
    def generate_romanization(self, text: str) -> Optional[str]:
        """
        Generate romanization for Japanese text.
        
        Args:
            text (str): The Japanese text (original or furigana)
            
        Returns:
            Optional[str]: The romanization or None if generation fails
        """
        try:
            # If text contains kanji, convert to furigana first
            if self.furigana_generator and self.furigana_generator.has_kanji(text):
                hiragana_text = self.furigana_generator.generate_furigana(text)
                if hiragana_text:
                    return self._generate_romanization(hiragana_text)
            else:
                return self._generate_romanization(text)
        except Exception as e:
            logger.error(f"Error generating romanization: {e}")
            return None
    
    def estimate_jlpt_level(self, japanese_text: str) -> Optional[str]:
        """
        Estimate JLPT level based on text complexity.
        
        This is a simplified estimation. For production use, you would want
        to integrate with a proper JLPT vocabulary database.
        
        Args:
            japanese_text (str): The Japanese text
            
        Returns:
            Optional[str]: Estimated JLPT level (N5, N4, N3, N2, N1) or None
        """
        try:
            if not self.furigana_generator:
                return None
                
            composition = self.furigana_generator.analyze_text_composition(japanese_text)
            kanji_count = composition['kanji']
            total_chars = sum(composition.values())
            
            if total_chars == 0:
                return None
            
            # Simple heuristic based on kanji density and complexity
            kanji_ratio = kanji_count / total_chars
            
            if kanji_ratio == 0:
                return "N5"  # No kanji, likely beginner
            elif kanji_ratio <= 0.2:
                return "N4"
            elif kanji_ratio <= 0.4:
                return "N3"
            elif kanji_ratio <= 0.6:
                return "N2"
            else:
                return "N1"  # High kanji density, advanced
                
        except Exception as e:
            logger.error(f"Error estimating JLPT level: {e}")
            return None
    
    def _generate_romanization(self, hiragana_text: str) -> str:
        """
        Convert hiragana text to romanization.
        
        Args:
            hiragana_text (str): Text in hiragana
            
        Returns:
            str: Romanized text
        """
        if not jaconv:
            # Fallback basic romanization mapping
            return self._basic_romanization(hiragana_text)
        
        try:
            # Use jaconv for accurate romanization
            romanized = jaconv.hira2hepburn(hiragana_text)
            return romanized
        except Exception as e:
            logger.error(f"Error in jaconv romanization: {e}")
            return self._basic_romanization(hiragana_text)
    
    def _basic_romanization(self, text: str) -> str:
        """
        Basic romanization fallback when jaconv is not available.
        
        Args:
            text (str): Text to romanize
            
        Returns:
            str: Basic romanized text
        """
        # This is a very basic mapping - not recommended for production
        basic_map = {
            'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
            'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
            'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
            'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
            'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
            'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
            'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
            'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
            'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
            'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
            'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
            'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
            'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
            'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
            'わ': 'wa', 'を': 'wo', 'ん': 'n',
            # Common particles
            'は': 'wa',  # When used as particle
            'を': 'o',   # When used as particle
        }
        
        result = ""
        for char in text:
            if char in basic_map:
                result += basic_map[char]
            elif char == ' ':
                result += ' '
            else:
                result += char  # Keep unknown characters as-is
        
        return result
    
    def _estimate_difficulty(self, text: str, composition: Dict[str, int]) -> int:
        """
        Estimate difficulty level on a 1-5 scale.
        
        Args:
            text (str): The Japanese text
            composition (Dict[str, int]): Character composition analysis
            
        Returns:
            int: Difficulty level (1-5)
        """
        try:
            total_chars = sum(composition.values())
            if total_chars == 0:
                return 1
            
            kanji_ratio = composition['kanji'] / total_chars
            text_length = len(text)
            
            # Base difficulty on kanji ratio and text length
            if kanji_ratio == 0:
                difficulty = 1  # No kanji
            elif kanji_ratio <= 0.2:
                difficulty = 2  # Low kanji density
            elif kanji_ratio <= 0.4:
                difficulty = 3  # Medium kanji density
            elif kanji_ratio <= 0.6:
                difficulty = 4  # High kanji density
            else:
                difficulty = 5  # Very high kanji density
            
            # Adjust for text length
            if text_length > 50:
                difficulty = min(5, difficulty + 1)
            elif text_length < 10:
                difficulty = max(1, difficulty - 1)
            
            return difficulty
            
        except Exception as e:
            logger.error(f"Error estimating difficulty: {e}")
            return 3  # Default to medium difficulty
    
    def _detect_sentence_type(self, text: str) -> str:
        """
        Detect the type of sentence based on ending patterns.
        
        Args:
            text (str): The Japanese text
            
        Returns:
            str: Sentence type (statement, question, exclamation, etc.)
        """
        text = text.strip()
        
        if text.endswith('？') or text.endswith('?'):
            return 'question'
        elif text.endswith('！') or text.endswith('!'):
            return 'exclamation'
        elif any(text.endswith(ending) for ending in ['です', 'である', 'だ', 'ます', 'る', 'た', 'い']):
            return 'statement'
        elif any(text.endswith(ending) for ending in ['ください', 'なさい', 'て']):
            return 'command'
        else:
            return 'other'

# Global instance for reuse
_japanese_processor = None

def get_japanese_processor() -> JapaneseProcessor:
    """
    Get a singleton instance of the JapaneseProcessor.
    
    Returns:
        JapaneseProcessor: The singleton instance
    """
    global _japanese_processor
    if _japanese_processor is None:
        _japanese_processor = JapaneseProcessor()
    return _japanese_processor

# Convenience functions
def process_japanese_text(text: str) -> Dict[str, any]:
    """
    Convenience function to process Japanese text.
    
    Args:
        text (str): The Japanese text
        
    Returns:
        Dict[str, any]: Processing results
    """
    processor = get_japanese_processor()
    return processor.process_japanese_sentence(text)

def generate_furigana_for_text(text: str) -> Optional[str]:
    """
    Convenience function to generate furigana.
    
    Args:
        text (str): The Japanese text
        
    Returns:
        Optional[str]: The furigana or None
    """
    processor = get_japanese_processor()
    return processor.generate_furigana(text)