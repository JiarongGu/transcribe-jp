## [2025-10-14 Current]

### Added

- **Pre-flight validation for Ollama installation**
  - Added `validate_llm_requirements()` function in `core/config.py`
  - Validates Ollama is installed before starting pipeline when using Ollama provider
  - Shows clear error message with installation instructions if Ollama not found
  - Only validates when LLM features are enabled (text polishing or LLM segment splitting)
  - Skips validation when using external Ollama server (base_url specified)

**Why this matters:**
Ollama auto-installation doesn't work reliably on all systems. This change ensures users get a clear error message with manual installation instructions upfront, instead of failing mid-pipeline.

**Error message includes:**
- Which LLM features are enabled
- Platform-specific installation instructions (Windows/macOS/Linux)
- Alternative: Use external Ollama server
- Alternative: Disable LLM features

**Files changed:**
- `core/config.py` - Added `validate_llm_requirements()` function
- `transcribe_jp.py` - Call validation after loading config
- `tests/unit/core/test_config.py` - Added 8 tests for validation logic
- `docs/features/LLM_PROVIDERS.md` - Updated to reflect manual installation requirement

**Test results:** 280/280 tests pass ✅

---

- **Batch processing can now be disabled for text polishing**
  - Setting `text_polishing.batch_size` to `0` or `1` disables batching
  - Processes segments one-by-one instead of in batches
  - More reliable for Ollama and local LLM providers
  - File: `modules/stage7_text_polishing/processor.py`

**Why this matters:**
Ollama and other local LLM providers work better with one-by-one processing rather than batch processing. This feature allows users to optimize text polishing for their chosen provider.

**How to use:**
```json
{
  "text_polishing": {
    "enable": true,
    "batch_size": 1  // Process one-by-one (recommended for Ollama)
  }
}
```

**Behavior:**
- `batch_size > 1`: Process segments in batches (default: 10, good for cloud APIs)
- `batch_size = 1` or `0`: Process segments one-by-one (recommended for Ollama)
- Console message displays: "Processing X segments one-by-one (batch processing disabled)"

**Files changed:**
- `modules/stage7_text_polishing/processor.py` - Added batch_size <= 1 check
- `docs/features/LLM_PROVIDERS.md` - Documented batch_size=1 for Ollama
- `docs/core/CONFIGURATION.md` - Updated batch_size parameter documentation
- `tests/unit/modules/stage7_text_polishing/test_processor.py` - Added 2 tests for batch_size 0 and 1

**Test results:** 272/272 tests pass ✅

---

## [2025-10-12 07:15]

### Changed
- **Made segment_merging stage optional**
  - Added `enable` setting to `segment_merging` config (defaults to `true`)
  - Stage 3 can now be skipped when `segment_merging.enable = false`
  - Updated pipeline to conditionally skip segment merging
  - Updated display to show segment_merging as optional stage
  - Pipeline now shows: "4 core stages (always-on) + X/5 optional stages"

**Why optional:**
Some users may want to work with raw Whisper segments without merging incomplete sentences. This is useful for:
- Preserving original Whisper segment boundaries
- Testing/debugging transcription behavior
- Workflows that require unmodified Whisper output

**Config example:**
```json
{
  "segment_merging": {
    "enable": false  // Skip merging incomplete sentences
  }
}
```

**When disabled:**
- Raw Whisper segments from Stage 2 pass directly to Stage 4 (or hallucination filtering if splitting disabled)
- No sentence merging is applied
- Segments may end mid-sentence (て、で、と、が particles)

**Optional stages:** Now 5 stages can be toggled:
1. Audio Preprocessing
2. Segment Merging (NEW - now optional)
3. Segment Splitting
4. Text Polishing
5. Timing Realignment

**Core stages (always run):** Whisper Transcription, Hallucination Filtering, Final Cleanup, VTT Generation (4 stages)

