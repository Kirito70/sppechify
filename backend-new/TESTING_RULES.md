# Testing Convention and Rules

## 📋 Testing Rules for Japanese Learning App

### **MANDATORY TESTING RULES**

1. **USE PYTEST FRAMEWORK ONLY**
   - All tests must use pytest framework
   - All test files must be in `backend-new/tests/` directory
   - All test files must follow `test_*.py` naming convention
   - All test classes must start with `Test*`
   - All test functions must start with `test_*`

2. **NO CUSTOM TEST FILES OUTSIDE TESTS DIRECTORY**
   - ❌ **NEVER create test files in root directory**
   - ❌ **NEVER create standalone test scripts**  
   - ❌ **NEVER use print() based tests**
   - ✅ **ALWAYS use pytest framework and fixtures**

3. **TEST ORGANIZATION**
   ```
   backend-new/tests/
   ├── conftest.py              # Shared fixtures
   ├── test_app_startup.py      # App startup & configuration tests
   ├── test_basic_connection.py # Database connection tests
   ├── test_japanese_api.py     # Japanese learning API tests
   ├── test_user.py            # User management tests
   └── helpers/                # Test helper modules
       ├── generators.py
       └── mocks.py
   ```

4. **TEST EXECUTION COMMANDS**
   ```bash
   # Run all tests
   cd backend-new && uv run pytest tests/
   
   # Run specific test file
   cd backend-new && uv run pytest tests/test_japanese_api.py
   
   # Run specific test class
   cd backend-new && uv run pytest tests/test_japanese_api.py::TestJapaneseSentencesAPI
   
   # Run specific test
   cd backend-new && uv run pytest tests/test_japanese_api.py::TestJapaneseSentencesAPI::test_get_sentences_empty_list
   
   # Run with verbose output
   cd backend-new && uv run pytest tests/ -v
   ```

### **TEST CATEGORIES AND MARKERS**

Use pytest markers to categorize tests:

```python
@pytest.mark.unit          # Fast unit tests (no external dependencies)
@pytest.mark.integration   # Integration tests (require database/external services)  
@pytest.mark.japanese      # Japanese learning specific tests
@pytest.mark.api          # API endpoint tests
@pytest.mark.database     # Database-related tests
@pytest.mark.slow         # Tests that take more than a few seconds
```

### **FIXTURE CONVENTIONS**

Available fixtures in `conftest.py`:
- `client`: FastAPI TestClient for API testing
- `db`: Database session for integration tests
- `mock_db`: Mock database for unit tests
- `mock_redis`: Mock Redis for unit tests
- `sample_user_data`: Sample user data for tests
- `sample_japanese_sentence_data`: Sample Japanese sentence data
- `sample_user_progress_data`: Sample user progress data

### **TEST STRUCTURE EXAMPLE**

```python
"""Module docstring explaining what is being tested."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


class TestJapaneseLearning:
    """Test Japanese learning functionality."""
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality with no dependencies."""
        # Unit test code here
        assert True
    
    @pytest.mark.integration  
    def test_api_integration(self, client: TestClient):
        """Test API integration with test client."""
        response = client.get("/api/v1/sentences")
        assert response.status_code == 200
        
    @pytest.mark.japanese
    @pytest.mark.asyncio
    async def test_async_functionality(self, mock_db):
        """Test async functionality with mocks.""" 
        # Async test code here
        pass
```

### **TESTING BEST PRACTICES**

1. **Test Naming**
   - Use descriptive test names: `test_get_sentences_with_valid_jlpt_level`
   - Not: `test_sentences` or `test1`

2. **Test Independence**
   - Each test should be independent
   - Use fixtures for setup/teardown
   - Don't rely on test execution order

3. **Mock External Dependencies**
   - Mock database calls for unit tests
   - Mock external API calls
   - Use `mock_db` and `mock_redis` fixtures

4. **Assert Patterns**
   ```python
   # Good assertions
   assert response.status_code == 200
   assert "japanese_text" in response.json()
   assert len(data["sentences"]) == 5
   
   # Avoid generic assertions
   assert response  # Too generic
   assert True      # Meaningless
   ```

### **SKIP CONDITIONS**

Use pytest skip for conditional tests:
```python
@pytest.mark.skipif(condition, reason="Reason for skipping")
def test_conditional_feature():
    pass

def test_with_import_skip():
    pytest.importorskip("optional_dependency")
    # Test code here
```

### **ERROR HANDLING TESTS**

```python
def test_error_conditions():
    with pytest.raises(ValueError, match="Expected error message"):
        # Code that should raise ValueError
        pass
```

### **COMMANDS FOR DEVELOPERS**

```bash
# Install test dependencies
cd backend-new && uv add --dev pytest faker pytest-mock

# Run tests with coverage (optional)
cd backend-new && uv run pytest tests/ --cov=src

# Run only fast tests
cd backend-new && uv run pytest tests/ -m "not slow"

# Run only Japanese learning tests  
cd backend-new && uv run pytest tests/ -m japanese

# Run tests matching pattern
cd backend-new && uv run pytest tests/ -k "japanese"
```

---

## **⚠️ CRITICAL RULE FOR AI ASSISTANT**

**NEVER CREATE STANDALONE TEST FILES OR SCRIPTS**

When asked to test functionality:
1. ✅ Add tests to existing test files in `tests/` directory
2. ✅ Use pytest framework and fixtures  
3. ✅ Follow existing test patterns in the codebase
4. ❌ NEVER create test files outside `tests/` directory
5. ❌ NEVER create custom test runners or scripts
6. ❌ NEVER use print() based testing

**Example of what NOT to do:**
```bash
# ❌ DON'T DO THIS
python test_my_feature.py
python -c "print('Testing...')"
```

**Example of what TO do:**
```bash 
# ✅ DO THIS
cd backend-new && uv run pytest tests/test_japanese_api.py::TestJapaneseSentencesAPI::test_get_sentences_empty_list
```

---

**Current Test Status: ✅ 27 PASSED, 1 SKIPPED, 7 ERRORS**
- App startup tests: ✅ Working
- Database connection tests: ✅ Working  
- Japanese API tests: ✅ Working
- Basic integration tests: ✅ Working
- User tests: ⚠️ Need schema fixes (7 errors due to missing Japanese learning fields)