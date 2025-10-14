# LLM Provider Configuration Guide

**Quick Reference:** This document explains how to configure different LLM providers for transcribe-jp's intelligent features (segment splitting and text polishing).

**Last Updated:** 2025-10-11
**Related:** [CONFIGURATION.md](../core/CONFIGURATION.md), [config.local.json.example](../../config.local.json.example)

---

## Overview

transcribe-jp uses LLMs for two optional stages:
- **Stage 4 (Segment Splitting):** Intelligently splits long segments at natural phrase boundaries
- **Stage 7 (Text Polishing):** Polishes subtitle text for better readability

You can now choose from **three LLM providers**:

| Provider | Type | Cost | Best For |
|----------|------|------|----------|
| **Ollama** | Local | FREE | Segment splitting (simple task) |
| **Anthropic** | Cloud | Paid | Text polishing (quality matters) |
| **OpenAI** | Cloud | Paid | Alternative to Anthropic |

---

## Quick Start

### Option 1: FREE Local (Ollama) - Recommended

**Important:** Ollama must be installed manually before running transcribe-jp.

```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "model": "llama3.2:3b"
    }
  }
}
```

**Installation Steps:**

1. **Install Ollama:**
   - **Windows:** Download and run installer from https://ollama.com/download
   - **macOS:** `brew install ollama` or download from https://ollama.com/download
   - **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

2. **Verify Installation:**
   ```bash
   ollama --version
   ```

3. **Run transcribe-jp:**
   - The tool will automatically start Ollama server
   - Download the specified model (~2GB for llama3.2:3b)
   - Ready to use!

**What happens automatically after installation:**
1. ✅ Validates Ollama is installed before starting pipeline
2. ✅ Starts Ollama server as subprocess
3. ✅ **Automatically pulls model if not available (with progress bar)**
4. ✅ Ready to use!

### Option 2: Cloud API (Anthropic)

```json
{
  "llm": {
    "provider": "anthropic",
    "anthropic": {
      "api_key": "sk-ant-api03-...",
      "model": "claude-3-5-haiku-20241022"
    }
  }
}
```

### Option 3: Hybrid (Best of Both)

Use FREE Ollama for splitting, paid Claude for polishing:

```json
{
  "llm": {
    "provider": "ollama",  // Default provider (FREE)
    "ollama": {
      "model": "llama3.2:3b"
    },
    "anthropic": {
      "api_key": "sk-ant-..."
    }
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

---

## Detailed Provider Configuration

### Ollama (Local, FREE, AUTO-MANAGED SERVER)

**Benefits:**
- ✅ Completely FREE
- ✅ **Server automatically started and managed**
- ✅ Private (no data leaves your machine)
- ✅ Fast for local processing
- ✅ No internet required (after model download)

**Requirements:**
- **Ollama must be installed manually** (see installation steps below)
- GPU or CPU (2-4GB RAM recommended for llama3.2:3b)
- Internet (for initial model download only)

**Setup - REQUIRED MANUAL INSTALLATION:**

1. **Install Ollama** (one-time setup):
   - **Windows:** https://ollama.com/download
   - **macOS:** `brew install ollama`
   - **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

2. **Verify installation:**
   ```bash
   ollama --version
   ```

3. **Configure in config.json:**
   ```json
   {
     "llm": {
       "provider": "ollama",
       "ollama": {
         "model": "llama3.2:3b"
       }
     }
   }
   ```

**What happens automatically after you install Ollama:**
1. ✅ Validates Ollama is installed (shows error if not)
2. ✅ Starts Ollama server as subprocess
3. ✅ **Automatically pulls the specified model with progress bar** (if not already downloaded)
4. ✅ Ready to use!

**Model pulling features:**
- Shows download progress bar with percentage and size (e.g., "Downloading: |████░░| 45.2% (1.2GB/2.6GB)")
- Displays verification status
- Handles large models with 30-minute timeout
- Works for both auto-managed and external servers

**Setup - EXTERNAL SERVER (optional):**

If you prefer to manage Ollama server yourself or use a remote server:

1. **Install Ollama:**
   - Windows: https://ollama.com/download
   - macOS: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.com/install.sh | sh`

2. **Pull a model:**
   ```bash
   ollama pull llama3.2:3b
   ```

3. **Start Ollama:**
   ```bash
   ollama serve
   ```

4. **Configure with external URL:**
   ```json
   {
     "llm": {
       "provider": "ollama",
       "ollama": {
         "base_url": "http://localhost:11434",  // Use external Ollama server
         "model": "llama3.2:3b"
       }
     }
   }
   ```

