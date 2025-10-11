# Documentation Hub

> **👥 AUDIENCE:** This documentation hub is designed for **human developers** working on transcribe-jp.
> **🤖 AI assistants:** See [AI_GUIDE.md](AI_GUIDE.md) instead for AI-specific onboarding and guidelines.

Welcome to the transcribe-jp project documentation. This directory contains comprehensive guides for developers and users.

---

## 📚 Documentation System

This project uses a **two-audience documentation system**:

| Audience | File | Purpose |
|----------|------|---------|
| **Human Developers** | [README.md](README.md) (this file) | Developer-friendly hub with guides and references |
| **AI Assistants** | [AI_GUIDE.md](AI_GUIDE.md) | AI-specific quick reference, guidelines, and session history |
| **Everyone** | `docs/core/`, project root | Detailed knowledge organized by category |

**Both audiences** share the same detailed documentation, but have different entry points optimized for their needs.

---

## 📖 Core Documentation

### For Developers

- **[../README.md](../README.md)** - Start here! Project overview, installation, usage, and quick start
- **[core/ARCHITECTURE.md](core/ARCHITECTURE.md)** - System architecture, 9-stage pipeline design, and data flow
- **[core/CONFIGURATION.md](core/CONFIGURATION.md)** - Complete configuration reference for all stages
- **[core/PIPELINE_STAGES.md](core/PIPELINE_STAGES.md)** - Detailed breakdown of all 9 pipeline stages

### For Understanding the System

- **[core/ARCHITECTURE.md](core/ARCHITECTURE.md)** - 3-layer design, module organization, and pipeline flow
- **[../tests/README.md](../tests/README.md)** - Testing documentation (261 unit + 4 E2E tests)

### Development Guidelines

- **[AI_GUIDE.md](AI_GUIDE.md)** - Quick reference guide (useful for all developers)
  - Critical guidelines and workflows
  - Testing requirements
  - Common tasks and troubleshooting
  - Written for AI assistants but applicable to all developers

### Feature Documentation

- **[features/](features/)** - Individual pipeline stage documentation
  - Detailed guides for each of the 9 stages
  - Configuration examples
  - Usage patterns and troubleshooting
  - See [features/README.md](features/README.md) for complete index

### Change Tracking

- **[CHANGELOG.md](CHANGELOG.md)** - All notable changes to the project
- **[SESSIONS.md](SESSIONS.md)** - Development session history and lessons learned

---

## 🚀 Quick Start Guides

### For New Developers

1. Read [../README.md](../README.md) to understand what this project does and how to install it
2. Read [core/ARCHITECTURE.md](core/ARCHITECTURE.md) to understand the system design
3. Read [core/PIPELINE_STAGES.md](core/PIPELINE_STAGES.md) to understand each processing stage
4. Check [AI_GUIDE.md](AI_GUIDE.md) for development patterns and guidelines

### For Contributing Code

1. Read [AI_GUIDE.md](AI_GUIDE.md) first - contains critical guidelines and common mistakes
2. Review [CHANGELOG.md](CHANGELOG.md) to understand recent changes
3. Read [core/ARCHITECTURE.md](core/ARCHITECTURE.md) for technical details
4. Run tests: `python -X utf8 -m pytest tests/unit/ -q --tb=line` (all 261 must pass)
5. Update documentation and commit changes

### For Configuring the Pipeline

