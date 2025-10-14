# Development Sessions & Lessons Learned

This document tracks development sessions with lessons learned and key decisions. It benefits both **humans** (understanding the process) and **AI assistants** (learning patterns for future work).

**Add new entries at the top when completing significant work.**

## Archiving Policy

**To keep this file manageable and optimize token usage:**

- **Archive threshold:** When SESSIONS.md exceeds **400 lines**, archive older sessions
- **Archive naming:** `SESSIONS_ARCHIVE_YYYY-MM.md` (group by month, like CHANGELOG archives)
- **Keep recent:** Keep last **3-6 months** in main SESSIONS.md for immediate context
- **Archive location:** Same folder (`docs/maintenance/`)
- **Archive format:** Same structure, add header explaining it's an archive with date range

**When to archive:**
1. File exceeds 400 lines → move sessions older than 3 months to archive
2. New year starts → archive previous year's sessions (except last 3 months)
3. Major project milestone → consider archiving pre-milestone sessions

**Current status:** 328 lines (below threshold, no archiving needed yet)

---

## Session 2025-10-14 (Latest): Ollama Path Detection + Integration Tests

**What was done:**
1. **Enhanced Ollama executable path detection** - multi-location auto-detection for Windows/macOS/Linux
2. **Added manual configuration options** - executable_path and base_url config parameters
3. **Created comprehensive integration tests** - 8 test classes, 20+ test cases for Ollama
4. **Created diagnostic tool** - test_ollama_quick.py for timeout troubleshooting
5. **Documented Ollama configuration** - NEW OLLAMA_CONFIGURATION.md (540 lines)

**The problem:**
- Ollama can be installed in different locations on different PCs (standard, custom, portable)
- User reported Ollama "not found" even though it was installed
- Auto-detection only checked 1-2 locations per platform (insufficient)
- No way to manually specify Ollama path for non-standard installations
- Timeout issues difficult to diagnose (GPU vs CPU, model speed)

**The solution:**
1. **Multi-location detection:** Check PATH + 4-5 common locations per platform
2. **Manual config options:** Added `executable_path` (custom Ollama path) and enhanced `base_url` (external server)
3. **Priority system:** Custom path → PATH → Platform-specific locations → Fail with clear error
4. **Integration tests:** Cover installation detection, custom paths, external servers, generation, timeouts, error messages
5. **Diagnostic tool:** test_ollama_quick.py tests server connection + generation timing to identify slow model/CPU issues

**Key lessons:**
- ✅ Comprehensive path detection prevents "not found" errors on different PCs
- ✅ Manual configuration options essential for non-standard installations
- ✅ Integration tests catch real-world configuration issues
- ✅ Diagnostic tools help users self-diagnose issues
- ❌ DON'T assume PATH detection is sufficient - many installers don't add to PATH
- ❌ DON'T assume single installation location per platform
- ❌ DON'T skip integration tests for cross-platform features

**Files modified:**
- shared/ollama_manager.py - Enhanced `_get_ollama_executable()` with multi-location detection
- shared/llm_utils.py - Read and pass executable_path config to OllamaManager
- docs/features/OLLAMA_CONFIGURATION.md - NEW comprehensive configuration guide
- tests/integration/test_ollama.py - NEW integration test suite (600 lines, 8 classes)

**Test results:** ✅ 280/280 unit tests pass, 20+ integration tests created

---

## Session 2025-10-14 (Continued): Error Reporting + Model Pulling + Timeout + Config Optimization

**What was done:**
1. **Fixed progress bar duplication** in text polishing one-by-one mode
2. **Improved error reporting** - shows error type, segment number, actual text
3. **Added automatic model pulling with progress bar** for Ollama
4. **Added flexible timeout configuration** - common, provider-specific, stage-specific
5. **Added unlimited max_tokens feature** - set to 0 for no token limit
6. **Enhanced Ollama error handling** - detailed diagnostics for all timeout/connection scenarios

**Key lessons:**
- ✅ Progress bars should be called once per iteration, not in multiple code paths
- ✅ Error messages should show WHAT failed, WHERE, and WHY
- ✅ Large models (32B+) need 2-5 minutes timeout, not 30 seconds
- ✅ Timeout should be configurable at multiple levels (global, provider, stage)
- ❌ DON'T hardcode timeouts - models vary from 2B to 32B+ parameters
- ❌ **DON'T skip documentation updates** - violates Rule #3, breaks future sessions

**Test results:** ✅ 280/280 tests pass (no regressions)

