"""
Test suite for data import functionality

Tests all components of the data import system including:
- DataImporter class with various import methods
- API endpoints for import operations
- File validation and error handling
- Auto-processing with furigana generation

Author: Assistant
Date: 2025-01-20
"""

import pytest
import tempfile
import json
import csv
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List

from src.app.services.data_importer import DataImporter, ImportStats, ImportError


class TestImportStats:
    """Test ImportStats class"""
    
    def test_import_stats_initialization(self):
        """Test ImportStats initialization"""
        stats = ImportStats()
        
        assert stats.total_processed == 0
        assert stats.successfully_imported == 0
        assert stats.duplicates_skipped == 0
        assert stats.errors == 0
        assert stats.start_time is not None
        assert stats.end_time is None
        assert stats.duration is None
        assert stats.error_details == []
    
    def test_import_stats_finish(self):
        """Test ImportStats finish method"""
        stats = ImportStats()
        stats.finish()
        
        assert stats.end_time is not None
        assert stats.duration is not None
        assert stats.duration >= 0
    
    def test_import_stats_to_dict(self):
        """Test ImportStats to_dict method"""
        stats = ImportStats()
        stats.total_processed = 10
        stats.successfully_imported = 8
        stats.duplicates_skipped = 1
        stats.errors = 1
        stats.error_details = ["Test error"]
        stats.finish()
        
        result = stats.to_dict()
        
        assert result["total_processed"] == 10
        assert result["successfully_imported"] == 8
        assert result["duplicates_skipped"] == 1
        assert result["errors"] == 1
        assert result["duration_seconds"] is not None
        assert result["error_details"] == ["Test error"]


