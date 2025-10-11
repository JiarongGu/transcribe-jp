# AI Assistant Workflows for transcribe-jp

**Quick Reference:** Step-by-step workflows for common tasks

**Last Updated:** 2025-10-12
**Related:** [AI_GUIDE.md](../../AI_GUIDE.md), [GUIDELINES.md](GUIDELINES.md)

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

---

## Git Commit Workflow

**IMPORTANT:** Follow this workflow for ALL commits:

1. **Complete the work** (code + tests)
2. **Run all tests** (`python -m pytest tests/ -v -q --tb=line`)
3. **Update CHANGELOG.md** (add entry with Date + Time format)
4. **Stage all changes** (`git add -A`)
5. **Commit with descriptive message** (use template below)

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

Test results: 275/275 tests pass ✅

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Common Mistake:** Forgetting to update CHANGELOG.md before committing. The user specifically requested CHANGELOG updates for ALL commits.

---

## Changing Text Similarity Thresholds

### Current Configuration

**Similarity thresholds (0.75):**
- `timing_realignment.text_search.similarity: 0.75`
- `timing_realignment.time_based.similarity: 0.75`
- Tested with Japanese particles (これは vs これわ = 0.667)
- DO NOT lower below 0.7

### Procedure for Changing Thresholds

1. **Understand current behavior**
   - Read test cases in `tests/e2e/test_timing_realignment.py`
   - Check Japanese particle test cases

2. **Test with edge cases**
   ```python
   # These should match (particle variations)
   これは (kore wa) vs これわ = 0.667 similarity
   ```

3. **Update configuration**
   - Edit `config.json`
   - Update both `text_search.similarity` and `time_based.similarity`

4. **Run tests**
   ```bash
   python -X utf8 -m pytest tests/unit/ -q --tb=line
   python -X utf8 -m pytest tests/e2e/test_timing_realignment.py -v
   ```

5. **Document changes**
   - Update `CHANGELOG.md` with threshold change
   - Document reasoning in `LESSONS_LEARNED.md`
   - Update `core/CONFIGURATION.md` if needed

### Threshold Guidelines

- **0.75** - Current default, handles Japanese particles
- **0.7** - Minimum recommended (below this, too many false positives)
- **0.8** - Too strict, breaks particle variation handling
- **0.9** - Early termination threshold (exact match)

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
- `features/LLM_PROVIDERS.md` - Self-contained LLM configuration guide
- `maintenance/LESSONS_LEARNED.md` - Knowledge database of mistakes and design decisions
- `SESSIONS.md` - Development history and lessons learned
- `core/ARCHITECTURE.md` - System design and pipeline overview

### ❌ Don't Create New Document When:
1. **Topic fits existing document** - Add to CONFIGURATION.md, AI_GUIDE.md, etc.
2. **Topic is too small** - Less than 50 lines (add to existing doc)
3. **Topic is code-specific** - Add comments in code or docstrings
4. **Topic is temporary** - Add to CHANGELOG.md instead

### Organize Docs into Proper Folders

**Don't put all docs in `docs/` root. Use folders:**
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

## Updating Documentation

### Update AI_GUIDE.md when:
- You discover new AI-specific patterns or workflows
- You need to add critical guidelines
- **You create new knowledge base documents** (add to Quick Start list)

### Update LESSONS_LEARNED.md when:
- You make a mistake (document so others don't repeat it)
- You discover a gotcha or non-obvious issue
- You make a design decision (explain the reasoning)
- You solve a tricky problem (share the solution pattern)
- You refactor something (document why the new way is better)

### Update SESSIONS.md when:
- You complete significant work
- You want to document decisions/lessons
- You fix bugs or make improvements

### Good Update Example

```markdown
### ❌ DO NOT use LLM for text similarity
- Learned in commit 60d0256
- Use difflib.SequenceMatcher instead (NOT LLM)
- Comparing same audio transcribed twice = no semantic difference
- See: modules/stage6_timing_realignment/utils.py::calculate_text_similarity()
```

### Bad Update Example

```markdown
### DO NOT break things
- Don't make mistakes
```

**Key principle:** Add specific, actionable guidance with real examples and file references.

---

## Using the Knowledge Database

### LESSONS_LEARNED.md - Your First Stop

**[LESSONS_LEARNED.md](../LESSONS_LEARNED.md)** is a curated knowledge database of:
- **Mistakes to avoid** - Learn from past errors
- **Design decisions** - Understand why things are the way they are
- **Gotchas and patterns** - Non-obvious issues and solutions
- **Best practices** - Proven patterns for common tasks

**Always read LESSONS_LEARNED.md** before making architectural changes. It contains context that isn't obvious from code.

### Documentation Scaling Strategy ⚠️

**IMPORTANT:** As documentation grows, we risk exceeding token limits in future sessions.

**Current status (2025-10-12):** ~163 KB (~42K tokens, 21% of 200K context)

**See:** [DOCUMENTATION_SCALING_STRATEGY.md](../DOCUMENTATION_SCALING_STRATEGY.md) for complete strategy.

**Key actions for AI assistants:**
1. **When CHANGELOG.md > 50KB:** Archive previous month to `maintenance/CHANGELOG_ARCHIVE_YYYY-MM.md`
2. **When LESSONS_LEARNED.md > 30KB:** Split by topic into `maintenance/lessons/` folder
3. **Load docs strategically:** Don't read everything upfront - load task-specific docs only
4. **Monitor monthly:** Run size check script to track growth

**When to add to LESSONS_LEARNED.md:**
1. You made a mistake worth documenting
2. You discovered a non-obvious issue
3. You made a design decision with reasoning
4. You solved a tricky problem
5. You refactored and want to explain why

**Format:** See [LESSONS_LEARNED.md](../LESSONS_LEARNED.md#how-to-update-this-document) for template.

### SESSIONS.md - Development History

**[SESSIONS.md](../../SESSIONS.md)** tracks session-by-session development:
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

## See Also

- [AI_GUIDE.md](../../AI_GUIDE.md) - Main AI assistant guide
- [GUIDELINES.md](GUIDELINES.md) - Critical DO's and DON'Ts
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving guide
- [REFERENCE.md](REFERENCE.md) - Quick reference and key settings
- [LESSONS_LEARNED.md](../LESSONS_LEARNED.md) - Knowledge database
