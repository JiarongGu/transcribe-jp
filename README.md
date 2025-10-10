# Japanese Audio/Video Transcription Tool

A professional-grade transcription tool for Japanese media using OpenAI Whisper with advanced hallucination filtering and optional LLM-powered text polishing.

## ✨ Features

- **Multi-format Support**: WAV, MP3, M4A, AAC, FLAC, OGG, MP4, AVI, MKV, MOV, and more
- **9-Stage Processing Pipeline**: Clean, modular architecture with dedicated stages
- **Word-level Timestamps**: Precise timing for perfect subtitle synchronization
- **LLM-Powered Intelligence** (Optional):
  - Intelligent line splitting at natural boundaries (Claude)
  - Subtitle text polishing for better readability (Claude)
- **Advanced Hallucination Filtering**:
  - Repetitive pattern detection and condensation
  - Phrase blacklisting
  - Timing validation with re-transcription
  - Consecutive duplicate detection
- **Smart Sentence Merging**: Automatically combines incomplete sentences
- **Audio Normalization**: Adaptive volume normalization for optimal transcription
- **Dual-Method Timing Realignment**: Choose between text-search or time-based verification for perfect subtitle sync
- **Final Cleanup Stage**: Post-realignment stammer filtering and word clustering removal
- **Modular Architecture**: Each pipeline stage in its own module (9 stage modules + shared utilities)
- **Flexible Configuration**: JSON-based configuration with 1:1 stage-to-config mapping

## 📋 Requirements

- Python 3.8+
- ffmpeg (must be in PATH)
- CUDA GPU (optional, for 10-100x faster processing)
- Anthropic API key (optional, for LLM features)

## 🚀 Installation

### Basic Installation

```bash
# Clone or download this repository
cd transcribe-jp

# Install package
pip install -e .
```

### GPU Acceleration (Highly Recommended)

For **~10-100x faster** transcription with NVIDIA GPU:

1. **Check CUDA availability:**
   ```bash
   python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
   ```

2. **If False, install PyTorch with CUDA:**
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
   ```

3. **Verify:**
   ```bash
   python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
   ```

4. **Update config.json:**
   ```json
   {
     "whisper": {
       "device": "cuda"
     }
   }
   ```

### Installing ffmpeg

#### Windows:
```bash
# Using Chocolatey
choco install ffmpeg

# Using Winget
winget install ffmpeg

# Or download from: https://github.com/BtbN/FFmpeg-Builds/releases
```

#### Linux:
```bash
sudo apt install ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

## 📖 Usage

### Basic Usage

```bash
# Navigate to directory with media files
cd /path/to/your/media

# Run transcription
python transcribe_jp.py

# Or if installed
transcribe-jp
```

Transcripts will be saved to `transcripts/` as VTT files.

### Advanced Usage

```bash
# Transcribe with specific config
python transcribe_jp.py --config custom_config.json

# Process specific files
python transcribe_jp.py file1.mp4 file2.wav

# Specify output directory
python transcribe_jp.py --output-dir ./subtitles
```

## ⚙️ Configuration

Configuration is managed through `config.json` with **1:1 mapping** between config sections and pipeline stages.

**📖 See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for complete reference**

### Quick Start Config

