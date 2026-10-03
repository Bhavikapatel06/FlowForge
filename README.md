# Qoneqt AI Content Pipeline — Hackathon MVP

An automated, LLM-powered content production pipeline transforming raw ideas, trends, and topics into vertical, broadcast-ready videos for the Qoneqt Global Feed.

## 🎯 Project Overview

This project implements a repeatable 10-phase production pipeline:
1. **Foundation (Next.js + FastAPI)**
2. **AI Storyboard Engine**
3. **Human Review & Editor**
4. **Scene Generation (Image & Video Fallbacks)**
5. **Voice Synthesis (TTS)**
6. **Caption Alignment (SRT)**
7. **Video Composition (FFmpeg 9:16 vertical)**
8. **Quality Gate (Automated pre-flight checks)**
9. **Qoneqt Publishing Interface**
10. **Deployment & Deliverables**

---

## 🏗️ Repository Structure

```
FlowForge/
├── frontend/             # Next.js UI Dashboard
├── backend/              # FastAPI Application
├── pipeline/             # Modular pipeline stages
│   ├── research/         # Research & topic extraction
│   ├── script/           # Storyboard & LLM prompt logic
│   ├── scenes/           # Visual generation orchestrator
│   ├── voice/            # TTS generation
│   ├── captions/         # SRT alignment
│   ├── composer/         # Video composition engine
│   └── quality/          # Automated quality gate
├── generated/            # Local asset cache and build outputs
│   ├── scripts/
│   ├── scenes/
│   ├── images/
│   ├── audio/
│   ├── captions/
│   └── videos/
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Phase Status

- [x] **PHASE 0: Project Setup** - Directory structure, modular packages, environment configuration.
- [x] **PHASE 1: Foundation** - Next.js frontend connected to FastAPI backend (`POST /api/generate`).
- [x] **PHASE 2: AI Storyboard** - Topic to strict structured JSON storyboard with hook, script, 6 vertical scenes, prompts, and captions.
- [x] **PHASE 3: Human Review** - In-place editing of title, hook, script, and scene details, plus storyboard approval and state locking (`POST /api/storyboard/approve`).
- [ ] **PHASE 4: Scene Generation**
- [ ] **PHASE 5: Voice**
- [ ] **PHASE 6: Captions**
- [ ] **PHASE 7: Video Composer**
- [ ] **PHASE 8: Quality Gate**
- [ ] **PHASE 9: Qoneqt Publishing**
- [ ] **PHASE 10: Live Deployment**
