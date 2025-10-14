# Ollama Configuration Guide

**Quick Reference:** Advanced Ollama configuration options for custom installations and performance tuning.

**Last Updated:** 2025-10-14
**Related:** [LLM_PROVIDERS.md](LLM_PROVIDERS.md), [CONFIGURATION.md](../core/CONFIGURATION.md)

---

## Overview

This guide covers advanced Ollama configuration options for:
- Custom installation paths (when Ollama is installed in non-standard locations)
- External Ollama servers (remote or manually managed)
- Performance tuning (timeouts, model selection)
- Troubleshooting installation detection

For basic Ollama setup, see [LLM_PROVIDERS.md](LLM_PROVIDERS.md).

---

## Problem: Ollama Installed in Different Locations

**Issue:** On different PCs, Ollama might be installed in different locations:
- Windows: `C:\Program Files\Ollama\`, `%LOCALAPPDATA%\Programs\Ollama\`, custom paths
- macOS: `/usr/local/bin/`, `/opt/homebrew/bin/`, `/Applications/Ollama.app/`
- Linux: `/usr/local/bin/`, `~/.local/bin/`, `/opt/ollama/`

**Solution:** transcribe-jp now includes comprehensive auto-detection + manual configuration options.

---

## Automatic Detection (Default)

By default, transcribe-jp automatically detects Ollama in common locations:

**Windows:**
```
1. System PATH (shutil.which)
2. %LOCALAPPDATA%\Programs\Ollama\ollama.exe
3. C:\Program Files\Ollama\ollama.exe
4. C:\Program Files (x86)\Ollama\ollama.exe
5. %APPDATA%\Ollama\ollama.exe
```

**macOS:**
```
1. System PATH (shutil.which)
2. /usr/local/bin/ollama
3. /opt/homebrew/bin/ollama (Apple Silicon)
4. ~/.local/bin/ollama
5. /Applications/Ollama.app/Contents/MacOS/ollama
```

**Linux:**
```
1. System PATH (shutil.which)
2. ~/.local/bin/ollama
3. /usr/local/bin/ollama
4. /usr/bin/ollama
5. /opt/ollama/bin/ollama
```

**No configuration needed** - just install Ollama normally and transcribe-jp will find it.

---

## Manual Configuration Options

### Option 1: Custom Executable Path

If Ollama is installed in a non-standard location, specify the full path:

```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "model": "llama3.2:3b",
      "executable_path": "D:\\CustomPath\\ollama.exe"  // Windows
      // or
      "executable_path": "/opt/custom/ollama"  // macOS/Linux
    }
  }
}
```

**Use cases:**
- ✅ Custom installation directory
- ✅ Portable Ollama installation
- ✅ Company-managed installation path
- ✅ Multiple Ollama versions on same machine

**Priority:** Custom path is checked **first**, before auto-detection.

### Option 2: External Ollama Server

Use a manually managed or remote Ollama server:

```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "model": "llama3.2:3b",
      "base_url": "http://localhost:11434"  // Local external server
      // or
      "base_url": "http://192.168.1.100:11434"  // Remote server
    }
  }
}
```

**Use cases:**
- ✅ Manually start/stop Ollama (no auto-management)
- ✅ Remote Ollama server on another machine
- ✅ Shared Ollama server for multiple users
- ✅ Docker containerized Ollama

**Behavior:**
- Skips subprocess management (doesn't start/stop Ollama)
- Just verifies server is reachable
- Still auto-pulls model if needed

### Option 3: Both Custom Path AND External Server

For maximum control:

```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "model": "llama3.2:3b",
      "executable_path": "D:\\CustomPath\\ollama.exe",
      "base_url": "http://localhost:11434"
    }
  }
}
```

**Use case:** Custom Ollama path with external server management.

---

## Performance Configuration

### Timeout Configuration

If generation times out with smaller models, increase timeout:

**Global timeout** (applies to all LLM operations):
```json
{
  "llm": {
    "provider": "ollama",
    "timeout": 120,  // 2 minutes (default: 30s)
    "ollama": {
      "model": "qwen3:4b"
    }
  }
}
```

**Stage-specific timeout** (recommended for large models):
```json
{
  "llm": {
    "provider": "ollama",
    "timeout": 45,  // Default for splitting
    "ollama": {
      "model": "qwen3:8b"
    }
  },
  "text_polishing": {
    "enable": true,
    "llm_timeout": 180  // 3 minutes just for polishing
  }
}
```

**Recommended timeouts by model size:**

| Model Size | GPU | CPU |
|------------|-----|-----|
| 2-3B (llama3.2:3b) | 30-60s | 120-180s |
| 4-8B (qwen3:8b) | 45-90s | 180-300s |
| 13B+ (qwen3:32b) | 120-300s | 600s+ |

### Model Selection for Speed

If your model is too slow (even with GPU), use a smaller model:

**Fast models for Japanese:**
```json
{
  "ollama": {
    "model": "qwen3:1.7b"  // Fastest, 1GB, good quality (Qwen3 excels at Japanese)
    // or
    "model": "llama3.2:3b"  // Fast, 2GB, good quality
    // or
    "model": "qwen3:4b-instruct"  // Fast, 2.5GB, excellent (best for instructions)
  }
}
```

**For best quality (slower):**
```json
{
  "ollama": {
    "model": "qwen3:8b-instruct"  // 5.2GB, excellent quality + instruction following
    // or
    "model": "llama3.1:8b"  // 4.7GB, excellent quality
    // or
    "model": "qwen3:14b"  // 8.5GB, highest quality Qwen3 that fits in 12GB VRAM
  }
}
```

**Important:** Use `-instruct` models for text polishing - they're specifically fine-tuned to follow instructions better. Base models (without `-instruct`) are for general text generation.

### Batch Processing

Ollama works best with one-by-one processing:

```json
{
  "text_polishing": {
    "enable": true,
    "batch_size": 1  // Process one segment at a time
  }
}
```

---

## Complete Configuration Examples

### Example 1: Auto-Detected Installation (Simplest)

```json
{
  "llm": {
    "provider": "ollama",
    "timeout": 60,
    "ollama": {
      "model": "llama3.2:3b"
    }
  },
  "text_polishing": {
    "enable": true,
    "batch_size": 1
  }
}
```

**When to use:** Ollama installed normally in standard location.

### Example 2: Custom Installation Path

```json
{
  "llm": {
    "provider": "ollama",
    "timeout": 60,
    "ollama": {
      "model": "llama3.2:3b",
      "executable_path": "D:\\MyApps\\Ollama\\ollama.exe"
    }
  }
}
```

**When to use:** Ollama installed in custom directory, want auto-management.

### Example 3: External Server (Manually Managed)

```json
{
  "llm": {
    "provider": "ollama",
    "timeout": 60,
    "ollama": {
      "model": "llama3.2:3b",
      "base_url": "http://localhost:11434"
    }
  }
}
```

**When to use:** You start `ollama serve` manually or use remote server.

### Example 4: Performance Optimized (Large Model)

```json
{
  "llm": {
    "provider": "ollama",
    "timeout": 90,  // Default for all stages
    "ollama": {
      "model": "qwen3:8b"  // 8B model needs more time
    }
  },
  "segment_splitting": {
    "enable_llm": true
    // Uses 90s timeout (splitting is fast)
  },
  "text_polishing": {
    "enable": true,
    "batch_size": 1,
    "llm_timeout": 180  // 3 minutes for polishing
  }
}
```

**When to use:** Using larger models (8B+) with GPU, need different timeouts per stage.

### Example 5: Remote Ollama Server

```json
{
  "llm": {
    "provider": "ollama",
    "timeout": 120,  // Network latency
    "ollama": {
      "model": "llama3.2:3b",
      "base_url": "http://192.168.1.100:11434"  // Remote server
    }
  }
}
```

**When to use:** Using Ollama on a different machine (local network or cloud).

---

## Troubleshooting

### Issue: "Ollama executable not found"

**Diagnosis:**
```bash
# Check if Ollama is in PATH
where ollama  # Windows
which ollama  # macOS/Linux

