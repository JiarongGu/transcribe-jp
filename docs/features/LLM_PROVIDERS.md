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
| `llama3.2:3b` | 2GB | 4GB | Fast | Good |
| `gemma2:2b` | 1.6GB | 3GB | Very Fast | Fair |
| `qwen2.5:3b` | 2.3GB | 4GB | Fast | Good (better Japanese) |
| `llama3.1:8b` | 4.7GB | 8GB | Medium | Excellent |

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

**Problem:** You see "Ollama request timed out after 30s" errors

**Solution:**

1. **Increase global timeout** for the model:
   ```json
   {
     "llm": {
       "ollama": {
         "model": "qwen3:32b",
         "timeout": 120  // Increase to 2 minutes
       }
     }
   }
   ```

2. **Or override timeout for text polishing only** (recommended for large models):
   ```json
   {
     "llm": {
       "ollama": {
         "model": "qwen3:32b",
         "timeout": 60  // Default timeout
       }
     },
     "text_polishing": {
       "enable": true,
       "llm_timeout": 180  // 3 minutes just for text polishing
     }
   }
   ```

**Recommended timeouts by model size:**
- **2-3B models (GPU):** 30-60 seconds
- **7-8B models (GPU):** 60-120 seconds
- **32B+ models (GPU):** 120-300 seconds
- **Any model (CPU):** 2-5x longer than GPU

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
