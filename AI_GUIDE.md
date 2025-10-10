# AI Assistant Guide for transcribe-jp

> **📝 LIVING DOCUMENT:** This guide is maintained by AI assistants across sessions. If you discover new patterns, conventions, or lessons learned while working on this project, **UPDATE THIS DOCUMENT** and commit your changes. Future AI sessions depend on this knowledge.

This document provides context for AI assistants working on this project. It describes the project architecture, conventions, testing requirements, and important behavioral guidelines learned from real development sessions.

**Version:** 1.0
**Last Updated:** 2025-01-11 (Session: Stage 6 improvements + redundant feature removal)

---

## Project Overview

**transcribe-jp** is a Japanese audio transcription tool that uses OpenAI Whisper to generate high-quality, timestamped VTT subtitle files. The project focuses on accuracy, proper segmentation, and hallucination filtering for Japanese language content.

**Key Technologies:**
- OpenAI Whisper (large-v3) for transcription
- Anthropic Claude for LLM-based text processing
- Python 3.13
- pytest for testing

---

## Project Architecture

### 9-Stage Pipeline

The transcription process runs through 9 sequential stages. **DO NOT skip or reorder stages** without careful consideration:

```
1. Audio Preprocessing      → Normalize audio to -6.0 LUFS
2. Whisper Transcription    → Initial transcription with word timestamps
3. Segment Merging          → Merge incomplete Japanese sentences
4. Segment Splitting        → Split long segments with optional LLM
5. Hallucination Filtering  → Remove hallucinations and duplicates
6. Timing Realignment       → Re-transcribe to fix timing (CRITICAL STAGE)
7. Text Polishing           → Fix Japanese text with LLM
8. Final Cleanup            → Remove stammers and repetitions
9. VTT Generation           → Output final subtitle file
```

**Pipeline Entry Point:** `core/pipeline.py::run_pipeline()`

### Directory Structure

```
transcribe-jp/
├── core/
│   ├── config.py          # Configuration loading and validation
│   ├── pipeline.py        # Main 9-stage pipeline orchestration
│   └── display.py         # CLI UI and progress display
├── modules/
│   ├── stage1_audio_preprocessing/
│   ├── stage2_whisper_transcription/
│   ├── stage3_segment_merging/
│   ├── stage4_segment_splitting/
│   ├── stage5_hallucination_filtering/
│   ├── stage6_timing_realignment/    ⭐ Recently improved
│   ├── stage7_text_polishing/
│   ├── stage8_final_cleanup/
│   └── stage9_vtt_generation/
├── shared/
│   ├── text_utils.py      # Japanese text utilities
│   └── whisper_utils.py   # Whisper helper functions
├── tests/
│   ├── unit/              # Unit tests (261 tests)
│   └── e2e/               # End-to-end tests (4 test suites)
│       ├── test_media/    # Test audio files
│       ├── test_timing_realignment.py
│       ├── test_realignment_demonstration.py
│       ├── test_full_pipeline.py
│       └── test_fixes.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CONFIGURATION.md
│   ├── PIPELINE_STAGES.md
│   ├── IMPROVEMENTS.md
│   └── TESTING.md
├── config.json            # Main configuration file
├── transcribe_jp.py       # CLI entry point
└── README.md
```

---

## Recent Improvements (Context for Future Work)

### Stage 6: Timing Realignment Improvements (Completed)

**What was done:**
1. Upgraded text similarity from character matching to `difflib.SequenceMatcher` (+22% accuracy)
2. Added word-level timestamp matching fallback
3. Optimized search to max 5 segment combinations with early termination
4. Lowered thresholds from 0.95/1.0 to 0.75 (realistic for Japanese variations)
5. Removed redundant `enable_remove_irrelevant` feature (handled by Stage 5)

**Files modified:**
- `modules/stage6_timing_realignment/utils.py` - New similarity algorithm
- `modules/stage6_timing_realignment/text_search_realignment.py` - Optimized search
- `config.json` - Updated thresholds to 0.75
- Test files created with real Japanese audio (counting 1-10)

**Test Results:**
- 257/257 unit tests pass ✅
- E2E demonstration: 8/10 segments adjusted, 0 overlaps ✅
- Full 9-stage pipeline verified ✅

**Git History:**
```
60d0256 Remove redundant enable_remove_irrelevant feature
c4eafd2 Add full pipeline E2E test and cleanup test organization
000d91b init project
```

---