---

## Session 2025-10-14: Batch Processing Control + Ollama Pre-Flight Validation

**What was done:**
1. **Added batch processing disable feature** for text polishing
2. **Added Ollama pre-flight validation** - checks if Ollama installed before starting pipeline
3. **Updated documentation** across 4 docs files
4. **Added 10 new unit tests** (272 → 280 tests)

**Key lessons:**
- ✅ Check batch processing behavior for different providers (cloud vs local)
- ✅ Validate dependencies at startup, not mid-pipeline (better UX)
- ✅ Clear error messages with platform-specific instructions (Windows/macOS/Linux)
- ❌ DON'T assume auto-installation will work - manual installation is more reliable

**Test results:** ✅ 280/280 tests pass (+10 new tests)

---

## Session 2025-01-11 (Part 3): Streamline AI_GUIDE.md

**Git commits:**
- `d296cd6` - Streamline AI_GUIDE.md to remove redundancy with docs/

**What was done:**
1. Removed redundant sections from AI_GUIDE.md (project overview, architecture, directory structure)
2. These are now in docs/ (README, ARCHITECTURE, CHANGELOG)
3. Focused AI_GUIDE on AI-specific guidance, lessons, and decision frameworks
4. Reduced size: 674 lines → 458 lines (32% reduction)
5. Moved Session History to docs/SESSIONS.md (this file) so both humans and AI can access it

**Key lessons:**
- ✅ **Separate concerns:** Project docs (docs/) vs AI guidance (AI_GUIDE.md)
- ✅ **Reference don't duplicate:** Link to docs/ instead of copying
- ✅ **Focus on AI needs:** Guidelines, lessons, troubleshooting
- ✅ **Share session history:** docs/SESSIONS.md benefits both humans and AI

**Files modified:**
- `AI_GUIDE.md` - Restructured to remove redundancy
- `docs/SESSIONS.md` - Created (this file) for shared session history

---

## Session 2025-01-11 (Part 2): Stage 5 Re-filtering Fix

**Git commits:**
- `daa4fe7` - Add CHANGELOG.md and improve documentation guidelines
- `ca26b37` - Fix Stage 5: Re-filter segments after timing_validation

**What was done:**
1. Fixed filter order bug: timing_validation could introduce hallucination phrases
2. Added re-filtering step after timing_validation completes
3. Created 4 new tests to verify hallucinations are caught after re-transcription
4. Created docs/CHANGELOG.md for change history

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

**Key lessons:**
- 🐛 **Filter order matters:** Filters that modify text need re-filtering after them
- ✅ **Re-run filters on modified data:** When timing_validation re-transcribes, the new text needs filtering
- ✅ **Test the fix:** Created specific test cases to verify hallucinations are caught
- ✅ **User identified the bug:** User noticed phrase_filter should catch re-validated text
- ✅ **Update CHANGELOG.md:** User requested CHANGELOG.md in docs/ for change history

**Code change:**
```python
# modules/stage5_hallucination_filtering/processor.py
if timing_config.get("enable", False):
    segments = validate_segment_timing(segments, config, model, media_path)

    # If timing validation re-transcribed segments, re-run filters on the new text
    # This prevents re-validated segments from containing hallucination phrases
    if enable_revalidate_with_whisper:
        print("    - Re-filtering after timing validation")

        # Re-run phrase filter
        if phrase_config.get("enable", False):
            segments = remove_hallucination_phrases(segments, config)

        # Re-run consecutive duplicates filter
        if consecutive_config.get("enable", False):
            segments = remove_consecutive_duplicates(segments, config)
```

**Files modified:**
- `modules/stage5_hallucination_filtering/processor.py` - Added re-filtering after timing_validation
- `tests/unit/modules/stage5_hallucination_filtering/test_timing_validation_refilter.py` - 4 new tests
- `docs/CHANGELOG.md` - Created comprehensive change history
- `AI_GUIDE.md` - Updated documentation guidelines to require CHANGELOG updates

**Test results:** 261/261 unit tests pass ✅ (+4 new tests)

---

## Session 2025-01-11 (Part 1): Stage 6 Timing Realignment Improvements

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
6. Created AI_GUIDE.md as living document for future AI sessions

**The problem:**
- Stage 6 timing realignment had low accuracy for Japanese text
- Text similarity algorithm was too simple (character position matching)
- Thresholds were unrealistic (0.95/1.0) - didn't account for Japanese particle variations
- Search algorithm was inefficient (unlimited segment combinations)
- Found redundant `enable_remove_irrelevant` feature that duplicated Stage 5 functionality

