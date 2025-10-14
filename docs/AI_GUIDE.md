# AI Assistant Guide for transcribe-jp

> **LIVING DOCUMENT:** This guide is maintained by AI assistants across sessions. If you discover new patterns, conventions, or lessons learned while working on this project, **UPDATE THE DETAILED GUIDES** and commit your changes. Future AI sessions depend on this knowledge.

**Version:** 3.3
**Last Updated:** 2025-10-14
**Changes from v3.2:** Added prominent warnings that AI_GUIDE.md is navigation only, must read GUIDELINES.md and WORKFLOWS.md
**Latest update:** Session 2025-10-14 - Fixed navigation issue causing AI assistants to skip full checklists

---

## Purpose

This guide provides AI-specific context for working on transcribe-jp. It focuses on quick onboarding, navigation to detailed guides, and session history for easy catch-up.

**Token Optimization:** This file is intentionally compact. Detailed knowledge is in specialized guides - load only what you need for your current task.

**For detailed information, see the specialized guides below.**

---

## ⚠️ BEFORE YOU START: Read These First

This AI_GUIDE.md is a **NAVIGATION HUB** - it provides a summary and points you to detailed guides.

**🚨 CRITICAL: The "7 Critical Rules" below is a QUICK REFERENCE ONLY! 🚨**

**YOU MUST read the full checklists in:**
1. **[ai-assistant/GUIDELINES.md](ai-assistant/GUIDELINES.md)** - Complete DO's and DON'Ts (8 rules + 6 mistakes)
2. **[ai-assistant/WORKFLOWS.md](ai-assistant/WORKFLOWS.md)** - Step-by-step git commit workflow with full checklist

**❌ Common mistake:** Reading only AI_GUIDE.md's 6 rules and thinking that's everything
**✅ Correct approach:** AI_GUIDE.md for navigation → GUIDELINES.md + WORKFLOWS.md for full details

---

## 7 Critical Rules (Quick Reference - NOT Complete!)

**⚠️ This is a SUMMARY. Read [GUIDELINES.md](ai-assistant/GUIDELINES.md) for full rules!**

1. **ALWAYS run tests before committing** - All 280+ tests must pass
   ```bash
   python -X utf8 -m pytest tests/unit/ -q --tb=line
   ```

2. **ALWAYS update CHANGELOG.md BEFORE committing**
   - Add entry with Date + Time format: [2025-10-12 05:30]
   - Include: what changed, impact, files modified, test results

