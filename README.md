# Japanese Audio/Video Transcription Tool

A professional-grade transcription tool for Japanese media using OpenAI Whisper with advanced hallucination filtering and optional LLM-powered text polishing.

## ✨ Features

- **Multi-format Support**: WAV, MP3, M4A, AAC, FLAC, OGG, MP4, AVI, MKV, MOV, and more
- **9-Stage Processing Pipeline**: Clean, modular architecture
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
- **Dual-Method Timing Realignment**: Choose between text-search or time-based verification
- **Final Cleanup Stage**: Post-realignment stammer filtering and word clustering removal

## 📋 Requirements

- Python 3.8+
- ffmpeg (must be in PATH)
- CUDA GPU (optional, for 10-100x faster processing)
- Anthropic API key (optional, for LLM features)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd transcribe-jp

# Install package
pip install -e .
```

### 2. Install ffmpeg

**Windows:**
```bash
choco install ffmpeg
# or
winget install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 3. (Optional) GPU Acceleration

For **~10-100x faster** transcription:

```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# If False, install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Update config.json
{
  "whisper": {
    "device": "cuda"
  }
}
```

### 4. Run Transcription

```bash
# Navigate to directory with media files
cd /path/to/your/media

# Run transcription
transcribe-jp

# Or specify files
transcribe-jp file1.mp4 file2.wav
```

Transcripts will be saved to `transcripts/` as VTT files.

---

## ⚙️ Configuration

### Basic Config

Edit `config.json` to customize the pipeline:

```json
{
  "whisper": {
    "model": "large-v3",
    "device": "cuda"
  },
  "segment_splitting": {
    "max_line_length": 30,
    "enable_llm": true
  },
  "text_polishing": {
    "enable": true
  },
  "timing_realignment": {
    "enable": true,
    "method": "time_based"
  },
  "llm": {
    "anthropic_api_key": "<your-api-key-here>"
  }
}
```

### 🔐 API Key Security

**IMPORTANT:** Never commit your actual API key to version control.

**Option 1: Environment Variable (Recommended)**
```bash
export ANTHROPIC_API_KEY="your-actual-api-key"
```

**Option 2: Local Config File**
Create `config.local.json` (gitignored):
```json
{
  "llm": {
    "anthropic_api_key": "your-actual-api-key"
  }
}
```

### Pipeline Overview

The tool processes audio through 9 stages:

```
┌─────────────────────────────────────────────────────┐
│ Stage 1: Audio Preprocessing                        │
├─────────────────────────────────────────────────────┤
│ Stage 2: Whisper Transcription                      │
├─────────────────────────────────────────────────────┤
│ Stage 3: Segment Merging                            │
├─────────────────────────────────────────────────────┤
│ Stage 4: Segment Splitting (Optional: LLM)          │
├─────────────────────────────────────────────────────┤
│ Stage 5: Hallucination Filtering                    │
├─────────────────────────────────────────────────────┤
│ Stage 6: Timing Realignment                         │
├─────────────────────────────────────────────────────┤
│ Stage 7: Text Polishing (Optional: LLM)             │
├─────────────────────────────────────────────────────┤
│ Stage 8: Final Cleanup                              │
├─────────────────────────────────────────────────────┤
│ Stage 9: VTT Generation                             │
└─────────────────────────────────────────────────────┘
```

**📖 For detailed configuration options, see [docs/core/CONFIGURATION.md](docs/core/CONFIGURATION.md)**

**📖 For stage-by-stage details, see [docs/features/](docs/features/)**

---

## 🎯 Performance Tips

1. **Use GPU**: 10-100x faster with CUDA
2. **Choose Right Model**:
   - `tiny/base`: Fast, lower quality
   - `small/medium`: Good balance
   - `large-v3`: Best accuracy - **Recommended**
3. **Audio Normalization**: Enable for quiet/variable volume audio
4. **LLM Features**: Enable for better subtitle formatting (requires API key)
5. **Disable Optional Stages**: Turn off `timing_realignment` for 30-50% faster processing

---

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
- Enable audio normalization for better transcription quality

**📖 For more troubleshooting, see [docs/features/](docs/features/) for stage-specific issues**

---

## 📚 Documentation

### For Users
- **[Quick Start](#quick-start)** - Installation and basic usage (above)
- **[Configuration Guide](docs/core/CONFIGURATION.md)** - Complete config reference
- **[Features Documentation](docs/features/)** - Understand each pipeline stage

### For Developers
- **[Documentation Hub](docs/README.md)** - Complete documentation index
- **[Architecture](docs/core/ARCHITECTURE.md)** - System design and pipeline flow
- **[AI Guide](docs/AI_GUIDE.md)** - Development guidelines and best practices
- **[Testing](tests/README.md)** - Testing documentation (261 unit tests)

---

## 🧪 Testing

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

**Test Coverage:**
- ✅ 261 unit tests passing
- ✅ E2E pipeline tests
- ✅ All 9 stages covered

See [tests/README.md](tests/README.md) for detailed testing documentation.

---

## 🤝 Contributing

Contributions are welcome! The codebase uses a clean modular architecture:

1. Each stage is isolated in its own module folder
2. Core pipeline orchestrates by calling stage modules
3. 1:1 config mapping between config sections and stages
4. Comprehensive tests for all functionality

See [docs/core/ARCHITECTURE.md](docs/core/ARCHITECTURE.md) for detailed design information.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- OpenAI Whisper for state-of-the-art transcription
- Anthropic Claude for intelligent LLM features
- FFmpeg for media processing

---

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

---

*For changelog and version history, see [docs/CHANGELOG.md](docs/CHANGELOG.md)*