```json
{
  "audio_processing": {
    "enable": true,
    "target_loudness_lufs": -6.0
  },
  "whisper": {
    "model": "large-v3",
    "device": "cuda"
  },
  "segment_splitting": {
    "max_line_length": 30,
    "enable": true
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

### 9-Stage Pipeline

```
┌────────────────────────────────────────────────────┐
│ Stage 1: Audio Preprocessing   [audio_processing] │
├────────────────────────────────────────────────────┤
│ Stage 2: Whisper Transcription [whisper]          │
├────────────────────────────────────────────────────┤
│ Stage 3: Segment Merging        [segment_merging] │
├────────────────────────────────────────────────────┤
│ Stage 4: Segment Splitting      [segment_         │
│                                   splitting]       │
├────────────────────────────────────────────────────┤
│ Stage 5: Hallucination Filter   [hallucination_   │
│                                   filter]          │
├────────────────────────────────────────────────────┤
│ Stage 6: Timing Realignment     [timing_          │
│          • Text-search method    realignment]     │
│          • Time-based method                       │
├────────────────────────────────────────────────────┤
│ Stage 7: Text Polishing         [text_polishing]  │
├────────────────────────────────────────────────────┤
│ Stage 8: Final Cleanup          [final_cleanup]   │
├────────────────────────────────────────────────────┤
│ Stage 9: VTT Generation         (always enabled)  │
└────────────────────────────────────────────────────┘
```

### Configuration Sections

#### Stage 1: Audio Processing

```json
{
  "audio_processing": {
    "enable": true,
    "target_loudness_lufs": -6.0
  }
}
```

#### Stage 2: Whisper Transcription

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

#### Stage 3: Segment Merging

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

#### Stage 4: Segment Splitting

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

#### Stage 5: Hallucination Filter

```json
{
  "hallucination_filter": {
    "phrase_filter": {
      "enable": true,
      "phrases": ["ご視聴ありがとうございました"]
    },
    "consecutive_duplicates": {
      "enable": true,
      "min_occurrences": 4
    },
    "timing_validation": {
      "enable": true,
      "max_chars_per_second": 20,
      "enable_revalidate_with_whisper": true
    }
  }
}
```

#### Stage 6: Timing Realignment

Two methods available:
- **text_search**: Search for segment text in a window (sequential processing with overlap detection)
- **time_based**: Verify at expected time, expand window if needed (batch-processable)

```json
{
  "timing_realignment": {
    "enable": true,
    "method": "time_based",
    "min_gap": 0.1,
    "batch_size": 10,
    "text_search": {
      "search_padding": 3.0,
      "adjustment_threshold": 0.3
    },
    "time_based": {
      "expansion": 20.0,
      "expansion_attempts": 5,
      "similarity": 0.9
    }
  }
}
```

#### Stage 7: Text Polishing

```json
{
  "text_polishing": {
    "enable": true,
    "batch_size": 10
  }
}
```

#### Stage 8: Final Cleanup

Post-realignment cleanup filters (run after timing adjustments):

```json
{
  "final_cleanup": {
    "enable": true,
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
        "medium_duration_threshold": 5.0
      }
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

#### Global: LLM Settings

```json
{
  "llm": {
    "provider": "anthropic",
    "anthropic_api_key": "your-api-key",
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 1024,
    "temperature": 0.0
  }
}
```

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design, pipeline flow, and module organization
- **[CONFIGURATION.md](docs/CONFIGURATION.md)** - Complete configuration reference with all options
- **[PIPELINE_STAGES.md](docs/PIPELINE_STAGES.md)** - Detailed breakdown of all 9 pipeline stages

## 🏗️ Project Structure

```
transcribe-jp/
├── transcribe_jp.py           # CLI entry point
├── config.json                # Configuration file
├── requirements.txt           # Dependencies
├── setup.py                   # Package setup
│
├── core/                      # Core orchestration
│   ├── pipeline.py            # Main pipeline orchestrator (9 stages)
│   ├── config.py              # Configuration loader
│   └── display.py             # Pipeline status display
│
├── modules/                   # Processing modules (one per stage)
│   ├── stage1_audio_preprocessing/
│   │   └── processor.py       # Audio normalization
│   ├── stage2_whisper_transcription/
│   │   └── processor.py       # Whisper transcription wrapper
│   ├── stage3_segment_merging/
│   │   └── processor.py       # Merge incomplete sentences
│   ├── stage4_segment_splitting/
│   │   ├── basic_splitter.py  # Rule-based splitting
│   │   └── llm_splitter.py    # LLM intelligent splitting
│   ├── stage5_hallucination_filtering/
│   │   ├── duplicate_filter.py # Duplicate removal
│   │   ├── timing_validator.py # Timing validation
│   │   └── processor.py       # Filter orchestrator
│   ├── stage6_timing_realignment/
│   │   ├── processor.py       # Method dispatcher
│   │   ├── text_search_realignment.py   # Text-search method
│   │   ├── time_based_realignment.py    # Time-based method
│   │   └── utils.py           # Shared utilities
│   ├── stage7_text_polishing/
│   │   └── processor.py       # LLM text polishing
│   ├── stage8_final_cleanup/
│   │   ├── stammer_filter.py  # Repetition condensation
│   │   ├── word_filter.py     # Word filtering
│   │   └── processor.py       # Cleanup orchestrator
│   └── stage9_vtt_generation/
│       └── writer.py          # VTT file writer
│
├── shared/                    # Shared utilities
│   └── text_utils.py          # Text processing, formatting
│
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests (239 tests)
│   └── e2e/                   # End-to-end tests
│
└── docs/                      # Documentation
    ├── ARCHITECTURE.md
    ├── CONFIGURATION.md
    └── PIPELINE_STAGES.md
```

## 🎯 Performance Tips

1. **Use GPU**: 10-100x faster with CUDA
2. **Choose Right Model**:
   - `tiny`: Fastest, lowest quality (~1GB VRAM)
   - `base`: Fast, decent quality (~1GB VRAM)
   - `small`: Good balance (~2GB VRAM)
   - `medium`: Better accuracy (~5GB VRAM)
   - `large-v3`: Best accuracy (~10GB VRAM) - **Recommended**
3. **Audio Normalization**: Enable for quiet/variable volume audio
4. **LLM Features**: Enable for better subtitle formatting (requires API key)
5. **Disable Optional Stages**: Turn off `timing_realignment` for 30-50% faster processing

## 🔧 Troubleshooting

### ffmpeg not found
```bash
# Windows
choco install ffmpeg
# or
winget install ffmpeg

# Verify
ffmpeg -version
```

### CUDA not available
```bash
# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### Out of memory errors
- Use a smaller model (`medium` instead of `large-v3`)
- Process files one at a time
- Reduce `beam_size` in whisper config
- Lower `batch_size` for LLM stages

### LLM features not working
- Check API key is set in config.json or `ANTHROPIC_API_KEY` environment variable
- Verify `anthropic` package is installed: `pip install anthropic`
- Check you have API credits: https://console.anthropic.com/

### Subtitles out of sync
- Enable `timing_realignment` in config (Stage 6)
- Try switching methods: `"method": "text_search"` for more thorough search
- Increase `timing_realignment.text_search.search_padding` to 5.0
- Enable audio normalization for better transcription quality

## 📝 Example Workflow

```bash
# 1. Place video files in a directory
cd ~/Videos/japanese_lessons

# 2. Run transcription
transcribe-jp

# 3. Output will be in transcripts/
ls transcripts/
# lesson1.vtt
# lesson2.vtt
# lesson3.vtt

# 4. Use VTT files with video players (VLC, MPV, etc.)
vlc lesson1.mp4 --sub-file transcripts/lesson1.vtt
```

## 🧪 Testing

The project includes comprehensive unit and E2E tests:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_filters_hallucination.py -v

# Run E2E tests
pytest tests/e2e/ -v
```

**Test Coverage:**
- ✅ 257 unit tests passing
- ✅ E2E pipeline tests
- ✅ All 9 stages covered
- ✅ Hallucination filtering
- ✅ LLM splitting and polishing
- ✅ Dual-method timing realignment
- ✅ Final cleanup filters

See [tests/README.md](tests/README.md) for detailed testing documentation.

## 🤝 Contributing

Contributions are welcome! The codebase uses a clean modular architecture:

1. **Each stage is isolated** in its own module folder
2. **Core pipeline** orchestrates by calling stage modules
3. **1:1 config mapping** between config sections and stages
4. **Comprehensive tests** for all functionality

To add a new feature:
- Add filter to existing stage: Create file in `modules/stageN_name/`
- Add new stage: Create `modules/stageN_name/` with `processor.py` and integrate in `core/pipeline.py`

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design information.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- OpenAI Whisper for state-of-the-art transcription
- Anthropic Claude for intelligent LLM features
- FFmpeg for media processing

## 📚 Version History

- **v3.1.0** (2025-01): 9-stage pipeline with dual-method timing realignment
  - **NEW: Stage 8 (Final Cleanup)** - Post-realignment filters for stammer/word clustering
  - **ENHANCED: Stage 6** - Dual-method timing realignment (text-search vs time-based)
  - Stage 6 refactored into modular files (dispatcher, 2 methods, utils)
  - Moved stammer/word filters from Stage 5 → Stage 8 (run after timing adjustments)
  - **REORDERED**: Timing Realignment (Stage 6) now runs before Text Polishing (Stage 7)
  - Removed redundant `.enable` flags from method configs
  - Updated all documentation to reflect 9-stage architecture
  - 257 unit tests passing

- **v3.0.0** (2025-01): Fully modular 9-stage architecture
  - All stages now in dedicated modules
  - Stage 2 (Whisper) and Stage 9 (VTT) extracted to modules
  - Eliminated intermediate orchestrator files
  - Clean pipeline that directly calls stage modules
  - Updated documentation (ARCHITECTURE, CONFIGURATION, PIPELINE_STAGES)

- **v2.0.0** (2024-10): Modular refactor with config reorganization
  - Renamed `line_breaking` → `segment_splitting`
  - Split `audio_processing` from `whisper` config
  - Separate `text_polishing` config section
  - Created module folder structure
  - 1:1 stage-to-config mapping

- **v1.0.0**: Initial release
