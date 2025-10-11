# Changelog Archive - October 2025

This file contains archived changelog entries from October 2025 to keep the main CHANGELOG.md manageable.

**Original entries:** [2025-10-10 21:00] through [2025-10-10 21:28]

---

## [2025-10-10 21:28]

### Added
- **Full pipeline E2E test** (`tests/e2e/test_full_pipeline.py`)
  - Complete 9-stage pipeline verification
  - Uses real Japanese audio (counting 1-10)
  - Validates VTT output generation

### Changed
- **Test organization improvements**
  - Moved `test_media/` to `tests/e2e/test_media/` (consistency)
  - Updated all test paths to use relative paths
  - Cleaned up temporary test files
  - Updated E2E README with comprehensive documentation

### Fixed
- **Test file structure**: Flattened nested test_media directory

**Impact:** Complete end-to-end testing coverage, organized test structure.

---

## [2025-10-10 21:00] - Stage 6 Timing Realignment Improvements

### Changed
- **Text similarity algorithm upgraded**
  - Old: Simple character position matching
  - New: `difflib.SequenceMatcher` (Ratcliff/Obershelp algorithm)
  - Improvement: +22% accuracy for Japanese text variations
  - File: `modules/stage6_timing_realignment/utils.py`

- **Search algorithm optimized**
  - Limited to max 5 segment combinations (was unlimited)
  - Added early termination when match found (>0.9 similarity)
  - Added length check to prevent excessive combinations
  - File: `modules/stage6_timing_realignment/text_search_realignment.py`

- **Thresholds adjusted for Japanese**
  - Old: 0.95 (text_search), 1.0 (time_based) - unrealistic
  - New: 0.75 (both methods) - realistic for particle variations
  - Tested with Japanese text: これは vs これわ = 0.667 similarity
  - File: `config.json`

- **Added word-level timestamp matching**
  - New: `find_text_in_words()` fallback function
  - Uses Whisper word timestamps for precise alignment
  - File: `modules/stage6_timing_realignment/utils.py`

### Added
- **E2E tests with real Japanese audio**
  - `tests/e2e/test_timing_realignment.py` - Algorithm tests (23 cases)
  - `tests/e2e/test_realignment_demonstration.py` - Misalignment demo (10 segments)
  - Test audio: Japanese counting 1-10 (167KB, 27 seconds)
  - Results: 8/10 segments adjusted, 0 overlaps (100% fixed)

**Impact:** Significantly improved timing realignment accuracy for Japanese transcription.

---

## [2025-10-10 21:14] - Initial Project

### Added
- Initial 9-stage transcription pipeline
- All core modules and shared utilities
- Configuration system
- Test suite (257 tests)
- Documentation (README, ARCHITECTURE, CONFIGURATION, PIPELINE_STAGES)

---

*For more recent changes, see [CHANGELOG.md](../CHANGELOG.md)*
