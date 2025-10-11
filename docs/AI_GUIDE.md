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
2. [maintenance/LESSONS_LEARNED.md](maintenance/LESSONS_LEARNED.md) - **START HERE!** Knowledge database of mistakes to avoid
3. [core/ARCHITECTURE.md](core/ARCHITECTURE.md) - 9-stage pipeline, directory structure
4. [CHANGELOG.md](CHANGELOG.md) - Recent changes and git history
5. **This guide** - AI-specific guidelines and workflows

**Key Knowledge Base Documents (docs/ folder):**
- [maintenance/LESSONS_LEARNED.md](maintenance/LESSONS_LEARNED.md) - Mistakes, gotchas, and design decisions
- [features/LLM_PROVIDERS.md](features/LLM_PROVIDERS.md) - Comprehensive LLM provider configuration guide
- [core/CONFIGURATION.md](core/CONFIGURATION.md) - Full configuration reference
- [core/PIPELINE_STAGES.md](core/PIPELINE_STAGES.md) - Detailed stage documentation

**Key facts:**
- 9-stage Japanese transcription pipeline (Whisper → processing → VTT output)
- 270 unit tests + 4 E2E tests (all must pass before committing)
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
- [maintenance/LESSONS_LEARNED.md](maintenance/LESSONS_LEARNED.md) - Knowledge database
- [core/ARCHITECTURE.md](core/ARCHITECTURE.md) - System design
- [core/CONFIGURATION.md](core/CONFIGURATION.md) - Config reference
- [core/PIPELINE_STAGES.md](core/PIPELINE_STAGES.md) - Stage details
- [CHANGELOG.md](CHANGELOG.md) - Change history

---

## Using the Knowledge Database

### LESSONS_LEARNED.md - Your First Stop

**[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** is a curated knowledge database of:
- **Mistakes to avoid** - Learn from past errors
- **Design decisions** - Understand why things are the way they are
- **Gotchas and patterns** - Non-obvious issues and solutions
- **Best practices** - Proven patterns for common tasks

**Always read LESSONS_LEARNED.md** before making architectural changes. It contains context that isn't obvious from code.

**When to add to LESSONS_LEARNED.md:**
1. You made a mistake worth documenting
2. You discovered a non-obvious issue
3. You made a design decision with reasoning
4. You solved a tricky problem
5. You refactored and want to explain why

**Format:** See [LESSONS_LEARNED.md](maintenance/LESSONS_LEARNED.md#how-to-update-this-document) for template.

### SESSIONS.md - Development History

**[SESSIONS.md](SESSIONS.md)** tracks session-by-session development:
- What was accomplished
- Why decisions were made
- Lessons learned
- Context for future work

**When to update SESSIONS.md:**
- After completing significant work
- When fixing important bugs
- When making key decisions
- When learning valuable patterns

**Template available in SESSIONS.md** - Copy it when you complete work.

### Relationship Between Docs

```
LESSONS_LEARNED.md → Curated knowledge (mistakes, patterns, decisions)
SESSIONS.md        → Chronological history (what happened, when, why)
AI_GUIDE.md        → Quick reference (guidelines, workflows, tips)
CHANGELOG.md       → User-facing changes (what changed, impact)
```

**Use LESSONS_LEARNED.md** to prevent mistakes.
**Use SESSIONS.md** to understand project evolution.
**Use AI_GUIDE.md** for day-to-day development.
**Use CHANGELOG.md** to see what changed recently.

---

## Adding New Knowledge Base Documents

**When to create new knowledge documents in `docs/`:**

### ✅ Create New Document When:
1. **Topic is self-contained** - Can be understood independently
2. **Topic is substantial** - More than 100 lines of content
3. **Topic benefits multiple stakeholders** - Useful for users, developers, and AI assistants
4. **Topic needs detailed examples** - Step-by-step guides, troubleshooting, FAQs
5. **Topic is frequently referenced** - Will be linked from multiple places

**Examples:**
- `features/LLM_PROVIDERS.md` - Self-contained LLM configuration guide (users need it, AI assistants reference it)
- `maintenance/LESSONS_LEARNED.md` - Knowledge database of mistakes and design decisions
- `SESSIONS.md` - Development history and lessons learned (in docs root)
- `core/ARCHITECTURE.md` - System design and pipeline overview

### ❌ Don't Create New Document When:
1. **Topic fits existing document** - Add to CONFIGURATION.md, AI_GUIDE.md, etc.
2. **Topic is too small** - Less than 50 lines (add to existing doc)
3. **Topic is code-specific** - Add comments in code or docstrings
4. **Topic is temporary** - Add to CHANGELOG.md instead

### Organize Docs into Proper Folders

**Important:** Don't put all docs in `docs/` root. Use folders:
- `docs/core/` - Core system docs (ARCHITECTURE, CONFIGURATION, PIPELINE_STAGES)
- `docs/features/` - Feature-specific docs (LLM_PROVIDERS, stage guides)
- `docs/maintenance/` - Maintenance docs (AI_GUIDE, LESSONS_LEARNED, historical records)

### Document Structure Template

```markdown
# Document Title

**Quick Reference:** One-line summary of what this document covers

**Last Updated:** YYYY-MM-DD
**Related:** Links to related documents

---

## Overview

Brief introduction (2-3 paragraphs)

---

## Quick Start

Most common use case with minimal steps

---

## Detailed Sections

In-depth coverage with examples

---

## Troubleshooting

Common issues and solutions

---

## FAQ

Frequently asked questions

---

## See Also

- Links to related documents
- External resources
```

### How to Make Documents AI-Discoverable

**1. Add to AI_GUIDE.md Quick Start:**
```markdown
**Key Knowledge Base Documents (docs/ folder):**
- [YOUR_DOC.md](YOUR_DOC.md) - Brief description
```

**2. Add cross-references:**
- Link from related documents (CONFIGURATION.md, README.md, etc.)
- Use consistent naming: `[Document Name](path/to/doc.md)`

**3. Use clear headers:**
- AI assistants scan headers to understand content
- Use action-oriented titles: "How to Configure", "Troubleshooting Guide"
- Include keywords: "LLM", "Configuration", "Pipeline", "Testing"

**4. Add metadata at top:**
```markdown
**Last Updated:** YYYY-MM-DD
**Related:** [Related Doc 1](path), [Related Doc 2](path)
```

**5. Include Quick Reference:**
- One-line summary at the top
- AI assistants read this first to decide if document is relevant

### Knowledge Base Best Practices

1. **One topic per document** - Don't mix unrelated topics
2. **Start with examples** - Show, don't just tell
3. **Use tables for comparisons** - Easy to scan
4. **Include troubleshooting** - Common issues save time
5. **Link bidirectionally** - If A links to B, B should link back to A
6. **Update "Last Updated"** - Helps AI assistants assess freshness
7. **Keep it concise** - Break long docs into sub-documents

---

## How to Update This Guide

**Update AI_GUIDE.md when:**
- You discover new AI-specific patterns or workflows
- You need to add critical guidelines
- **You create new knowledge base documents** (add to Quick Start list)

**Update LESSONS_LEARNED.md when:**
- You make a mistake (document so others don't repeat it)
- You discover a gotcha or non-obvious issue
- You make a design decision (explain the reasoning)
- You solve a tricky problem (share the solution pattern)
- You refactor something (document why the new way is better)

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
