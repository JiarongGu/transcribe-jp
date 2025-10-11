# AI_GUIDE.md Refactoring Plan

**Created:** 2025-10-12
**Purpose:** Prevent AI_GUIDE.md from becoming unmanageably large

---

## Current Problems

**AI_GUIDE.md is 19 KB (557 lines) and growing:**
- Will hit 40-50 KB in 10-15 sessions
- Trying to be both quick reference AND comprehensive guide
- Duplicates content from other docs (CONFIGURATION.md, LESSONS_LEARNED.md)
- Growing sections: Critical Guidelines, Common Tasks, DO NOTs

**Not sustainable long-term.**

---

## Proposed Structure

### New Organization (3-Tier System)

```
docs/
├── AI_GUIDE.md (SLIM - 100 lines max, ~5KB)
│   ├── Quick Start (what to read first)
│   ├── 5 Critical Rules (non-negotiable)
│   ├── Links to detailed guides
│   └── Emergency contacts (CHANGELOG, LESSONS_LEARNED)
│
└── maintenance/
    └── ai/
        ├── GUIDELINES.md (DO/DON'T, patterns)
        ├── WORKFLOWS.md (common tasks, step-by-step)
        ├── TROUBLESHOOTING.md (common issues)
        └── REFERENCE.md (quick lookups, commands)
```

---

## Tier 1: AI_GUIDE.md (Entry Point)

**Target:** <100 lines, <5KB
**Purpose:** Get AI started fast, point to details

```markdown
# AI Assistant Quick Start

**🚀 Start Here:** This is your entry point. Everything else is linked below.

## 5 Critical Rules (Non-Negotiable)

1. ✅ Run ALL tests before committing (`pytest tests/`)
2. ✅ Update CHANGELOG.md BEFORE every commit
3. ✅ Read LESSONS_LEARNED.md before architectural changes
4. ✅ Archive CHANGELOG when >50KB (see DOCUMENTATION_SCALING_STRATEGY)
5. ✅ Don't skip these rules - user explicitly requested this workflow

## Quick Start Sequence

**For new sessions:**
1. Read [CHANGELOG.md](../CHANGELOG.md) (recent entries)
2. Read [LESSONS_LEARNED.md](LESSONS_LEARNED.md) (mistakes to avoid)
3. Check task type → load relevant guide (see below)

**Task-Specific Guides:**
- Configuration changes → [GUIDELINES.md](ai/GUIDELINES.md#configuration)
- Adding features → [WORKFLOWS.md](ai/WORKFLOWS.md#adding-features)
- Bug fixes → [TROUBLESHOOTING.md](ai/TROUBLESHOOTING.md)
- LLM changes → [maintenance/lessons/LLM_SYSTEM.md](lessons/LLM_SYSTEM.md)
- Testing → [REFERENCE.md](ai/REFERENCE.md#testing)

## Key Facts

- 9-stage Japanese transcription pipeline
- 275 tests (all must pass)
- Japanese-specific: particle variations, no spaces
- Test command: `python -m pytest tests/ -v -q --tb=line`

## Documentation Map

```
Quick Start (you are here)
    ↓
CHANGELOG.md → What changed recently?
    ↓
LESSONS_LEARNED.md → What mistakes to avoid?
    ↓
Task-specific guide → How to do X?
    ↓
REFERENCE.md → Quick command lookup
```

## Emergency Contacts

**Something broke?** → [TROUBLESHOOTING.md](ai/TROUBLESHOOTING.md)
**Need commands?** → [REFERENCE.md](ai/REFERENCE.md)
**Architectural question?** → [LESSONS_LEARNED.md](LESSONS_LEARNED.md)
**Recent changes?** → [CHANGELOG.md](../CHANGELOG.md)

---

*For detailed guidelines, workflows, and references, see docs/maintenance/ai/*
```

---

## Tier 2: Detailed Guides (docs/maintenance/ai/)

### A. GUIDELINES.md (DO/DON'T, Patterns)

**Target:** <30KB
**Content:**
- ✅ DO (Non-Negotiable) - detailed explanations
- ❌ DO NOT (Common Mistakes) - with examples
- Configuration patterns
- Japanese text handling
- LLM usage guidelines
- Code organization principles

**Sections:**
```markdown
# AI Assistant Guidelines

## Critical Do's
## Critical Don'ts
## Configuration Patterns
## Japanese Language Handling
## LLM Usage Guidelines
## Code Organization
## Testing Guidelines
```

### B. WORKFLOWS.md (Common Tasks)

**Target:** <30KB
**Content:**
- Step-by-step task workflows
- Adding new filter
- Modifying text similarity
- Creating new stage
- Updating documentation
- Git commit workflow