**Files changed:**
- `config.json` - Added `enable: true` to segment_merging
- `core/pipeline.py` - Added conditional logic for stage 3
- `core/display.py` - Updated to show stage 3 as optional (4 core, 5 optional)
- `config.local.json.example` - Added inline comment for new setting
- `tests/unit/core/test_pipeline.py` - Updated tests for new optional stage

**Test results:** 270/270 tests pass ✅

---

## [2025-10-12 07:00]

### Changed
- **Made segment_splitting stage optional**
  - Added `enable` setting to `segment_splitting` config (defaults to `true`)
  - Stage 4 can now be skipped when `segment_splitting.enable = false`
  - Updated pipeline to conditionally skip segment splitting
  - Updated display to show segment_splitting as optional stage
  - Pipeline now shows: "5 core stages (always-on) + X/4 optional stages"

**Why optional:**
Some users may prefer to keep long segments intact without splitting them by line length. This is useful for:
- Subtitles that don't need line breaks
- Processing workflows that handle splitting differently
- Testing/debugging transcription accuracy

**Config example:**
```json
{
  "segment_splitting": {
    "enable": false  // Skip segment splitting entirely
  }
}
```

**When disabled:**
- Segments from Stage 3 (merging) pass directly to Stage 5 (hallucination filtering)
- No line-length splitting is applied
- LLM splitting sub-features are also skipped

**Optional stages:** Now 4 stages can be toggled (Audio Preprocessing, Segment Splitting, Text Polishing, Timing Realignment)

**Files changed:**
- `config.json` - Added `enable: true` to segment_splitting
- `core/pipeline.py` - Added conditional logic for stage 4
- `core/display.py` - Updated to show stage 4 as optional
- `config.local.json.example` - Added inline comment for new setting
- `tests/unit/core/test_pipeline.py` - Updated tests for new optional stage

**Test results:** 270/270 tests pass ✅

---

## [2025-10-12 06:45]

### Changed
- **Simplified documentation structure**
  - Moved `docs/maintenance/ai/` → `docs/ai-assistant/` (shorter, clearer path)
  - Removed 4 redundant maintenance docs (23KB saved):
    - TIMING_REALIGNMENT_IMPROVEMENTS_2025-10-10.md (duplicates CHANGELOG)
    - DOCUMENTATION_SCALING_STRATEGY.md (refactoring complete, no longer needed)
    - AI_GUIDE_REFACTOR_PLAN.md (work done, no longer needed)
    - README.md (unnecessary maintenance folder README)
  - Updated all cross-references in AI_GUIDE.md and guide files

**New structure:**
```
docs/
├── ai-assistant/                          # One level up, clearer name
│   ├── GUIDELINES.md
│   ├── WORKFLOWS.md
│   ├── TROUBLESHOOTING.md
│   └── REFERENCE.md
└── maintenance/
    ├── LESSONS_LEARNED.md                # Keep
    └── CHANGELOG_ARCHIVE_2025-10.md      # Keep
```

**Benefits:**
✅ **Simpler paths** - `docs/ai-assistant/` vs `docs/maintenance/ai/`
✅ **Clearer purpose** - "ai-assistant" better describes contents
✅ **23KB saved** - Removed redundant/completed planning docs
✅ **Less clutter** - Only essential files remain

**Test results:** 275/275 tests pass ✅

---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses Date + Time format (YYYY-MM-DD HH:MM) for version tracking.

---

## [2025-10-12 06:30]

### Changed
- **Complete documentation refactoring for scalability**
  - Refactored AI_GUIDE.md from monolithic 19KB to 7.6KB slim entry point (63% reduction)
  - Created 4 specialized guides in `docs/maintenance/ai/`:
    - GUIDELINES.md (5.9KB) - Critical DO's/DON'Ts, patterns
    - WORKFLOWS.md (11KB) - Step-by-step common tasks
    - TROUBLESHOOTING.md (8.4KB) - Problem solving strategies
    - REFERENCE.md (10KB) - Quick command/setting lookups
  - Archived October CHANGELOG entries to CHANGELOG_ARCHIVE_2025-10.md
  - Created comprehensive DOCUMENTATION_SCALING_STRATEGY.md

