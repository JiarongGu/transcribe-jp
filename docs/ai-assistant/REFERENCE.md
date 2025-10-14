# AI Assistant Quick Reference for transcribe-jp

**Quick Reference:** Essential commands, settings, and file locations at a glance

**Last Updated:** 2025-10-12
**Related:** [AI_GUIDE.md](../AI_GUIDE.md), [GUIDELINES.md](GUIDELINES.md)

---

## Essential Commands

### Run Tests

```bash
# Unit tests (fast, 261 tests)
python -X utf8 -m pytest tests/unit/ -q --tb=line

# E2E tests (slow, 4 suites)
python -X utf8 -m pytest tests/e2e/ -v

# All tests
python -X utf8 -m pytest tests/ -v

# Specific test file
python -X utf8 -m pytest tests/unit/modules/stage6_timing_realignment/test_processor.py -v
```

### Git Commands

```bash
# Check status
git status

# View changes
git diff --stat

# Recent commits
git log --oneline -10

# Stage all changes
git add -A

# Commit (see WORKFLOWS.md for template)
git commit -m "message"
```

### Pipeline Execution

```bash
# Run full pipeline
python main.py input.mp4

# With custom config
python main.py input.mp4 --config config.local.json

# Specific stages only
python main.py input.mp4 --stages 1-6
```

---

## Key Configuration Settings

**Location:** `config.json`
**Override:** `config.local.json` (deep merge, not tracked in git)
**Full reference:** [core/CONFIGURATION.md](../core/CONFIGURATION.md)

### Similarity Thresholds (0.75)

```json
{
  "timing_realignment": {
    "text_search": {
      "similarity": 0.75
    },
    "time_based": {
      "similarity": 0.75
    }
  }
}
```

**Guidelines:**
- Tested with Japanese particles (これは vs これわ = 0.667)
- DO NOT lower below 0.7
- DO NOT raise above 0.8 (breaks particle handling)

### Timing Validation (Stage 5)

```json
{
  "hallucination_filter": {
    "timing_validation": {
      "enable": true,
      "enable_revalidate_with_whisper": true,
      "max_chars_per_second": 20
    }
  }
}
```

**How it works:**
- Re-transcribes segments > 20 chars/sec (physically impossible)
- After re-transcription, re-runs phrase_filter + consecutive_duplicates

### Whisper Settings

```json
{
  "whisper": {
    "model": "large-v3",
    "condition_on_previous_text": false,
    "initial_prompt": "日本語の会話です。句読点を適切に使用してください。",
    "language": "ja"
  }
}
```

**Why these settings:**
- `large-v3` - Best accuracy for Japanese
- `condition_on_previous_text: false` - Prevents error propagation
- `initial_prompt` - Reduces hallucinations, improves punctuation

### LLM Settings

```json
{
  "llm": {
    "provider": "ollama",
    "max_tokens": 1024,
    "temperature": 0.0,
    "timeout": 60,
    "ollama": {
      "model": "llama3.2:3b",
      "executable_path": "D:\\CustomPath\\ollama.exe",  // Optional: Custom Ollama path
      "base_url": "http://localhost:11434"  // Optional: External Ollama server
    }
  },
  "text_polishing": {
    "enable": true,
    "batch_size": 1,
    "llm_timeout": 180
  }
}
```

**Key settings:**
- `max_tokens: 0` - Unlimited tokens (no limit, useful for large batches)
- `timeout` - Request timeout (stage > provider > common > default 30s)
- `llm_timeout` - Stage-specific timeout override (e.g., 180s for text polishing with large models)
- `batch_size: 1` - Recommended for Ollama (more reliable than batching)
- `executable_path` - Custom path to ollama executable (for non-standard installations)
- `base_url` - External Ollama server URL (skips auto-management)

**Timeout guidelines:**
- 2-3B models: 30-60s
- 7-8B models: 60-120s
- 32B+ models: 120-300s

**Ollama path detection** (automatic):
- Windows: PATH, %LOCALAPPDATA%\Programs\Ollama, C:\Program Files\Ollama, C:\Program Files (x86)\Ollama, %APPDATA%\Ollama
- macOS: PATH, /usr/local/bin, /opt/homebrew/bin, ~/.local/bin, /Applications/Ollama.app/Contents/MacOS
- Linux: PATH, ~/.local/bin, /usr/local/bin, /usr/bin, /opt/ollama/bin
- See [OLLAMA_CONFIGURATION.md](../features/OLLAMA_CONFIGURATION.md) for advanced configuration