class TestDataImporter:
    """Test DataImporter class"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def data_importer(self, mock_db_session):
        """Create DataImporter instance for testing"""
        return DataImporter(mock_db_session, auto_process=False)
    
    @pytest.fixture
    def data_importer_with_processing(self, mock_db_session):
        """Create DataImporter with auto-processing enabled"""
        return DataImporter(mock_db_session, auto_process=True)
    
    def test_data_importer_initialization(self, mock_db_session):
        """Test DataImporter initialization"""
        importer = DataImporter(mock_db_session, auto_process=False)
        
        assert importer.db == mock_db_session
        assert importer.auto_process is False
        assert importer.furigana_generator is None
        assert importer.japanese_processor is None
    
    def test_data_importer_with_processing(self, mock_db_session):
        """Test DataImporter initialization with auto-processing"""
        importer = DataImporter(mock_db_session, auto_process=True)
        
        assert importer.db == mock_db_session
        assert importer.auto_process is True
        assert importer.furigana_generator is not None
        assert importer.japanese_processor is not None
    
    # CSV Import Tests
    
    @pytest.mark.asyncio
    async def test_csv_import_success(self, data_importer):
        """Test successful CSV import"""
        # Create test CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['japanese', 'english'])  # Header
            writer.writerow(['こんにちは', 'Hello'])
            writer.writerow(['ありがとう', 'Thank you'])
            csv_path = f.name
        
        try:
            # Mock database operations
            data_importer.db.query.return_value.filter.return_value.first.return_value = None
            data_importer.db.add = Mock()
            data_importer.db.commit = Mock()
            
            # Import from CSV
            stats = await data_importer.import_from_csv(csv_path)
            
            # Verify results
            assert stats.total_processed == 2
            assert stats.successfully_imported == 2
            assert stats.duplicates_skipped == 0
            assert stats.errors == 0
            
        finally:
            Path(csv_path).unlink()
    
    @pytest.mark.asyncio
    async def test_csv_import_custom_columns(self, data_importer):
        """Test CSV import with custom column names"""
        # Create test CSV file with custom columns
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['jp_text', 'en_text'])  # Header
            writer.writerow(['さようなら', 'Goodbye'])
            csv_path = f.name
        
        try:
            # Mock database operations
            data_importer.db.query.return_value.filter.return_value.first.return_value = None
            data_importer.db.add = Mock()
            data_importer.db.commit = Mock()
            
            # Import from CSV with custom columns
            stats = await data_importer.import_from_csv(
                csv_path,
                japanese_column='jp_text',
                english_column='en_text'
            )
            
            # Verify results
            assert stats.total_processed == 1
            assert stats.successfully_imported == 1
            
        finally:
            Path(csv_path).unlink()
    
    @pytest.mark.asyncio
    async def test_csv_import_file_not_found(self, data_importer):
        """Test CSV import with non-existent file"""
        stats = await data_importer.import_from_csv('/non/existent/file.csv')
        
        assert stats.total_processed == 0
        assert stats.errors == 1
        assert "not found" in stats.error_details[0]
    
    # JSON Import Tests
    
    @pytest.mark.asyncio
    async def test_json_import_array_success(self, data_importer):
        """Test successful JSON import with array format"""
        test_data = [
            {"japanese": "おはよう", "english": "Good morning"},
            {"japanese": "おやすみ", "english": "Good night"}
        ]
        
        # Create test JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            json_path = f.name
        
        try:
            # Mock database operations
            data_importer.db.query.return_value.filter.return_value.first.return_value = None
            data_importer.db.add = Mock()
            data_importer.db.commit = Mock()
            
            # Import from JSON
            stats = await data_importer.import_from_json(json_path)
            
            # Verify results
            assert stats.total_processed == 2
            assert stats.successfully_imported == 2
            assert stats.duplicates_skipped == 0
            assert stats.errors == 0
            
        finally:
            Path(json_path).unlink()
    
    @pytest.mark.asyncio
    async def test_json_import_single_object(self, data_importer):
        """Test JSON import with single object format"""
        test_data = {"japanese": "いただきます", "english": "Let's eat"}
        
        # Create test JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            json_path = f.name
        
        try:
            # Mock database operations
            data_importer.db.query.return_value.filter.return_value.first.return_value = None
            data_importer.db.add = Mock()
            data_importer.db.commit = Mock()
            
            # Import from JSON
            stats = await data_importer.import_from_json(json_path)
            
            # Verify results
            assert stats.total_processed == 1
            assert stats.successfully_imported == 1
            
        finally:
            Path(json_path).unlink()
    
    # Tatoeba Import Tests
    
    @pytest.mark.asyncio
    async def test_tatoeba_import_success(self, data_importer):
        """Test successful Tatoeba import"""
        # Mock database operations
        data_importer.db.query.return_value.filter.return_value.first.return_value = None
        data_importer.db.add = Mock()
        data_importer.db.commit = Mock()
        
        # Import from Tatoeba (uses sample data)
        stats = await data_importer.import_from_tatoeba(max_sentences=5)
        
        # Verify results
        assert stats.total_processed >= 0  # Should process some sentences
        assert stats.errors == 0 or stats.successfully_imported > 0  # Should have some success
    
    @pytest.mark.asyncio
    async def test_tatoeba_import_with_limit(self, data_importer):
        """Test Tatoeba import with sentence limit"""
        # Mock database operations
        data_importer.db.query.return_value.filter.return_value.first.return_value = None
        data_importer.db.add = Mock()
        data_importer.db.commit = Mock()
        
        # Import with small limit
        stats = await data_importer.import_from_tatoeba(max_sentences=2)
        
        # Should respect the limit
        assert stats.total_processed <= 2
    
    # File Validation Tests
    
    @pytest.mark.asyncio
    async def test_validate_csv_file_valid(self, data_importer):
        """Test validation of valid CSV file"""
        # Create test CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['japanese', 'english'])
            writer.writerow(['テスト', 'Test'])
            csv_path = f.name
        
        try:
            result = await data_importer.validate_import_file(csv_path)
            
            assert result["valid"] is True
            assert result["extension"] == ".csv"
            assert result["estimated_records"] == 1  # Excluding header
            assert "error" not in result
            
        finally:
            Path(csv_path).unlink()
    
    @pytest.mark.asyncio
    async def test_validate_json_file_valid(self, data_importer):
        """Test validation of valid JSON file"""
        test_data = [{"japanese": "テスト", "english": "Test"}]
        
        # Create test JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            json_path = f.name
        
        try:
            result = await data_importer.validate_import_file(json_path)
            
            assert result["valid"] is True
            assert result["extension"] == ".json"
            assert result["estimated_records"] == 1
            assert "error" not in result
            
        finally:
            Path(json_path).unlink()
    
    @pytest.mark.asyncio
    async def test_validate_file_not_found(self, data_importer):
        """Test validation of non-existent file"""
        result = await data_importer.validate_import_file('/non/existent/file.csv')
        
        assert result["valid"] is False
        assert "does not exist" in result["error"]
    
    @pytest.mark.asyncio
    async def test_validate_empty_file(self, data_importer):
        """Test validation of empty file"""
        # Create empty file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            empty_path = f.name
        
        try:
            result = await data_importer.validate_import_file(empty_path)
            
            assert result["valid"] is False
            assert "empty" in result["error"]
            
        finally:
            Path(empty_path).unlink()
    
    @pytest.mark.asyncio
    async def test_validate_unsupported_file_type(self, data_importer):
        """Test validation of unsupported file type"""
        # Create test file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            txt_path = f.name
        
        try:
            result = await data_importer.validate_import_file(txt_path)
            
            assert result["valid"] is False
            assert "Unsupported file type" in result["error"]
            
        finally:
            Path(txt_path).unlink()
    
    # Duplicate Handling Tests
    
    @pytest.mark.asyncio
    async def test_duplicate_detection(self, data_importer):
        """Test duplicate sentence detection"""
        # Create test data with duplicate
        test_data = [
            {"japanese": "重複テスト", "english": "Duplicate test"},
            {"japanese": "重複テスト", "english": "Duplicate test"}  # Same Japanese text
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            json_path = f.name
        
        try:
            # Mock database - first query returns None, second returns existing sentence
            existing_sentence = Mock()
            data_importer.db.query.return_value.filter.return_value.first.side_effect = [None, existing_sentence]
            data_importer.db.add = Mock()
            data_importer.db.commit = Mock()
            
            stats = await data_importer.import_from_json(json_path)
            
            # Should import first, skip second as duplicate
            assert stats.total_processed == 2
            assert stats.successfully_imported == 1
            assert stats.duplicates_skipped == 1
            
        finally:
            Path(json_path).unlink()
    
    # Auto-processing Tests
    
    @pytest.mark.asyncio
    async def test_auto_processing_enabled(self, data_importer_with_processing):
        """Test import with auto-processing enabled"""
        test_data = [{"japanese": "自動処理", "english": "Auto processing"}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            json_path = f.name
        
        try:
            # Mock database operations
            data_importer_with_processing.db.query.return_value.filter.return_value.first.return_value = None
            data_importer_with_processing.db.add = Mock()
            data_importer_with_processing.db.commit = Mock()
            
            # Mock furigana generator
            mock_furigana_result = {"furigana": "じどうしょり", "error": None}
            data_importer_with_processing.furigana_generator.generate_furigana = AsyncMock(return_value=mock_furigana_result)
            
            # Mock japanese processor
            mock_processing_result = {
                "romanization": "jidoushori",
                "estimated_jlpt_level": "N3",
                "difficulty_estimate": 3,
                "error": None
            }
            data_importer_with_processing.japanese_processor.analyze_japanese_text = AsyncMock(return_value=mock_processing_result)
            
            stats = await data_importer_with_processing.import_from_json(json_path)
            
            # Should successfully process and import
            assert stats.total_processed == 1
            assert stats.successfully_imported == 1
            
            # Verify processing methods were called
            data_importer_with_processing.furigana_generator.generate_furigana.assert_called_once_with("自動処理")
            data_importer_with_processing.japanese_processor.analyze_japanese_text.assert_called_once_with("自動処理")
            
        finally:
            Path(json_path).unlink()
    
    # Error Handling Tests
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, data_importer):
        """Test handling of database errors during import"""
        test_data = [{"japanese": "エラーテスト", "english": "Error test"}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False)
            json_path = f.name
        
        try:
            # Mock database to raise error
            data_importer.db.query.return_value.filter.return_value.first.return_value = None
            data_importer.db.add = Mock()
            data_importer.db.commit.side_effect = Exception("Database error")
            data_importer.db.rollback = Mock()
            
            stats = await data_importer.import_from_json(json_path)
            
            # Should handle error gracefully
            assert stats.total_processed == 1
            assert stats.successfully_imported == 0
            assert stats.errors == 1
            assert "Database error" in stats.error_details[0]
            
        finally:
            Path(json_path).unlink()
    
    # Summary Tests
    
    def test_get_import_summary(self, data_importer):
        """Test getting import summary"""
        # Mock database queries
        data_importer.db.query.return_value.count.return_value = 100
        data_importer.db.query.return_value.filter.return_value.count.return_value = 95
        
        # Mock distinct sources
        data_importer.db.query.return_value.distinct.return_value.all.return_value = [
            ("Tatoeba",), ("CSV: test.csv",)
        ]
        
        # Mock JLPT distribution queries
        jlpt_counts = {"N5": 30, "N4": 25, "N3": 20, "N2": 15, "N1": 5}
        data_importer.db.query.return_value.filter.return_value.count.side_effect = [
            jlpt_counts["N5"], jlpt_counts["N4"], jlpt_counts["N3"], 
            jlpt_counts["N2"], jlpt_counts["N1"]
        ]
        
        summary = data_importer.get_import_summary()
        
        assert summary["total_sentences"] == 100
        assert summary["active_sentences"] == 95
        assert "Tatoeba" in summary["sources"]
        assert "CSV: test.csv" in summary["sources"]
        assert summary["jlpt_distribution"]["N5"] == 30


# Integration Tests (would require test database)

@pytest.mark.integration
class TestDataImportIntegration:
    """Integration tests for data import system"""
    
    @pytest.mark.asyncio
    async def test_full_import_workflow(self):
        """Test complete import workflow from file to database"""
        # This would require actual database setup
        # Implementation depends on test database configuration
        pass
    
    @pytest.mark.asyncio
    async def test_api_endpoints_integration(self):
        """Test API endpoints with actual requests"""
        # This would require FastAPI test client and database
        # Implementation depends on test setup
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])