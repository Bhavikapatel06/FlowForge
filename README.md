# FlowForge — Qoneqt AI Content Pipeline 🎬🚀
> **Qoneqt × CTRL FREAK 2026 AI Challenge MVP**  
> **Team:** Hackora • **Institution:** CHARUSAT  
> **Members:** Bhavika Patel • Bhumi Shah • Nandit Kalaria • Sil Shah  

An automated, LLM-powered content production pipeline transforming raw ideas, trends, and topics into vertical (9:16, 1080×1920), broadcast-ready videos for the **Qoneqt Global Feed**.

---

## 📑 Table of Contents
1. [The Problem & Gap](#1-the-problem--gap)
2. [Our Solution](#2-our-solution)
3. [Architecture & Workflow](#3-architecture--workflow)
4. [Tech Stack](#4-tech-stack)
5. [Setup Instructions](#5-setup-instructions)
6. [Environment Variables](#6-environment-variables)
7. [Phase-by-Phase Pipeline Explanation](#7-phase-by-phase-pipeline-explanation)
8. [How to Run Locally](#8-how-to-run-locally)
9. [Deployment Guide](#9-deployment-guide)
10. [Qoneqt Publishing Workflow](#10-qoneqt-publishing-workflow)
11. [Verification & Test Suite](#11-verification--test-suite)

---

## 1. The Problem & Gap

### The Core Problem
* **Fragmented Workflow**: Content research, scriptwriting, visual asset creation, voice synthesis, and video editing reside in disconnected tools.
* **Inconsistent Output**: Format, tone, resolution, and pacing fluctuate wildly between generation runs.
* **Costly to Scale**: Generating one one-off clip is straightforward; producing dozens of cohesive, publish-ready videos daily is not.
* **Missing Safeguards**: Off-the-shelf generative AI lacks automated quality gates, leading to audio desynchronization, incorrect aspect ratios, and broken media reaching social feeds.

### The Real Gap
> **"The gap is not video generation. It is the pipeline."**

Existing solutions rely either on manual editing that fails to scale or one-shot AI video generators that produce unformatted, silent clips without narrative coherence, localized voiceovers, subtitles, or platform publishing hooks.

---

## 2. Our Solution

**One continuous, model-agnostic AI pipeline that transforms any topic, idea, or trend into a publish-ready vertical video and deploys it to the Qoneqt Global Feed.**

* **Repeatable Production Flow**: Structured JSON schemas connect every stage from initial prompt to final MP4.
* **Independent Stage Retries**: If Scene 3 fails visual rendering, only Scene 3 retries—preserving all prior compute and state.
* **Strict Quality Gate**: 7 automated pre-flight checks inspect resolution, audio streams, caption alignment, and container compliance before enabling publishing.
* **Regional & Community Aware**: Multi-lingual neural voices supporting **English, Hindi, and Gujarati** narration with synchronous on-screen captions.

---

## 3. Architecture & Workflow

```
[ User Input / Trend ]
         │
         ▼
[ Phase 1: Foundation ] ─── FastAPI Backend + Next.js UI Dashboard
         │
         ▼
[ Phase 2: AI Storyboard ] ── Gemini / Structured Engine (Strict JSON Schema)
         │                   Hook + 6 Timed Scenes + Narration + Prompts + Captions
         ▼
[ Phase 3: Human Review ] ── In-place Story Editor & Approval Locking
         │
         ▼
[ Phase 4: Scene Generation ] ── 9:16 Vertical Visuals (Pollinations AI + Canvas Fallback)
         │                       Independent per-scene retry
         ▼
[ Phase 5: Voice (TTS) ] ──── Neural Narration (edge-tts / regional Hindi/Gujarati/English)
         │                    Output: generated/audio/narration.mp3
         ▼
[ Phase 6: Captions ] ────── Synchronized SRT, WebVTT & ASS Subtitles
         │                    Output: generated/captions/captions.srt
         ▼
[ Phase 7: FFmpeg Composer ] ── 1080×1920 (9:16) Vertical Video Assembly
         │                      H.264 FastStart Web Playable Container
         ▼
[ Phase 8: Quality Gate ] ──── 7 Pre-Flight Automated Verification Checks
         │                      Video, Container, Duration, 9:16, Audio, Captions, Scenes
         ▼
[ Phase 9: Qoneqt Publish ] ── Cryptographic Receipt + Signed Global Feed Release
         │
         ▼
[ Qoneqt Global Feed ]
```

---

## 4. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Frontend** | Next.js 14, React 18, Lucide Icons | Responsive glassmorphism dashboard, real-time pipeline status, interactive editors |
| **Backend & API** | FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous API, strict schema validation, static media streaming |
| **AI LLM Engine** | Gemini 1.5 Flash / Modular LLM Abstraction | Strict JSON storyboard generator with automatic fallback guarantees |
| **Visual Generation** | Pollinations AI (1080x1920 9:16) + PIL Synthetic Canvas | Model-agnostic scene generation with zero-downtime offline fallback |
| **Voice Synthesis** | Microsoft Edge TTS (Azure Neural) | Multi-regional voices: English (`en-US-ChristopherNeural`), Hindi (`hi-IN-MadhurNeural`), Gujarati (`gu-IN-DhwaniNeural`) |
| **Captions** | SubRip (SRT), WebVTT, ASS | Millisecond-accurate scene subtitle synchronization |
| **Video Engine** | FFmpeg 7.1 via `imageio-ffmpeg` | 1080×1920 9:16 vertical video composition, FastStart web streaming |
| **Testing** | Pytest, TestClient, Httpx | 100% test coverage across Phases 1 through 9 |

---

## 5. Setup Instructions

### Prerequisites
* **Python 3.10+** (Tested on Python 3.12 / 3.14)
* **Node.js 18+** & **npm 9+**
* **Git**

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Bhavikapatel06/FlowForge.git
   cd FlowForge
   ```

2. **Backend Setup**:
   ```bash
   # Install Python requirements
   pip install -r backend/requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 6. Environment Variables

Copy `.env.example` to `.env` in the project root:

```bash
cp .env.example .env
```

Configurable variables:

```ini
# Server Configuration
PORT=8000
HOST=0.0.0.0
FRONTEND_PORT=3000

# LLM Configuration (Optional: built-in structured generator works out of the box)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Image Generation
IMAGE_PROVIDER=auto  # Options: auto, pollinations, canvas_synthetic

# TTS Configuration
TTS_PROVIDER=edge-tts # Options: edge-tts, synthetic_cadence

# Qoneqt Platform Gateway (Configured once official endpoints/keys are provided)
QONEQT_API_URL=
QONEQT_API_KEY=
```

---

## 7. Phase-by-Phase Pipeline Explanation

### Phase 1: Foundation
* Establishes the decoupled Next.js + FastAPI client-server architecture.
* Health monitoring endpoint at `GET /api/health`.

### Phase 2: AI Storyboard
* Transforms topic into strict, structured JSON containing video title, 3-second viral hook, total duration (30-45s), keywords, and 6 timed scenes.
* Validated strictly against Pydantic models.

### Phase 3: Human Review & Approval
* Interactive review stage allowing creators to edit the title, hook, narrative script, visual prompts, and subtitles.
* Approval button locks state to `generated/scripts/approved_storyboard.json` before initiating media generation.

### Phase 4: Scene Visuals Generation
* Modular `generate_scene_visual(scene)` abstraction.
* Generates 1080×1920 9:16 vertical cards.
* **Isolated Failure Domain**: Independent retry endpoint (`POST /api/scenes/retry/{scene_id}`) regenerates failing scenes without touching others.

### Phase 5: Voice Synthesis
* Takes approved narration text and renders `generated/audio/narration.mp3`.
* Supports multi-regional voices (English, Hindi, Gujarati).

### Phase 6: Captions Alignment
* Generates synchronized `captions.srt`, `captions.vtt`, and styled `captions.ass` from storyboard scene timings.

### Phase 7: FFmpeg Video Composition
* Merges vertical scene visuals, narration audio, and captions into `generated/videos/final.mp4`.
* Strict 1080×1920 (9:16) vertical format with H.264 FastStart for instant browser playback.

### Phase 8: Quality Gate
* Automated 7-point pre-flight check:
  1. File integrity & size
  2. H.264 FastStart playability
  3. Target duration compliance (25–50s)
  4. 9:16 vertical ratio (1080×1920)
  5. AAC stereo audio stream detection
  6. Subtitle synchronization
  7. Scene completeness (all scenes accounted for)
* Emits `STATUS: READY TO PUBLISH`.

### Phase 9: Qoneqt Publishing
* Modular publishing abstraction adhering to the **zero fake endpoints** rule.
* Enforces Quality Gate verification before unlocking publication.
* Generates a signed cryptographic release manifest with SHA-256 hash.

### Phase 10: Live Deployment
* Complete environment encapsulation, production builds, and container/cloud readiness.

---

## 8. How to Run Locally

### 1. Start the FastAPI Backend
```bash
python backend/main.py
```
*Backend runs at:* `http://localhost:8000` (API docs: `http://localhost:8000/docs`)

### 2. Start the Next.js Frontend
```bash
cd frontend
npm run dev
```
*Frontend runs at:* `http://localhost:3000`

### 3. Open in Browser
Visit `http://localhost:3000` to interact with the full dashboard or click **"One-Click Full Run"** to watch all 10 phases execute live!

---

## 9. Deployment Guide

### Option A: Cloud / VPS Deployment (Docker / PM2)
1. **Backend**:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm run build
   npm run start -- -p 3000
   ```

### Option B: Vercel + Cloud Run / Render
* **Frontend**: Deploy `frontend/` directly to Vercel. Set `NEXT_PUBLIC_API_URL` to your backend URL.
* **Backend**: Deploy `backend/` to Render, Railway, or Google Cloud Run with Python 3.11+.

---

## 10. Qoneqt Publishing Workflow

The publishing module (`pipeline/publish/publisher.py`) is designed with strict hackathon integrity:

1. **Gatekeeper Validation**: If Quality Gate checks fail, the publish button remains locked.
2. **Cryptographic Sealing**: Computes SHA-256 fingerprint of `final.mp4`.
3. **Environment Injection**:
   * If `QONEQT_API_URL` and `QONEQT_API_KEY` are defined, sends an authenticated multipart payload to the live Qoneqt gateway.
   * If awaiting official gateway credentials, outputs a verified, signed release package manifest stored in `generated/publish_receipt.json`.

---

## 11. Verification & Test Suite

Each phase has a dedicated test script ensuring independent reliability:

```bash
# Run all phase verification tests individually
python backend/test_phase1.py   # Phase 1: Health & Base API
python backend/test_phase2.py   # Phase 2: Storyboard Structure
python backend/test_phase3.py   # Phase 3: Human Review & Locking
python backend/test_phase4.py   # Phase 4: Scene Generation & Retry
python backend/test_phase5.py   # Phase 5: Voice Synthesis
python backend/test_phase6.py   # Phase 6: Captions Synchronization
python backend/test_phase7.py   # Phase 7: FFmpeg Video Composition
python backend/test_phase8.py   # Phase 8: Quality Gate Pre-Flight
python backend/test_phase9.py   # Phase 9: Qoneqt Publishing Abstraction

# Run the complete end-to-end integration test
python backend/test_all_phases.py
```

---

<div align="center">
  <b>Built with ❤️ by Team Hackora for the Qoneqt × CTRL FREAK 2026 AI Challenge</b>
</div>
