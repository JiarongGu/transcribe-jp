# Application Logging System

**Purpose:** Standardized logging system with multiple severity levels for capturing application events, debugging information, and errors.

**Last Updated:** 2025-10-15
**Related:** [LLM_PROVIDERS.md](LLM_PROVIDERS.md), [TROUBLESHOOTING.md](../ai-assistant/TROUBLESHOOTING.md)

---

## Overview

The application uses a centralized logging system that provides standardized logging with multiple severity levels. This helps with debugging, error tracking, and monitoring application behavior during transcription and LLM processing.

---

## Logging Levels

The logging system supports five standard levels (following Python's logging module):

| Level | Value | Purpose | When to Use | Output |
|-------|-------|---------|-------------|--------|
| **DEBUG** | 10 | Detailed diagnostic info | Development, troubleshooting | File only |
| **INFO** | 20 | General informational messages | Normal operations, milestones | File only |
| **WARNING** | 30 | Warning messages | Recoverable issues, deprecations | File + Console |
| **ERROR** | 40 | Error messages | Errors that don't stop execution | File + Console |
| **CRITICAL** | 50 | Critical failures | Severe errors requiring attention | File + Console |

**Note:** Console only shows WARNING and above. All levels are logged to file.

---

## Log File Location

Logs are stored in the `transcripts/logs/` directory:

```
transcripts/
├── logs/
│   ├── 20251015.log                    # Daily general log
│   ├── 20251015_143022_123456_json_error.log  # Detailed JSON error
│   ├── 20251015_143045_789012_exception.log   # Detailed exception
│   └── ...
└── (your .vtt files here)
```

**Log Types:**
- **Daily log:** `YYYYMMDD.log` - All logging events for the day
- **JSON error detail:** `YYYYMMDD_HHMMSS_microseconds_json_error.log` - Detailed JSON decode errors
- **Exception detail:** `YYYYMMDD_HHMMSS_microseconds_exception.log` - Detailed exception information

---

## Using the Logger

### Basic Usage

```python
from shared.logger import get_logger

logger = get_logger()

# Log at different levels
logger.debug("Detailed debugging information")
logger.info("Processing stage 7: text polishing")
logger.warning("Model temperature is high, results may vary")
logger.error("Failed to parse JSON response")
logger.critical("Cannot connect to LLM provider")
```

### Logging with Context

Add structured context to any log message:

```python
from shared.logger import get_logger

logger = get_logger()

context = {
    "stage": "text_polishing",
    "batch_num": 3,
    "total_segments": 50,
    "model": "qwen2.5:7b"
}

logger.info("Starting text polishing", context=context)
logger.error("Batch processing failed", context=context)
```

**Console output:**
```
ERROR: Batch processing failed | Context: {'stage': 'text_polishing', 'batch_num': 3, ...}
```

**File output:**
```
2025-10-15 14:30:22 | ERROR    | Batch processing failed | Context: {'stage': 'text_polishing', 'batch_num': 3, ...}
```

---

## Specialized Logging Functions

### JSON Decode Error Logging

For JSON parsing failures, use the specialized method that creates a detailed error file:

```python
from shared.logger import get_logger

logger = get_logger()

try:
    data = json.loads(llm_response)
except json.JSONDecodeError as e:
    context = {
        "stage": "text_polishing",
        "batch_num": 3,
        "processing_mode": "batch"
    }

    # Creates detailed log file with full LLM response and prompt
    log_path = logger.log_json_decode_error(
        error=e,
        raw_response=llm_response,
        prompt=original_prompt,
        context=context
    )

    # Log is automatically added to daily log
    # Detailed file created at: transcripts/logs/YYYYMMDD_HHMMSS_microseconds_json_error.log
```

### Exception Logging

For general exceptions, use the exception logging method:

```python
from shared.logger import get_logger

logger = get_logger()

try:
    result = perform_operation()
except Exception as e:
    context = {
        "operation": "segment_splitting",
        "input_file": "audio.mp3"
    }

    # Creates detailed exception log with traceback
    log_path = logger.log_exception(
        error=e,
        operation="Segment splitting",
        context=context,
        level=logger.ERROR  # Optional: default is ERROR
    )
```

---

## Daily Log Format

The daily log (`YYYYMMDD.log`) contains all events:

```
2025-10-15 14:25:10 | INFO     | Starting transcription pipeline
2025-10-15 14:25:15 | DEBUG    | Loading audio file: audio.mp3 | Context: {'size': 15728640, 'duration': 180}
2025-10-15 14:25:20 | INFO     | Stage 1: Preprocessing complete
2025-10-15 14:30:22 | ERROR    | JSONDecodeError in text_polishing stage | Context: {'stage': 'text_polishing', 'batch_num': 3}
2025-10-15 14:30:22 | INFO     | Detailed error log saved: 20251015_143022_123456_json_error.log
2025-10-15 14:35:00 | WARNING  | Model temperature is high (0.8), results may vary
2025-10-15 14:40:00 | INFO     | Transcription complete: output.vtt
```

---

## Detailed JSON Error Log Format

When `log_json_decode_error()` is called, a detailed file is created:

```
================================================================================
JSON DECODE ERROR - DETAILED LOG
================================================================================

Timestamp: 2025-10-15 14:30:22
Error Type: JSONDecodeError
Error Message: Extra data: line 1 column 2 (char 1)

--------------------------------------------------------------------------------
ERROR DETAILS
--------------------------------------------------------------------------------
Message: Extra data
Line: 1, Column: 2
Position: 25

--------------------------------------------------------------------------------
CONTEXT
--------------------------------------------------------------------------------
stage: text_polishing
batch_num: 3
batch_size: 10
total_segments: 50
processing_mode: batch

--------------------------------------------------------------------------------
RAW LLM RESPONSE (156 characters)
--------------------------------------------------------------------------------
{"polished": ["整形後のテキスト"]}
説明: このテキストは整形されました。

--------------------------------------------------------------------------------
PROMPT SENT TO LLM (450 characters)
--------------------------------------------------------------------------------
これは音声認識によって生成された日本語字幕です...
(full prompt content here)

================================================================================
END OF LOG
================================================================================
```

---

## Detailed Exception Log Format

When `log_exception()` is called, a detailed file is created:

```
================================================================================
EXCEPTION - DETAILED LOG
================================================================================

Timestamp: 2025-10-15 14:35:10
Operation: Segment splitting
Error Type: RuntimeError
Error Message: Model 'qwen3:8b' not found on Ollama server

--------------------------------------------------------------------------------
CONTEXT
--------------------------------------------------------------------------------
stage: segment_splitting
model: qwen3:8b
input_file: audio.mp3

--------------------------------------------------------------------------------
TRACEBACK
--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "modules/stage4_segment_splitting/llm_splitter.py", line 125, in split_segment
    response = llm_provider.generate(prompt)
  File "shared/llm_utils.py", line 244, in generate
    raise RuntimeError(f"Model '{self.model}' not found on Ollama server.")
RuntimeError: Model 'qwen3:8b' not found on Ollama server

================================================================================
END OF LOG
================================================================================
```

---

## Common Logging Patterns

### Logging Stage Progress

```python
logger.info(f"Starting {stage_name}")
logger.debug(f"Processing {len(items)} items", context={"stage": stage_name})
logger.info(f"Completed {stage_name}")
```

### Logging Warnings

```python
if temperature > 0.5:
    logger.warning(
        f"High temperature ({temperature}) may produce unpredictable results",
        context={"model": model_name, "temperature": temperature}
    )
```

### Logging Errors

```python
try:
    result = process_batch(batch)
except Exception as e:
    logger.error(
        f"Batch {batch_num} failed: {str(e)}",
        context={"batch_num": batch_num, "batch_size": len(batch)}
    )
    # Optionally log detailed exception
    logger.log_exception(e, f"Batch {batch_num} processing", context={...})
```

---

## Configuration

### Default Settings

```python
from shared.logger import get_logger

# Default: logs to transcripts/logs/, logger name "transcribe-jp"
logger = get_logger()
```

### Custom Settings

```python
from shared.logger import get_logger

# Custom log directory and logger name
logger = get_logger(log_dir="custom_logs", name="my-app")
```

### Custom Log Levels (if needed)

```python
from shared.logger import AppLogger

logger = AppLogger()

# Use specific log levels
logger.logger.setLevel(AppLogger.DEBUG)  # Capture all levels
logger.logger.setLevel(AppLogger.WARNING)  # Only warnings and above
```

---

## Log Retention

- Logs are **never automatically deleted**
- Daily logs accumulate one per day
- Detailed error logs accumulate as errors occur
- Consider periodic cleanup for old logs

**Manual cleanup examples:**

```bash
# Delete logs older than 30 days (Windows PowerShell)
Get-ChildItem transcripts/logs/ -Filter *.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item

# Delete logs older than 30 days (Linux/Mac)
find transcripts/logs/ -name "*.log" -mtime +30 -delete

# Archive old logs
tar -czf logs_archive_2025-10.tar.gz transcripts/logs/202510*.log
rm transcripts/logs/202510*.log
```

---

## Best Practices

### 1. Use Appropriate Levels

```python
# ✅ Good
logger.debug("Variable value: {value}")          # Development details
logger.info("Processing complete")                # Milestones
logger.warning("Deprecated config option used")   # Recoverable issues
logger.error("Failed to process item")            # Errors
logger.critical("Cannot connect to required service")  # Critical failures

# ❌ Bad
logger.error("Processing complete")               # Not an error
logger.info("Critical system failure")            # Too low level
```

### 2. Add Context

```python
# ✅ Good - includes context
logger.error("Batch processing failed", context={
    "batch_num": 3,
    "stage": "text_polishing",
    "model": "qwen2.5:7b"
})

# ❌ Bad - no context
logger.error("Batch processing failed")
```

### 3. Use Specialized Methods for Rich Details

```python
# ✅ Good - uses specialized method for JSON errors
try:
    data = json.loads(response)
except json.JSONDecodeError as e:
    logger.log_json_decode_error(e, response, prompt, context)

# ❌ Bad - loses important details
try:
    data = json.loads(response)
except json.JSONDecodeError as e:
    logger.error(f"JSON error: {e}")
```

### 4. Don't Log Sensitive Data

```python
# ✅ Good - no sensitive data
logger.info("API key configured", context={"provider": "anthropic"})

# ❌ Bad - exposes sensitive data
logger.info(f"Using API key: {api_key}")
```

---

## Integration with Existing Code

The logging system is already integrated into:

### Text Polishing (Stage 7)
- Logs batch processing progress (INFO)
- Captures JSON decode errors with full context
- Logs retry attempts (DEBUG)

### Segment Splitting (Stage 4)
- Logs LLM splitting operations (INFO)
- Captures JSON decode errors with segment context
- Logs timing information (DEBUG)

### LLM Utils
- Automatically logs all JSON decode errors with detailed information
- Provides raw response and prompt in detailed log files

---

## Troubleshooting

### No logs appearing

Check if log directory exists:
```python
from pathlib import Path
Path("transcripts/logs").mkdir(parents=True, exist_ok=True)
```

### Too many log files

Implement log rotation or periodic cleanup (see Log Retention section above)

### Logs missing details

Make sure to:
1. Use appropriate log level (DEBUG for detailed info)
2. Add context parameter to log calls
3. Use specialized methods for rich error details

---

## See Also

- [LLM_PROVIDERS.md](LLM_PROVIDERS.md) - LLM provider configuration
- [TROUBLESHOOTING.md](../ai-assistant/TROUBLESHOOTING.md) - General troubleshooting
- [shared/logger.py](../../shared/logger.py) - Logger implementation