1. Read [../README.md](../README.md#configuration) for quick start config
2. See [core/CONFIGURATION.md](core/CONFIGURATION.md) for complete reference
3. Understand stage behavior in [core/PIPELINE_STAGES.md](core/PIPELINE_STAGES.md)
4. Check [features/](features/) for individual stage deep-dives

### For Understanding a Specific Stage

1. Check [features/README.md](features/README.md) for stage list
2. Read the specific stage documentation (e.g., [features/STAGE6_TIMING_REALIGNMENT.md](features/STAGE6_TIMING_REALIGNMENT.md))
3. Review configuration in [core/CONFIGURATION.md](core/CONFIGURATION.md)
4. Check implementation in `modules/stageN_*/` folder

---

## 📚 Documentation Structure

```
transcribe-jp/
├── README.md                    # Main project overview (START HERE)
├── LICENSE                      # MIT License
│
├── docs/                        # Documentation hub
│   ├── README.md                # This file - Documentation hub
│   ├── AI_GUIDE.md              # AI assistant quick reference
│   ├── CHANGELOG.md             # Change history
│   ├── SESSIONS.md              # Development session history
│   ├── core/                    # Core project documentation
│   │   ├── ARCHITECTURE.md      # System design and pipeline flow
│   │   ├── CONFIGURATION.md     # Complete config reference
│   │   └── PIPELINE_STAGES.md   # Detailed stage breakdown
│   ├── features/                # Individual stage documentation
│   │   ├── README.md            # Features index
│   │   ├── STAGE4_SEGMENT_SPLITTING.md
│   │   ├── STAGE5_HALLUCINATION_FILTERING.md
│   │   ├── STAGE6_TIMING_REALIGNMENT.md
│   │   └── ... (9 stages)
│   └── maintenance/             # Historical technical records
│       └── TIMING_REALIGNMENT_IMPROVEMENTS_2025-10-10.md
│
├── tests/                       # Test suite
│   ├── README.md                # Testing documentation
│   ├── unit/                    # 261 unit tests
│   └── e2e/                     # 4 E2E tests
│       └── README.md            # E2E test documentation
│
├── core/                        # Core orchestration code
├── modules/                     # 9 stage processing modules
└── shared/                      # Shared utilities
```

---

## 🔍 Finding Information

### "How do I install and use this?"
→ See [../README.md](../README.md#installation)

### "What does this project do?"
→ See [../README.md](../README.md#features)

### "How does the 9-stage pipeline work?"
→ See [core/ARCHITECTURE.md](core/ARCHITECTURE.md#pipeline-flow)

### "What does each stage do?"
→ See [core/PIPELINE_STAGES.md](core/PIPELINE_STAGES.md)

### "How do I configure stage X?"
→ See [core/CONFIGURATION.md](core/CONFIGURATION.md) or [features/STAGEX_NAME.md](features/)

### "How does Stage 6 Timing Realignment work?"
→ See [features/STAGE6_TIMING_REALIGNMENT.md](features/STAGE6_TIMING_REALIGNMENT.md)

### "What's the project structure?"
→ See [core/ARCHITECTURE.md](core/ARCHITECTURE.md#directory-structure)

### "How do I run tests?"
→ See [AI_GUIDE.md](AI_GUIDE.md#testing-requirements) or [../tests/README.md](../tests/README.md)

### "What changed recently?"
→ See [CHANGELOG.md](CHANGELOG.md)

### "What lessons have been learned?"
→ See [SESSIONS.md](SESSIONS.md)

---

## 🤝 Contributing to Documentation

### When to Update Documentation

- **../README.md** - When adding user-facing features or changing installation/usage
- **core/ARCHITECTURE.md** - When modifying system design or pipeline structure
- **core/CONFIGURATION.md** - When adding/changing config options
- **core/PIPELINE_STAGES.md** - When modifying stage behavior
- **features/STAGEX_*.md** - When modifying specific stage implementation or behavior
- **AI_GUIDE.md** - When discovering new patterns or lessons learned
- **CHANGELOG.md** - For ALL significant changes (required)
- **SESSIONS.md** - When completing significant work or making key decisions

### Documentation Standards

1. **Use Markdown** - GitHub Flavored Markdown (GFM)
2. **Add Examples** - Code examples, diagrams, and usage patterns
3. **Link Related Docs** - Cross-reference other documentation with relative paths
4. **Keep Updated** - Update docs when you change code
5. **Be Specific** - Include file paths, line numbers, and concrete examples

---

## 📦 Related Resources

### External Resources
- [OpenAI Whisper Documentation](https://github.com/openai/whisper)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Python Testing with pytest](https://docs.pytest.org/)

### Internal Resources
- Source Code: `../core/`, `../modules/`, `../shared/`
- Tests: `../tests/unit/`, `../tests/e2e/`
- Config: `../config.json`

---

## 💡 Tips

- **Use the search function** in your editor to find specific topics across all docs
- **Follow links** between documents - they're there to help you navigate
- **Update as you go** - If you find documentation outdated, update it
- **Ask questions** - If documentation is unclear, improve it for the next developer
- **Run tests before committing** - All 261 unit tests must pass

---

*This documentation hub is maintained by the team. Keep it updated and helpful!*

*Last updated: 2025-10-11*
