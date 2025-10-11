# Configuration Reference

This document provides a complete reference for all configuration options in `config.json`.

## Overview

The configuration file uses a **1:1 mapping** between config sections and pipeline stages.

### Configuration Files

The system supports multiple configuration sources with priority order:

1. **`config.json`** - Base configuration (committed to git)
2. **`config.local.json`** - Local overrides (gitignored, optional)
3. **`ANTHROPIC_API_KEY`** - Environment variable (highest priority)

**Deep merge:** `config.local.json` is deep-merged with `config.json`, meaning you only need to specify the values you want to override.

**Example:**
```bash
# config.json has:
{"llm": {"provider": "anthropic", "model": "claude-3"}}

# config.local.json only overrides API key:
{"llm": {"anthropic_api_key": "sk-ant-..."}}

# Result: Both are merged, provider and model preserved
{"llm": {"provider": "anthropic", "model": "claude-3", "anthropic_api_key": "sk-ant-..."}}
```

### Quick Setup

1. Copy example file: `cp config.local.json.example config.local.json`
2. Edit `config.local.json` with your settings
3. Only include settings you want to override

**✅ Safe:** `config.local.json` is gitignored and won't be committed

---

## Stage Configuration

| Config Section | Pipeline Stage | Purpose |
|----------------|----------------|---------|
| `audio_processing` | Stage 1 | Audio normalization |
| `whisper` | Stage 2 | Speech-to-text transcription |
| `segment_merging` | Stage 3 | Merge incomplete sentences |
| `segment_splitting` | Stage 4 | Split long segments |
| `hallucination_filter` | Stage 5 | Remove Whisper artifacts |
| `text_polishing` | Stage 6 | LLM text refinement |
| `timing_realignment` | Stage 7 | Final timing QA |
| `llm` | Global | LLM connection settings |

## Configuration Sections

### Stage 1: Audio Processing

Normalizes audio volume before transcription for consistent results.

```json
{
  "audio_processing": {
    "enable": true,
    "target_loudness_lufs": -6.0
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_normalize` | boolean | `true` | Enable audio volume normalization |
| `target_loudness_lufs` | float | `-6.0` | Target loudness in LUFS (recommended: -6 to -12) |

**Notes:**
- Normalization improves transcription quality for quiet or inconsistent audio
- LUFS (Loudness Units relative to Full Scale) is the standard for perceived loudness
- `-6.0` is good for speech; use `-12.0` for very quiet audio

---

### Stage 2: Whisper Transcription

Core speech-to-text transcription using OpenAI Whisper.

