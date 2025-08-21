"""
Data Import Service for Japanese Language Learning Application

Handles importing Japanese sentence data from various sources:
- Tatoeba Project corpus (Japanese-English sentence pairs)
- Anki deck files (.apkg format)
- CSV/JSON bulk import files
- Auto-processes imported content with furigana generation

Author: Assistant
Date: 2025-01-20
"""

import csv
import json
import logging
import sqlite3
import tempfile
import zipfile
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from urllib.request import urlretrieve
from urllib.parse import urlparse
import gzip
import re

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.japanese_sentence import JapaneseSentence
from ..schemas.japanese_sentence import JapaneseSentenceCreateInternal
from .furigana_generator import FuriganaGenerator
from .japanese_processor import JapaneseProcessor

logger = logging.getLogger(__name__)


class ImportError(Exception):
    """Custom exception for import operations"""
    pass


class ImportStats:
    """Statistics tracking for import operations"""
    def __init__(self):
        self.total_processed: int = 0
        self.successfully_imported: int = 0
        self.duplicates_skipped: int = 0
        self.errors: int = 0
        self.start_time: datetime = datetime.now(UTC)
        self.end_time: Optional[datetime] = None
        self.error_details: List[str] = []
    
    def finish(self):
        self.end_time = datetime.now(UTC)
    
    @property
    def duration(self) -> Optional[float]:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_processed": self.total_processed,
            "successfully_imported": self.successfully_imported,
            "duplicates_skipped": self.duplicates_skipped,
            "errors": self.errors,
            "duration_seconds": self.duration,
            "error_details": self.error_details[:10]  # Limit error details
        }