---

## Key File Locations

### Core Pipeline

- **Entry point:** `main.py`
- **Pipeline:** `core/pipeline.py::run_pipeline()`
- **Config:** `config.json`

### Stage Processors

```
modules/
├── stage1_preprocessing/
├── stage2_transcription/
├── stage3_segment_merging/
├── stage4_segment_splitting/
├── stage5_hallucination_filter/
├── stage6_timing_realignment/
├── stage7_text_polishing/
├── stage8_final_cleanup/
└── stage9_vtt_export/
```

### Shared Utilities

- **Text utils:** `shared/text_utils.py` (Japanese normalization, utilities)
- **Whisper utils:** `shared/whisper_utils.py` (Audio loading, transcription)
- **LLM utils:** `shared/llm_utils.py` (Provider-agnostic LLM interface)
- **Segment utils:** `shared/segment.py` (Segment data structure)

### Tests

- **Unit:** `tests/unit/` (280 tests)
- **Integration:** `tests/integration/` (20+ tests, requires OLLAMA_AVAILABLE=true)
- **E2E:** `tests/e2e/` (4 suites)
- **Test audio:** `tests/e2e/test_media/japanese_test.mp3` (27s, 167KB)
- **Diagnostic:** `test_ollama_quick.py` (Ollama timeout troubleshooting)

### Documentation

```
docs/
├── README.md                          # Documentation index
├── AI_GUIDE.md                        # Main AI assistant guide
├── CHANGELOG.md                       # User-facing changes
├── SESSIONS.md                        # Development history
├── core/
│   ├── ARCHITECTURE.md                # System design
│   ├── CONFIGURATION.md               # Config reference
│   └── PIPELINE_STAGES.md             # Stage details
├── features/
│   ├── LLM_PROVIDERS.md               # LLM configuration guide
│   └── OLLAMA_CONFIGURATION.md        # Advanced Ollama configuration
└── maintenance/
    ├── LESSONS_LEARNED.md             # Knowledge database
    ├── DOCUMENTATION_SCALING_STRATEGY.md
    └── ai/
        ├── GUIDELINES.md              # This refactor!
        ├── WORKFLOWS.md
        ├── TROUBLESHOOTING.md
        └── REFERENCE.md
```

---

## Key Functions and Classes

### Text Similarity

**Location:** `modules/stage6_timing_realignment/utils.py`

```python
def calculate_text_similarity(text1: str, text2: str) -> float:
    """Uses difflib.SequenceMatcher (Ratcliff/Obershelp algorithm)"""
```

**Behavior:**
- Strips punctuation: `[、。！？\s]`
- Returns 0.0-1.0 ratio
- DO NOT use LLM for this (see GUIDELINES.md)

### Japanese Text Normalization

**Location:** `shared/text_utils.py`

```python
def normalize_japanese_text(text: str) -> str:
    """Full-width → half-width, katakana variants, etc."""

def is_sentence_complete(text: str) -> bool:
    """Check if Japanese sentence is complete (enders vs incomplete)"""
```

### Segment Data Structure

**Location:** `shared/segment.py`

```python
class Segment:
    def __init__(self, start: float, end: float, text: str):
        self.start = start
        self.end = end
        self.text = text
        self.metadata = {}
```

---

## Pipeline Stage Order

**Critical:** Stage order matters! (See GUIDELINES.md)

1. **Preprocessing** - Prepare audio
2. **Transcription** - Whisper transcription
3. **Segment Merging** - Join incomplete sentences
4. **Segment Splitting** - Optional LLM semantic splitting
5. **Hallucination Filter** - Remove hallucinations, timing validation
6. **Timing Realignment** - Re-transcribe and realign timing
7. **Text Polishing** - Optional LLM text improvement
8. **Final Cleanup** - Remove stammers, duplicates
9. **VTT Export** - Generate final VTT file

**Key ordering rules:**
- Filtering BEFORE realignment (5 → 6)
- Polishing AFTER realignment (6 → 7)
- Re-filtering AFTER timing_validation (Stage 5)

