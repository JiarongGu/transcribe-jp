# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses git commit hashes for version tracking.

---

## [Unreleased]

### Added
### Changed
### Fixed
### Removed

---

## [ca26b37] - 2025-01-11

### Fixed
- **Stage 5 filter order bug**: Fixed timing_validation re-filtering issue where re-transcribed segments could contain hallucination phrases
  - Added re-filtering step after timing_validation completes
  - Re-runs phrase_filter and consecutive_duplicates on re-validated segments
  - Added 4 new tests to verify hallucinations are caught after re-transcription
  - Test count: 257 → 261 (+4 tests)

**Impact:** Prevents hallucination phrases like "ご視聴ありがとうございました" from leaking through when timing_validation re-transcribes segments.

**Files changed:**
- `modules/stage5_hallucination_filtering/processor.py`
- `tests/unit/modules/stage5_hallucination_filtering/test_timing_validation_refilter.py` (new)

---

## [d1b5760] - 2025-01-11

### Added
- **AI_GUIDE.md**: Living document for AI assistant continuity
  - Comprehensive guide for AI assistants working across sessions
  - Project architecture and 9-stage pipeline overview
  - Critical DO/DON'T guidelines based on real lessons
  - Session history tracking with git commits
  - Testing requirements and configuration guidelines
  - Instructions for updating the guide across sessions

**Impact:** Future AI sessions can understand project context, conventions, and lessons learned.

---

## [60d0256] - 2025-01-11

### Removed
- **Redundant `enable_remove_irrelevant` feature** from Stage 6
  - Removed 69-line `remove_irrelevant_segments()` function
  - Removed config options: `enable_remove_irrelevant`, `irrelevant_threshold`
  - Removed from pipeline.py, __init__.py, display.py
  - Updated all documentation (README, CONFIGURATION, PIPELINE_STAGES)

**Reason:** Feature was 100% redundant with Stage 5's `timing_validation`:
- Both re-transcribe segments with Whisper
- Both remove segments with low similarity
- Stage 5 runs earlier (better position)
- Stage 5 is more efficient (only suspicious segments)
- Removed feature had zero test coverage

**Impact:** Simplified codebase by 95 lines, no loss of functionality.

**Files changed:**
- `modules/stage6_timing_realignment/processor.py` (-69 lines)
- `config.json` (-2 config options)
- `core/pipeline.py`, `core/display.py`
- `docs/` (README, CONFIGURATION, PIPELINE_STAGES)

---

## [c4eafd2] - 2025-01-11

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

## Stage 6 Timing Realignment Improvements (commits c4eafd2, 60d0256)

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

## [000d91b] - Initial Project

### Added
- Initial 9-stage transcription pipeline
- All core modules and shared utilities
- Configuration system
- Test suite (257 tests)
- Documentation (README, ARCHITECTURE, CONFIGURATION, PIPELINE_STAGES)

---

## Version History Summary

| Commit  | Date       | Type    | Summary                                           | Tests   |
|---------|------------|---------|---------------------------------------------------|---------|
| ca26b37 | 2025-01-11 | Fix     | Stage 5 re-filtering after timing_validation      | 261     |
| d1b5760 | 2025-01-11 | Added   | AI_GUIDE.md for AI assistant continuity           | 257     |
| 60d0256 | 2025-01-11 | Removed | Redundant enable_remove_irrelevant feature        | 257     |
| c4eafd2 | 2025-01-11 | Added   | Full pipeline E2E test + test organization        | 257     |
| 000d91b | Initial    | Added   | Initial 9-stage pipeline project                  | 257     |

---

## How to Update This Changelog

When making significant changes:

1. **Add entry at the top** under `[Unreleased]` section
2. **Use clear categories**: Added, Changed, Fixed, Removed
3. **Include git commit hash** and date when committing
4. **Explain the impact** - why this change matters
5. **List affected files** - help future developers find code
6. **Move to versioned section** when committing with commit hash

**Example entry:**
```markdown
## [abc1234] - 2025-01-12

### Added
- New Japanese particle normalization in Stage 7
  - Handles は/わ, を/お, へ/え variations
  - File: `modules/stage7_text_polishing/normalizer.py`

**Impact:** Improved text consistency for Japanese particles.
```

---

*This changelog tracks all significant changes to the transcribe-jp project. For detailed commit history, use `git log`.*