**Recommended models for Japanese:**

| Model | Size | RAM | Speed | Quality |
|-------|------|-----|-------|---------|
| `qwen3:1.7b` | 1GB | 3GB | Very Fast | Good (Qwen3 is excellent for Japanese) |
| `llama3.2:3b` | 2GB | 4GB | Fast | Good |
| `qwen3:4b-instruct` | 2.5GB | 4GB | Fast | Excellent (best for instructions) |
| `qwen3:8b-instruct` | 5.2GB | 8GB | Medium | Excellent (better instruction following) |
| `llama3.1:8b` | 4.7GB | 8GB | Medium | Excellent |

**Note:** Use `-instruct` models for text polishing (better at following instructions). Base models without `-instruct` are for general text generation.

**Configuration options:**

```json
{
  "ollama": {
    "model": "llama3.2:3b",                           // Model name (required)
    "timeout": 30,                                    // Request timeout in seconds (default: 30)
    "base_url": "http://localhost:11434"             // Optional: Use external Ollama server
  }
}
```

**Notes:**
- `base_url` is optional. If omitted, Ollama is automatically managed as a subprocess.
- `timeout` controls how long to wait for each LLM request. Increase for larger models:
  - **Small models (2-3B):** 30-60 seconds
  - **Medium models (7-8B):** 60-120 seconds
  - **Large models (32B+):** 120-300 seconds

**Timeout tips for large models:**
- If you see "Ollama request timed out" errors, increase the timeout
- You can also override timeout per stage (see "Stage-Specific Timeout Override" below)

