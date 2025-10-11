# AI Assistant Guidelines for transcribe-jp

**Quick Reference:** Critical DO's and DON'Ts for AI assistants working on this project

**Last Updated:** 2025-10-12
**Related:** [AI_GUIDE.md](../../AI_GUIDE.md), [LESSONS_LEARNED.md](../LESSONS_LEARNED.md)

---

## Critical Guidelines for AI Assistants

### ✅ DO (Non-Negotiable)

1. **ALWAYS run tests before committing**
   ```bash
   python -X utf8 -m pytest tests/unit/ -q --tb=line
   ```
   All 261 tests must pass. No exceptions.

2. **ALWAYS update CHANGELOG.md BEFORE committing**
   - User explicitly requested this for ALL commits
   - Add entry with Date + Time format: [2025-10-12 05:30]
   - Include: What changed, impact, files modified, test results
   - Update Version History Summary table at bottom
   - See [WORKFLOWS.md](WORKFLOWS.md) "Git Commit Workflow" section for full process

3. **ALWAYS suggest git commit after completing tasks**
   - Ask: "Should I commit these changes to git?"
   - User explicitly requested this behavior
   - Create descriptive commits with test results
   - Use co-authorship footer (see git commit template in WORKFLOWS.md)

4. **Update documentation for ALL significant changes**
   - **CHANGELOG.md** - What changed, when, impact (REQUIRED - see #2)
   - **SESSIONS.md** - Why, lessons learned, context
   - **../README.md** - User-facing features/changes
   - **core/CONFIGURATION.md** - Config option changes
   - **core/PIPELINE_STAGES.md** - Stage behavior changes

5. **Update AI_GUIDE.md when you learn something**
   - Add new patterns to guidelines
   - Document mistakes in "DO NOT" section
   - Add troubleshooting for tricky issues
   - Update Session History (see template in AI_GUIDE.md)

6. **Check for redundancy before adding features**
   - **Stage 5** = Hallucination filtering (phrase_filter, timing_validation)
   - **Stage 6** = Timing realignment (re-transcription)
   - **Stage 8** = Final cleanup (stammers, duplicates)
   - Search codebase first: `grep -r "feature_name"`

7. **Follow Japanese text conventions**
   - No spaces between segments
   - Particle variations: は/わ, を/お, へ/え (use 0.75 similarity threshold)
   - Sentence enders: 。？！ね よ わ な か
   - Incomplete markers: て で と が けど

8. **Use centralized utilities (don't reimplement)**
   - `shared/text_utils.py` - Text normalization, Japanese utils
   - `shared/whisper_utils.py` - Audio loading, transcription
   - `modules/stage6_timing_realignment/utils.py` - Re-transcription, similarity

---

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

## Japanese Language Guidelines

### Particle Variations

**Whisper transcribes particles differently:**
- は (particle) vs わ (wa sound)
- を (particle) vs お (o sound)
- へ (particle) vs え (e sound)

→ **Solution:** 0.75 similarity threshold handles these

### Sentence Structure

**Enders:** 。？！ね よ わ な か
**Incomplete:** て で と が けど ども たり

- Stage 3 merges incomplete, Stage 4 splits at enders

### Text Normalization

**Location:** `shared/text_utils.py`

Features:
- Full-width → half-width
- No spaces between words
- Katakana variants (ヴ → ブ)

---

## Performance Considerations

### Most Expensive Operations

1. **Whisper** (Stage 2, 6) - ~10-20min per hour of audio (GPU)
2. **LLM** (Stage 4, 7) - Optional splitting/polishing, use batching
3. **Stage 6 Timing Realignment** - Re-transcribes every segment

### Optimization Tips

- Use `batch_size` config for parallel processing
- Limit search windows (Stage 6: max 5 segments)
- Use early termination (similarity >= 0.9 → stop searching)
- Cache transcription results when possible

---

## Testing Requirements

### Unit Tests

**Location:** `tests/unit/` (261 tests)

```bash
python -X utf8 -m pytest tests/unit/ -q --tb=line
```

- All must pass before committing
- Add tests for new features
- Windows: use `-X utf8` flag for Japanese text

### E2E Tests

**Location:** `tests/e2e/` (4 suites)

```bash
python -X utf8 -m pytest tests/e2e/ -v
```

- Required for pipeline changes
- Test audio: `tests/e2e/test_media/japanese_test.mp3` (Japanese counting 1-10, 27s, 167KB)

---

## See Also

- [AI_GUIDE.md](../../AI_GUIDE.md) - Main AI assistant guide
- [WORKFLOWS.md](WORKFLOWS.md) - Common workflows and git procedures
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving guide
- [REFERENCE.md](REFERENCE.md) - Quick reference and key settings
- [LESSONS_LEARNED.md](../LESSONS_LEARNED.md) - Knowledge database