## Critical Guidelines for AI Assistants

### ✅ DO

1. **Always run tests before committing**
   ```bash
   python -X utf8 -m pytest tests/unit/ -q --tb=line
   ```

2. **ALWAYS suggest git commit after making changes**
   - After completing any task, ask user: "Should I commit these changes to git?"
   - When user confirms, create descriptive commit with test results
   - This ensures work is saved and has clear history
   - **Never forget this step** - it was explicitly requested by user

3. **Update THIS document (AI_GUIDE.md) when you learn something new**
   - Discovered a new pattern? Add it to guidelines
   - Found a common mistake? Add to "DO NOT" section
   - Solved a tricky issue? Add to troubleshooting
   - Modified a threshold? Document why in "Configuration Guidelines"
   - This is a living document - keep it current for future AI sessions!

4. **Maintain test coverage**
   - Add tests for new features
   - Update tests when modifying behavior
   - Run E2E tests for pipeline changes

5. **Follow Japanese text conventions**
   - No spaces between concatenated segments
   - Handle particle variations (は vs わ, を vs お)
   - Respect sentence enders: 。？！ね よ わ な か
   - Use proper incomplete markers: て で と が けど

6. **Update documentation (REQUIRED for all changes)**
   - **docs/CHANGELOG.md** - Add entry for ALL significant changes (new features, bug fixes, removals)
   - **AI_GUIDE.md** - Update Session History when completing significant work
   - **README.md** - Update for user-facing changes (features, installation, usage)
   - **docs/CONFIGURATION.md** - Update for config option changes
   - **docs/PIPELINE_STAGES.md** - Update for stage behavior changes
   - **Note:** CHANGELOG.md and AI_GUIDE.md should be updated together - CHANGELOG for what changed, AI_GUIDE for why and lessons learned