---

## Japanese Language Quick Reference

### Particle Variations

| Written | Spoken | Similarity |
|---------|--------|------------|
| これは  | これわ  | 0.667      |
| これを  | これお  | 0.714      |
| そこへ  | そこえ  | 0.750      |

→ **0.75 threshold handles these**

### Sentence Markers

**Complete (enders):**
```
。？！ね よ わ な か
```

**Incomplete (needs merging):**
```
て で と が けど ども たり
```

### Text Normalization

- Full-width → half-width (１２３ → 123)
- Katakana variants (ヴ → ブ)
- No spaces between words
- Punctuation: 、 (comma) 。 (period)

---

## Test Coverage Stats

**Current:** 300+ tests (280 unit + 20+ integration + 4 E2E + 1 smoke)

**By module:**
- Stage 1: Preprocessing
- Stage 2: Transcription
- Stage 3: Segment merging
- Stage 4: LLM splitting
- Stage 5: Hallucination filter
- Stage 6: Timing realignment
- Stage 7: Text polishing
- Stage 8: Final cleanup
- Stage 9: VTT export

**E2E test audio:**
- Japanese counting 1-10
- 27 seconds, 167KB
- Tests full pipeline

---

## Documentation Map

```
START HERE
├── README.md                    # Project overview, installation, usage
├── maintenance/LESSONS_LEARNED  # Knowledge database (read FIRST!)
└── AI_GUIDE.md                  # Main AI guide (you are here)
    ├── ai-assistant/GUIDELINES.md      # Critical DO's and DON'Ts
    ├── ai-assistant/WORKFLOWS.md       # Common tasks, git workflow
    ├── ai-assistant/TROUBLESHOOTING.md # Problem solving
    └── ai-assistant/REFERENCE.md       # Quick reference (this file)

DETAILED DOCS
├── core/ARCHITECTURE.md              # System design, 9-stage pipeline
├── core/CONFIGURATION.md             # Full config reference
├── core/PIPELINE_STAGES.md           # Stage-by-stage details
├── features/LLM_PROVIDERS.md         # LLM provider configuration
├── features/OLLAMA_CONFIGURATION.md  # Advanced Ollama configuration
├── CHANGELOG.md                      # Recent changes, git history
└── SESSIONS.md                       # Development history, context
```

---

## Quick Decision Trees

### Should I add a filter?

```
Is it hallucination-related?
├─ YES → Stage 5 (hallucination_filter)
└─ NO → Is it cleanup-related?
    ├─ YES → Stage 8 (final_cleanup)
    └─ NO → Document why new stage is needed
```

### Should I use LLM?

```
Is this a semantic task?
├─ YES → LLM is appropriate (Stage 4 splitting, Stage 7 polishing)
└─ NO → Use deterministic approach
    ├─ Text similarity → difflib.SequenceMatcher
    ├─ Timing validation → Whisper re-transcription
    └─ Pattern matching → regex
```

### Should I create a new doc?

```
Is content > 100 lines?
├─ YES → Is it self-contained?
│   ├─ YES → Create new doc
│   └─ NO → Add to existing doc
└─ NO → Add to existing doc
```

---

## Emergency Quick Fixes

### Tests suddenly failing

```bash
# 1. Check git status
git status

# 2. See what changed
git diff

# 3. Run specific failing test
python -X utf8 -m pytest path/to/test.py -v

# 4. Revert if needed
git checkout -- path/to/file.py
```

### Unicode errors

```bash
# Always use -X utf8 flag on Windows
python -X utf8 -m pytest tests/unit/ -q --tb=line
```

### Import errors

```bash
# Verify you're in project root
pwd  # Should be: y:\Tools\transcribe-jp

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

---

## See Also

- [AI_GUIDE.md](../AI_GUIDE.md) - Main AI assistant guide
- [GUIDELINES.md](GUIDELINES.md) - Critical DO's and DON'Ts
- [WORKFLOWS.md](WORKFLOWS.md) - Common workflows and procedures
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving guide
- [core/CONFIGURATION.md](../core/CONFIGURATION.md) - Full config reference
- [features/LLM_PROVIDERS.md](../features/LLM_PROVIDERS.md) - LLM configuration