3. **ALWAYS verify related documentation is updated** ⚠️ CRITICAL - MOST VIOLATED RULE
   - After updating CHANGELOG, search: `grep -r "feature_name" docs/ --include="*.md"`
   - **Check ALL these locations:**
     - `docs/core/` (ARCHITECTURE.md, CONFIGURATION.md, PIPELINE_STAGES.md)
     - `docs/features/` (stage-specific docs, especially LLM_PROVIDERS.md)
     - `docs/ai-assistant/` (WORKFLOWS.md, GUIDELINES.md, REFERENCE.md, TROUBLESHOOTING.md)
     - Root level (README.md, AI_GUIDE.md)
     - Config files (config.local.json.example)
   - See [WORKFLOWS.md Documentation Verification](ai-assistant/WORKFLOWS.md#documentation-verification)
   - **Code + docs must be updated together** - no exceptions!

   **⚠️ VIOLATION CONSEQUENCES:**
   - Next AI session won't know about new features
   - Users won't find documentation for error messages
   - Technical debt accumulates
   - **Ask yourself BEFORE every commit: "What docs need updating?"**

4. **ALWAYS suggest git commit after completing tasks**
   - Ask: "Should I commit these changes to git?"
   - Use co-authorship footer (see [WORKFLOWS.md](ai-assistant/WORKFLOWS.md))

5. **Check for redundancy before adding features**
   - Stage 5 = hallucinations, Stage 6 = timing, Stage 8 = cleanup
   - Search first: `grep -r "feature_name"`

6. **Follow Japanese text conventions**
   - No spaces, particle variations (は/わ, を/お), 0.75 similarity threshold

7. **❌ NEVER revert or unstage user changes** ⚠️ TRUST ISSUE
   - If a file is staged, the user put it there intentionally
   - **NEVER run:** `git restore --staged`, `git restore`, `git reset HEAD`, `git checkout --`
   - AI can ADD changes, but NEVER REMOVE user's work
   - Only exception: User explicitly asks "please revert X"
   - See [LESSONS_LEARNED.md Git and Version Control](maintenance/LESSONS_LEARNED.md#git-and-version-control)

---

## Quick Start Sequence

**First time working on this project? Read in this order:**

1. [README.md](../README.md) - Project overview, installation, basic usage
2. [maintenance/LESSONS_LEARNED.md](maintenance/LESSONS_LEARNED.md) - **START HERE!** Mistakes to avoid
3. [core/ARCHITECTURE.md](core/ARCHITECTURE.md) - 9-stage pipeline, directory structure
4. [CHANGELOG.md](CHANGELOG.md) - Recent changes and git history
5. **[ai-assistant/GUIDELINES.md](ai-assistant/GUIDELINES.md)** - **MANDATORY!** Complete rules (8 DO's + 6 DON'Ts)
6. **[ai-assistant/WORKFLOWS.md](ai-assistant/WORKFLOWS.md)** - **READ BEFORE COMMITTING!** Git workflow checklist

**⚠️ CRITICAL for committing:** Read GUIDELINES.md #1-3 and WORKFLOWS.md "Git Commit Workflow" section BEFORE making any commits!

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
- **285 tests** - 280 unit + 4 E2E + 1 smoke test (all must pass before committing)
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
├── maintenance/SESSIONS.md                  # Development history (chronological)
├── features/LLM_PROVIDERS.md                # LLM provider configuration
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

## Session History

**For detailed session history, see [maintenance/SESSIONS.md](maintenance/SESSIONS.md)**

Session history has been moved to a dedicated file to keep AI_GUIDE.md compact and optimize token usage. SESSIONS.md contains:
- Chronological development history
- Problem/solution context for each session
- Lessons learned and key takeaways
- Files modified and test results
- Template for documenting new sessions

**Latest sessions:**
- 2025-10-14: Ollama Path Detection + Integration Tests
- 2025-10-14: Error Reporting + Model Pulling + Timeout Configuration
- 2025-10-14: Batch Processing Control + Ollama Pre-Flight Validation

**Read [SESSIONS.md](maintenance/SESSIONS.md) for full details and context.**

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
□ Did I add session history to maintenance/SESSIONS.md? (REQUIRED for significant work)

Then check if updates needed in specialized guides:
□ GUIDELINES.md - Did I discover new patterns or make critical mistakes?
□ WORKFLOWS.md - Did I create/improve a workflow or procedure?
□ REFERENCE.md - Did I create new utilities, commands, or patterns?
□ TROUBLESHOOTING.md - Did I solve a tricky problem?
□ LESSONS_LEARNED.md - Did I discover gotchas or design decisions?

If YES to any specialized guide, update it!
```

**⚠️ MANDATORY PRE-COMMIT CHECKLIST FOR USER-FACING CHANGES:**

Use this checklist BEFORE every commit that adds user-facing features:

```markdown
□ Added error messages? → Update LLM_PROVIDERS.md or TROUBLESHOOTING.md
□ Added config parameters? → Update CONFIGURATION.md + REFERENCE.md
□ Changed timeout/max_tokens behavior? → Update LLM_PROVIDERS.md
□ Added new commands/scripts? → Update REFERENCE.md
□ Changed error handling? → Update relevant troubleshooting docs
□ Changed CLI output/progress bars? → No doc update needed (internal)
□ Only refactored/fixed bugs? → Check if error messages changed

**If you added code that users will SEE or CONFIGURE, you MUST update docs!**
```

**Example violations to avoid:**
- ❌ Added detailed Ollama error messages → Forgot to document them
- ❌ Added max_tokens=0 feature → Forgot to document in CONFIGURATION.md
- ❌ Changed timeout priority → Forgot to update LLM_PROVIDERS.md
- ✅ Fixed progress bar bug → No user-visible config changes, no docs needed
- ✅ Refactored internal code → No user impact, no docs needed

**Keep this file under 450 lines** - It's a navigation hub, not a knowledge base

---

## Version History

**v3.3 (2025-10-14):** Added prominent warnings that AI_GUIDE.md is a navigation hub, not the complete rulebook. AI assistants were skipping GUIDELINES.md and WORKFLOWS.md, causing incomplete commits. Added "BEFORE YOU START" section and emphasized reading full guides before committing.

**v3.2 (2025-10-14):** Added Session History section for long-term maintenance tracking.

**v3.1 (2025-10-12):** Initial restructure to separate navigation (AI_GUIDE.md) from detailed guides (GUIDELINES.md, WORKFLOWS.md, etc.).

---

*This guide structure was created 2025-10-12 to improve navigation and reduce token usage. Session history added 2025-10-14 for long-term maintenance. It is a living document maintained by AI assistants across sessions.*