**Sections:**
```markdown
# AI Assistant Workflows

## Adding a New Filter
## Modifying Text Similarity
## Creating a New Stage
## Updating Configuration
## Git Commit Workflow
## Documentation Updates
```

### C. TROUBLESHOOTING.md (Common Issues)

**Target:** <20KB
**Content:**
- Unicode errors
- Import errors
- Test failures
- Timing overlaps
- Similarity issues
- LLM problems

**Sections:**
```markdown
# AI Assistant Troubleshooting

## Test Failures
## Unicode/Encoding Issues
## Import Errors
## Pipeline Issues
## Timing Problems
## LLM Issues
```

### D. REFERENCE.md (Quick Lookups)

**Target:** <10KB
**Content:**
- Command quick reference
- File locations
- Key configuration values
- Threshold values
- Common grep patterns

**Sections:**
```markdown
# AI Assistant Quick Reference

## Test Commands
## Git Commands
## Key File Locations
## Configuration Values
## Similarity Thresholds
## Grep Patterns
```

---

## Tier 3: Topic-Specific Knowledge (docs/maintenance/lessons/)

**Created as needed when LESSONS_LEARNED.md > 30KB**

```
docs/maintenance/lessons/
├── CONFIGURATION.md (config patterns, nested structures)
├── LLM_SYSTEM.md (provider system, automation)
├── JAPANESE_HANDLING.md (particles, text processing)
├── TESTING.md (test patterns, coverage)
└── PIPELINE_ARCHITECTURE.md (stage order, data flow)
```

---

## Migration Plan

### Phase 1: Create New Structure (Immediate)
1. Create `docs/maintenance/ai/` folder
2. Split AI_GUIDE.md into 4 files:
   - GUIDELINES.md (DO/DON'T sections)
   - WORKFLOWS.md (Common Tasks section)
   - TROUBLESHOOTING.md (Troubleshooting section)
   - REFERENCE.md (Quick Reference section)
3. Rewrite AI_GUIDE.md as slim entry point (<100 lines)
4. Update all cross-references

### Phase 2: Update References (Immediate)
1. Update README.md to point to new AI_GUIDE
2. Update LESSONS_LEARNED.md cross-references
3. Update CHANGELOG.md mentions
4. Test that all links work

### Phase 3: Monitor and Adjust (Ongoing)
1. Track file sizes monthly
2. Split GUIDELINES.md if >30KB
3. Create topic-specific lessons when needed

---

## Benefits of New Structure

### For AI Assistants
✅ **Faster startup** - Read 100-line entry point instead of 500+ lines
✅ **Task-focused** - Load only relevant guide for current task
✅ **Less context usage** - Don't load everything upfront
✅ **Better navigation** - Clear hierarchy and organization

### For Maintainability
✅ **Scalable** - Each guide can grow independently
✅ **Organized** - Related content grouped together
✅ **Discoverable** - Clear naming and structure
✅ **Focused** - Each file has single purpose

### For Token Budget
✅ **Saves ~10K tokens** - Don't load all AI docs at once
✅ **On-demand loading** - Load task-specific guides only
✅ **Sustainable growth** - Can handle 10x more content

---

## Size Limits

| File | Target Size | When to Split |
|------|-------------|---------------|
| AI_GUIDE.md | <10KB (<100 lines) | Never - keep slim |
| GUIDELINES.md | <30KB | Split into subtopics |
| WORKFLOWS.md | <30KB | Split by workflow type |
| TROUBLESHOOTING.md | <20KB | Split by problem area |
| REFERENCE.md | <10KB | Split by reference type |

---

## Implementation Checklist

- [ ] Create `docs/maintenance/ai/` folder
- [ ] Extract GUIDELINES.md from AI_GUIDE.md
- [ ] Extract WORKFLOWS.md from AI_GUIDE.md
- [ ] Extract TROUBLESHOOTING.md from AI_GUIDE.md
- [ ] Extract REFERENCE.md from AI_GUIDE.md
- [ ] Rewrite AI_GUIDE.md as entry point (<100 lines)
- [ ] Update all cross-references
- [ ] Update README.md
- [ ] Update LESSONS_LEARNED.md
- [ ] Test all links work
- [ ] Update DOCUMENTATION_SCALING_STRATEGY.md with new structure
- [ ] Commit changes

---

## Success Criteria

✅ AI_GUIDE.md < 10KB (currently 19KB)
✅ Task-specific loading saves >10K tokens per session
✅ Each guide has single, clear purpose
✅ All links work and are discoverable
✅ Structure scales to 10x current content

---

*This refactoring follows the principles in DOCUMENTATION_SCALING_STRATEGY.md and ensures AI_GUIDE.md remains manageable as the project grows.*