```json
{
  "whisper": {
    "model": "large-v3",
    "device": "cuda",
    "compression_ratio_threshold": 3.0,
    "logprob_threshold": -1.5,
    "no_speech_threshold": 0.2,
    "beam_size": 5,
    "best_of": 5,
    "patience": 2.0,
    "initial_prompt": "日本語の会話です。",
    "condition_on_previous_text": false
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `"large-v3"` | Whisper model size (tiny/base/small/medium/large/large-v3) |
| `device` | string | `"cuda"` | Device to use ("cuda" for GPU, "cpu" for CPU) |
| `compression_ratio_threshold` | float | `3.0` | Skip segments with compression ratio > threshold |
| `logprob_threshold` | float | `-1.5` | Skip segments with avg log probability < threshold |
| `no_speech_threshold` | float | `0.2` | Skip segments with no-speech probability > threshold |
| `beam_size` | integer | `5` | Beam search size (higher = more accurate, slower) |
| `best_of` | integer | `5` | Number of candidates in beam search |
| `patience` | float | `2.0` | Beam search patience factor |
| `initial_prompt` | string | `""` | Prompt to guide transcription style |
| `condition_on_previous_text` | boolean | `false` | Use previous text as context (can cause repetition) |

**Model Selection:**
- `tiny`: Fastest, lowest accuracy (~1GB VRAM)
- `base`: Fast, moderate accuracy (~1GB VRAM)
- `small`: Good balance (~2GB VRAM)
- `medium`: High accuracy (~5GB VRAM)
- `large-v3`: Best accuracy (~10GB VRAM) - **Recommended**

**Quality Tips:**
- Use `large-v3` for best quality
- Set `condition_on_previous_text: false` to avoid repetition hallucinations
- Adjust thresholds lower for more aggressive filtering, higher for more complete transcription

---

### Stage 3: Segment Merging

Merges segments that end with incomplete sentence markers.

```json
{
  "segment_merging": {
    "incomplete_markers": ["て", "で", "と", "が", "けど", "ども", "たり"],
    "sentence_enders": ["。", "？", "！", "?", "!", "ね", "よ", "わ", "な", "か"],
    "max_merge_gap": 0.5,
    "merge_length_buffer": 15
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `incomplete_markers` | array | See above | Particles indicating incomplete sentences |
| `sentence_enders` | array | See above | Characters indicating complete sentences |
| `max_merge_gap` | float | `0.5` | Max gap (seconds) between segments to merge |
| `merge_length_buffer` | integer | `15` | Extra characters allowed when merging |

**Notes:**
- Prevents subtitles from cutting off mid-sentence
- Only merges segments close in time (`max_merge_gap`)
- Respects `max_line_length` with buffer allowance

---

### Stage 4: Segment Splitting

Splits long segments into readable subtitle lines.

```json
{
  "segment_splitting": {
    "max_line_length": 30,
    "primary_breaks": ["。", "？", "！", "?", "!"],
    "secondary_breaks": ["、", "わ", "ね", "よ"],
    "enable": true,
    "enable_revalidate": true,
    "revalidation_confidence_threshold": 0.7
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_line_length` | integer | `30` | Maximum characters per subtitle line |
| `primary_breaks` | array | See above | Best places to split (sentence endings) |
| `secondary_breaks` | array | See above | OK places to split (commas, particles) |
| `enable` | boolean | `true` | Use AI for intelligent splitting |
| `enable_revalidate` | boolean | `true` | Re-validate LLM splits with Whisper |
| `revalidation_confidence_threshold` | float | `0.7` | Confidence threshold for revalidation |

**Splitting Behavior:**
1. **Basic splitting**: Splits at punctuation marks within `max_line_length`
2. **LLM splitting** (if `enable: true`): AI finds natural break points
3. **Revalidation** (if `enable_revalidate: true`): Whisper verifies splits match audio

**Notes:**
- `max_line_length: 30` is optimal for Japanese subtitles
- LLM splitting handles complex sentences better than rule-based
- Revalidation prevents splits in middle of words

---

### Stage 5: Hallucination Filtering

Removes Whisper transcription artifacts and repetitive hallucinations.

```json
{
  "hallucination_filter": {
    "phrase_filter": {
      "enable": true,
      "phrases": [
        "ご視聴ありがとうございました",
        "ご視聴いただきありがとうございます"
      ]
    },
    "stammer_filter": {
      "enable": true,
      "word_repetition": {
        "max_pattern_length": 15,
        "min_repetitions": 5,
        "condensed_display_count": 3
      },
      "vocalization_replacement": {
        "enable": false,
        "vocalization_options": ["あ", "ん", "うん", "はぁ", "ふぅ"],
        "short_duration_threshold": 2.0,
        "medium_duration_threshold": 5.0,
        "short_repeat_count": 1,
        "medium_repeat_count": 2,
        "long_repeat_count": 3
      }
    },
    "consecutive_duplicates": {
      "enable": true,
      "min_occurrences": 4
    },
    "timing_validation": {
      "enable": true,
      "max_chars_per_second": 20,
      "enable_revalidate_with_whisper": true
    },
    "global_word_filter": {
      "enable": false,
      "min_occurrences": 12
    },
    "cluster_filter": {
      "enable": false,
      "time_window_seconds": 60,
      "min_occurrences": 6
    }
  }
}
```

#### Phrase Filter

Removes exact phrase matches (e.g., common YouTube outros).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `true` | Enable phrase filtering |
| `phrases` | array | See above | Exact phrases to remove |

#### Stammer Filter

Condenses repetitive word patterns (e.g., "あああああ" → "あ...").

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `true` | Enable stammer filtering |
| `max_pattern_length` | integer | `15` | Max characters in repeated pattern |
| `min_repetitions` | integer | `5` | Min repetitions to condense |
| `condensed_display_count` | integer | `3` | How many times to show in output |

**Vocalization Replacement** (optional sub-feature):

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `false` | Replace repetitions with vocalizations |
| `vocalization_options` | array | See above | Replacement sounds |
| `short_duration_threshold` | float | `2.0` | Threshold for short segments (seconds) |
| `medium_duration_threshold` | float | `5.0` | Threshold for medium segments |
| `short_repeat_count` | integer | `1` | Repetitions for short segments |
| `medium_repeat_count` | integer | `2` | Repetitions for medium segments |
| `long_repeat_count` | integer | `3` | Repetitions for long segments |

#### Consecutive Duplicates

Removes identical consecutive segments (common Whisper hallucination pattern).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `true` | Enable consecutive duplicate removal |
| `min_occurrences` | integer | `4` | Min consecutive repeats to merge/remove |

**Note:** Vocalization replacement is handled in Stage 8 (final_cleanup), not here.

#### Timing Validation

Validates and optionally re-transcribes segments with suspicious timing.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `true` | Enable timing validation |
| `max_chars_per_second` | integer | `20` | Max reading speed (chars/second) |
| `enable_revalidate_with_whisper` | boolean | `true` | Re-transcribe suspicious segments |

**Notes:**
- Catches segments where text is too long/short for audio duration
- Revalidation prevents false positives

#### Global Word Filter

Removes words that appear too frequently (likely hallucinations).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `false` | Enable global word filtering |
| `min_occurrences` | integer | `12` | Min occurrences to consider hallucination |

**Warning:** Aggressive filtering. Disable by default.

#### Cluster Filter

Removes words that cluster in time windows (likely hallucinations).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `false` | Enable cluster filtering |
| `time_window_seconds` | float | `60.0` | Time window for clustering |
| `min_occurrences` | integer | `6` | Min occurrences in window |

**Warning:** Can remove legitimate repeated words. Disable by default.

---

### Stage 6: Text Polishing

LLM-based text refinement for natural Japanese.

```json
{
  "text_polishing": {
    "enable": true,
    "batch_size": 10
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `true` | Enable LLM text polishing |
| `batch_size` | integer | `10` | Segments per API call (reduces costs) |

**What it does:**
- Fixes grammar and particle usage
- Normalizes casual speech to standard Japanese
- Corrects Whisper transcription errors
- Preserves original meaning and timing

**Notes:**
- Requires LLM API key (see `llm` section)
- Uses batching to reduce API costs
- Gracefully falls back to original text on failure

---

### Stage 7: Timing Realignment

Final timing QA using Whisper to verify text matches audio.

```json
{
  "timing_realignment": {
    "enable": true,
    "search_padding": 3.0,
    "adjustment_threshold": 0.3,
    "min_gap": 0.1,
    "batch_size": 10
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable` | boolean | `true` | Enable timing realignment |
| `search_padding` | float | `3.0` | Seconds to search before/after segment |
| `adjustment_threshold` | float | `0.3` | Min time difference to adjust |
| `min_gap` | float | `0.1` | Minimum gap between segments |
| `batch_size` | integer | `10` | Segments to process in parallel |

**What it does:**
- Re-transcribes each segment's audio region
- Finds exact timing of text in audio
- Adjusts segment boundaries for perfect sync

**Notes:**
- Most expensive stage (re-transcribes all segments)
- Significantly improves subtitle sync quality
- Set `enable: false` for faster processing

---

### Global: LLM Settings

Connection settings for LLM providers (used in Stages 4 and 6).

```json
{
  "llm": {
    "provider": "ollama",
    "model": "llama3.2:3b",
    "max_tokens": 1024,
    "temperature": 0.0,
    "ollama_base_url": "http://localhost:11434",
    "anthropic_api_key": "<your-api-key>",
    "openai_api_key": "<your-api-key>"
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider` | string | `"ollama"` | LLM provider: `"ollama"`, `"anthropic"`, or `"openai"` |
| `model` | string | `"llama3.2:3b"` | Model name (provider-specific) |
| `max_tokens` | integer | `1024` | Max tokens per API response |
| `temperature` | float | `0.0` | Sampling temperature (0 = deterministic) |
| `ollama_base_url` | string | `"http://localhost:11434"` | Ollama server URL (only for Ollama) |
| `timeout` | integer | `30` | Request timeout in seconds (only for Ollama) |
| `anthropic_api_key` | string | `""` | Claude API key (only for Anthropic) |
| `api_key_env` | string | `"ANTHROPIC_API_KEY"` | Environment variable for API key |
| `openai_api_key` | string | `""` | OpenAI API key (only for OpenAI) |

#### Provider: Ollama (Local, FREE)

**Recommended for: Segment splitting** (simple task, cost-effective)

```json
{
  "llm": {
    "provider": "ollama",
    "model": "llama3.2:3b",
    "ollama_base_url": "http://localhost:11434",
    "max_tokens": 512
  }
}
```

**Setup:**
1. Install Ollama: https://ollama.com/download
2. Pull a model: `ollama pull llama3.2:3b`
3. Start Ollama (runs automatically on Windows/Mac)

**Recommended models for Japanese:**
- `llama3.2:3b` - Fast, good for simple tasks (2GB RAM)
- `gemma2:2b` - Very fast, lightweight (1.6GB RAM)
- `qwen2.5:3b` - Good Japanese support (2.3GB RAM)

**Pros:** FREE, private, no API costs, fast for local use
**Cons:** Requires local GPU/CPU, lower quality than Claude

#### Provider: Anthropic (Cloud, Paid)

**Recommended for: Text polishing** (quality matters)

```json
{
  "llm": {
    "provider": "anthropic",
    "anthropic_api_key": "sk-ant-api03-...",
    "model": "claude-3-5-haiku-20241022",
    "max_tokens": 1024
  }
}
```

**Setup:**
1. Sign up at https://console.anthropic.com/
2. Create API key
3. Add to config.json or set `ANTHROPIC_API_KEY` environment variable

**Model options:**
- `claude-3-5-haiku-20241022` - Fast, cheap (~$0.25-1.00/hour)
- `claude-3-5-sonnet-20241022` - High quality (~$3-15/hour)
- `claude-sonnet-4-5-20250929` - Highest quality, expensive (~$15-75/hour)

**Pros:** Highest quality, best Japanese support, reliable
**Cons:** Paid API, requires internet, per-token costs

#### Provider: OpenAI (Cloud, Paid)

**Alternative to Anthropic**

```json
{
  "llm": {
    "provider": "openai",
    "openai_api_key": "sk-proj-...",
    "model": "gpt-4o-mini",
    "max_tokens": 1024
  }
}
```

**Setup:**
1. Sign up at https://platform.openai.com/
2. Create API key
3. Add to config.json or set `OPENAI_API_KEY` environment variable

**Model options:**
- `gpt-4o-mini` - Fast, cheap (~$0.15-0.60/hour)
- `gpt-4o` - High quality (~$5-20/hour)

**Pros:** Good quality, widely available
**Cons:** Paid API, slightly worse than Claude for Japanese

#### Stage-Specific LLM Override

You can use different providers for different stages to optimize costs:

```json
{
  "llm": {
    "provider": "ollama",
    "model": "llama3.2:3b"
  },
  "segment_splitting": {
    "enable_llm": true
    // Uses global "ollama" provider (FREE)
  },
  "text_polishing": {
    "enable": true,
    "llm_provider": "anthropic"  // Override to use Anthropic for this stage
  }
}
```

This uses **FREE Ollama** for splitting, **paid Claude** for polishing.

**Cost comparison for 1 hour transcription:**
- Ollama (local): **$0** - FREE!
- Anthropic Haiku: ~$0.25-1.00
- Anthropic Sonnet: ~$3.00-15.00
- OpenAI GPT-4o-mini: ~$0.15-0.60

#### Configuration Examples

See [LLM_PROVIDERS.md](../LLM_PROVIDERS.md) for comprehensive LLM provider guide and [config.local.json.example](../../config.local.json.example) for configuration examples.

**Recommended setup (cost-effective):**
- Global: Ollama for segment splitting (FREE)
- Stage 7: Claude Haiku for text polishing (cheap, high quality)

---

## Example Configurations

### Minimal (Fast, No LLM)

For quick transcription without AI enhancement:

```json
{
  "audio_processing": {
    "enable": true,
    "target_loudness_lufs": -6.0
  },
  "whisper": {
    "model": "medium",
    "device": "cuda"
  },
  "segment_merging": {},
  "segment_splitting": {
    "max_line_length": 30,
    "enable": false
  },
  "hallucination_filter": {
    "phrase_filter": {"enable": false},
    "stammer_filter": {"enable": false},
    "consecutive_duplicates": {"enable": false},
    "timing_validation": {"enable": false}
  },
  "text_polishing": {
    "enable": false
  },
  "timing_realignment": {
    "enable": false
  },
  "llm": {}
}
```

**Processing time:** ~5-10 minutes for 1 hour audio (GPU)

---

### Maximum Quality (Slow, All Features)

For best quality transcription with all enhancements:

```json
{
  "audio_processing": {
    "enable": true,
    "target_loudness_lufs": -6.0
  },
  "whisper": {
    "model": "large-v3",
    "device": "cuda",
    "beam_size": 5,
    "best_of": 5
  },
  "segment_merging": {
    "max_merge_gap": 0.5
  },
  "segment_splitting": {
    "max_line_length": 30,
    "enable": true,
    "enable_revalidate": true
  },
  "hallucination_filter": {
    "phrase_filter": {"enable": true},
    "stammer_filter": {"enable": true},
    "consecutive_duplicates": {"enable": true},
    "timing_validation": {
      "enable": true,
      "enable_revalidate_with_whisper": true
    }
  },
  "text_polishing": {
    "enable": true,
    "batch_size": 10
  },
  "timing_realignment": {
    "enable": true
  },
  "llm": {
    "provider": "anthropic",
    "anthropic_api_key": "your-key-here",
    "model": "claude-sonnet-4-5-20250929"
  }
}
```

**Processing time:** ~20-40 minutes for 1 hour audio (GPU + API calls)

---

## Configuration Tips

### Performance Optimization

**GPU Acceleration:**
- Set `whisper.device: "cuda"` for 10-100x speedup
- Requires NVIDIA GPU with CUDA support

**Disable Optional Stages:**
- Set `timing_realignment.enable: false` (saves 30-50% time)
- Set `segment_splitting.enable: false` (saves API costs)
- Set `text_polishing.enable: false` (saves API costs)

### Quality Optimization

**Best Transcription:**
- Use `whisper.model: "large-v3"`
- Set `whisper.beam_size: 5` and `whisper.best_of: 5`
- Enable `timing_realignment` for perfect sync

**Best Text:**
- Enable `text_polishing.enable: true`
- Enable `segment_splitting.enable: true`
- Enable all hallucination filters

### Cost Optimization

**Reduce LLM API Costs:**
- Increase `batch_size` in text_polishing and splitting
- Use smaller model: `claude-3-haiku-20240307`
- Disable `text_polishing.enable` if quality is acceptable

### Audio-Specific Settings

**Very Quiet Audio:**
- Set `audio_processing.target_loudness_lufs: -12.0`

**Noisy Audio:**
- Lower `whisper.compression_ratio_threshold` to 2.5
- Lower `whisper.logprob_threshold` to -2.0

**Fast Speech:**
- Increase `segment_splitting.max_line_length` to 40
- Increase `hallucination_filter.timing_validation.max_chars_per_second` to 25

**ASMR/Breathing Sounds:**
- Enable `hallucination_filter.stammer_filter.vocalization_replacement`
- Adjust duration thresholds to match audio pacing

---

## Troubleshooting

### Subtitles out of sync
- Enable `timing_realignment.enable: true`
- Increase `timing_realignment.search_padding` to 5.0

### Too many missing words
- Increase `whisper.no_speech_threshold` to 0.3
- Decrease `whisper.logprob_threshold` to -2.0
- Disable aggressive filters (global_word_filter, cluster_filter)

### Too many repetitions/hallucinations
- Enable `hallucination_filter.stammer_filter`
- Enable `hallucination_filter.consecutive_duplicates`
- Lower `whisper.compression_ratio_threshold` to 2.5

### Text quality is poor
- Enable `text_polishing.enable: true`
- Enable `segment_splitting.enable: true`
- Use better Whisper model: `large-v3`

### Processing is too slow
- Use smaller model: `medium` or `small`
- Disable `timing_realignment`
- Disable LLM features
- Reduce `whisper.beam_size` to 3

### API costs too high
- Increase `batch_size` to 20
- Use cheaper model: `claude-3-haiku-20240307`
- Disable `text_polishing` if acceptable
