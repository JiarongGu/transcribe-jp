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

```bash
# 1. Install Ollama
# Download from: https://ollama.com/download

# 2. Pull a model
ollama pull llama3.2:3b

# 3. Update config.json
```

```json
{
  "llm": {
    "provider": "ollama",
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "llama3.2:3b"
    }
  }
}
```

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
    "provider": "ollama",
    "ollama": {
      "model": "llama3.2:3b"
    },
    "anthropic": {
      "api_key": "sk-ant-..."
    }
  },
  "segment_splitting": {
    "enable_llm": true
  },
  "text_polishing": {
    "enable": true,
    "llm_provider": "anthropic",
    "llm_config": {
      "anthropic": {
        "api_key": "sk-ant-..."
      }
    }
  }
}
```

---

## Detailed Provider Configuration

### Ollama (Local, FREE)

**Benefits:**
- ✅ Completely FREE
- ✅ Private (no data leaves your machine)
- ✅ Fast for local processing
- ✅ No internet required

**Requirements:**
- GPU or CPU (2-4GB RAM recommended)
- Ollama installed locally

**Setup:**

1. **Install Ollama:**
   - Download: https://ollama.com/download
   - Windows: Runs as Windows service (automatic)
   - Mac: Runs in menu bar (automatic)
   - Linux: `curl -fsSL https://ollama.com/install.sh | sh`

2. **Pull a model:**
   ```bash
   ollama pull llama3.2:3b
   ```

3. **Configure:**
   ```json
   {
     "llm": {
       "provider": "ollama",
       "max_tokens": 1024,
       "temperature": 0.0,
       "ollama": {
         "base_url": "http://localhost:11434",
         "model": "llama3.2:3b",
         "timeout": 30
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
    "base_url": "http://localhost:11434",  // Ollama server URL
    "model": "llama3.2:3b",                // Model name
    "timeout": 30                           // Request timeout (seconds)
  }
}
```

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

## Stage-Specific Provider Override

You can use **different providers for different stages** to optimize cost vs. quality:

```json
{
  "llm": {
    "provider": "ollama",
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
    "llm_provider": "anthropic",           // Override to use Anthropic
    "llm_config": {
      "anthropic": {
        "model": "claude-3-5-haiku-20241022"
      }
    }
  }
}
```

**How it works:**
1. Global `llm.provider` sets the default
2. Stage-specific `llm_provider` overrides for that stage
3. Stage-specific `llm_config` merges with global config

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

    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "llama3.2:3b",
      "timeout": 30
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

### Stage-Specific Override

```json
{
  "segment_splitting": {
    "enable_llm": true,
    "llm_provider": "ollama",              // Override global provider
    "llm_config": {
      "ollama": {
        "model": "llama3.2:3b"            // Stage-specific model
      },
      "max_tokens": 512                    // Stage-specific param
    }
  }
}
```

---

## Troubleshooting

### Ollama: "Connection refused"

**Problem:** Cannot connect to Ollama server

**Solution:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama (Linux)
systemctl start ollama

# Reinstall if needed
# https://ollama.com/download
```

### Ollama: "Model not found"

**Problem:** Model not pulled

**Solution:**
```bash
# Pull the model
ollama pull llama3.2:3b

# Verify it's available
ollama list
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

### Performance: Slow generation

**Ollama:**
- Use smaller model: `gemma2:2b`
- Check GPU usage
- Ensure adequate RAM

**Cloud APIs:**
- Check internet connection
- Use faster model (haiku/mini)
- Reduce `max_tokens`

---

## FAQ

**Q: Which provider should I use?**
A: Start with **Ollama** (free). Upgrade to Anthropic Claude if quality matters.

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