7. **Use proper git commit messages**
   - Clear summary line
   - Detailed explanation of changes
   - Include test results
   - Add co-authorship footer:
   ```
   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

8. **Verify redundancy before adding features**
   - Check if Stage 5 already handles it (hallucination filtering)
   - Check if Stage 6 already handles it (timing realignment)
   - Check if Stage 8 already handles it (final cleanup)

9. **Use centralized utilities**
   - `shared/text_utils.py` - Text normalization, Japanese utilities
   - `shared/whisper_utils.py` - Audio loading, transcription helpers
   - `modules/stage6_timing_realignment/utils.py` - Re-transcription

### ❌ DO NOT

1. **Do NOT add features without checking for redundancy**
   - Example: `enable_remove_irrelevant` was redundant with Stage 5's `timing_validation`
   - Always search codebase for similar functionality first

2. **Do NOT change pipeline stage order**
   - The 9-stage order is carefully designed
   - Hallucination filtering MUST happen before timing realignment
   - Text polishing MUST happen after timing realignment

3. **Do NOT lower quality thresholds without testing**
   - Current thresholds are tuned for Japanese (0.75 similarity)
   - Test with real Japanese audio before changing

4. **Do NOT commit without running tests**
   - All 261 unit tests must pass
   - E2E tests should be verified for major changes

5. **Do NOT add features that are already disabled**
   - If a feature is disabled by default, investigate why
   - It may be redundant, buggy, or too expensive

6. **Do NOT use LLM for tasks that don't need it**
   - Text similarity: Use difflib (not LLM)
   - Timing validation: Use Whisper re-transcription (not LLM)
   - Only use LLM for semantic understanding (splitting, polishing)

7. **Do NOT remove test files without verification**
   - Test audio in `tests/e2e/test_media/` is essential
   - E2E tests verify pipeline correctness

8. **Do NOT expose sensitive information**
   - API keys should be in config.json (not committed)
   - Use placeholders in documentation examples

---

## Testing Requirements

### Unit Tests (Required)

**Location:** `tests/unit/`
**Count:** 261 tests
**Run command:**
```bash
python -X utf8 -m pytest tests/unit/ -q --tb=line
```

**Coverage areas:**
- Each stage's processor logic
- Utility functions (text_utils, whisper_utils)
- Configuration loading and validation
- Edge cases (empty segments, overlaps, duplicates)

### E2E Tests (Required for Pipeline Changes)

**Location:** `tests/e2e/`
**Test suites:**

1. **test_timing_realignment.py** - Algorithm tests (23 cases)
   - Text similarity variations
   - Japanese particle handling
   - Whisper transcription variations

2. **test_realignment_demonstration.py** - Misalignment fixes
   - Tests 10 intentionally misaligned segments
   - Verifies overlap elimination
   - Uses real Whisper timestamps

3. **test_full_pipeline.py** - Complete 9-stage test
   - End-to-end pipeline verification
   - Uses real Japanese audio (counting 1-10)
   - Validates VTT output

4. **test_fixes.py** - Regression tests
   - Bug fix verifications

**Run command:**
```bash
python -X utf8 -m pytest tests/e2e/ -v
```

### Test Audio

**Location:** `tests/e2e/test_media/japanese_test.mp3`
**Content:** Japanese counting 1-10 (一、二、三...十)
**Duration:** ~27 seconds
**Size:** 167 KB
**Source:** Downloaded from YouTube with yt-dlp

---

## Configuration Guidelines

### config.json Structure

**Critical settings to understand:**

```json
{
  "whisper": {
    "model": "large-v3",              // Best quality for Japanese
    "initial_prompt": "日本語の会話です...",  // Prevents hallucinations
    "condition_on_previous_text": false  // Prevents error propagation
  },

  "hallucination_filter": {
    "timing_validation": {
      "enable": true,
      "enable_revalidate_with_whisper": true  // Re-transcribes suspicious segments
    }
  },

  "timing_realignment": {
    "enable": true,
    "method": "time_based",           // Batch-processable method
    "text_search": {
      "similarity": 0.75              // Tuned for Japanese variations
    },
    "time_based": {
      "similarity": 0.75              // Tuned for Japanese variations
    }
  }
}
```

### When to Modify Thresholds

**Similarity thresholds (0.75):**
- Tested with Japanese particle variations (これは vs これわ = 0.667)
- Tested with Whisper variations (punctuation differences)
- DO NOT lower below 0.7 without extensive testing

**Timing thresholds:**
- `max_chars_per_second: 20` - Physically impossible to speak faster
- `min_gap: 0.1` - Minimum gap between segments

---

## Common Tasks

### Adding a New Filter

1. Determine correct stage (5=hallucinations, 8=cleanup)
2. Add filter logic in `modules/stageN_*/filters.py`
3. Import in `modules/stageN_*/processor.py`
4. Add configuration in `config.json`
5. Write unit tests in `tests/unit/modules/stageN_*/`
6. Update `docs/CONFIGURATION.md`
7. Run all tests before committing

### Modifying Text Similarity

**Current implementation:** `modules/stage6_timing_realignment/utils.py::calculate_text_similarity()`

```python
def calculate_text_similarity(text1, text2):
    """Uses difflib.SequenceMatcher (Ratcliff/Obershelp algorithm)"""
    clean1 = re.sub(r'[、。！？\s]', '', text1)
    clean2 = re.sub(r'[、。！？\s]', '', text2)

    matcher = difflib.SequenceMatcher(None, clean1, clean2, autojunk=False)
    return matcher.ratio()
