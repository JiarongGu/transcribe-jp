# AI Assistant Guide for transcribe-jp

> **📝 LIVING DOCUMENT:** This guide is maintained by AI assistants across sessions. If you discover new patterns, conventions, or lessons learned while working on this project, **UPDATE THIS DOCUMENT** and commit your changes. Future AI sessions depend on this knowledge.

This document provides AI-specific context for working on transcribe-jp. It focuses on guidelines, lessons learned, and decision-making frameworks that aren't covered in the regular project documentation.

**Version:** 2.0
**Last Updated:** 2025-01-11
**Changes from v1.0:** Removed redundancy with docs/, focused on AI-specific guidance

---

## Quick Start for AI Assistants

**Read these first:**
1. [README.md](../README.md) - Project overview, installation, usage
2. [core/ARCHITECTURE.md](core/ARCHITECTURE.md) - 9-stage pipeline, directory structure
3. [CHANGELOG.md](CHANGELOG.md) - Recent changes and git history
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
   - Update CHANGELOG.md with Date + Time format (e.g., [2025-01-11 14:30]) instead of git hash

3. **Update documentation for ALL significant changes**
   - **CHANGELOG.md** - What changed, when, impact (REQUIRED)
   - **SESSIONS.md** - Why, lessons learned, context
   - **../README.md** - User-facing features/changes
   - **core/CONFIGURATION.md** - Config option changes
   - **core/PIPELINE_STAGES.md** - Stage behavior changes

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
   - CHANGELOG = what/when/impact (use Date + Time format: [2025-01-11 14:30])
   - AI_GUIDE = why/lessons/context
   - Never use git hash in CHANGELOG headers - use Date + Time instead

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

See [core/CONFIGURATION.md](core/CONFIGURATION.md) for full reference. AI assistants should know these:

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
6. Update docs: `core/CONFIGURATION.md`, `CHANGELOG.md`
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
   - Document in `core/CONFIGURATION.md`

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
- [README.md](../README.md) - User guide
- [core/ARCHITECTURE.md](core/ARCHITECTURE.md) - System design
- [core/CONFIGURATION.md](core/CONFIGURATION.md) - Config reference
- [core/PIPELINE_STAGES.md](core/PIPELINE_STAGES.md) - Stage details
- [CHANGELOG.md](CHANGELOG.md) - Change history

---

## Session History & Lessons Learned

**Session history has moved to [SESSIONS.md](SESSIONS.md)** where it benefits both humans and AI assistants.

**Why the move:**
- Humans can understand the development process
- AI assistants can learn from past patterns
- Located in docs/ with other project documentation
- More accessible to all team members

**When to update SESSIONS.md:**
- After completing significant work
- When fixing important bugs
- When making key decisions
- When learning valuable patterns

**Template available in SESSIONS.md** - Copy it when you complete work.

---

## How to Update This Guide

**Update AI_GUIDE.md when:**
- You discover new AI-specific patterns
- You find common mistakes to avoid
- You solve tricky issues (add to Troubleshooting)
- You modify configuration behavior (update guidelines)

**Update SESSIONS.md when:**
- You complete significant work
- You want to document decisions/lessons
- You fix bugs or make improvements

**Good update example:**
```markdown
### ❌ DO NOT use LLM for text similarity
- Learned in commit 60d0256
- Use difflib.SequenceMatcher instead (NOT LLM)
- Comparing same audio transcribed twice = no semantic difference
- See: modules/stage6_timing_realignment/utils.py::calculate_text_similarity()
```

**Bad update example:**
```markdown
### DO NOT break things
- Don't make mistakes
```

**Key principle:** Add specific, actionable guidance with real examples and file references.

---

*This guide was created in session 2025-01-11. It is a living document maintained by AI assistants across sessions. Session history is now in [SESSIONS.md](SESSIONS.md).*
