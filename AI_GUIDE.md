# AI Assistant Guide for transcribe-jp

> **📝 LIVING DOCUMENT:** This guide is maintained by AI assistants across sessions. If you discover new patterns, conventions, or lessons learned while working on this project, **UPDATE THIS DOCUMENT** and commit your changes. Future AI sessions depend on this knowledge.

This document provides AI-specific context for working on transcribe-jp. It focuses on guidelines, lessons learned, and decision-making frameworks that aren't covered in the regular project documentation.

**Version:** 2.0
**Last Updated:** 2025-01-11
**Changes from v1.0:** Removed redundancy with docs/, focused on AI-specific guidance

---

## Quick Start for AI Assistants

**Read these first:**
1. [README.md](README.md) - Project overview, installation, usage
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - 9-stage pipeline, directory structure
3. [docs/CHANGELOG.md](docs/CHANGELOG.md) - Recent changes and git history
4. **This guide** - AI-specific guidelines and lessons learned

**Key facts:**
- 9-stage Japanese transcription pipeline (Whisper → processing → VTT output)
- 261 unit tests + 4 E2E tests (all must pass before committing)
- Japanese-specific: particle variations, no spaces, sentence structure
- Stage order is critical: filtering before realignment, polishing after
- Test command: `python -X utf8 -m pytest tests/unit/ -q --tb=line`

---

## Critical Guidelines for AI Assistants

### ✅ DO (Non-Negotiable)

1. **ALWAYS run tests before committing**
   ```bash
   python -X utf8 -m pytest tests/unit/ -q --tb=line
   ```
   All 261 tests must pass. No exceptions.

2. **ALWAYS suggest git commit after completing tasks**
   - Ask: "Should I commit these changes to git?"
   - User explicitly requested this behavior
   - Create descriptive commits with test results
   - Use co-authorship footer (see git commit template below)

3. **Update documentation for ALL significant changes**
   - **docs/CHANGELOG.md** - What changed, when, impact (REQUIRED)
   - **AI_GUIDE.md Session History** - Why, lessons learned, context
   - **README.md** - User-facing features/changes
   - **docs/CONFIGURATION.md** - Config option changes
   - **docs/PIPELINE_STAGES.md** - Stage behavior changes

4. **Update THIS document (AI_GUIDE.md) when you learn something**
   - Add new patterns to guidelines
   - Document mistakes in "DO NOT" section
   - Add troubleshooting for tricky issues
   - Update Session History (see template below)

5. **Check for redundancy before adding features**
   - **Stage 5** = Hallucination filtering (phrase_filter, timing_validation)
   - **Stage 6** = Timing realignment (re-transcription)
   - **Stage 8** = Final cleanup (stammers, duplicates)
   - Search codebase first: `grep -r "feature_name"`

6. **Follow Japanese text conventions**
   - No spaces between segments
   - Particle variations: は/わ, を/お, へ/え (use 0.75 similarity threshold)
   - Sentence enders: 。？！ね よ わ な か
   - Incomplete markers: て で と が けど