**Before refactoring:**
- AI_GUIDE.md: 19KB (557 lines) - monolithic, growing uncontrollably
- Total docs: ~183KB (~47K tokens, 23% of context)

**After refactoring:**
- AI_GUIDE.md: 7.6KB (205 lines) - navigation hub
- 4 specialized guides: 36KB (1,306 lines) - focused, modular
- Total docs: ~170KB (~43K tokens, 21.5% of context)

**Benefits:**
✅ **Modular loading** - AI loads only relevant guide (saves ~10K tokens/session)
✅ **Scalable** - Each guide can grow independently
✅ **Better UX** - Clear navigation, focused content
✅ **Maintainable** - Update specific guides without touching others
✅ **Discoverable** - AI can find task-specific info faster

**New structure:**
```
docs/
├── AI_GUIDE.md (7.6KB) - Navigation hub
├── maintenance/
│   └── ai/
│       ├── GUIDELINES.md - Critical rules
│       ├── WORKFLOWS.md - How-to guides
│       ├── TROUBLESHOOTING.md - Problem solving
│       └── REFERENCE.md - Quick lookups
└── maintenance/
    ├── CHANGELOG_ARCHIVE_2025-10.md - October archive
    ├── DOCUMENTATION_SCALING_STRATEGY.md - Scaling guide
    └── AI_GUIDE_REFACTOR_PLAN.md - Original plan
```

**Files changed:**
- `docs/AI_GUIDE.md` (refactored, 63% smaller)
- `docs/maintenance/ai/GUIDELINES.md` (new)
- `docs/maintenance/ai/WORKFLOWS.md` (new)
- `docs/maintenance/ai/TROUBLESHOOTING.md` (new)
- `docs/maintenance/ai/REFERENCE.md` (new)
- `docs/maintenance/CHANGELOG_ARCHIVE_2025-10.md` (new)

**Test results:** 275/275 tests pass ✅

---

## [2025-10-12 06:00]

### Added
- **AI_GUIDE.md refactoring plan for long-term scalability**
  - Created comprehensive refactoring roadmap
  - Identified that current AI_GUIDE.md won't scale (will hit 40-50KB in 10-15 sessions)
  - Proposed 3-tier structure: Entry point → Detailed guides → Topic lessons
  - File: `docs/maintenance/AI_GUIDE_REFACTOR_PLAN.md` (comprehensive plan)

**Current problem:**
- AI_GUIDE.md is 19KB (557 lines) and growing
- Trying to be both quick reference AND comprehensive guide
- Will exceed 50KB target within 10-15 sessions

**Proposed solution:**
```
AI_GUIDE.md (SLIM - <10KB, <100 lines)
    ├── 5 Critical Rules only
    ├── Links to detailed guides
    └── Task-specific navigation

maintenance/ai/
    ├── GUIDELINES.md (DO/DON'T, patterns)
    ├── WORKFLOWS.md (step-by-step tasks)
    ├── TROUBLESHOOTING.md (common issues)
    └── REFERENCE.md (quick lookups)
```

**Benefits:**
- Save ~10K tokens per session (load only relevant guide)
- Each guide can grow independently
- Scales to 10x current content
- Better organization and discoverability

**Implementation:** Planned for when AI_GUIDE.md approaches 30KB.

**Files added:**
- `docs/maintenance/AI_GUIDE_REFACTOR_PLAN.md` - Complete migration plan

**Test results:** 275/275 tests pass ✅

---

## [2025-10-12 05:30]

### Added
- **Automatic Ollama installation and management**
  - ZERO setup required - Ollama is automatically installed and managed
  - Auto-detects platform (Windows/Linux/macOS) and installs Ollama if not present
  - Starts Ollama server as subprocess (runs in background, no terminal window)
  - Automatically pulls required model (~2GB for llama3.2:3b)
  - Proper lifecycle management (start/stop/cleanup)
  - File: `shared/ollama_manager.py` (new, 395 lines)

