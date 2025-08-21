"""
Furigana generation service for Japanese text processing.

This module provides functionality to generate furigana (hiragana readings) for Japanese text
containing kanji characters. It uses pykakasi as the primary engine with fallback mechanisms.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
import pykakasi
import jaconv

logger = logging.getLogger(__name__)

class FuriganaGenerator:
    """
    A service for generating furigana (hiragana readings) for Japanese text.
    
    This class handles the conversion of kanji characters to their hiragana readings,
    which is essential for Japanese language learning applications.
    """
    
    def __init__(self):
        """Initialize the furigana generator with pykakasi."""
        try:
            self.kakasi = pykakasi.kakasi()
            self.kakasi.setMode('J', 'H')  # Kanji to Hiragana
            self.kakasi.setMode('K', 'H')  # Katakana to Hiragana
            self.kakasi.setMode('a', 'a')  # ASCII unchanged
            self.conv = self.kakasi.getConverter()
            logger.info("FuriganaGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FuriganaGenerator: {e}")
            self.conv = None
    
    def generate_furigana(self, japanese_text: str) -> Optional[str]:
        """
        Generate furigana for the given Japanese text.
        
        Args:
            japanese_text (str): The Japanese text containing kanji
            
        Returns:
            Optional[str]: The furigana (hiragana reading) or None if generation fails
            
        Example:
            >>> generator = FuriganaGenerator()
            >>> generator.generate_furigana("今日は晴れです")
            "きょうははれです"
        """
        if not japanese_text or not japanese_text.strip():
            return None
            
        if not self.conv:
            logger.error("Kakasi converter not initialized")
            return None
            
        try:
            # Clean the input text
            cleaned_text = self._clean_text(japanese_text)
            
            # Convert to hiragana using pykakasi
            furigana = self.conv.do(cleaned_text)
            
            # Post-process the result
            furigana = self._post_process_furigana(furigana)
            
            logger.debug(f"Generated furigana for '{japanese_text}': '{furigana}'")
            return furigana
            
        except Exception as e:
            logger.error(f"Error generating furigana for '{japanese_text}': {e}")
            return None
    
    def generate_furigana_with_markup(self, japanese_text: str) -> Optional[str]:
        """
        Generate furigana with HTML ruby markup for display purposes.
        
        Args:
            japanese_text (str): The Japanese text containing kanji
            
        Returns:
            Optional[str]: HTML with ruby markup or None if generation fails
            
        Example:
            >>> generator = FuriganaGenerator()
            >>> generator.generate_furigana_with_markup("今日は晴れです")
            "<ruby>今日<rt>きょう</rt></ruby>は<ruby>晴れ<rt>はれ</rt></ruby>です"
        """
        if not japanese_text or not japanese_text.strip():
            return None
            
        if not self.conv:
            logger.error("Kakasi converter not initialized")
            return None
            
        try:
            # This is a simplified implementation
            # For production, you'd want more sophisticated kanji detection and pairing
            furigana = self.generate_furigana(japanese_text)
            if not furigana:
                return None
                
            # For now, return a simple format
            # TODO: Implement proper ruby markup with kanji-furigana pairing
            return f"<ruby>{japanese_text}<rt>{furigana}</rt></ruby>"
            
        except Exception as e:
            logger.error(f"Error generating furigana markup for '{japanese_text}': {e}")
            return None
    
    def has_kanji(self, text: str) -> bool:
        """
        Check if the text contains kanji characters.
        
        Args:
            text (str): The text to check
            
        Returns:
            bool: True if text contains kanji, False otherwise
        """
        # Kanji Unicode ranges: 4E00-9FFF (CJK Unified Ideographs)
        kanji_pattern = r'[\u4e00-\u9fff]+'
        return bool(re.search(kanji_pattern, text))
    
    def extract_kanji(self, text: str) -> List[str]:
        """
        Extract all kanji characters from the text.
        
        Args:
            text (str): The text to extract kanji from
            
        Returns:
            List[str]: List of unique kanji characters found
        """
        kanji_pattern = r'[\u4e00-\u9fff]'
        kanji_chars = re.findall(kanji_pattern, text)
        return list(set(kanji_chars))  # Return unique kanji
    
    def analyze_text_composition(self, text: str) -> Dict[str, int]:
        """
        Analyze the composition of Japanese text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, int]: Dictionary with counts of different character types
        """
        result = {
            'kanji': 0,
            'hiragana': 0,
            'katakana': 0,
            'ascii': 0,
            'other': 0
        }
        
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # Kanji
                result['kanji'] += 1
            elif '\u3040' <= char <= '\u309f':  # Hiragana
                result['hiragana'] += 1
            elif '\u30a0' <= char <= '\u30ff':  # Katakana
                result['katakana'] += 1
            elif char.isascii():  # ASCII
                result['ascii'] += 1
            else:
                result['other'] += 1
                
        return result
    
    def _clean_text(self, text: str) -> str:
        """
        Clean the input text for processing.
        
        Args:
            text (str): The text to clean
            
        Returns:
            str: The cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Convert full-width ASCII to half-width if needed
        text = jaconv.z2h(text, ascii=True, digit=True)
        
        return text
    
    def _post_process_furigana(self, furigana: str) -> str:
        """
        Post-process the generated furigana.
        
        Args:
            furigana (str): The raw furigana to process
            
        Returns:
            str: The processed furigana
        """
        # Convert any remaining katakana to hiragana
        furigana = jaconv.kata2hira(furigana)
        
        # Remove extra spaces
        furigana = re.sub(r'\s+', '', furigana)
        
        return furigana

# Global instance for reuse
_furigana_generator = None

def get_furigana_generator() -> FuriganaGenerator:
    """
    Get a singleton instance of the FuriganaGenerator.
    
    Returns:
        FuriganaGenerator: The singleton instance
    """
    global _furigana_generator
    if _furigana_generator is None:
        _furigana_generator = FuriganaGenerator()
    return _furigana_generator

# Convenience functions
def generate_furigana(text: str) -> Optional[str]:
    """
    Convenience function to generate furigana for text.
    
    Args:
        text (str): The Japanese text
        
    Returns:
        Optional[str]: The furigana or None
    """
    generator = get_furigana_generator()
    return generator.generate_furigana(text)

def has_kanji(text: str) -> bool:
    """
    Convenience function to check if text has kanji.
    
    Args:
        text (str): The text to check
        
    Returns:
        bool: True if text contains kanji
    """
    generator = get_furigana_generator()
    return generator.has_kanji(text)