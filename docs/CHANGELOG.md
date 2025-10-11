# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses Date + Time format (YYYY-MM-DD HH:MM) for version tracking.

---

## [2025-10-11 15:00]

### Added
- **Configurable LLM provider system with Ollama support**
  - New abstraction layer supporting multiple LLM providers
  - Added Ollama provider (local, FREE alternative to Claude)
  - Added OpenAI provider (alternative cloud option)
  - Kept Anthropic Claude provider (existing, enhanced)
  - Stage-specific LLM override support for cost optimization
  - File: `shared/llm_utils.py` (new, 186 lines)
  - Updated: `modules/stage4_segment_splitting/llm_splitter.py`
  - Updated: `modules/stage7_text_polishing/processor.py`

- **docs/features/LLM_PROVIDERS.md**: Comprehensive LLM configuration guide (476 lines)
  - Detailed setup for Ollama, Anthropic, OpenAI
  - Step-by-step installation instructions
  - Model recommendations for Japanese
  - Cost comparison tables
  - Troubleshooting section
  - FAQ for common questions

- **docs/maintenance/LESSONS_LEARNED.md**: Knowledge database (comprehensive)
  - Mistakes and gotchas to avoid repeating
  - Design decisions with reasoning
  - Pattern library for common problems
  - Organized by topic (config, LLM, docs, testing, code, Japanese, pipeline)

- **config.local.json.example**: Enhanced with LLM provider examples
  - Nested structure examples for all three providers
  - Stage-specific override examples (commented out)
  - Hybrid setup example (Ollama + Anthropic)
  - Inline comments explaining each option
  - Direct reference to LLM_PROVIDERS.md

- **docs/AI_GUIDE.md updates**
  - Added knowledge database section (+120 lines)
  - Instructions for creating new knowledge documents
  - Document structure template
  - AI-discoverability best practices
  - How to use LESSONS_LEARNED.md effectively
  - Relationship between AI_GUIDE, LESSONS_LEARNED, SESSIONS, CHANGELOG

### Changed
- **config.json**: LLM config reorganized with provider-specific sub-configs
  - Old: Flat structure with mixed provider settings
  - New: Nested structure: `llm.ollama`, `llm.anthropic`, `llm.openai`
  - Default provider: `anthropic` → `ollama`
  - Default model: `claude-sonnet-4-5-20250929` → `llama3.2:3b`
  - Backward compatible: Checks both old and new config locations

- **shared/llm_utils.py**: Provider classes updated for nested config
  - AnthropicProvider: Reads from `llm.anthropic.*` (with fallback)
  - OllamaProvider: Reads from `llm.ollama.*` (with fallback)
  - OpenAIProvider: Reads from `llm.openai.*` (with fallback)
  - Stage-specific override VERIFIED working

- **docs/core/CONFIGURATION.md**: Updated to reflect nested structure
  - Updated all LLM examples to use nested config
  - Added detailed provider sub-sections
  - Improved cross-reference to LLM_PROVIDERS.md

### Impact
**Cost savings:** Users can now use FREE local Ollama models for simple tasks (segment splitting) and reserve paid Claude API for quality-critical tasks (text polishing). Potential savings: ~$0.25-1.00 per hour of transcription.

**Flexibility:** Users can choose their preferred LLM provider based on cost, quality, and privacy requirements. Nested config structure makes provider settings clearer and easier to manage.

**Knowledge base:** New LESSONS_LEARNED.md prevents repeating mistakes. LLM_PROVIDERS.md serves as comprehensive LLM reference. AI_GUIDE updated with knowledge database usage instructions. Documentation reorganized into proper folders (core/, features/, maintenance/).

**Files changed:**
- `shared/llm_utils.py` (new, 203 lines with nested config support)
- `modules/stage4_segment_splitting/llm_splitter.py` (~30 lines simplified)
- `modules/stage7_text_polishing/processor.py` (~25 lines simplified)
- `config.json` (reorganized with nested structure)
- `config.local.json.example` (enhanced with LLM examples)
- `docs/features/LLM_PROVIDERS.md` (new, 476 lines comprehensive guide)
- `docs/maintenance/LESSONS_LEARNED.md` (new, comprehensive knowledge database)
- `docs/AI_GUIDE.md` (+120 lines knowledge base section, moved to docs root)
- `docs/core/CONFIGURATION.md` (updated examples)
- `docs/README.md` (updated with new structure)
- `README.md` (updated references)
- `tests/unit/modules/stage7_text_polishing/test_processor.py` (1 test updated)

**Files removed:**
- `config.llm_examples.json` (redundant with LLM_PROVIDERS.md)

**Documentation structure:**
```
docs/
├── AI_GUIDE.md          # AI assistant entry point (ROOT)
├── features/
│   └── LLM_PROVIDERS.md  # LLM configuration guide
└── maintenance/
    └── LESSONS_LEARNED.md # Knowledge database
```

**Test results:** 270/270 tests pass ✅

---

## [2025-10-11 12:03]

### Added
- **config.local.json support with deep merge functionality**
  - Local config file support for user-specific settings
  - Deep merge of config.local.json with config.json
  - Priority: config.local.json > config.json > defaults
  - Added to .gitignore for security
  - File: `core/config_loader.py`