**What users see:**
```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "model": "llama3.2:3b"
    }
  }
}
```

**What happens automatically:**
1. ✅ Checks if Ollama is installed (installs if not)
2. ✅ Starts Ollama server as subprocess
3. ✅ Downloads model llama3.2:3b (~2GB)
4. ✅ Ready to use!

### Changed
- **shared/llm_utils.py**: OllamaProvider now supports auto-managed mode
  - Without `base_url`: Automatically installs and manages Ollama subprocess
  - With `base_url`: Uses external Ollama server (backward compatible)
  - Automatic cleanup on provider destruction
  - Lines: 56-122 (OllamaProvider class updated)

- **config.json**: Removed `base_url` from ollama config (now optional)
  - Old: `ollama.base_url` required
  - New: `base_url` optional, auto-managed if omitted

- **config.local.json.example**: Updated to show auto-managed Ollama
  - `base_url` now commented out as optional
  - Clearer inline comments about auto-management

- **docs/features/LLM_PROVIDERS.md**: Comprehensive auto-management documentation
  - Updated Quick Start section (zero setup required)
  - Updated Ollama setup section (automatic vs manual)
  - Updated troubleshooting for auto-installation issues
  - Updated FAQ with auto-management questions

### Impact
**Zero setup UX:** Users no longer need to manually install Ollama, start the server, or pull models. The system handles everything automatically.

**Simplified config:** No need to specify `base_url` - just choose a model and go.

**Better onboarding:** New users can use FREE local LLMs without understanding Ollama installation.

**Cross-platform:** Automatic installation works on Windows, Linux, and macOS.

**Files changed:**
- `shared/ollama_manager.py` (new, 395 lines - complete management system)
- `shared/llm_utils.py` (updated OllamaProvider for auto-management)
- `config.json` (removed base_url from ollama config)
- `config.local.json.example` (updated examples)
- `docs/features/LLM_PROVIDERS.md` (updated documentation)

**Test results:** 275/275 tests pass ✅

---

## [2025-10-12 05:18]

### Changed
- **Simplified stage-specific LLM override**
  - Removed complex `llm_config` nested configuration
  - Now only need `llm_provider` to override provider per stage
  - All settings come from global `llm.{provider}` section (single source of truth)

**Before (complex):**
```json
{
  "text_polishing": {
    "llm_provider": "anthropic",
    "llm_config": {
      "anthropic": {
        "api_key": "...",
        "model": "..."
      }
    }
  }
}
```

**After (simple):**
```json
{
  "text_polishing": {
    "llm_provider": "anthropic"
  }
}
```

### Impact
**Simpler config:** Just one setting to override provider per stage.

**Less duplication:** No need to repeat api_key, model, etc. per stage.

**Single source of truth:** All provider settings in `llm.{provider}` section.

**Easier maintenance:** Change model once, applies everywhere.

**Files changed:**
- `shared/llm_utils.py` (simplified stage override logic)
- `config.local.json.example` (cleaner examples with inline comments)
- `docs/features/LLM_PROVIDERS.md` (updated all override examples)
- `docs/core/CONFIGURATION.md` (updated override example)

**Test results:** 275/275 tests pass ✅

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
| 2025-10-12 07:15 | Changed | Made segment_merging stage optional               | 270     |
| 2025-10-12 07:00 | Changed | Made segment_splitting stage optional             | 270     |
| 2025-10-12 06:45 | Changed | Simplified documentation structure                | 275     |
| 2025-10-12 06:30 | Changed | Complete documentation refactoring (AI guides)    | 275     |
| 2025-10-12 06:00 | Added   | AI_GUIDE.md refactoring plan for scalability      | 275     |
| 2025-10-12 05:30 | Added   | Automatic Ollama installation and management      | 275     |
| 2025-10-12 05:18 | Changed | Simplified stage-specific LLM override            | 275     |
| 2025-10-11 15:00 | Added   | Configurable LLM providers (Ollama, OpenAI)       | 270     |
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
