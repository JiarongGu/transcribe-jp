# AI Assistant Troubleshooting Guide for transcribe-jp

**Quick Reference:** Solutions to common problems and debugging strategies

**Last Updated:** 2025-10-12
**Related:** [AI_GUIDE.md](../../AI_GUIDE.md), [GUIDELINES.md](GUIDELINES.md)

---

## Common Issues and Solutions

### Tests fail with Unicode errors

**Problem:** Tests fail with `UnicodeDecodeError` or similar encoding errors

**Solution:** Use `python -X utf8` flag
- Windows uses CP1252 by default
- Japanese text requires UTF-8 encoding

```bash
python -X utf8 -m pytest tests/unit/ -q --tb=line
```

---

### Import errors

**Problem:** `ModuleNotFoundError` or `ImportError` when running tests or scripts

**Solutions:**
1. Check Python path includes project root
2. Verify `__init__.py` exports are correct
3. Ensure you're running from project root directory

```bash
# Check current directory
pwd

# Should be: y:\Tools\transcribe-jp
```

---

### Timing overlaps after Stage 6

**Problem:** Segments overlap after timing realignment (Stage 6)

**Expected behavior:** Stage 6 should eliminate overlaps

**Debug steps:**
1. Check `min_gap: 0.1` in config.json
2. Verify Stage 6 is enabled
3. Check test: `tests/e2e/test_timing_realignment.py`

**Related config:**
```json
{
  "timing_realignment": {
    "enable": true,
    "min_gap": 0.1
  }
}
```

---

### Similarity threshold too strict/loose

**Problem:** Too many segments being merged/not merged during timing realignment

**Current setting:** 0.75 (tuned for Japanese)

**Guidelines:**
- **Don't raise above 0.8** - Breaks particle variation handling
- **Don't lower below 0.7** - Too many false positives

**Test case:**
```python
# Japanese particles should match at 0.75
これは (kore wa) vs これわ = 0.667 similarity
# With 0.75 threshold, these should still match
```

**Debug steps:**
1. Check current threshold in `config.json`
2. Run: `tests/e2e/test_timing_realignment.py`
3. Review: `modules/stage6_timing_realignment/utils.py::calculate_text_similarity()`

---

### Whisper hallucinations not filtered

**Problem:** Obvious hallucinations (repeated phrases, nonsense) appearing in output

**Debug steps:**
1. Verify Stage 5 is enabled: `hallucination_filter.enable: true`
2. Check phrase_filter patterns in config
3. Verify timing_validation is enabled
4. Check timing threshold: `timing_validation.max_chars_per_second: 20`

**Related config:**
```json
{
  "hallucination_filter": {
    "enable": true,
    "phrase_filter": {
      "enable": true,
      "patterns": ["ご視聴ありがとうございました", "チャンネル登録", ...]
    },
    "timing_validation": {
      "enable": true,
      "max_chars_per_second": 20
    }
  }
}
```

---

### LLM provider errors

**Problem:** LLM stages (4, 7) failing with provider errors

**Solution:** See [features/LLM_PROVIDERS.md](../../features/LLM_PROVIDERS.md) for complete guide

**Quick checks:**
1. Verify API key is set (environment variable or config)
2. Check provider is supported: OpenAI, Anthropic, Google, OpenRouter
3. Verify model name is correct
4. Check rate limits / quotas

---

### Tests pass but pipeline fails

**Problem:** Unit tests pass but E2E tests or real runs fail

**Debug steps:**
1. Run E2E tests: `python -X utf8 -m pytest tests/e2e/ -v`
2. Check test audio: `tests/e2e/test_media/japanese_test.mp3`
3. Enable debug logging in `config.json`:
   ```json
   {
     "logging": {
       "level": "DEBUG"
     }
   }
   ```
4. Check pipeline stage order (Stage 5 before 6, Stage 7 after 6)

---

### Performance issues (slow processing)

**Problem:** Pipeline takes too long to process audio

**Most expensive operations:**
1. **Whisper** (Stage 2, 6) - ~10-20min per hour of audio (GPU)
2. **LLM** (Stage 4, 7) - Optional splitting/polishing
3. **Stage 6 Timing Realignment** - Re-transcribes every segment

**Optimization tips:**
- Use GPU for Whisper (CUDA)
- Disable optional stages (4, 7) if not needed
- Use `batch_size` config for parallel processing
- Limit search windows (Stage 6: max 5 segments)

---

## Questions to Ask Before Making Changes

### 1. Does this already exist in another stage?

