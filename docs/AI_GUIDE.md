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

**🚨 CRITICAL: The "6 Critical Rules" below is a QUICK REFERENCE ONLY! 🚨**

**YOU MUST read the full checklists in:**
1. **[ai-assistant/GUIDELINES.md](ai-assistant/GUIDELINES.md)** - Complete DO's and DON'Ts (8 rules + 6 mistakes)
2. **[ai-assistant/WORKFLOWS.md](ai-assistant/WORKFLOWS.md)** - Step-by-step git commit workflow with full checklist

**❌ Common mistake:** Reading only AI_GUIDE.md's 6 rules and thinking that's everything
**✅ Correct approach:** AI_GUIDE.md for navigation → GUIDELINES.md + WORKFLOWS.md for full details

---

## 6 Critical Rules (Quick Reference - NOT Complete!)

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

### Session 2025-10-14 (Latest): Ollama Path Detection + Integration Tests

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
1. **Multi-location detection:** Check PATH + 4-5 common locations per platform (Windows: %LOCALAPPDATA%, Program Files, Program Files (x86), %APPDATA%; macOS: /usr/local/bin, /opt/homebrew/bin, ~/.local/bin, /Applications/Ollama.app; Linux: ~/.local/bin, /usr/local/bin, /usr/bin, /opt/ollama/bin)
2. **Manual config options:** Added `executable_path` (custom Ollama path) and enhanced `base_url` (external server) config parameters
3. **Priority system:** Custom path → PATH → Platform-specific locations → Fail with clear error
4. **Integration tests:** Cover installation detection, custom paths, external servers, generation, timeouts, error messages
5. **Diagnostic tool:** test_ollama_quick.py tests server connection + generation timing to identify slow model/CPU issues

**Key lessons:**
- ✅ Comprehensive path detection prevents "not found" errors on different PCs
- ✅ Manual configuration options essential for non-standard installations (portable, custom directory, remote server)
- ✅ Integration tests catch real-world configuration issues (different install locations, paths, servers)
- ✅ Diagnostic tools help users self-diagnose issues (timeout = slow model, not "Ollama broken")
- ✅ Document both automatic AND manual configuration (users need fallback when auto-detection fails)
- ✅ Priority system makes behavior predictable (custom path always wins)
- ✅ Platform-specific paths vary widely (Windows alone has 4+ common locations)
- ❌ DON'T assume PATH detection is sufficient - many installers don't add to PATH
- ❌ DON'T assume single installation location per platform - users install in custom locations
- ❌ DON'T skip integration tests for cross-platform features - path detection is OS-specific

**Files modified:**
- shared/ollama_manager.py - Enhanced `_get_ollama_executable()` with multi-location detection (lines 44-101), added executable_path + base_url parameters
- shared/llm_utils.py - Read and pass executable_path config to OllamaManager
- docs/features/OLLAMA_CONFIGURATION.md - NEW comprehensive configuration guide (540 lines)
- config.local.json.example - Added executable_path example
- tests/integration/test_ollama.py - NEW integration test suite (600 lines, 8 classes)
- test_ollama_quick.py - NEW diagnostic tool for timeout troubleshooting

**Test results:** ✅ 280/280 unit tests pass, 20+ integration tests created
**Impact:**
- Cross-platform Ollama detection works reliably on any PC (standard or custom installation)
- Users can manually configure Ollama path when auto-detection fails
- Integration tests catch configuration issues before they affect users
- Diagnostic tool helps users identify timeout issues (model speed, GPU vs CPU)

### Session 2025-10-14 (Continued): Error Reporting + Model Pulling + Timeout + Config Optimization

**What was done:**
1. **Fixed progress bar duplication** in text polishing one-by-one mode
2. **Improved error reporting** - shows error type, segment number, actual text
3. **Added automatic model pulling with progress bar** for Ollama
4. **Added flexible timeout configuration** - common, provider-specific, stage-specific
5. **Added unlimited max_tokens feature** - set to 0 for no token limit
6. **Enhanced Ollama error handling** - detailed diagnostics for all timeout/connection scenarios
7. **Optimized config** - downgraded to qwen3:8b for RTX 4070, removed unnecessary llm_timeout
8. **Updated documentation** - LLM_PROVIDERS.md with comprehensive error scenarios

**The problem:**
- Progress bar displayed twice during one-by-one processing
- Error messages didn't show WHY batches were failing
- Models weren't auto-pulled when missing - pipeline just failed
- 30-second timeout too short for large models (qwen3:32b = 32B parameters)
- No way to set different timeouts for different stages
- max_tokens limit could cause incomplete responses with large batches

**The solution:**
1. **Progress bar:** Moved `_print_progress()` to single location after both code paths
2. **Error reporting:** Added error type/message, segment number, actual failing text
3. **Model pulling:** Added `_ensure_model()` that checks and auto-pulls with progress bar
4. **Timeout config:** Three-level priority system (stage > provider > common > default)
5. **Unlimited tokens:** `max_tokens: 0` → Ollama omits limit, Anthropic uses 4096, OpenAI uses None
6. **Config update:** `timeout: 60` global, `llm_timeout: 180` for text polishing, `batch_size: 1`

**Key lessons:**
- ✅ Progress bars should be called once per iteration, not in multiple code paths
- ✅ Error messages should show WHAT failed, WHERE, and WHY (error type + message)
- ✅ Detailed error messages with bullet points improve debugging experience dramatically
- ✅ Large models (32B+) need 2-5 minutes timeout, not 30 seconds
- ✅ Different stages have different performance needs (splitting fast, polishing slow)
- ✅ Auto-pulling models with progress bar improves UX dramatically
- ✅ Timeout should be configurable at multiple levels (global, provider, stage)
- ✅ max_tokens=0 for unlimited prevents cut-off responses with large batches
- ✅ **CRITICAL**: Update documentation IMMEDIATELY when adding error handling or user-facing features
- ❌ DON'T hardcode timeouts - models vary from 2B to 32B+ parameters
- ❌ DON'T assume 1024 tokens is enough for all batch sizes - scale with batch_size or use 0
- ❌ **DON'T skip documentation updates** - violates Rule #3, breaks future sessions

**Files modified:**
- modules/stage7_text_polishing/processor.py - Progress bar fix + error reporting
- shared/ollama_manager.py - Enhanced model pulling with progress bar
- shared/llm_utils.py - _ensure_model(), timeout support, max_tokens=0, detailed error handling
- docs/features/LLM_PROVIDERS.md - Comprehensive timeout + error scenarios documentation
- docs/core/CONFIGURATION.md - Updated LLM parameter docs
- docs/ai-assistant/REFERENCE.md - Added LLM quick reference
- config.json - Optimized for qwen3:8b with timeout: 45, batch_size: 1
- test_ollama_integration.py - Integration test script

**Test results:** ✅ 280/280 tests pass (no regressions)
**Impact:**
- Clear error diagnosis (can see timeout, JSON parsing, connection errors)
- Auto model pulling (no manual "ollama pull" needed)
- Large models work reliably (proper timeout for 32B models)

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
