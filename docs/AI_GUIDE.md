# AI Assistant Guide for transcribe-jp

> **LIVING DOCUMENT:** This guide is maintained by AI assistants across sessions. If you discover new patterns, conventions, or lessons learned while working on this project, **UPDATE THE DETAILED GUIDES** and commit your changes. Future AI sessions depend on this knowledge.

**Version:** 3.0
**Last Updated:** 2025-10-12
**Changes from v2.0:** Split into focused guides (GUIDELINES, WORKFLOWS, TROUBLESHOOTING, REFERENCE)

---

## Purpose

This guide provides AI-specific context for working on transcribe-jp. It focuses on guidelines, lessons learned, and decision-making frameworks that aren't covered in the regular project documentation.

**For detailed information, see the specialized guides below.**

---

## 5 Critical Rules (Non-Negotiable)

1. **ALWAYS run tests before committing** - All 275 tests must pass
   ```bash
   python -X utf8 -m pytest tests/unit/ -q --tb=line
   ```

2. **ALWAYS update CHANGELOG.md BEFORE committing**
   - Add entry with Date + Time format: [2025-10-12 05:30]
   - Include: what changed, impact, files modified, test results

3. **ALWAYS suggest git commit after completing tasks**
   - Ask: "Should I commit these changes to git?"
   - Use co-authorship footer (see [WORKFLOWS.md](ai-assistant/WORKFLOWS.md))

4. **Check for redundancy before adding features**
   - Stage 5 = hallucinations, Stage 6 = timing, Stage 8 = cleanup
   - Search first: `grep -r "feature_name"`

5. **Follow Japanese text conventions**
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

## How to Update This Guide

**Update AI_GUIDE.md when:**
- Restructuring documentation
- Adding new specialized guides
- Changing navigation structure

**Update the detailed guides when:**
- **GUIDELINES.md** - New AI-specific patterns, critical rules, language guidelines
- **WORKFLOWS.md** - New common tasks, workflow improvements, documentation procedures
- **TROUBLESHOOTING.md** - New problems/solutions, debugging strategies
- **REFERENCE.md** - New commands, settings, file locations

**Update LESSONS_LEARNED.md when:**
- You make a mistake worth documenting
- You discover a gotcha or design decision
- You solve a tricky problem

**Update SESSIONS.md when:**
- You complete significant work
- You want to document context for future work

---

*This guide structure was created 2025-10-12 to improve navigation and reduce token usage. It is a living document maintained by AI assistants across sessions.*