**Pipeline stages:**
- **Stage 5** = Hallucination filtering (phrase_filter, timing_validation)
- **Stage 6** = Timing realignment (re-transcription)
- **Stage 8** = Final cleanup (stammers, duplicates)

**Action:** Search codebase first
```bash
grep -r "feature_name" modules/
```

---

### 2. Will this break tests?

**Action:** Run tests after changes
```bash
# Unit tests (fast, 261 tests)
python -X utf8 -m pytest tests/unit/ -q --tb=line

# E2E tests (slow, 4 suites)
python -X utf8 -m pytest tests/e2e/ -v
```

**Rule:** All tests must pass before committing

---

### 3. Is this Japanese-specific?

**Check:**
- Particle variations (は/わ, を/お, へ/え)
- Sentence structure (enders vs incomplete)
- Text normalization (full-width, katakana)

**Action:** Use `shared/text_utils.py` for Japanese text handling

---

### 4. Does this need configuration?

**Best practices:**
1. Add to `config.json` with sensible defaults
2. Document in `core/CONFIGURATION.md`
3. Allow config override via `config.local.json`
4. Use descriptive config keys

**Example:**
```json
{
  "stage_name": {
    "enable": true,
    "feature_name": {
      "threshold": 0.75,
      "max_value": 100
    }
  }
}
```

---

### 5. Is there test coverage?

**Requirements:**
- Add unit tests for new functions
- Add E2E tests for pipeline changes
- Test Japanese-specific behavior
- Test edge cases

**Test locations:**
- Unit: `tests/unit/modules/stageN_*/`
- E2E: `tests/e2e/`

---

### 6. Did I update documentation?

**Required for ALL changes:**
- **CHANGELOG.md** - What changed, when, impact (REQUIRED)
- **AI_GUIDE.md** - AI-specific lessons learned
- **README.md** - User-facing features/changes
- **core/CONFIGURATION.md** - Config option changes
- **core/PIPELINE_STAGES.md** - Stage behavior changes

**Update order:**
1. Make code changes
2. Run tests
3. Update docs
4. Commit (docs included in same commit)

---

## Debugging Strategies

### 1. Enable DEBUG logging

**Edit config.json:**
```json
{
  "logging": {
    "level": "DEBUG",
    "file": "transcribe.log"
  }
}
```

**View logs:**
```bash
tail -f transcribe.log
```

---

### 2. Run specific test

**Single test file:**
```bash
python -X utf8 -m pytest tests/unit/modules/stage6_timing_realignment/test_processor.py -v
```

**Single test function:**
```bash
python -X utf8 -m pytest tests/unit/modules/stage6_timing_realignment/test_processor.py::test_function_name -v
```

---

### 3. Use print debugging

**Add debug output:**
```python
print(f"DEBUG: variable_name = {variable_name}")
print(f"DEBUG: segment = {segment.to_dict()}")
```

**Remove before committing!**

---

### 4. Check git history

**Recent commits:**
```bash
git log --oneline -10
```

**Changes to specific file:**
```bash
git log -p -- path/to/file.py
```

**Who changed what:**
```bash
git blame path/to/file.py
```

---

### 5. Compare with working version

**Show changes:**
```bash
git diff HEAD~1 path/to/file.py
```

**Checkout previous version:**
```bash
git checkout HEAD~1 -- path/to/file.py
```

---

## Getting Unstuck

### When you're stuck, try:

1. **Read LESSONS_LEARNED.md** - Has someone solved this before?
2. **Check SESSIONS.md** - What was the context for this code?
3. **Run tests** - What's actually failing?
4. **Read the code** - Start from entry point, follow execution
5. **Check git history** - When did this break? What changed?
6. **Ask specific questions** - What exactly is confusing?

### Questions that help:

- What is the expected behavior?
- What is the actual behavior?
- What changed recently?
- Does this work in tests but fail in production?
- Is this Japanese-specific?

---

## See Also

- [AI_GUIDE.md](../../AI_GUIDE.md) - Main AI assistant guide
- [GUIDELINES.md](GUIDELINES.md) - Critical DO's and DON'Ts
- [WORKFLOWS.md](WORKFLOWS.md) - Common workflows
- [REFERENCE.md](REFERENCE.md) - Quick reference and key settings
- [LESSONS_LEARNED.md](../LESSONS_LEARNED.md) - Knowledge database
- [features/LLM_PROVIDERS.md](../../features/LLM_PROVIDERS.md) - LLM troubleshooting