**max_tokens tips:**
- `max_tokens` controls the maximum response length from the LLM
- **Set to 0 for unlimited** (no token limit - useful for large batches or long responses)
  - **Ollama**: Omits `num_predict` parameter, lets model generate freely
  - **Anthropic**: Uses 4096 tokens (reasonable default, since Claude requires a limit)
  - **OpenAI**: Uses None (no limit, up to model's context window)
- **For batch_size=1:** 1024 tokens is sufficient (single segment response)
- **For batch_size=10:** May need 2048-4096 tokens (10 segments in JSON array), or set to 0
- If you see incomplete JSON responses or cut-off text, increase `max_tokens` or set to 0
- **Recommendation:** Use `batch_size: 1` with `max_tokens: 1024` for Ollama (most reliable)

**Performance tip for Ollama:**

Ollama works best with one-by-one processing rather than batch processing. Set `batch_size: 1` in text_polishing config:

```json
{
  "text_polishing": {
    "enable": true,
    "batch_size": 1
  }
}
```

This disables batch processing and processes each segment individually, which is more reliable for local LLM providers like Ollama.

---

### Anthropic Claude (Cloud, Paid)

**Benefits:**
- ✅ Highest quality output
- ✅ Best Japanese language support
- ✅ Most reliable
- ❌ Requires internet
- ❌ Costs per token

**Setup:**

1. **Get API key:**
   - Sign up: https://console.anthropic.com/
   - Create API key
   - Or use environment variable: `ANTHROPIC_API_KEY`

2. **Configure:**
   ```json
   {
     "llm": {
       "provider": "anthropic",
       "max_tokens": 1024,
       "temperature": 0.0,
       "anthropic": {
         "api_key": "sk-ant-api03-...",
         "api_key_env": "ANTHROPIC_API_KEY",
         "model": "claude-3-5-haiku-20241022"
       }
     }
   }
   ```

**Model options:**

| Model | Speed | Cost/hour | Best For |
|-------|-------|-----------|----------|
| `claude-3-5-haiku-20241022` | Fast | $0.25-1 | Most tasks |
| `claude-3-5-sonnet-20241022` | Medium | $3-15 | High quality needed |
| `claude-sonnet-4-5-20250929` | Slow | $15-75 | Maximum quality |

**Configuration options:**

```json
{
  "anthropic": {
    "api_key": "sk-ant-...",               // Your API key
    "api_key_env": "ANTHROPIC_API_KEY",   // Or env variable name
    "model": "claude-3-5-haiku-20241022"  // Model to use
  }
}
```

---

### OpenAI (Cloud, Paid)

**Benefits:**
- ✅ Good quality
- ✅ Widely available
- ❌ Slightly worse than Claude for Japanese
- ❌ Costs per token

**Setup:**

1. **Get API key:**
   - Sign up: https://platform.openai.com/
   - Create API key
   - Or use environment variable: `OPENAI_API_KEY`

2. **Configure:**
   ```json
   {
     "llm": {
       "provider": "openai",
       "max_tokens": 1024,
       "temperature": 0.0,
       "openai": {
         "api_key": "sk-proj-...",
         "api_key_env": "OPENAI_API_KEY",
         "model": "gpt-4o-mini"
       }
     }
   }
   ```

**Model options:**

| Model | Speed | Cost/hour | Best For |
|-------|-------|-----------|----------|
| `gpt-4o-mini` | Fast | $0.15-0.6 | Most tasks |
| `gpt-4o` | Medium | $5-20 | High quality |

**Configuration options:**

```json
{
  "openai": {
    "api_key": "sk-proj-...",              // Your API key
    "api_key_env": "OPENAI_API_KEY",      // Or env variable name
    "model": "gpt-4o-mini"                 // Model to use
  }
}
```

---

## Stage-Specific Overrides

### Provider Override

You can use **different providers for different stages** to optimize cost vs. quality:

```json
{
  "llm": {
    "provider": "ollama",  // Default provider
    "ollama": {
      "model": "llama3.2:3b"
    },
    "anthropic": {
      "api_key": "sk-ant-...",
      "model": "claude-3-5-haiku-20241022"
    }
  },
  "segment_splitting": {
    "enable_llm": true
    // Uses global "ollama" provider (FREE)
  },
  "text_polishing": {
    "enable": true,
    "llm_provider": "anthropic"  // Override to use Anthropic for this stage only
  }
}
```

**How it works:**
1. Global `llm.provider` sets the default provider
2. Stage-specific `llm_provider` overrides for that stage
3. All provider settings come from the global `llm.{provider}` section

### Timeout Override

You can also override the **timeout per stage** for large models or complex tasks:

```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "model": "qwen3:32b",
      "timeout": 60  // Default timeout for all stages
    }
  },
  "segment_splitting": {
    "enable_llm": true
    // Uses default 60s timeout (splitting is fast)
  },
  "text_polishing": {
    "enable": true,
    "llm_timeout": 180  // Override: 3 minutes for polishing (slower task with 32B model)
  }
}
```

**When to use timeout override:**
- ✅ Using large models (13B, 32B+) for text polishing
- ✅ Text polishing takes longer than segment splitting
- ✅ Batch processing with large batch sizes
- ✅ Running on CPU instead of GPU

**Example configurations:**

**Small model (3B), GPU:**
```json
{
  "llm": { "ollama": { "model": "llama3.2:3b", "timeout": 30 } }
}
```

**Large model (32B), GPU:**
```json
{
  "llm": { "ollama": { "model": "qwen3:32b", "timeout": 60 } },
  "text_polishing": { "llm_timeout": 180 }  // 3 minutes for polishing
}
```

**Large model (32B), CPU:**
```json
{
  "llm": { "ollama": { "model": "qwen3:32b", "timeout": 120 } },
  "text_polishing": { "llm_timeout": 300 }  // 5 minutes for polishing
}
```

---

## Cost Comparison

Approximate costs for processing **1 hour of audio transcription**:

| Provider | Model | Cost | Notes |
|----------|-------|------|-------|
| Ollama | llama3.2:3b | **$0** | FREE! Uses your GPU/CPU |
| Ollama | llama3.1:8b | **$0** | FREE! Better quality, needs 8GB RAM |
| Anthropic | claude-3-5-haiku | $0.25-1.00 | Good balance |
| Anthropic | claude-3-5-sonnet | $3.00-15.00 | High quality |
| Anthropic | claude-sonnet-4-5 | $15.00-75.00 | Maximum quality |
| OpenAI | gpt-4o-mini | $0.15-0.60 | Cheaper alternative |
| OpenAI | gpt-4o | $5.00-20.00 | Premium option |

**💡 Cost-saving tip:** Use FREE Ollama for segment splitting (simple task), reserve paid APIs for text polishing (quality-critical).

---

## Configuration Reference

### Global LLM Config

```json
{
  "llm": {
    "provider": "ollama",                  // Default provider
    "max_tokens": 1024,                    // Max response length
    "temperature": 0.0,                    // Randomness (0=deterministic)
    "timeout": 60,                         // Common timeout for all providers (optional)

    "ollama": {
      "model": "llama3.2:3b",              // Auto-managed (no base_url needed)
      "timeout": 30                        // Provider-specific timeout (overrides common)
    },

    "anthropic": {
      "api_key": "<your-key>",
      "api_key_env": "ANTHROPIC_API_KEY",
      "model": "claude-3-5-haiku-20241022"
    },

    "openai": {
      "api_key": "<your-key>",
      "api_key_env": "OPENAI_API_KEY",
      "model": "gpt-4o-mini"
    }
  }
}
```

**Timeout priority:**
1. Stage-specific `llm_timeout` (highest priority)
2. Provider-specific `ollama.timeout` or `openai.timeout`
3. Common `llm.timeout` (applies to all providers)
4. Default 30 seconds (lowest priority)

### Stage-Specific Override

```json
{
  "segment_splitting": {
    "enable_llm": true,
    "llm_provider": "ollama"  // Override to use different provider for this stage
  },
  "text_polishing": {
    "enable": true,
    "llm_provider": "anthropic"  // Override to use different provider for this stage
  }
}
```

**Note:** Provider settings (model, api_key, etc.) come from global `llm.{provider}` section.

---

## Troubleshooting

### Ollama: "Ollama is not installed!" error

**Problem:** You see an error that Ollama is not installed

**Solution:**
1. Install Ollama manually:
   - **Windows:** https://ollama.com/download
   - **macOS:** `brew install ollama`
   - **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

2. Verify installation:
   ```bash
   ollama --version
   ```

3. Restart your terminal and run transcribe-jp again

**Alternative:** Use external Ollama server by specifying `base_url`:
```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "llama3.2:3b"
  }
}
```

### Ollama: Model download slow

**Problem:** Model download taking too long

**Solution:**
- First download is ~2GB for llama3.2:3b (progress bar shows download speed)
- Use smaller model: `gemma2:2b` (1.6GB)
- Check internet connection
- transcribe-jp will automatically pull the model with progress display
- Or download manually if preferred: `ollama pull llama3.2:3b`

### Ollama: "Connection refused" (manual mode)

**Problem:** Cannot connect to external Ollama server

**Solution:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama manually
ollama serve

# Or remove base_url to use auto-managed mode
```

### Anthropic: "API key not found"

**Problem:** No API key configured

**Solution:**
```bash
# Option 1: Environment variable
export ANTHROPIC_API_KEY=sk-ant-...

# Option 2: Config file
{
  "anthropic": {
    "api_key": "sk-ant-..."
  }
}
```

### Anthropic: "Rate limit exceeded"

**Problem:** Too many API requests

**Solution:**
- Reduce `text_polishing.batch_size`
- Wait and retry
- Upgrade API tier

### Ollama: Batch processing issues

**Problem:** Batch processing fails or produces inconsistent results with Ollama

**Solution:**
Disable batch processing by setting `batch_size: 1`:
```json
{
  "text_polishing": {
    "batch_size": 1
  }
}
```

This forces one-by-one processing, which is more reliable for local LLM providers.

### Ollama: "Request timed out" error

**Problem:** You see "Ollama request timed out after Xs" errors

**The error message will show:**
```
Ollama request timed out after 45s.
  Possible causes:
  - Model 'qwen3:8b' is too slow (try smaller model or increase timeout)
  - Server is under heavy load
  - Using CPU instead of GPU (check Ollama logs)
  Solution: Increase timeout in config: llm.timeout = 60 or more
```

**Solution:**

1. **Increase global timeout** for the model:
   ```json
   {
     "llm": {
       "timeout": 60  // Applies to all stages
     }
   }
   ```

2. **Or override timeout for text polishing only** (recommended for large models):
   ```json
   {
     "llm": {
       "timeout": 45  // Default for all stages
     },
     "text_polishing": {
       "enable": true,
       "llm_timeout": 90  // Override: longer timeout just for polishing
     }
   }
   ```

**Recommended timeouts by model size:**
- **2-3B models (GPU):** 30-60 seconds
- **7-8B models (GPU):** 45-90 seconds
- **32B+ models (GPU):** 120-300 seconds
- **Any model (CPU):** 2-5x longer than GPU

**Check if GPU is being used:**
```bash
# Start Ollama and watch logs
ollama serve

# Look for: "Using NVIDIA GeForce RTX 4070" or similar
# If you see "Using CPU", model will be very slow
```

### Ollama: "Cannot connect to server" error

**Problem:** You see connection errors

**The error message will show:**
```
Cannot connect to Ollama server at http://localhost:11434.
  Possible causes:
  - Ollama server not running (start with: ollama serve)
  - Wrong base_url in config (check llm.ollama.base_url)
  - Server crashed (check Ollama logs)
  Solution: Verify Ollama is running and accessible
```

**Solution:**
1. **Check if Ollama is running:**
   ```bash
   ollama list  # Should show installed models
   ```

2. **Start Ollama if not running:**
   ```bash
   ollama serve
   ```

3. **Check base_url in config** (if using external server):
   ```json
   {
     "llm": {
       "ollama": {
         "base_url": "http://localhost:11434"  // Verify this is correct
       }
     }
   }
   ```

### Ollama: "Server connection interrupted" error

**Problem:** Connection drops mid-response

**The error message will show:**
```
Ollama server connection interrupted mid-response.
  Possible causes:
  - Server crashed during generation
  - Network issues
  - Out of memory (model too large for available VRAM/RAM)
  Solution: Check Ollama server logs for errors
```

**Solution:**
1. **Check Ollama logs** (in the terminal where `ollama serve` is running)
2. **Model too large for VRAM/RAM:**
   - RTX 4070 (12GB): Use qwen3:8b or smaller
   - If out of memory, use smaller model: llama3.2:3b (2GB)
3. **Check system resources:**
   ```bash
   # Windows: Task Manager > Performance
   # Linux: nvidia-smi
   ```

### Ollama: "Model not found" error

**Problem:** Model not available on server

**The error message will show:**
```
Model 'qwen3:8b' not found on Ollama server. Please pull it: ollama pull qwen3:8b
```

**Solution:**
The pipeline will automatically attempt to pull the model. If auto-pull fails:
```bash
ollama pull qwen3:8b
```

### Ollama: "Invalid JSON response" error

**Problem:** Server returned error instead of JSON

**The error message will show:**
```
Invalid JSON response from Ollama server.
  Server may have returned an error message instead of JSON.
  Solution: Check Ollama server logs for details
```

**Solution:**
1. **Check Ollama server logs** for actual error
2. **Common causes:**
   - Model crashed during generation
   - VRAM/RAM exhausted
   - Server encountered internal error

### Text Polishing: "'list' object has no attribute 'get'" error

**Problem:** Text polishing fails with `AttributeError: 'list' object has no attribute 'get'`

**Example error:**
```
WARNING: Segment 1/10 failed: AttributeError: 'list' object has no attribute 'get'
```

**Cause:** Some LLMs (like Qwen models) sometimes return a direct JSON array `["text1", "text2"]` instead of the expected dict format `{"polished": ["text1", "text2"]}`.

**Solution:** This error has been fixed in the latest version. The code now handles both response formats automatically. If you're still seeing this error:

1. **Update to the latest version** of transcribe-jp
2. **Check your LLM configuration** - ensure model is properly specified
3. **Try with batch_size: 1** for more reliable processing:
   ```json
   {
     "text_polishing": {
       "batch_size": 1
     }
   }
   ```

**Technical details:** The fix adds type checking to handle both dict `{"polished": [...]}` and list `[...]` response formats from different LLMs.

### Performance: Slow generation

**Ollama:**
- Use smaller model: `gemma2:2b` or `llama3.2:3b`
- Check GPU usage
- Ensure adequate RAM
- Disable batch processing: `batch_size: 1` (more reliable)
- **Increase timeout** if getting timeout errors (see above)

**Cloud APIs:**
- Check internet connection
- Use faster model (haiku/mini)
- Reduce `max_tokens`

---

## FAQ

**Q: Which provider should I use?**
A: Start with **Ollama** (free, auto-managed). Upgrade to Anthropic Claude if quality matters.

**Q: Do I need to install Ollama manually?**
A: Yes! You must install Ollama manually before using it with transcribe-jp. Download from https://ollama.com/download.

**Q: What happens on first run with Ollama?**
A: The system automatically: (1) Validates Ollama is installed, (2) Starts Ollama server, (3) **Pulls the model with progress bar** showing download percentage and size (~2GB for llama3.2:3b).

**Q: Can I use my existing Ollama installation?**
A: Yes! transcribe-jp detects and uses your existing Ollama installation. Or specify `base_url` to use an external server.

**Q: Can I use different providers for different stages?**
A: Yes! Use stage-specific override. See "Stage-Specific Provider Override" above.

**Q: Do I need a GPU for Ollama?**
A: No, but it's faster. CPU works fine with smaller models (2-3B parameters).

**Q: Which model is best for Japanese?**
A: Ollama: `qwen2.5:3b` or `llama3.2:3b`. Anthropic: Any Claude model.

**Q: How much does Anthropic cost?**
A: ~$0.25-1/hour with Haiku for typical transcription.

**Q: Can I disable LLM features entirely?**
A: Yes, set `segment_splitting.enable_llm: false` and `text_polishing.enable: false`.

---

## See Also

- [CONFIGURATION.md](../core/CONFIGURATION.md) - Full configuration reference
- [config.local.json.example](../../config.local.json.example) - Example configurations
- [Ollama Models](https://ollama.com/library) - Browse available models
- [Anthropic Pricing](https://anthropic.com/pricing) - API pricing details