```

**If modifying:**
1. Test with Japanese text variations
2. Test with particle differences (は/わ, を/お)
3. Test with punctuation variations
4. Update tests in `tests/e2e/test_timing_realignment.py`

### Adding New Stage Configuration

1. Add to `config.json`
2. Document in `docs/CONFIGURATION.md` with:
   - Parameter table (name, type, default, description)
   - Example JSON snippet
   - "What it does" explanation
   - Performance notes
3. Add validation in `core/config.py::load_config()`
4. Display in `core/display.py::display_pipeline_status()`

---

## Performance Considerations

### Most Expensive Operations

1. **Whisper transcription** (Stage 2, 6)
   - ~10-20 min for 1 hour audio (GPU)
   - Minimize re-transcription calls

2. **LLM calls** (Stage 4, 7)
   - Stage 4: Optional LLM splitting
   - Stage 7: Text polishing batches
   - Use batch processing when possible

3. **Stage 6: Timing Realignment**
   - Re-transcribes each segment
   - Most expensive stage if enabled
   - Use `method: "time_based"` (batch-processable)

### Optimization Tips

- Use `batch_size` config for parallel processing
- Cache transcription results when possible
- Limit search windows (Stage 6: max 5 segments)
- Use early termination when match found

---

## Japanese Language Specifics

### Text Normalization

**Handled by:** `shared/text_utils.py`

```python
# Common normalizations:
- Full-width → Half-width numbers/punctuation
- Katakana normalization (ヴ → ブ variants)
- Space handling (Japanese has no spaces between words)
```

### Particle Variations

Whisper may transcribe particles differently:
- は (wa) vs わ (wa)
- を (wo) vs お (o)
- へ (e) vs え (e)

**Current similarity algorithm handles these variations** with 0.75 threshold.

### Sentence Structure

**Sentence enders:** 。？！ね よ わ な か
**Incomplete markers:** て で と が けど ども たり

Stage 3 merges incomplete sentences, Stage 4 splits at enders.

---

## Debug Commands

### Run Full Pipeline
```bash
python transcribe_jp.py path/to/audio.mp3
```

### Run Specific Test Suite
```bash
python -X utf8 -m pytest tests/unit/modules/stage6_timing_realignment/ -v
```

### Run E2E with Output
```bash
python -X utf8 -m pytest tests/e2e/test_full_pipeline.py -v -s
```

### Check Git Status
```bash
git status
git diff --stat
git log --oneline -10
```

---

## When Something Breaks

### Common Issues

1. **Tests fail with Unicode errors**
   - Use: `python -X utf8` flag
   - Windows uses CP1252 by default

2. **Import errors**
   - Check Python path includes project root
   - Verify `__init__.py` exports are correct

3. **Whisper errors**
   - Check CUDA availability: `torch.cuda.is_available()`
   - Verify model loaded: `whisper.load_model("large-v3")`

4. **Timing overlaps**
   - Stage 6 should eliminate overlaps
   - Check `min_gap` configuration (0.1s default)

5. **High similarity threshold failures**
   - Japanese text has variations
   - 0.75 is tuned for Japanese (don't raise above 0.8)

---

## Questions to Ask Before Making Changes

1. **Does this functionality already exist in another stage?**
   - Check Stage 5 for hallucination filtering
   - Check Stage 6 for timing adjustments
   - Check Stage 8 for cleanup operations

2. **Will this break existing tests?**
   - Run unit tests after changes
   - Run E2E tests for pipeline modifications

3. **Does this need configuration?**
   - Add to config.json with sensible defaults
   - Document in docs/CONFIGURATION.md

4. **Is this Japanese-specific?**
   - Use shared/text_utils.py for Japanese utilities
   - Consider particle variations and sentence structure

5. **Is this performance-critical?**
   - Minimize Whisper re-transcription calls
   - Batch LLM operations when possible
   - Use early termination in loops

6. **Is there test coverage?**
   - Add unit tests for new functions
   - Add E2E tests for pipeline changes

---

## Useful References

### Internal Documentation
- `README.md` - User guide and quick start
- `AI_GUIDE.md` - This guide (for AI assistants)
- `docs/CHANGELOG.md` - Complete change history with git commits
- `docs/ARCHITECTURE.md` - System design overview
- `docs/CONFIGURATION.md` - Complete config reference
- `docs/PIPELINE_STAGES.md` - Detailed stage documentation

### External Resources
- [Whisper GitHub](https://github.com/openai/whisper)
- [Claude API Docs](https://docs.anthropic.com/)
- [difflib Documentation](https://docs.python.org/3/library/difflib.html)

---

## Final Notes

This project prioritizes **accuracy over speed** for Japanese transcription. The 9-stage pipeline is carefully designed to:

1. Get best initial transcription (Whisper large-v3)
2. Merge/split according to Japanese sentence structure
3. Filter hallucinations early (Stage 5)
4. Fix timing precisely (Stage 6)
5. Polish text for readability (Stage 7)
6. Clean up artifacts (Stage 8)

**The pipeline order matters.** Don't skip stages or add redundant features without careful analysis.

**When in doubt, check existing code first.** This project has comprehensive utilities in `shared/` and stage-specific logic in `modules/`. Reuse existing functions rather than reimplementing.

**Test everything.** 261 unit tests and 4 E2E suites exist for a reason. Use them.

---

## Session History & Lessons Learned

This section tracks major changes and lessons learned across AI sessions. **Add new entries at the top** when you complete significant work.

### Session 2025-01-11 (Part 2): Stage 5 Re-filtering Fix

**Git commits:**
- `<pending>` - Fix Stage 5 to re-filter after timing_validation

**What was done:**
1. Fixed filter order bug: timing_validation could introduce hallucination phrases
2. Added re-filtering step after timing_validation completes
3. Created 4 new tests to verify hallucinations are caught after re-transcription
4. Updated AI_GUIDE.md with this lesson

**The problem:**
```
OLD FLOW (BUGGY):
1. phrase_filter removes "ご視聴ありがとうございました"
2. consecutive_duplicates removes repetitions
3. timing_validation re-transcribes → new text might be hallucination!
4. Bug: hallucination phrase kept (phrase_filter already ran)
```

**The solution:**
```
NEW FLOW (FIXED):
1. phrase_filter, consecutive_duplicates, merge_single_char
2. timing_validation re-transcribes suspicious segments
3. Re-run phrase_filter + consecutive_duplicates on re-validated segments ✅
```

**Key lessons learned:**
- 🐛 **Filter order matters:** Filters that modify text need re-filtering after them
- ✅ **Re-run filters on modified data:** When timing_validation re-transcribes, the new text needs filtering
- ✅ **Test the fix:** Created specific test cases to verify hallucinations are caught
- ✅ **User identified the bug:** User noticed phrase_filter should catch re-validated text
- ✅ **Update CHANGELOG.md:** User requested CHANGELOG.md in docs/ for change history (separate from AI_GUIDE session history)

**Files modified:**
- `modules/stage5_hallucination_filtering/processor.py` - Added re-filtering after timing_validation
- `tests/unit/modules/stage5_hallucination_filtering/test_timing_validation_refilter.py` - 4 new tests
- `docs/CHANGELOG.md` - Created comprehensive change history
- `AI_GUIDE.md` - Updated documentation guidelines to require CHANGELOG updates

**Test results:** 261/261 unit tests pass ✅ (+4 new tests)

---

### Session 2025-01-11 (Part 1): Stage 6 Timing Realignment Improvements

**Git commits:**
- `d1b5760` - Add AI_GUIDE.md - Living document for AI assistant continuity
- `60d0256` - Remove redundant enable_remove_irrelevant feature
- `c4eafd2` - Add full pipeline E2E test and cleanup test organization

**What was done:**
1. Improved Stage 6 timing realignment accuracy (+22% with difflib)
2. Optimized search algorithm (max 5 segments, early termination)
3. Lowered thresholds from 0.95 to 0.75 (realistic for Japanese)
4. Removed redundant `enable_remove_irrelevant` feature
5. Created E2E tests with real Japanese audio (counting 1-10)
6. Created AI_GUIDE.md as living document for future sessions

**Key lessons learned:**
- ❌ **Always check for redundancy:** `enable_remove_irrelevant` was 100% redundant with Stage 5's `timing_validation`
- ✅ **Stage 5 handles hallucination filtering:** Don't add duplicate filtering in Stage 6
- ✅ **Test with real Japanese audio:** Particle variations (は vs わ) need 0.75 threshold
- ✅ **Commit frequently:** User asked "lets commit to git" - should proactively suggest commits after completing tasks
- ✅ **Living documentation:** User wanted this guide to be updatable across sessions

**Files modified:**
- `modules/stage6_timing_realignment/utils.py` - difflib similarity
- `modules/stage6_timing_realignment/processor.py` - removed 69 lines
- `config.json` - thresholds updated to 0.75
- `tests/e2e/` - comprehensive E2E test suite
- `AI_GUIDE.md` - created living document

**Test results:** 257/257 unit tests pass ✅

---

### Template for Next Session

**Copy this template when you complete significant work:**

```markdown
### Session YYYY-MM-DD: [Brief Description]

**Git commits:**
- `<hash>` - <commit message>

**What was done:**
1.
2.

**Key lessons learned:**
-

**Files modified:**
-

**Test results:** X/X tests pass ✅
```

---

## How to Update This Guide

When you discover something worth documenting:

1. **Read the relevant section** - Don't duplicate existing info
2. **Add specific examples** - Real code, real file paths, real commands
3. **Reference git commits** - So future AIs can trace decisions
4. **Add to Session History** - Document what you learned and why
5. **Commit the changes** - This guide should be version controlled

**Example of good update:**
```markdown
### ❌ DO NOT use LLM for text similarity
- Learned in commit 60d0256
- Text similarity should use difflib.SequenceMatcher (not LLM)
- Comparing same audio transcribed twice = no semantic difference needed
- See modules/stage6_timing_realignment/utils.py::calculate_text_similarity()
```

**Example of bad update:**
```markdown
### DO NOT break things
- Don't make mistakes
```

---

*This guide was created in session 2025-01-11. It is a living document - please keep it updated!*