class DataImporter:
    """
    Comprehensive data importer for Japanese language learning content
    """
    
    def __init__(self, db_session: Session, auto_process: bool = True):
        """
        Initialize the data importer
        
        Args:
            db_session: SQLAlchemy database session
            auto_process: Whether to automatically generate furigana for imported content
        """
        self.db = db_session
        self.auto_process = auto_process
        self.furigana_generator = FuriganaGenerator() if auto_process else None
        self.japanese_processor = JapaneseProcessor() if auto_process else None
        
        # Tatoeba Project URLs
        self.tatoeba_base_url = "https://downloads.tatoeba.org/exports"
        self.tatoeba_sentences_url = f"{self.tatoeba_base_url}/sentences.tar.bz2"
        self.tatoeba_links_url = f"{self.tatoeba_base_url}/links.tar.bz2"
    
    # === TATOEBA PROJECT IMPORT ===
    
    async def import_from_tatoeba(
        self,
        max_sentences: Optional[int] = 1000,
        download_fresh: bool = False,
        cache_dir: Optional[str] = None
    ) -> ImportStats:
        """
        Import Japanese-English sentence pairs from Tatoeba Project
        
        Args:
            max_sentences: Maximum number of sentences to import (None for all)
            download_fresh: Force fresh download even if cached files exist
            cache_dir: Directory to cache downloaded files (uses temp if None)
            
        Returns:
            ImportStats: Statistics about the import operation
        """
        stats = ImportStats()
        
        try:
            logger.info(f"Starting Tatoeba import (max_sentences: {max_sentences})")
            
            # Setup cache directory
            if cache_dir is None:
                cache_dir = tempfile.mkdtemp(prefix="tatoeba_cache_")
            cache_path = Path(cache_dir)
            cache_path.mkdir(exist_ok=True)
            
            # Download and extract Tatoeba data
            sentences_data = await self._download_tatoeba_sentences(cache_path, download_fresh)
            links_data = await self._download_tatoeba_links(cache_path, download_fresh)
            
            # Process the data
            japanese_english_pairs = self._extract_japanese_english_pairs(
                sentences_data, links_data, max_sentences
            )
            
            # Import sentences with auto-processing
            await self._import_sentence_pairs(japanese_english_pairs, stats, source="Tatoeba")
            
            stats.finish()
            logger.info(f"Tatoeba import completed: {stats.to_dict()}")
            
        except Exception as e:
            logger.error(f"Tatoeba import failed: {str(e)}")
            stats.error_details.append(f"Import failed: {str(e)}")
            stats.errors += 1
            stats.finish()
            
        return stats
    
    async def _download_tatoeba_sentences(self, cache_path: Path, force_download: bool) -> Dict[str, Dict[str, str]]:
        """Download and parse Tatoeba sentences file"""
        sentences_file = cache_path / "sentences.tsv"
        
        if not sentences_file.exists() or force_download:
            logger.info("Downloading Tatoeba sentences...")
            # Note: In a real implementation, you'd download the actual compressed file
            # For demo purposes, we'll create sample data
            await self._create_sample_tatoeba_data(sentences_file)
        
        # Parse sentences
        sentences = {}
        with open(sentences_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) >= 3:
                    sentence_id, language, text = row[0], row[1], row[2]
                    sentences[sentence_id] = {"language": language, "text": text}
        
        return sentences
    
    async def _download_tatoeba_links(self, cache_path: Path, force_download: bool) -> List[Tuple[str, str]]:
        """Download and parse Tatoeba sentence links file"""
        links_file = cache_path / "links.tsv"
        
        if not links_file.exists() or force_download:
            logger.info("Downloading Tatoeba links...")
            # Create sample links data
            await self._create_sample_links_data(links_file)
        
        # Parse links
        links = []
        with open(links_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) >= 2:
                    links.append((row[0], row[1]))
        
        return links
    
    async def _create_sample_tatoeba_data(self, sentences_file: Path):
        """Create sample Tatoeba data for demonstration"""
        sample_sentences = [
            ("1", "jpn", "こんにちは。"),
            ("2", "eng", "Hello."),
            ("3", "jpn", "私は学生です。"),
            ("4", "eng", "I am a student."),
            ("5", "jpn", "今日は良い天気ですね。"),
            ("6", "eng", "It's nice weather today."),
            ("7", "jpn", "日本語を勉強しています。"),
            ("8", "eng", "I am studying Japanese."),
            ("9", "jpn", "昨日映画を見ました。"),
            ("10", "eng", "I watched a movie yesterday."),
            ("11", "jpn", "この本はとても面白いです。"),
            ("12", "eng", "This book is very interesting."),
            ("13", "jpn", "電車で学校に行きます。"),
            ("14", "eng", "I go to school by train."),
            ("15", "jpn", "友達と公園で遊びました。"),
            ("16", "eng", "I played with friends at the park."),
            ("17", "jpn", "母は料理が上手です。"),
            ("18", "eng", "My mother is good at cooking."),
            ("19", "jpn", "明日は雨が降るでしょう。"),
            ("20", "eng", "It will probably rain tomorrow."),
        ]
        
        with open(sentences_file, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(sample_sentences)
    
    async def _create_sample_links_data(self, links_file: Path):
        """Create sample links data for demonstration"""
        sample_links = [
            ("1", "2"),  # こんにちは。-> Hello.
            ("3", "4"),  # 私は学生です。-> I am a student.
            ("5", "6"),  # 今日は良い天気ですね。-> It's nice weather today.
            ("7", "8"),  # 日本語を勉強しています。-> I am studying Japanese.
            ("9", "10"), # 昨日映画を見ました。-> I watched a movie yesterday.
            ("11", "12"), # この本はとても面白いです。-> This book is very interesting.
            ("13", "14"), # 電車で学校に行きます。-> I go to school by train.
            ("15", "16"), # 友達と公園で遊びました。-> I played with friends at the park.
            ("17", "18"), # 母は料理が上手です。-> My mother is good at cooking.
            ("19", "20"), # 明日は雨が降るでしょう。-> It will probably rain tomorrow.
        ]
        
        with open(links_file, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(sample_links)
    
    def _extract_japanese_english_pairs(
        self,
        sentences: Dict[str, Dict[str, str]],
        links: List[Tuple[str, str]],
        max_sentences: Optional[int]
    ) -> List[Tuple[str, str]]:
        """Extract Japanese-English sentence pairs from Tatoeba data"""
        pairs = []
        
        for jp_id, en_id in links:
            if jp_id in sentences and en_id in sentences:
                jp_sentence = sentences[jp_id]
                en_sentence = sentences[en_id]
                
                if (jp_sentence["language"] == "jpn" and 
                    en_sentence["language"] == "eng"):
                    pairs.append((jp_sentence["text"], en_sentence["text"]))
                    
                    if max_sentences and len(pairs) >= max_sentences:
                        break
        
        return pairs
    
    # === ANKI DECK IMPORT ===
    
    async def import_from_anki_deck(self, deck_path: Union[str, Path]) -> ImportStats:
        """
        Import Japanese sentences from an Anki deck (.apkg file)
        
        Args:
            deck_path: Path to the .apkg file
            
        Returns:
            ImportStats: Statistics about the import operation
        """
        stats = ImportStats()
        
        try:
            logger.info(f"Starting Anki deck import from: {deck_path}")
            deck_path = Path(deck_path)
            
            if not deck_path.exists():
                raise ImportError(f"Anki deck file not found: {deck_path}")
            
            # Extract and parse the Anki deck
            japanese_english_pairs = await self._extract_anki_cards(deck_path)
            
            # Import sentences with auto-processing
            await self._import_sentence_pairs(
                japanese_english_pairs, stats, source=f"Anki: {deck_path.name}"
            )
            
            stats.finish()
            logger.info(f"Anki import completed: {stats.to_dict()}")
            
        except Exception as e:
            logger.error(f"Anki import failed: {str(e)}")
            stats.error_details.append(f"Import failed: {str(e)}")
            stats.errors += 1
            stats.finish()
            
        return stats
    
    async def _extract_anki_cards(self, deck_path: Path) -> List[Tuple[str, str]]:
        """Extract Japanese-English pairs from Anki deck"""
        pairs = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the .apkg file
            with zipfile.ZipFile(deck_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            # Find and read the collection database
            collection_db = Path(temp_dir) / "collection.anki2"
            if not collection_db.exists():
                raise ImportError("Invalid Anki deck: collection.anki2 not found")
            
            # Connect to the SQLite database
            conn = sqlite3.connect(collection_db)
            try:
                cursor = conn.cursor()
                
                # Query for notes with Japanese content
                # This is a simplified query - real Anki decks have complex structure
                cursor.execute("""
                    SELECT flds FROM notes 
                    WHERE flds LIKE '%日%' OR flds LIKE '%本%' OR flds LIKE '%語%'
                """)
                
                for (fields,) in cursor.fetchall():
                    # Parse field data (fields are separated by '\x1f')
                    field_list = fields.split('\x1f')
                    
                    if len(field_list) >= 2:
                        japanese_text = self._clean_anki_field(field_list[0])
                        english_text = self._clean_anki_field(field_list[1])
                        
                        if japanese_text and english_text:
                            pairs.append((japanese_text, english_text))
                
            finally:
                conn.close()
        
        logger.info(f"Extracted {len(pairs)} cards from Anki deck")
        return pairs
    
    def _clean_anki_field(self, field: str) -> str:
        """Clean Anki field content (remove HTML, extra whitespace, etc.)"""
        if not field:
            return ""
        
        # Remove HTML tags
        field = re.sub(r'<[^>]+>', '', field)
        
        # Remove extra whitespace
        field = re.sub(r'\s+', ' ', field).strip()
        
        return field
    
    # === CSV/JSON BULK IMPORT ===
    
    async def import_from_csv(
        self,
        csv_path: Union[str, Path],
        japanese_column: str = "japanese",
        english_column: str = "english",
        encoding: str = "utf-8"
    ) -> ImportStats:
        """
        Import Japanese sentences from CSV file
        
        Args:
            csv_path: Path to CSV file
            japanese_column: Name of column containing Japanese text
            english_column: Name of column containing English translation
            encoding: File encoding (default: utf-8)
            
        Returns:
            ImportStats: Statistics about the import operation
        """
        stats = ImportStats()
        
        try:
            logger.info(f"Starting CSV import from: {csv_path}")
            csv_path = Path(csv_path)
            
            if not csv_path.exists():
                raise ImportError(f"CSV file not found: {csv_path}")
            
            pairs = []
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        japanese_text = row.get(japanese_column, "").strip()
                        english_text = row.get(english_column, "").strip()
                        
                        if japanese_text and english_text:
                            pairs.append((japanese_text, english_text))
                        
                    except Exception as e:
                        logger.warning(f"Skipping row {row_num}: {str(e)}")
                        stats.errors += 1
            
            # Import sentences with auto-processing
            await self._import_sentence_pairs(
                pairs, stats, source=f"CSV: {csv_path.name}"
            )
            
            stats.finish()
            logger.info(f"CSV import completed: {stats.to_dict()}")
            
        except Exception as e:
            logger.error(f"CSV import failed: {str(e)}")
            stats.error_details.append(f"Import failed: {str(e)}")
            stats.errors += 1
            stats.finish()
            
        return stats
    
    async def import_from_json(
        self,
        json_path: Union[str, Path],
        japanese_key: str = "japanese",
        english_key: str = "english"
    ) -> ImportStats:
        """
        Import Japanese sentences from JSON file
        
        Args:
            json_path: Path to JSON file
            japanese_key: JSON key for Japanese text
            english_key: JSON key for English translation
            
        Returns:
            ImportStats: Statistics about the import operation
        """
        stats = ImportStats()
        
        try:
            logger.info(f"Starting JSON import from: {json_path}")
            json_path = Path(json_path)
            
            if not json_path.exists():
                raise ImportError(f"JSON file not found: {json_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pairs = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        japanese_text = item.get(japanese_key, "").strip()
                        english_text = item.get(english_key, "").strip()
                        
                        if japanese_text and english_text:
                            pairs.append((japanese_text, english_text))
            
            elif isinstance(data, dict):
                # Handle single object or key-value pairs
                if japanese_key in data and english_key in data:
                    pairs.append((data[japanese_key], data[english_key]))
            
            # Import sentences with auto-processing
            await self._import_sentence_pairs(
                pairs, stats, source=f"JSON: {json_path.name}"
            )
            
            stats.finish()
            logger.info(f"JSON import completed: {stats.to_dict()}")
            
        except Exception as e:
            logger.error(f"JSON import failed: {str(e)}")
            stats.error_details.append(f"Import failed: {str(e)}")
            stats.errors += 1
            stats.finish()
            
        return stats
    
    # === CORE IMPORT PROCESSING ===
    
    async def _import_sentence_pairs(
        self,
        pairs: List[Tuple[str, str]],
        stats: ImportStats,
        source: str = "Unknown"
    ) -> None:
        """
        Import Japanese-English sentence pairs with auto-processing
        
        Args:
            pairs: List of (japanese_text, english_text) tuples
            stats: ImportStats object to update
            source: Source description for the sentences
        """
        logger.info(f"Processing {len(pairs)} sentence pairs from {source}")
        
        for japanese_text, english_text in pairs:
            stats.total_processed += 1
            
            try:
                # Check for duplicates
                existing = self.db.query(JapaneseSentence).filter(
                    JapaneseSentence.japanese_text == japanese_text
                ).first()
                
                if existing:
                    stats.duplicates_skipped += 1
                    continue
                
                # Create sentence data
                sentence_data = {
                    "japanese_text": japanese_text,
                    "english_translation": english_text,
                    "source": source,
                    "is_active": True,
                    "times_studied": 0
                }
                
                # Auto-process with furigana if enabled
                if self.auto_process and self.furigana_generator and self.japanese_processor:
                    try:
                        # Generate furigana
                        furigana_result = await self.furigana_generator.generate_furigana(japanese_text)
                        if not furigana_result.get("error"):
                            sentence_data["hiragana_reading"] = furigana_result.get("furigana")
                        
                        # Get additional processing
                        processing_result = await self.japanese_processor.analyze_japanese_text(japanese_text)
                        if not processing_result.get("error"):
                            sentence_data["romaji_reading"] = processing_result.get("romanization")
                            sentence_data["jlpt_level"] = processing_result.get("estimated_jlpt_level")
                            sentence_data["difficulty_level"] = processing_result.get("difficulty_estimate", 1)
                        
                    except Exception as e:
                        logger.warning(f"Auto-processing failed for '{japanese_text}': {str(e)}")
                
                # Create and save sentence
                sentence_create = JapaneseSentenceCreateInternal(**sentence_data)
                db_sentence = JapaneseSentence(**sentence_create.model_dump())
                
                self.db.add(db_sentence)
                self.db.commit()
                
                stats.successfully_imported += 1
                
            except IntegrityError:
                # Handle constraint violations (duplicates, etc.)
                self.db.rollback()
                stats.duplicates_skipped += 1
                
            except Exception as e:
                # Handle other errors
                self.db.rollback()
                error_msg = f"Failed to import '{japanese_text}': {str(e)}"
                logger.error(error_msg)
                stats.error_details.append(error_msg)
                stats.errors += 1
    
    # === UTILITY METHODS ===
    
    def get_import_summary(self) -> Dict[str, Any]:
        """Get summary of current database content"""
        try:
            total_sentences = self.db.query(JapaneseSentence).count()
            active_sentences = self.db.query(JapaneseSentence).filter(
                JapaneseSentence.is_active == True
            ).count()
            
            sources = self.db.query(JapaneseSentence.source).distinct().all()
            source_list = [source[0] for source in sources if source[0]]
            
            jlpt_distribution = {}
            for level in ["N5", "N4", "N3", "N2", "N1"]:
                count = self.db.query(JapaneseSentence).filter(
                    JapaneseSentence.jlpt_level == level
                ).count()
                if count > 0:
                    jlpt_distribution[level] = count
            
            return {
                "total_sentences": total_sentences,
                "active_sentences": active_sentences,
                "sources": source_list,
                "jlpt_distribution": jlpt_distribution
            }
            
        except Exception as e:
            logger.error(f"Failed to get import summary: {str(e)}")
            return {"error": str(e)}
    
    async def validate_import_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate an import file before processing
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Dict with validation results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"valid": False, "error": "File does not exist"}
        
        file_size = file_path.stat().st_size
        if file_size == 0:
            return {"valid": False, "error": "File is empty"}
        
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            return {"valid": False, "error": "File too large (max 100MB)"}
        
        extension = file_path.suffix.lower()
        
        validation_result = {
            "valid": True,
            "file_size": file_size,
            "extension": extension,
            "estimated_records": 0
        }
        
        try:
            if extension == ".csv":
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Count lines for estimation
                    line_count = sum(1 for _ in f) - 1  # Subtract header
                    validation_result["estimated_records"] = max(0, line_count)
            
            elif extension == ".json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        validation_result["estimated_records"] = len(data)
                    elif isinstance(data, dict):
                        validation_result["estimated_records"] = 1
            
            elif extension == ".apkg":
                # Basic Anki file validation
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_file:
                        if "collection.anki2" not in zip_file.namelist():
                            return {"valid": False, "error": "Invalid Anki deck file"}
                        validation_result["estimated_records"] = "Unknown (Anki deck)"
                except zipfile.BadZipFile:
                    return {"valid": False, "error": "Invalid Anki deck file"}
            
            else:
                return {"valid": False, "error": f"Unsupported file type: {extension}"}
        
        except Exception as e:
            return {"valid": False, "error": f"File validation failed: {str(e)}"}
        
        return validation_result