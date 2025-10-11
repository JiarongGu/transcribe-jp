# Documentation Scaling Strategy

**Created:** 2025-10-12
**Purpose:** Prevent documentation from exceeding token limits in future AI sessions

---

## Current State (2025-10-12)

**Total documentation size:** ~163 KB (~42K tokens)
**Context window:** 200K tokens
**Current usage:** 21% of context

**Growth rate:** ~5-10K tokens per session (CHANGELOG + LESSONS_LEARNED)

**Projection:** At current rate, docs will hit 100K tokens (50% of context) in **~10-20 sessions**.

---

## The Problem

1. **CHANGELOG.md** grows linearly forever (18.4 KB, will be 100KB+ in 1 year)
2. **LESSONS_LEARNED.md** grows with each architectural decision (17.9 KB)
3. **AI_GUIDE.md** grows as we add patterns (18.3 KB)
4. Reading all docs upfront consumes too much context

---

## Solution: Scalable Documentation Architecture

### 1. **Monthly CHANGELOG Archival** ✅ IMPLEMENTED

**Problem:** CHANGELOG grows 2-3K tokens per session indefinitely.

**Solution:** Archive entries older than current month.

**Structure:**
```
docs/
├── CHANGELOG.md (current month only, <50KB target)
└── maintenance/
    ├── CHANGELOG_ARCHIVE_2025-10.md
    ├── CHANGELOG_ARCHIVE_2025-11.md
    └── CHANGELOG_ARCHIVE_2025-12.md
```

**When to archive:**
- At the start of each new month
- When CHANGELOG.md exceeds 50KB (~12K tokens)
- Keep Version History Summary table complete (all entries)