7. **Use centralized utilities (don't reimplement)**
   - `shared/text_utils.py` - Text normalization, Japanese utils
   - `shared/whisper_utils.py` - Audio loading, transcription
   - `modules/stage6_timing_realignment/utils.py` - Re-transcription, similarity

### ❌ DO NOT (Common Mistakes)

1. **Do NOT skip test runs** - 261 tests must pass before commit

2. **Do NOT change pipeline stage order** without deep analysis
   - Hallucination filtering BEFORE timing realignment (Stage 5 → 6)
   - Text polishing AFTER timing realignment (Stage 6 → 7)
   - Re-filtering AFTER timing_validation (learned in session 2025-01-11)

3. **Do NOT add features that duplicate existing functionality**
   - Example: `enable_remove_irrelevant` was redundant with Stage 5's `timing_validation` (removed in commit 60d0256)
   - Always grep for similar code first

4. **Do NOT lower thresholds without testing**
   - Similarity: 0.75 (tuned for Japanese particle variations)
   - Don't go below 0.7 without extensive testing
   - Test with: これは vs これわ = 0.667 similarity

5. **Do NOT use LLM for non-semantic tasks**
   - Text similarity → use `difflib.SequenceMatcher` (NOT LLM)
   - Timing validation → use Whisper re-transcription (NOT LLM)
   - Use LLM only for: semantic splitting (Stage 4), text polishing (Stage 7)

6. **Do NOT commit without updating CHANGELOG.md**
   - User explicitly requested this
   - CHANGELOG = what/when/impact
   - AI_GUIDE = why/lessons/context

---

## Testing Requirements

**Unit tests:** `tests/unit/` (261 tests)
- Run: `python -X utf8 -m pytest tests/unit/ -q --tb=line`
- All must pass before committing
- Add tests for new features
- Windows: use `-X utf8` flag for Japanese text

**E2E tests:** `tests/e2e/` (4 suites)
- Run: `python -X utf8 -m pytest tests/e2e/ -v`
- Required for pipeline changes
- Test audio: `tests/e2e/test_media/japanese_test.mp3` (Japanese counting 1-10, 27s, 167KB)

---

## Key Configuration Settings

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for full reference. AI assistants should know these:

**Similarity thresholds (0.75):**
- `timing_realignment.text_search.similarity: 0.75`
- `timing_realignment.time_based.similarity: 0.75`
- Tested with Japanese particles (これは vs これわ = 0.667)
- DO NOT lower below 0.7

**Timing validation (Stage 5):**
- `hallucination_filter.timing_validation.enable: true`
- `hallucination_filter.timing_validation.enable_revalidate_with_whisper: true`
- Re-transcribes segments > 20 chars/sec (physically impossible)
- After re-transcription, re-runs phrase_filter + consecutive_duplicates (fixed 2025-01-11)

**Whisper settings:**
- `model: "large-v3"` - Best for Japanese
- `condition_on_previous_text: false` - Prevents error propagation
- `initial_prompt: "日本語の会話です..."` - Reduces hallucinations

---

## Common Tasks

### Adding a New Filter

1. Determine stage: 5=hallucinations, 8=cleanup
2. Add logic: `modules/stageN_*/filters.py`
3. Import in: `modules/stageN_*/processor.py`
4. Add config: `config.json`
5. Write tests: `tests/unit/modules/stageN_*/`
6. Update docs: `docs/CONFIGURATION.md`, `docs/CHANGELOG.md`
7. Run tests: All 261 must pass

### Modifying Text Similarity

**Current:** `modules/stage6_timing_realignment/utils.py::calculate_text_similarity()`
- Uses `difflib.SequenceMatcher` (Ratcliff/Obershelp algorithm)
- Strips punctuation: `[、。！？\s]`
- Returns 0.0-1.0 ratio

**If modifying:**
1. Test with Japanese particle variations (は/わ, を/お)
2. Test with punctuation differences
3. Update tests: `tests/e2e/test_timing_realignment.py`
4. Document threshold changes in CHANGELOG.md

### Git Commit Template

```bash
git commit -m "Brief summary line

Detailed explanation of:
- What changed
- Why it changed
- Impact on users/developers

Files changed:
- file1.py - description
- file2.py - description

Test results: 261/261 tests pass ✅

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Performance Considerations

**Most expensive operations:**
1. **Whisper** (Stage 2, 6) - ~10-20min per hour of audio (GPU)
2. **LLM** (Stage 4, 7) - Optional splitting/polishing, use batching
3. **Stage 6 Timing Realignment** - Re-transcribes every segment

**Optimization tips:**
- Use `batch_size` config for parallel processing
- Limit search windows (Stage 6: max 5 segments)
- Use early termination (similarity >= 0.9 → stop searching)
- Cache transcription results when possible

---

## Japanese Language Specifics

**Particle variations** (Whisper transcribes differently):
- は (particle) vs わ (wa sound)
- を (particle) vs お (o sound)
- へ (particle) vs え (e sound)

→ Solution: 0.75 similarity threshold handles these

**Sentence structure:**
- Enders: 。？！ね よ わ な か
- Incomplete: て で と が けど ども たり
- Stage 3 merges incomplete, Stage 4 splits at enders

**Text normalization:** `shared/text_utils.py`
- Full-width → half-width
- No spaces between words
- Katakana variants (ヴ → ブ)

---

## Troubleshooting

**Tests fail with Unicode errors:**
- Solution: Use `python -X utf8` flag
- Windows uses CP1252 by default

**Import errors:**
- Check Python path includes project root
- Verify `__init__.py` exports

**Timing overlaps after Stage 6:**
- Stage 6 should eliminate overlaps
- Check `min_gap: 0.1` in config.json

**Similarity threshold too strict:**
- 0.75 is tuned for Japanese
- Don't raise above 0.8 (breaks particle variation handling)

---

## Questions to Ask Before Making Changes

1. **Does this already exist in another stage?**
   - Stage 5 = filtering, Stage 6 = timing, Stage 8 = cleanup

2. **Will this break tests?**
   - Run unit tests after changes
   - Run E2E for pipeline modifications

3. **Is this Japanese-specific?**
   - Use `shared/text_utils.py`
   - Consider particle variations

4. **Does this need configuration?**
   - Add to `config.json` with sensible defaults
   - Document in `docs/CONFIGURATION.md`

5. **Is there test coverage?**
   - Add unit tests for new functions
   - Add E2E for pipeline changes

6. **Did I update documentation?**
   - CHANGELOG.md (REQUIRED for all changes)
   - AI_GUIDE.md Session History
   - Other docs as needed

---

## Quick Reference

**Run tests:**
```bash
python -X utf8 -m pytest tests/unit/ -q --tb=line
python -X utf8 -m pytest tests/e2e/ -v
```

**Check git:**
```bash
git status
git diff --stat
git log --oneline -10
```

**Key files:**
- Pipeline: `core/pipeline.py::run_pipeline()`
- Config: `config.json`
- Text similarity: `modules/stage6_timing_realignment/utils.py::calculate_text_similarity()`
- Japanese utils: `shared/text_utils.py`

**Documentation:**
- [README.md](README.md) - User guide
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) - Config reference
- [docs/PIPELINE_STAGES.md](docs/PIPELINE_STAGES.md) - Stage details
- [docs/CHANGELOG.md](docs/CHANGELOG.md) - Change history

---

## Session History & Lessons Learned

**Add new entries at the top when completing significant work.** This is the core value of this guide - knowledge continuity across AI sessions.

### Session 2025-01-11 (Part 3): Streamline AI_GUIDE.md

**Git commits:**
- `<pending>` - Streamline AI_GUIDE.md to remove redundancy with docs/

**What was done:**
1. Removed redundant sections (project overview, architecture, directory structure)
2. These are now in docs/ (README, ARCHITECTURE, CHANGELOG)
3. Focused AI_GUIDE on AI-specific guidance, lessons, and decision frameworks
4. Reduced size: 674 lines → ~420 lines (38% reduction)

**Key lessons:**
- ✅ **Separate concerns:** Project docs (docs/) vs AI guidance (AI_GUIDE.md)
- ✅ **Reference don't duplicate:** Link to docs/ instead of copying
- ✅ **Focus on AI needs:** Guidelines, lessons, troubleshooting, session history

**Files modified:**
- `AI_GUIDE.md` - Restructured to remove redundancy

---

### Session 2025-01-11 (Part 2): Stage 5 Re-filtering Fix

**Git commits:**
- `daa4fe7` - Add CHANGELOG.md and improve documentation guidelines
- `ca26b37` - Fix Stage 5: Re-filter segments after timing_validation

**What was done:**
1. Fixed filter order bug: timing_validation could introduce hallucination phrases
2. Added re-filtering step after timing_validation completes
3. Created 4 new tests to verify hallucinations are caught
4. Created docs/CHANGELOG.md for change history

**The problem:**
```
OLD FLOW (BUGGY):
1. phrase_filter removes "ご視聴ありがとうございました"
2. timing_validation re-transcribes → might return hallucination!
3. Bug: hallucination kept (phrase_filter already ran)
```

**The solution:**
```
NEW FLOW (FIXED):
1. phrase_filter, consecutive_duplicates, merge_single_char
2. timing_validation re-transcribes suspicious segments
3. Re-run phrase_filter + consecutive_duplicates ✅
```

**Key lessons:**
- 🐛 **Filter order matters:** Filters that modify text need re-filtering after them
- ✅ **User identified bug:** User noticed phrase_filter should catch re-validated text
- ✅ **Test the fix:** Created specific test cases (4 new tests, 257→261)
- ✅ **CHANGELOG.md created:** User requested change history in docs/

**Files modified:**
- `modules/stage5_hallucination_filtering/processor.py` - Re-filtering logic
- `tests/.../test_timing_validation_refilter.py` - 4 new tests
- `docs/CHANGELOG.md` - Created
- `AI_GUIDE.md` - Documentation guidelines

**Test results:** 261/261 pass ✅

---

### Session 2025-01-11 (Part 1): Stage 6 Improvements + AI_GUIDE Created

**Git commits:**
- `d1b5760` - Add AI_GUIDE.md - Living document for AI assistant continuity
- `60d0256` - Remove redundant enable_remove_irrelevant feature
- `c4eafd2` - Add full pipeline E2E test and cleanup test organization

**What was done:**
1. Improved Stage 6 timing realignment accuracy (+22% with difflib.SequenceMatcher)
2. Optimized search algorithm (max 5 segments, early termination)
3. Lowered thresholds from 0.95/1.0 to 0.75 (realistic for Japanese)
4. Removed redundant `enable_remove_irrelevant` feature (69 lines deleted)
5. Created E2E tests with real Japanese audio (counting 1-10)
6. Created AI_GUIDE.md as living document

**Key lessons:**
- ❌ **Check redundancy:** `enable_remove_irrelevant` was 100% redundant with Stage 5's `timing_validation`
- ✅ **Stage 5 handles filtering:** Don't add duplicate filtering in Stage 6
- ✅ **Test with real audio:** Particle variations (は vs わ) need 0.75 threshold
- ✅ **Commit frequently:** User asked "lets commit to git" - proactively suggest commits
- ✅ **Living documentation:** User wanted guide updatable across sessions

**Files modified:**
- `modules/stage6_timing_realignment/utils.py` - difflib similarity
- `modules/stage6_timing_realignment/processor.py` - removed 69 lines
- `config.json` - thresholds updated to 0.75
- `tests/e2e/` - comprehensive E2E suite
- `AI_GUIDE.md` - created (v1.0)

**Test results:** 257/257 pass ✅

---

### Template for Next Session

Copy this when you complete significant work:

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

1. **Read relevant section first** - Don't duplicate
2. **Add specific examples** - Real code, file paths, commands
3. **Reference git commits** - For traceability
4. **Update Session History** - Document what you learned and why
5. **Commit the changes** - Version control this guide

**Good example:**
```markdown
### ❌ DO NOT use LLM for text similarity
- Learned in commit 60d0256
- Use difflib.SequenceMatcher instead (NOT LLM)
- Comparing same audio transcribed twice = no semantic difference
- See: modules/stage6_timing_realignment/utils.py::calculate_text_similarity()
```

**Bad example:**
```markdown
### DO NOT break things
- Don't make mistakes
```

---

*This guide was created in session 2025-01-11. It is a living document maintained by AI assistants across sessions. Please keep it updated!*