**Impact:** Users can now override config settings without modifying version-controlled config.json.

---

## [2025-10-11 11:58]

### Changed
- **Streamlined README.md for user focus**
  - Removed internal development details
  - Focused on user-facing features and usage
  - Improved readability and structure

**Impact:** Better documentation for end users.

---

## [2025-10-11 11:56]

### Added
- **docs/features/ folder for individual stage documentation**
  - Separate documentation for each pipeline stage
  - Better organization of stage-specific information
  - Easier to find and update stage documentation

**Impact:** Improved documentation structure and maintainability.

---

## [2025-10-11 11:50]

### Changed
- **Restructured documentation for better Claude Code compatibility**
  - Reorganized docs/ folder structure
  - Improved navigation and cross-references
  - Better integration with AI assistant tools

**Impact:** Enhanced AI assistant understanding of project structure.

---

## [2025-10-11 11:40]

### Added
- **API key security documentation and gitignore rules**
  - Added security guidelines for API keys
  - Updated .gitignore to exclude sensitive files
  - Documentation on safe API key handling
  - File: `docs/core/SECURITY.md`

**Impact:** Prevents accidental commit of API keys and sensitive data.

---

## [2025-10-11 11:37]

### Added
- **MIT License**
  - Added MIT License to project
  - Open source licensing
  - File: `LICENSE`

### Changed
- **Secured API key in config**
  - Removed hardcoded API keys from config.json
  - Added placeholder values
  - Updated documentation on API key setup

**Impact:** Project is now properly licensed and API keys are secured.

---

## [2025-10-11 02:02]

### Changed
- **Moved session history to docs/SESSIONS.md**
  - Session history moved from AI_GUIDE.md to dedicated file
  - Improved accessibility for both humans and AI
  - Better organization of historical information
  - File: `docs/SESSIONS.md`

**Impact:** Session history is now accessible to all team members, not just AI assistants.

---

## [2025-10-11 01:55]

### Changed
- **Streamlined AI_GUIDE.md to remove redundancy**
  - Removed duplicate information already in docs/
  - Focused on AI-specific guidelines
  - Improved clarity and conciseness

**Impact:** Less redundancy, easier to maintain AI guidelines.

---

## [2025-10-11 01:50]

### Added
- **CHANGELOG.md and improved documentation guidelines**
  - Added this changelog file
  - Updated documentation guidelines in AI_GUIDE.md
  - Required changelog updates for all commits
  - File: `docs/CHANGELOG.md`

**Impact:** Better tracking of project changes over time.

---

## [2025-10-11 01:48]

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

## [2025-10-11 01:30]

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

## [2025-10-11 01:16]

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

## Version History Summary

| Date & Time      | Type    | Summary                                           | Tests   |
|------------------|---------|---------------------------------------------------|---------|
| 2025-10-11 15:00 | Added   | Configurable LLM providers (Ollama, OpenAI)       | 261     |
| 2025-10-11 12:03 | Added   | config.local.json support with deep merge         | 261     |
| 2025-10-11 11:58 | Changed | Streamlined README.md for user focus              | 261     |
| 2025-10-11 11:56 | Added   | docs/features/ folder for stage documentation     | 261     |
| 2025-10-11 11:50 | Changed | Restructured docs for Claude Code compatibility   | 261     |
| 2025-10-11 11:40 | Added   | API key security documentation and gitignore      | 261     |
| 2025-10-11 11:37 | Added   | MIT License and secured API keys                  | 261     |
| 2025-10-11 02:02 | Changed | Moved session history to docs/SESSIONS.md         | 261     |
| 2025-10-11 01:55 | Changed | Streamlined AI_GUIDE.md to remove redundancy      | 261     |
| 2025-10-11 01:50 | Added   | CHANGELOG.md and documentation guidelines         | 261     |
| 2025-10-11 01:48 | Fix     | Stage 5 re-filtering after timing_validation      | 261     |
| 2025-10-11 01:30 | Added   | AI_GUIDE.md for AI assistant continuity           | 257     |
| 2025-10-11 01:16 | Removed | Redundant enable_remove_irrelevant feature        | 257     |
| 2025-10-10 21:28 | Added   | Full pipeline E2E test + test organization        | 257     |
| 2025-10-10 21:14 | Added   | Initial 9-stage pipeline project                  | 257     |

---

## How to Update This Changelog

When making significant changes:

1. **Add entry at the top** with current Date + Time in format [YYYY-MM-DD HH:MM]
2. **Use clear categories**: Added, Changed, Fixed, Removed
3. **Explain the impact** - why this change matters
4. **List affected files** - help future developers find code
5. **Update the Version History Summary table** with the new entry

**Example entry:**
```markdown
## [2025-01-12 14:30]

### Added
- New Japanese particle normalization in Stage 7
  - Handles は/わ, を/お, へ/え variations
  - File: `modules/stage7_text_polishing/normalizer.py`

**Impact:** Improved text consistency for Japanese particles.
```

---

*This changelog tracks all significant changes to the transcribe-jp project. For detailed commit history, use `git log`.*