**Implementation:**
1. Create `CHANGELOG_ARCHIVE_YYYY-MM.md` in `docs/maintenance/`
2. Move all entries from that month to archive
3. Add link in main CHANGELOG: "For entries before YYYY-MM-DD, see CHANGELOG_ARCHIVE_YYYY-MM.md"
4. Keep Version History Summary table (it's small, ~2KB)

### 2. **Topic-Based LESSONS_LEARNED Splits** (Future)

**When to implement:** When LESSONS_LEARNED.md > 30KB (~7.5K tokens)

**Problem:** Single file grows with every architectural decision.

**Solution:** Split by topic category.

**Structure:**
```
docs/maintenance/
├── LESSONS_LEARNED.md (index + critical lessons only)
└── lessons/
    ├── CONFIGURATION.md
    ├── LLM_SYSTEM.md
    ├── JAPANESE_HANDLING.md
    ├── TESTING.md
    └── PIPELINE_ARCHITECTURE.md
```

**LESSONS_LEARNED.md becomes:**
```markdown
# Lessons Learned - Quick Reference

**Critical lessons (read first):**
1. [Configuration Design](lessons/CONFIGURATION.md#nested-configs)
2. [LLM Provider System](lessons/LLM_SYSTEM.md#automate-dependencies)
3. [Japanese Text Handling](lessons/JAPANESE_HANDLING.md#particle-variations)

**Full topic guides:**
- [Configuration Design](lessons/CONFIGURATION.md)
- [LLM Provider System](lessons/LLM_SYSTEM.md)
- [Japanese Language Handling](lessons/JAPANESE_HANDLING.md)
- [Testing Practices](lessons/TESTING.md)
- [Pipeline Architecture](lessons/PIPELINE_ARCHITECTURE.md)
```

### 3. **Smart Documentation Loading Strategy** (Recommended Pattern)

**Problem:** AI doesn't need ALL docs at once.

**Solution:** Load docs on-demand based on task.

**Pattern for AI assistants:**

```markdown
## Step 1: Initial Context (Always Load)
- README.md (~2K tokens)
- AI_GUIDE.md (~5K tokens)
- CHANGELOG.md - Recent entries only (last month, ~5K tokens)

Total: ~12K tokens

## Step 2: Task-Specific Loading (Load as Needed)

**For config changes:**
- docs/core/CONFIGURATION.md
- docs/maintenance/lessons/CONFIGURATION.md

**For LLM work:**
- docs/features/LLM_PROVIDERS.md
- docs/maintenance/lessons/LLM_SYSTEM.md

**For pipeline stage work:**
- docs/core/PIPELINE_STAGES.md
- docs/features/STAGE{N}_*.md

**For Japanese text issues:**
- docs/maintenance/lessons/JAPANESE_HANDLING.md

**For testing:**
- docs/maintenance/lessons/TESTING.md
```

### 4. **Documentation Size Limits** (Enforcement Rules)

**File size targets:**

| File | Target Size | Token Limit | Action When Exceeded |
|------|-------------|-------------|---------------------|
| CHANGELOG.md | <50KB | <12K tokens | Archive previous month |
| LESSONS_LEARNED.md | <30KB | <7.5K tokens | Split by topic |
| AI_GUIDE.md | <25KB | <6K tokens | Move detailed info to topic docs |
| CONFIGURATION.md | <30KB | <7.5K tokens | Split by feature area |
| Any single doc | <50KB | <12K tokens | Consider splitting |

**Total documentation target:** <200KB (<50K tokens = 25% of 200K context)

### 5. **Index-Based Navigation** (Future Enhancement)

**When to implement:** When total docs > 200KB

**Create master index:**
```markdown
# Documentation Master Index

**Quick Start (12K tokens):**
- README.md
- AI_GUIDE.md
- CHANGELOG.md (recent)

**By Topic:**
- [Configuration](INDEX.md#configuration) (5 docs, 15K tokens)
- [LLM System](INDEX.md#llm-system) (3 docs, 12K tokens)
- [Pipeline Stages](INDEX.md#pipeline) (12 docs, 30K tokens)
- [Testing](INDEX.md#testing) (4 docs, 8K tokens)

**By Task:**
- Adding new pipeline stage → [Guide](INDEX.md#add-stage)
- Changing config structure → [Guide](INDEX.md#config-change)
- Improving Japanese handling → [Guide](INDEX.md#japanese)
```

---

## Implementation Checklist

### Phase 1: Immediate (When CHANGELOG > 50KB)
- [x] Create CHANGELOG_ARCHIVE_2025-10.md
- [ ] Move old entries to archive
- [ ] Update CHANGELOG.md with archive link
- [ ] Update AI_GUIDE.md with archival instructions

### Phase 2: Short-term (When LESSONS_LEARNED > 30KB)
- [ ] Create docs/maintenance/lessons/ folder
- [ ] Split LESSONS_LEARNED.md by topic
- [ ] Create topic-specific lesson files
- [ ] Update LESSONS_LEARNED.md as index
- [ ] Update AI_GUIDE.md with new structure

### Phase 3: Medium-term (When total docs > 150KB)
- [ ] Implement smart loading strategy in AI_GUIDE
- [ ] Create documentation loading decision tree
- [ ] Add token budget tracking to AI_GUIDE
- [ ] Create INDEX.md master navigation

### Phase 4: Long-term (When total docs > 250KB)
- [ ] Consider separate documentation repository
- [ ] Implement documentation search tool
- [ ] Create doc summarization system
- [ ] AI-powered doc retrieval based on task

---

## AI Assistant Instructions

**When starting a new session:**

1. **Check total doc size:**
   ```bash
   find docs -name "*.md" -exec cat {} \; | wc -c
   ```
   If > 200KB (50K tokens), implement next scaling phase.

2. **Load strategically:**
   - Always: README, AI_GUIDE, recent CHANGELOG
   - Task-specific: Only load docs relevant to current task
   - Don't load archives unless specifically needed

3. **Before adding to docs:**
   - Check if existing doc can be trimmed
   - Consider if info belongs in archive
   - Check if doc exceeds size limits

4. **Monthly archival (start of month):**
   - Create new CHANGELOG_ARCHIVE_{YEAR}-{MONTH}.md
   - Move previous month's entries
   - Update links in main CHANGELOG

---

## Monitoring Script

```bash
# Add this to check documentation health
python -c "
import os
from pathlib import Path

total = 0
large_files = []

for md_file in Path('docs').rglob('*.md'):
    size = md_file.stat().st_size
    total += size
    if size > 50000:  # 50KB
        large_files.append((str(md_file), size))

print(f'Total: {total/1024:.1f} KB (~{total//4:,} tokens)')
print(f'Status: {'🔴 ACTION NEEDED' if total > 200000 else '🟢 OK'}')
print(f'\nLarge files (>50KB):')
for f, s in large_files:
    print(f'  {f}: {s/1024:.1f} KB (~{s//4:,} tokens)')
"
```

**Run this monthly to track documentation growth.**

---

## Success Metrics

✅ **Short-term:** CHANGELOG stays <50KB
✅ **Medium-term:** Total docs stay <200KB (50K tokens, 25% of context)
✅ **Long-term:** AI can find relevant docs in <5K tokens per session

---

*This strategy ensures documentation scales gracefully as the project grows, preventing context window exhaustion in future AI sessions.*
