# AI Assistant Guide for transcribe-jp

> **LIVING DOCUMENT:** This guide is maintained by AI assistants across sessions. If you discover new patterns, conventions, or lessons learned while working on this project, **UPDATE THE DETAILED GUIDES** and commit your changes. Future AI sessions depend on this knowledge.

**Version:** 3.2
**Last Updated:** 2025-10-14
**Changes from v3.1:** Added Session History section for long-term maintenance
**Latest update:** Session 2025-10-14 - Batch processing control + Ollama validation

---

## Purpose

This guide provides AI-specific context for working on transcribe-jp. It focuses on quick onboarding, navigation to detailed guides, and session history for easy catch-up.

**Token Optimization:** This file is intentionally compact. Detailed knowledge is in specialized guides - load only what you need for your current task.

**For detailed information, see the specialized guides below.**

---

## 6 Critical Rules (Non-Negotiable)

1. **ALWAYS run tests before committing** - All 270+ tests must pass
   ```bash
   python -X utf8 -m pytest tests/unit/ -q --tb=line
   ```

2. **ALWAYS update CHANGELOG.md BEFORE committing**
   - Add entry with Date + Time format: [2025-10-12 05:30]
   - Include: what changed, impact, files modified, test results

3. **ALWAYS verify related documentation is updated**
   - After updating CHANGELOG, search: `grep -r "feature_name" docs/ --include="*.md"`
   - **Check ALL these locations:**
     - `docs/core/` (ARCHITECTURE.md, CONFIGURATION.md, PIPELINE_STAGES.md)
     - `docs/features/` (stage-specific docs)
     - `docs/ai-assistant/` (WORKFLOWS.md, GUIDELINES.md)
     - Root level (README.md, AI_GUIDE.md)
     - Config files (config.local.json.example)
   - See [WORKFLOWS.md Documentation Verification](ai-assistant/WORKFLOWS.md#documentation-verification)
   - **Code + docs must be updated together** - no exceptions!

4. **ALWAYS suggest git commit after completing tasks**
   - Ask: "Should I commit these changes to git?"
   - Use co-authorship footer (see [WORKFLOWS.md](ai-assistant/WORKFLOWS.md))

5. **Check for redundancy before adding features**
   - Stage 5 = hallucinations, Stage 6 = timing, Stage 8 = cleanup
   - Search first: `grep -r "feature_name"`

6. **Follow Japanese text conventions**
   - No spaces, particle variations (は/わ, を/お), 0.75 similarity threshold

---

## Quick Start Sequence

**First time working on this project? Read in this order:**

1. [README.md](../README.md) - Project overview, installation, basic usage
2. [maintenance/LESSONS_LEARNED.md](maintenance/LESSONS_LEARNED.md) - **START HERE!** Mistakes to avoid
3. [core/ARCHITECTURE.md](core/ARCHITECTURE.md) - 9-stage pipeline, directory structure
4. [CHANGELOG.md](CHANGELOG.md) - Recent changes and git history
5. **[ai-assistant/GUIDELINES.md](ai-assistant/GUIDELINES.md)** - Critical DO's and DON'Ts (detailed)

---

## Detailed AI Guides

### [GUIDELINES.md](ai-assistant/GUIDELINES.md)
**Critical DO's and DON'Ts for AI assistants**

- Complete list of DO's (8 rules) and DON'Ts (6 common mistakes)
- Japanese language guidelines (particles, sentence structure, normalization)
- Performance considerations (Whisper, LLM, optimization tips)
- Testing requirements (unit + E2E)

**Read this when:** Starting work, unsure about best practices, adding features

---

### [WORKFLOWS.md](ai-assistant/WORKFLOWS.md)
**Step-by-step workflows for common tasks**

- Adding new filters
- Modifying text similarity thresholds
- Git commit workflow (with template)
- **Documentation verification workflow** (Critical! Read before every commit)
- Adding new knowledge base documents
- Updating documentation (CHANGELOG, SESSIONS, LESSONS_LEARNED)

**Read this when:** Performing routine tasks, making commits, updating docs

---

### [TROUBLESHOOTING.md](ai-assistant/TROUBLESHOOTING.md)
**Solutions to common problems and debugging strategies**

- Unicode errors, import errors, timing overlaps
- Tests pass but pipeline fails
- Performance issues
- Questions to ask before making changes
- Debugging strategies (logging, specific tests, git history)

**Read this when:** Stuck on a problem, tests failing, unexpected behavior

---

### [REFERENCE.md](ai-assistant/REFERENCE.md)
**Quick reference for commands, settings, and file locations**

- Essential commands (tests, git, pipeline)
- Key configuration settings (similarity, Whisper, timing validation)
- File locations (core, stages, utilities, tests, docs)
- Pipeline stage order
- Japanese language quick reference
- Documentation map

**Read this when:** Need quick lookup, forgot a command, finding a file

---

## Key Facts

- **9-stage Japanese transcription pipeline** - Whisper → processing → VTT output
- **275 tests** - 270 unit + 4 E2E + 1 smoke test (all must pass before committing)
- **Japanese-specific** - Particle variations, no spaces, sentence structure
- **Stage order is critical** - Filtering before realignment, polishing after
- **Test command:** `python -X utf8 -m pytest tests/unit/ -q --tb=line`
- **Config:** `config.json` + `config.local.json` (deep merge, local not tracked)

---

## Documentation Map

```
AI ASSISTANT GUIDES
├── AI_GUIDE.md (this file)                  # Overview + navigation
└── ai-assistant/
    ├── GUIDELINES.md                        # Critical DO's and DON'Ts
    ├── WORKFLOWS.md                         # Step-by-step workflows
    ├── TROUBLESHOOTING.md                   # Problem solving
    └── REFERENCE.md                         # Quick reference

KNOWLEDGE BASE (read these!)
├── maintenance/LESSONS_LEARNED.md           # Mistakes, patterns, decisions
├── features/LLM_PROVIDERS.md                # LLM provider configuration
├── SESSIONS.md                              # Development history
└── CHANGELOG.md                             # Recent changes

CORE SYSTEM DOCS
├── README.md                                # User guide
├── core/ARCHITECTURE.md                     # System design
├── core/CONFIGURATION.md                    # Config reference
└── core/PIPELINE_STAGES.md                  # Stage details
```

**Navigation tips:**
- **Starting out?** → LESSONS_LEARNED.md + GUIDELINES.md
- **Doing a task?** → WORKFLOWS.md
- **Something broken?** → TROUBLESHOOTING.md
- **Need quick info?** → REFERENCE.md

---

## Using the Knowledge Database

### LESSONS_LEARNED.md - Your First Stop

**[maintenance/LESSONS_LEARNED.md](maintenance/LESSONS_LEARNED.md)** is a curated knowledge database of:
- Mistakes to avoid
- Design decisions and reasoning
- Gotchas and non-obvious issues
- Best practices for common tasks

**Always read LESSONS_LEARNED.md before making architectural changes.** It contains context that isn't obvious from code.

---

### Relationship Between Docs

```
LESSONS_LEARNED.md → Curated knowledge (mistakes, patterns, decisions)
SESSIONS.md        → Chronological history (what happened, when, why)
AI_GUIDE.md        → Navigation hub (links to detailed guides)
GUIDELINES.md      → Critical rules (DO's and DON'Ts)
WORKFLOWS.md       → How-to guides (step-by-step procedures)
TROUBLESHOOTING.md → Problem solving (common issues, debugging)
REFERENCE.md       → Quick lookup (commands, settings, locations)
CHANGELOG.md       → User-facing changes (what changed, impact)
```

---

## Session History & Lessons Learned

### Session 2025-10-14: Batch Processing Control + Ollama Pre-Flight Validation

**What was done:**
1. **Added batch processing disable feature** for text polishing
2. **Added Ollama pre-flight validation** - checks if Ollama installed before starting pipeline
3. **Updated documentation** across 4 docs files
4. **Added 10 new unit tests** (272 → 280 tests)

**The problem:**
- Ollama doesn't work well with batch processing (should process one-by-one)
- Ollama auto-installation doesn't work reliably - users got confusing errors mid-pipeline
- No way to disable batching for local LLM providers

**The solution:**
1. **Batch disable:** Set `text_polishing.batch_size` to 0 or 1 → processes one-by-one
2. **Pre-flight check:** Validates Ollama installed BEFORE starting (shows clear installation instructions)
3. **Smart validation:** Only checks when LLM features enabled, skips for external servers

**Key lessons:**
- ✅ Check batch processing behavior for different providers (cloud vs local)
- ✅ Validate dependencies at startup, not mid-pipeline (better UX)
- ✅ Clear error messages with platform-specific instructions (Windows/macOS/Linux)
- ✅ Always provide alternatives (external server, disable features)
- ❌ DON'T assume auto-installation will work - manual installation is more reliable

**Files modified:**
- core/config.py - Added `validate_llm_requirements()` (98 lines)
- transcribe_jp.py - Call validation after loading config
- modules/stage7_text_polishing/processor.py - Batch disable logic
- docs/features/LLM_PROVIDERS.md - Updated Ollama installation docs
- docs/core/CONFIGURATION.md - Updated batch_size parameter
- tests/unit/core/test_config.py - 8 validation tests
- tests/unit/modules/stage7_text_polishing/test_processor.py - 2 batch tests
- docs/CHANGELOG.md - Documented both features

**Test results:** ✅ 280/280 tests pass (+10 new tests)
**Impact:** Users get clear error upfront instead of mid-pipeline failure

---

## Template for Next Session

Copy this when you complete significant work:

```markdown
### Session YYYY-MM-DD: [Brief Description]

**What was done:**
1.
2.

**The problem:** (if applicable)
[Describe the issue]

**The solution:** (if applicable)
[Describe how you solved it]

**Key lessons:**
- ✅ [What went well]
- ❌ [What to avoid]
- 🐛 [Bugs discovered]

**Files modified:**
- file.py - what changed

**Test results:** [X/X tests pass, +Y new tests]
**Impact:** [Performance/UX improvements if applicable]
```

---

## How to Update This Guide

**Update AI_GUIDE.md when:**
- Restructuring documentation
- Adding new specialized guides
- Changing navigation structure
- **Adding session history** (end of every significant work session)

**Update the detailed guides when:**
- **GUIDELINES.md** - New AI-specific patterns, critical rules, language guidelines
- **WORKFLOWS.md** - New common tasks, workflow improvements, documentation procedures
- **TROUBLESHOOTING.md** - New problems/solutions, debugging strategies
- **REFERENCE.md** - New commands, settings, file locations

**Update LESSONS_LEARNED.md when:**
- You make a mistake worth documenting
- You discover a gotcha or design decision
- You solve a tricky problem

**Documentation Update Checklist (use this BEFORE saying you're done!):**

```markdown
When completing significant work, ask yourself:

□ Did I update CHANGELOG.md with what changed? (REQUIRED)
□ Did I add session history to AI_GUIDE.md? (REQUIRED for significant work)

Then check if updates needed in specialized guides:
□ GUIDELINES.md - Did I discover new patterns or make critical mistakes?
□ WORKFLOWS.md - Did I create/improve a workflow or procedure?
□ REFERENCE.md - Did I create new utilities, commands, or patterns?
□ TROUBLESHOOTING.md - Did I solve a tricky problem?
□ LESSONS_LEARNED.md - Did I discover gotchas or design decisions?

If YES to any specialized guide, update it!
```

**Keep this file under 400 lines** - It's a navigation hub, not a knowledge base

---

*This guide structure was created 2025-10-12 to improve navigation and reduce token usage. Session history added 2025-10-14 for long-term maintenance. It is a living document maintained by AI assistants across sessions.*
