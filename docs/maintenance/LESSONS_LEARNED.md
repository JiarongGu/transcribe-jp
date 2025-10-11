# Lessons Learned - Knowledge Database

**Quick Reference:** Mistakes, gotchas, and design decisions to prevent future issues. Read this before making architectural changes.

**Last Updated:** 2025-10-11
**Related:** [AI_GUIDE.md](AI_GUIDE.md), [SESSIONS.md](SESSIONS.md), [CHANGELOG.md](CHANGELOG.md)

---

## Purpose

This document captures **lessons learned** across all development sessions to:
1. **Prevent repeating mistakes** - Learn from past errors
2. **Document design decisions** - Why things are the way they are
3. **Provide context** - Background that's not obvious from code
4. **Guide future development** - What to do (and what NOT to do)

**For AI Assistants:** Read this document early in your session to understand project patterns and avoid known pitfalls.

---

## Table of Contents

1. [Configuration Design](#configuration-design)
2. [LLM Provider System](#llm-provider-system)
3. [Documentation Structure](#documentation-structure)
4. [Testing Practices](#testing-practices)
5. [Code Organization](#code-organization)
6. [Japanese Language Handling](#japanese-language-handling)
7. [Pipeline Architecture](#pipeline-architecture)

---

## Configuration Design

### ✅ Lesson: Use Nested Configs for Provider-Specific Settings

**Date:** 2025-10-11
**Context:** LLM provider configuration refactor

**Mistake:** Initially used flat config structure mixing settings from different providers:
```json
{
  "llm": {
    "provider": "ollama",
    "ollama_base_url": "...",
    "anthropic_api_key": "...",
    "openai_api_key": "...",
    "model": "..."  // Which provider's model?
  }
}
```

**Problem:**
- Unclear which settings belong to which provider
- Name collisions (all providers need "model", "api_key", etc.)
- Hard to understand configuration at a glance
- Difficult to extend with new providers

**Solution:** Nested structure with provider-specific sub-configs:
```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "llama3.2:3b"
    },
    "anthropic": {
      "api_key": "...",
      "model": "claude-3-5-haiku-20241022"
    },
    "openai": {
      "api_key": "...",
      "model": "gpt-4o-mini"
    }
  }
}
```

**Benefits:**
- Clear separation of concerns
- No name collisions
- Easy to add new providers
- Self-documenting structure
- Users can configure all providers at once

**Implementation:** [shared/llm_utils.py](../shared/llm_utils.py)

**Backward Compatibility:** Always check both old and new locations:
```python
# Check nested config first, fall back to flat
model = config.get("ollama", {}).get("model") or config.get("model", "default")
```

**Lesson:** When different providers/modes/types need similar settings, use nested configs instead of prefixes.

---

### ✅ Lesson: Stage-Specific Overrides Need Clear Naming

**Date:** 2025-10-11
**Context:** Implementing stage-specific LLM provider override

**Mistake:** Unclear whether stage overrides work and how to use them.

**Solution:** Document and test stage-specific override pattern:
```json
{
  "llm": {
    "provider": "ollama"  // Global default
  },
  "text_polishing": {
    "enable": true,
    "llm_provider": "anthropic",  // Override for this stage
    "llm_config": {
      "anthropic": {
        "api_key": "..."
      }
    }
  }
}
```

**Pattern:**
1. `{stage_name}.llm_provider` - Override provider for specific stage
2. `{stage_name}.llm_config` - Merge with global `llm` config
3. Global `llm` config provides defaults

**Lesson:** Always verify complex config features work and document with examples.

---

## LLM Provider System

### ✅ Lesson: Don't Create Example Config Files, Use Documentation Instead

**Date:** 2025-10-11
**Context:** Removing `config.llm_examples.json`

**Mistake:** Created separate `config.llm_examples.json` file with configuration examples.

**Problems:**
1. **Redundant** - Same information exists in documentation
2. **Gets outdated** - Example file not updated with docs
3. **User confusion** - Is it a real config or just examples?
4. **Maintenance burden** - Update both file and docs
5. **Not discoverable** - Users might not find it

**Solution:** Use documentation and `config.local.json.example` instead:
- **LLM_PROVIDERS.md** - Comprehensive guide with inline examples
- **config.local.json.example** - Real config template users copy
- **CONFIGURATION.md** - Reference documentation

**Benefits:**
- Single source of truth
- Examples in context with explanations
- Users copy working template
- Less maintenance

**Lesson:** Example config files are redundant with good documentation. Use docs + config.local.json.example instead.

---

### ✅ Lesson: Provider Abstraction Should Be Simple

**Date:** 2025-10-11
**Context:** Implementing LLM provider system

**Good Decision:** Simple provider abstraction with one method:
```python
class LLMProvider:
    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        pass
```

**Why it works:**
- Single responsibility: generate text from prompt
- Easy to add new providers (just implement one method)
- No complex interfaces or multiple methods
- Handles provider-specific details internally

**Anti-pattern to avoid:**
```python
# Don't do this - too complex
class LLMProvider:
    def initialize(self): pass
    def validate_config(self): pass
    def prepare_request(self): pass
    def send_request(self): pass
    def parse_response(self): pass
    def handle_error(self): pass
```

**Lesson:** Keep abstractions simple. One well-defined method is better than many small ones.

---

## Documentation Structure

### ✅ Lesson: Create Topic-Specific Docs for Complex Features

**Date:** 2025-10-11
**Context:** Creating LLM_PROVIDERS.md

**Good Decision:** Created separate `docs/LLM_PROVIDERS.md` for LLM configuration.

**Why:**
- **Self-contained** - Stands alone, no dependencies
- **Comprehensive** - Setup, examples, troubleshooting, FAQ
- **User-focused** - Solves complete user problem
- **AI-discoverable** - Listed in AI_GUIDE.md Quick Start
- **Maintainable** - Single place for all LLM info

**When to create topic-specific docs:**
1. Feature is substantial (>100 lines)
2. Needs detailed examples and troubleshooting
3. Benefits multiple stakeholders (users, developers, AI)
4. Self-contained topic
5. Will be frequently referenced

**Structure to use:**
```markdown
# Title
Quick Reference + Metadata
Overview
Quick Start (most common use case)
Detailed Sections (in-depth)
Troubleshooting
FAQ
See Also (cross-references)
```

**Lesson:** Don't cram everything into CONFIGURATION.md or README.md. Create focused topic docs.

---

### ✅ Lesson: Documentation Should Be AI-Discoverable

**Date:** 2025-10-11
**Context:** Adding knowledge base section to AI_GUIDE.md

**Pattern:** Make docs discoverable for AI assistants:

1. **List in AI_GUIDE.md Quick Start:**
   ```markdown
   **Key Knowledge Base Documents:**
   - [LLM_PROVIDERS.md](LLM_PROVIDERS.md) - Description
   ```

2. **Add metadata at top:**
   ```markdown
   **Quick Reference:** One-line summary
   **Last Updated:** 2025-10-11
   **Related:** [Doc1](link), [Doc2](link)
   ```

3. **Use clear, keyword-rich headers:**
   - "How to Configure Ollama" ✅
   - "Setup" ❌ (too vague)

4. **Cross-reference bidirectionally:**
   - If A links to B, B should link to A

5. **Include Quick Reference at top:**
   - AI assistants read this first to decide relevance

**Lesson:** Optimize documentation for AI assistant discovery, not just humans.

---

### ✅ Lesson: Separate User Docs from Developer Docs

**Date:** 2025-10-11
**Context:** Documentation restructure

**Good Decision:** Clear separation:
- **User docs:** README.md, LLM_PROVIDERS.md
- **Developer docs:** ARCHITECTURE.md, PIPELINE_STAGES.md
- **AI/maintainer docs:** AI_GUIDE.md, LESSONS_LEARNED.md

**Don't mix:** Avoid putting implementation details in user docs or vice versa.

**Lesson:** Keep docs focused on their audience. Users don't need implementation details.

---

## Testing Practices

### ✅ Lesson: Update Test Assertions When Error Messages Change

**Date:** 2025-10-11
**Context:** LLM provider refactor broke one test

**Mistake:** Changed error message without updating test:
```python
# Old code
print("Warning: API key not found")

# New code
print(f"Warning: Failed to initialize {provider} provider: API key not found")

# Test still expected old message
assert "Warning: API key not found" in output  # ❌ Fails
```

**Solution:** Update test to match new error message:
```python
assert "Warning: Failed to initialize" in output
assert "API key not found" in output
```

**Lesson:** When refactoring, search for test assertions on error messages you change.

**Command to check:**
```bash
grep -r "API key not found" tests/
```

---

### ✅ Lesson: Test Configuration Backward Compatibility

**Date:** 2025-10-11
**Context:** Nested config structure

**Good Decision:** Added fallback to old config structure:
```python
# Check new location first, fall back to old
api_key = config.get("anthropic", {}).get("api_key") or config.get("anthropic_api_key")
```

**Why:**
- Doesn't break existing user configs
- Smooth migration path
- Can deprecate old structure later

**Lesson:** When changing config structure, support both old and new for backward compatibility.

---

## Code Organization

### ✅ Lesson: Centralize Shared Utilities Early

**Date:** Multiple sessions
**Context:** Text utilities, LLM utilities

**Good Decision:** Created `shared/` directory:
- `shared/text_utils.py` - Text normalization, Japanese utils
- `shared/whisper_utils.py` - Whisper transcription
- `shared/llm_utils.py` - LLM provider abstraction

**Anti-pattern:** Copy-pasting similar code in multiple modules.

**Lesson:** When you need same functionality in 2+ places, extract to `shared/`.

---

### ✅ Lesson: Provider Classes Should Handle Their Own Config

**Date:** 2025-10-11
**Context:** LLM provider classes

**Good Decision:** Each provider extracts its own config:
```python
class OllamaProvider:
    def __init__(self, config):
        ollama_config = config.get("ollama", {})
        self.model = ollama_config.get("model", "default")
```

**Why:**
- Provider knows what config it needs
- Encapsulation - config details stay in provider
- Easy to add provider-specific options

**Anti-pattern:** Central config extractor:
```python
# Don't do this
def extract_ollama_config(config):
    return {...}
```

**Lesson:** Let classes handle their own config extraction.

---

## Japanese Language Handling

### ✅ Lesson: Particle Variations Require Fuzzy Matching

**Date:** Earlier sessions
**Context:** Timing realignment

**Key Finding:** Whisper transcribes same audio differently:
- は (particle) vs わ (wa sound)
- を (particle) vs お (o sound)

**Solution:** Use similarity threshold of 0.75 instead of exact matching.

**Implementation:** `difflib.SequenceMatcher` for fuzzy text comparison.

**Lesson:** Japanese text matching needs fuzzy comparison due to particle ambiguity.

---

## Pipeline Architecture

### ✅ Lesson: Stage Order Matters - Filter Before Realignment

**Date:** Earlier sessions
**Context:** Pipeline stage ordering

**Critical Order:**
1. Stage 5: Hallucination filtering
2. Stage 6: Timing realignment
3. Stage 7: Text polishing

**Why:**
- Filter hallucinations before expensive re-transcription
- Realign timing before polishing (polishing changes text)
- Polish after timing is final

**Lesson:** Don't change pipeline stage order without deep analysis.

---

### ✅ Lesson: LLM Should Only Be Used for Semantic Tasks

**Date:** Earlier sessions
**Context:** Don't use LLM for text similarity

**Good:** LLM for semantic understanding
- Segment splitting (natural phrase boundaries)
- Text polishing (grammar, punctuation)

**Bad:** LLM for non-semantic tasks
- Text similarity → Use `difflib.SequenceMatcher`
- Timing validation → Use Whisper re-transcription
- Pattern matching → Use regex

**Why:**
- Expensive (API costs)
- Slower than algorithms
- Unnecessary for deterministic tasks
- Harder to test/debug

**Lesson:** Use LLM only when semantic understanding is required.

---

## How to Update This Document

### Adding New Lessons

**Format:**
```markdown
### ✅ Lesson: Clear Title Describing The Lesson

**Date:** YYYY-MM-DD
**Context:** What were you working on?

**Mistake/Decision:** What happened? (Include code examples)

**Problem/Why:** What was wrong? Why did you do it this way?

**Solution/Benefit:** How did you fix it? What's better now?

**Lesson:** One-sentence takeaway for future developers.

**Implementation:** Link to relevant code/docs if applicable.
```

**Categories:**
- Configuration Design
- LLM Provider System
- Documentation Structure
- Testing Practices
- Code Organization
- Japanese Language Handling
- Pipeline Architecture
- *Add new categories as needed*

### When to Add a Lesson

Add a lesson when:
1. **You made a mistake** - Document it so others don't repeat it
2. **You discovered a gotcha** - Something non-obvious that caused problems
3. **You made a design decision** - Explain the reasoning for future reference
4. **You solved a tricky problem** - Share the solution pattern
5. **You refactored something** - Document why the new way is better

### What NOT to Add

Don't add:
- General programming advice (use language-specific guides)
- Obvious best practices (follow PEP 8, write tests, etc.)
- Temporary workarounds (document in code comments instead)
- Incomplete investigations (wait until you have a conclusion)

### Update AI_GUIDE.md Too

When adding significant lessons:
1. Update this document with details
2. Add key takeaway to AI_GUIDE.md "DO NOT" or "DO" sections
3. Link from AI_GUIDE.md to this document for details

**Example:**
```markdown
# In AI_GUIDE.md
### ❌ DO NOT create example config files
- Use documentation instead (see LESSONS_LEARNED.md)
- Example: config.llm_examples.json was redundant with LLM_PROVIDERS.md
```

---

## Quick Reference Checklist

Before making major changes, ask:

- [ ] Is this configuration change backward compatible?
- [ ] Do I need nested config structure for provider-specific settings?
- [ ] Should this be a separate doc instead of adding to existing ones?
- [ ] Will this work with Japanese particle variations?
- [ ] Am I using LLM when an algorithm would work better?
- [ ] Does this change affect pipeline stage order?
- [ ] Have I updated test assertions for changed error messages?
- [ ] Is this properly cross-referenced in AI_GUIDE.md?
- [ ] Did I add a lesson to LESSONS_LEARNED.md?

---

## See Also

- [AI_GUIDE.md](AI_GUIDE.md) - AI assistant guidelines (references this doc)
- [SESSIONS.md](SESSIONS.md) - Detailed session history
- [CHANGELOG.md](CHANGELOG.md) - What changed and when
- [ARCHITECTURE.md](core/ARCHITECTURE.md) - System design
- [PIPELINE_STAGES.md](core/PIPELINE_STAGES.md) - Pipeline details

---

*This document was created in session 2025-10-11. It is a living knowledge base maintained across sessions to prevent repeating mistakes and preserve design context.*