**The solution:**

1. **Upgraded similarity algorithm:**
   - Old: Simple character position comparison
   - New: `difflib.SequenceMatcher` (Ratcliff/Obershelp algorithm)
   - Result: +22% accuracy improvement
   - File: `modules/stage6_timing_realignment/utils.py`

2. **Optimized search:**
   - Limited to max 5 segment combinations (was unlimited)
   - Added early termination when similarity >= 0.9
   - Added length checks to prevent excessive combinations
   - File: `modules/stage6_timing_realignment/text_search_realignment.py`

3. **Adjusted thresholds:**
   - Old: 0.95 (text_search), 1.0 (time_based)
   - New: 0.75 (both methods)
   - Tested with: これは vs これわ = 0.667 similarity
   - Realistic for Japanese particle variations
   - File: `config.json`

4. **Removed redundant feature:**
   - Found `enable_remove_irrelevant` in Stage 6
   - Analysis showed 100% redundancy with Stage 5's `timing_validation`
   - Both re-transcribe segments with Whisper
   - Both compare similarity and remove low-match segments
   - Stage 5 is more efficient (only processes suspicious segments)
   - Stage 5 runs earlier in pipeline (better position)
   - Deleted 69 lines of redundant code
   - Files: `modules/stage6_timing_realignment/processor.py`, `config.json`, `core/pipeline.py`

**Key lessons:**
- ❌ **Always check for redundancy:** `enable_remove_irrelevant` was 100% redundant with Stage 5's `timing_validation`
- ✅ **Stage 5 handles hallucination filtering:** Don't add duplicate filtering in Stage 6
- ✅ **Test with real Japanese audio:** Particle variations (は vs わ) need 0.75 threshold
- ✅ **Commit frequently:** User asked "lets commit to git" - should proactively suggest commits after completing tasks
- ✅ **Living documentation:** User wanted this guide to be updatable across sessions
- ✅ **Search before implementing:** Always grep codebase for similar functionality

**Testing:**
- Created E2E tests with real Japanese audio
- Downloaded Japanese counting (1-10) from YouTube with yt-dlp
- 167KB, 27 seconds duration
- Transcribes to: "1、2、3、4、5、6、7、8、9、10。"
- Test results: 8/10 segments adjusted, 2 overlaps → 0 overlaps (100% fixed)

**Files modified:**
- `modules/stage6_timing_realignment/utils.py` - difflib similarity algorithm
- `modules/stage6_timing_realignment/text_search_realignment.py` - Optimized search
- `modules/stage6_timing_realignment/processor.py` - Removed 69 lines (enable_remove_irrelevant)
- `config.json` - Updated thresholds to 0.75, removed redundant config options
- `tests/e2e/test_timing_realignment.py` - Algorithm tests (23 cases)
- `tests/e2e/test_realignment_demonstration.py` - Misalignment demonstration
- `tests/e2e/test_full_pipeline.py` - Complete 9-stage pipeline test
- `AI_GUIDE.md` - Created v1.0 as living document

**Test results:** 257/257 unit tests pass ✅

---

## Template for Next Session

Copy this when you complete significant work:

```markdown
## Session YYYY-MM-DD: [Brief Description]

**Git commits:**
- `<hash>` - <commit message>

**What was done:**
1.
2.

**The problem:**
[Describe the issue]

**The solution:**
[Describe how you solved it]

**Key lessons:**
- ✅ [What went well]
- ❌ [What to avoid]
- 🐛 [Bugs discovered]

**Files modified:**
- file.py - what changed

**Test results:** X/X tests pass ✅
```

---

## How to Update This Document

**When to update:**
- After completing significant work
- When fixing important bugs
- When making architectural decisions
- When learning important patterns

**What to include:**
- Git commits (for traceability)
- Problem description (context)
- Solution description (what you did)
- Key lessons (for future reference)
- Files modified (for code navigation)
- Test results (verify quality)

**For AI assistants:**
- Add entry at the top (reverse chronological)
- Use the template above
- Focus on lessons learned
- Include code examples when relevant
- Reference git commits for traceability

**For humans:**
- This helps understand decision-making process
- Shows evolution of the codebase
- Documents why things are the way they are
- Helps onboard new contributors

---

*This document benefits both humans (understanding process) and AI assistants (learning patterns). Keep it updated after significant work.*