# Check if Ollama is installed
# Windows: Check C:\Program Files\Ollama\ or %LOCALAPPDATA%\Programs\Ollama\
# macOS: Check /usr/local/bin/ollama
# Linux: Check /usr/local/bin/ollama
```

**Solution 1:** Add Ollama to PATH
```bash
# Windows: Add to System Environment Variables
# macOS/Linux: Add to ~/.bashrc or ~/.zshrc
export PATH="/usr/local/bin:$PATH"
```

**Solution 2:** Use `executable_path` in config
```json
{
  "ollama": {
    "executable_path": "/full/path/to/ollama"
  }
}
```

### Issue: "Cannot reach external Ollama server"

**Diagnosis:**
```bash
# Test if server is reachable
curl http://localhost:11434/api/tags

# Or on Windows PowerShell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
```

**Solution:**
1. Ensure Ollama server is running: `ollama serve`
2. Check firewall settings (if remote server)
3. Verify `base_url` in config matches actual server URL
4. For remote servers, ensure Ollama is bound to network interface:
   ```bash
   OLLAMA_HOST=0.0.0.0:11434 ollama serve
   ```

### Issue: "Model generation too slow (timeout)"

**Diagnosis:** Run the diagnostic test:
```bash
python test_ollama_quick.py
```

Look for generation time:
- **< 5s**: Excellent (GPU)
- **5-15s**: Good (GPU with large model, or CPU with small model)
- **15-30s**: Slow (need timeout increase)
- **> 30s**: Very slow (check GPU usage, use smaller model)

**Solution 1:** Increase timeout
```json
{
  "llm": {
    "timeout": 120  // or higher
  }
}
```

**Solution 2:** Use smaller model
```json
{
  "ollama": {
    "model": "llama3.2:3b"  // Instead of qwen3:8b
  }
}
```

**Solution 3:** Check GPU usage
```bash
# Windows/Linux with NVIDIA
nvidia-smi

