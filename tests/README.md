# Tests for Transcribe-JP

Comprehensive test suite for the transcribe-jp project.

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/unit/test_processing_utils.py
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run tests by marker
```bash
pytest -m unit          # Run only unit tests
pytest -m slow          # Run only slow tests
pytest -m "not slow"    # Skip slow tests
```

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── unit/                            # Unit tests
│   ├── test_config.py              # Config loading tests (8 tests)
│   ├── test_processing_utils.py    # Utils tests (22 tests)
│   └── test_filters_hallucination.py  # Hallucination filter tests (24 tests)
└── fixtures/                        # Test data and fixtures
```

## Test Coverage

### Core Modules (8 tests)
- `core.config._get_value()` - Configuration key resolution
- `core.config.load_config()` - Config file loading
- Backward compatibility with UPPERCASE and snake_case

### Processing Utils (22 tests)
- `format_timestamp()` - VTT timestamp formatting
- `clean_sound_effects()` - Text cleaning
- `simplify_repetitions()` - Repetition handling
- `split_long_lines()` - Line breaking logic

### Hallucination Filters (24 tests)
- `is_only_repetitive_stammer()` - Stammer detection
- `merge_single_char_segments()` - Single char merging
- `condense_word_repetitions()` - Repetition condensing
- `detect_global_hallucination_words()` - Global detection

## Writing New Tests

### Test Organization

Tests are organized by module and functionality:

```python
class TestFunctionName:
    """Test the function_name function"""

    def test_basic_case(self):
        """Test description"""
        result = function_name(input)
        assert result == expected

    def test_edge_case(self):
        """Test edge case"""
        result = function_name(edge_input)
        assert result == expected_edge
```

### Using Fixtures

Common fixtures are defined in `conftest.py`:

```python
def test_with_config(sample_config):
    """Use the sample_config fixture"""
    result = process_with_config(sample_config)
    assert result is not None
```

### Test Markers

Mark tests appropriately:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.slow
def test_expensive_operation():
    pass

@pytest.mark.requires_ffmpeg
def test_audio_processing():
    pass
```

## Test Guidelines

1. **Test One Thing**: Each test should verify one specific behavior
2. **Descriptive Names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests clearly
   ```python
   # Arrange
   input_data = "test"

   # Act
   result = function(input_data)

   # Assert
   assert result == expected
   ```
4. **Test Edge Cases**: Empty strings, None, extreme values
5. **Japanese Text**: Include Japanese text in relevant tests
6. **Fixtures**: Use fixtures for reusable test data
7. **Mocking**: Mock external dependencies (ffmpeg, Whisper, APIs)

## Current Test Results

```
========== 54 tests passed in 0.09s ==========
```

### Breakdown:
- ✅ Config tests: 8/8 passing
- ✅ Processing utils: 22/22 passing
- ✅ Hallucination filters: 24/24 passing

## Adding New Tests

When adding new functionality:

1. Create test file: `tests/unit/test_module_name.py`
2. Add test class: `class TestFunctionName:`
3. Write test methods: `def test_specific_behavior(self):`
4. Run tests: `pytest tests/unit/test_module_name.py -v`
5. Check coverage: `pytest --cov=module_name`

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest tests/ --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors
Make sure you're running from the project root:
```bash
cd /path/to/transcribe-jp
pytest
```

### Missing Dependencies
Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Encoding Issues
Tests use UTF-8 for Japanese text. Ensure your terminal supports UTF-8.

## Future Test Areas

Areas that could benefit from additional testing:

- [ ] `processing.segmentation` - Segment splitting logic
- [ ] `processing.merging` - Segment merging
- [ ] `filters.duplicates` - Duplicate removal
- [ ] `filters.timing` - Timing validation
- [ ] `core.vtt_writer` - VTT generation pipeline
- [ ] Integration tests with actual audio files
- [ ] LLM module tests (with mocking)