# Look for ollama.exe process using GPU
# If not using GPU, check NVIDIA drivers and CUDA installation
```

### Issue: "Generation works but very slow on GPU"

**Possible causes:**
1. **First request is slow** - model needs to load into VRAM (normal)
2. **GPU memory insufficient** - model is offloading to system RAM
3. **GPU thermal throttling** - GPU overheating, reducing performance
4. **Background GPU usage** - other applications using GPU

**Diagnosis:**
```bash
# Check VRAM usage
nvidia-smi

# Model VRAM requirements:
# llama3.2:3b = ~2GB
# qwen3:4b = ~2.5GB
# qwen3:8b = ~5GB
# qwen3:32b = ~20GB

# If "Memory-Usage" shows high percentage, model might be offloading to RAM
```

**Solution:**
1. Close other GPU-intensive applications (games, video editors, browsers with hardware acceleration)
2. Use smaller model if VRAM is insufficient
3. Ensure adequate GPU cooling
4. Check GPU drivers are up-to-date

---

## Configuration Priority

When multiple configuration options are specified, priority is:

**Executable detection:**
1. Custom `executable_path` (highest priority)
2. System PATH (`shutil.which`)
3. Platform-specific common locations
4. Installation fails (lowest priority)

**Timeout configuration:**
1. Stage-specific `llm_timeout` (e.g., `text_polishing.llm_timeout`)
2. Provider-specific timeout (`ollama.timeout`)
3. Common `llm.timeout`
4. Default 30 seconds

**Server management:**
- If `base_url` is set → External server mode (no subprocess management)
- If `base_url` is NOT set → Auto-managed mode (starts/stops Ollama)

---

## See Also

- [LLM_PROVIDERS.md](LLM_PROVIDERS.md) - Basic Ollama setup and provider comparison
- [CONFIGURATION.md](../core/CONFIGURATION.md) - Full configuration reference
- [Integration Tests](../../tests/integration/test_ollama.py) - Test cases for Ollama
- [Ollama Documentation](https://github.com/ollama/ollama) - Official Ollama docs

---

**Last Updated:** 2025-10-14 - Added comprehensive path detection and custom configuration options
