"use client";

import { useState, useEffect, useRef } from "react";
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Clock,
  Tag,
  Film,
  MessageSquare,
  FileText,
  Sliders,
  Check,
  ChevronRight,
  Eye,
  RefreshCw,
  Lock,
  Edit3,
  Save,
  Volume2,
  Subtitles,
  Video,
  ShieldCheck,
  Send,
  Download,
  Play,
  RotateCcw,
  Zap,
  Globe,
  Radio,
  Maximize2,
} from "lucide-react";


export default function Home() {
  const [topic, setTopic] = useState("AI in student life");
  const [style, setStyle] = useState("Educational");
  const [language, setLanguage] = useState("English");

  // Loading states per phase
  const [loadingStoryboard, setLoadingStoryboard] = useState(false);
  const [approving, setApproving] = useState(false);
  const [generatingScenes, setGeneratingScenes] = useState(false);
  const [retryingSceneId, setRetryingSceneId] = useState(null);
  const [generatingVoice, setGeneratingVoice] = useState(false);
  const [generatingCaptions, setGeneratingCaptions] = useState(false);
  const [composingVideo, setComposingVideo] = useState(false);
  const [checkingQuality, setCheckingQuality] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [runningAll, setRunningAll] = useState(false);

  // Progressive feedback simulation while generating
  const [progressStep, setProgressStep] = useState(0);
  const [error, setError] = useState(null);
  
  // Pipeline Data States
  const [storyboard, setStoryboard] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isApproved, setIsApproved] = useState(false);
  const [approvalInfo, setApprovalInfo] = useState(null);

  const [scenes, setScenes] = useState([]);
  const [voiceData, setVoiceData] = useState(null);
  const [captionsData, setCaptionsData] = useState(null);
  const [videoData, setVideoData] = useState(null);
  const [qualityReport, setQualityReport] = useState(null);
  const [publishReceipt, setPublishReceipt] = useState(null);

  const videoRef = useRef(null);
  const API_BASE = "http://localhost:8000";

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen();
      } else if (videoRef.current.webkitRequestFullscreen) {
        videoRef.current.webkitRequestFullscreen();
      } else if (videoRef.current.msRequestFullscreen) {
        videoRef.current.msRequestFullscreen();
      }
    }
  };


  const progressSteps = [
    "Analyzing topic & trend context",
    "Synthesizing high-retention hook",
    "Composing vertical narration script",
    "Planning 9:16 vertical scenes & visual prompts",
  ];

  useEffect(() => {
    let interval;
    if (loadingStoryboard) {
      setProgressStep(0);
      interval = setInterval(() => {
        setProgressStep((prev) => (prev < progressSteps.length - 1 ? prev + 1 : prev));
      }, 700);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [loadingStoryboard]);

  // Auto-hydrate pipeline state on mount so completed assets are immediately viewable
  useEffect(() => {
    const hydrateState = async () => {
      try {
        const appRes = await fetch(`${API_BASE}/api/storyboard/approved`);
        if (appRes.ok) {
          const appData = await appRes.json();
          if (appData) {
            setStoryboard(appData);
            setIsApproved(true);
          }
        }
        const scRes = await fetch(`${API_BASE}/api/scenes`);
        if (scRes.ok) {
          const scData = await scRes.json();
          if (scData.scenes && scData.scenes.length > 0) setScenes(scData.scenes);
        }
        const vRes = await fetch(`${API_BASE}/api/voice`);
        if (vRes.ok) {
          const vData = await vRes.json();
          if (vData) setVoiceData(vData);
        }
        const capRes = await fetch(`${API_BASE}/api/captions`);
        if (capRes.ok) {
          const capData = await capRes.json();
          if (capData) setCaptionsData(capData);
        }
        const compRes = await fetch(`${API_BASE}/api/compose/status`);
        if (compRes.ok) {
          const compData = await compRes.json();
          if (compData) setVideoData(compData);
        }
        const qRes = await fetch(`${API_BASE}/api/quality/report`);
        if (qRes.ok) {
          const qData = await qRes.json();
          if (qData) setQualityReport(qData);
        }
        const pubRes = await fetch(`${API_BASE}/api/publish/receipt`);
        if (pubRes.ok) {
          const pubData = await pubRes.json();
          if (pubData) setPublishReceipt(pubData);
        }
      } catch (err) {
        // Non-blocking on initial cold starts
      }
    };
    hydrateState();
  }, []);


  // Phase 2: Generate Storyboard
  const handleGenerateStoryboard = async (e) => {
    if (e) e.preventDefault();
    if (!topic.trim()) return;

    setLoadingStoryboard(true);
    setError(null);
    setStoryboard(null);
    setIsApproved(false);
    setApprovalInfo(null);
    setIsEditing(false);
    setScenes([]);
    setVoiceData(null);
    setCaptionsData(null);
    setVideoData(null);
    setQualityReport(null);
    setPublishReceipt(null);

    try {
      const res = await fetch(`${API_BASE}/api/storyboard`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic.trim(), style, language }),
      });

      if (!res.ok) throw new Error(`Storyboard generation failed (HTTP ${res.status})`);
      const data = await res.json();
      setStoryboard(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to generate storyboard");
    } finally {
      setLoadingStoryboard(false);
    }
  };

  // Phase 3: Approve Storyboard
  const handleApprove = async () => {
    if (!storyboard) return;
    setApproving(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/storyboard/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(storyboard),
      });

      if (!res.ok) throw new Error(`Approval failed (HTTP ${res.status})`);
      const data = await res.json();
      setIsApproved(true);
      setApprovalInfo(data);
      setIsEditing(false);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to approve storyboard");
    } finally {
      setApproving(false);
    }
  };

  // Phase 4: Generate All Scenes
  const handleGenerateScenes = async () => {
    setGeneratingScenes(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/scenes/generate?provider=auto`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`Scene generation failed (HTTP ${res.status})`);
      const data = await res.json();
      setScenes(data.scenes || []);
    } catch (err) {
      console.error(err);
      setError(err.message || "Scene generation failed");
    } finally {
      setGeneratingScenes(false);
    }
  };

  // Phase 4: Retry Single Scene (Isolated Error Handling)
  const handleRetryScene = async (sceneId) => {
    setRetryingSceneId(sceneId);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/scenes/retry/${sceneId}?provider=auto`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`Scene ${sceneId} retry failed`);
      const updatedScene = await res.json();
      setScenes((prev) =>
        prev.map((s) => (s.scene_id === sceneId ? { ...s, ...updatedScene } : s))
      );
    } catch (err) {
      console.error(err);
      setError(err.message || `Failed to retry Scene ${sceneId}`);
    } finally {
      setRetryingSceneId(null);
    }
  };

  // Phase 5: Generate Voice Narration
  const handleGenerateVoice = async () => {
    setGeneratingVoice(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/voice/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          script: storyboard?.script,
          language: storyboard?.language || language,
        }),
      });
      if (!res.ok) throw new Error(`Voice generation failed (HTTP ${res.status})`);
      const data = await res.json();
      setVoiceData(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Voice generation failed");
    } finally {
      setGeneratingVoice(false);
    }
  };

  // Phase 6: Generate Captions
  const handleGenerateCaptions = async () => {
    setGeneratingCaptions(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/captions/generate`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`Caption generation failed (HTTP ${res.status})`);
      const data = await res.json();
      setCaptionsData(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Caption generation failed");
    } finally {
      setGeneratingCaptions(false);
    }
  };

  // Phase 7: Compose Video via FFmpeg
  const handleComposeVideo = async () => {
    setComposingVideo(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/compose`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`Video composition failed (HTTP ${res.status})`);
      const data = await res.json();
      setVideoData(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Video composition failed");
    } finally {
      setComposingVideo(false);
    }
  };

  // Phase 8: Run Quality Gate Checks
  const handleRunQualityGate = async () => {
    setCheckingQuality(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/quality/check`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`Quality check failed (HTTP ${res.status})`);
      const data = await res.json();
      setQualityReport(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Quality check failed");
    } finally {
      setCheckingQuality(false);
    }
  };

  // Phase 9: Publish to Qoneqt Global Feed
  const handlePublish = async () => {
    setPublishing(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ channel: "global-feed" }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Publishing failed");
      }
      const data = await res.json();
      setPublishReceipt(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Publishing to Qoneqt failed");
    } finally {
      setPublishing(false);
    }
  };

  // One-Click End-to-End Runner
  const handleRunAll = async () => {
    setRunningAll(true);
    setError(null);

    try {
      // 1. Generate Storyboard
      setLoadingStoryboard(true);
      const sbRes = await fetch(`${API_BASE}/api/storyboard`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic.trim(), style, language }),
      });
      const sb = await sbRes.json();
      setStoryboard(sb);
      setLoadingStoryboard(false);

      // 2. Auto-approve
      setApproving(true);
      const appRes = await fetch(`${API_BASE}/api/storyboard/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sb),
      });
      const appData = await appRes.json();
      setIsApproved(true);
      setApprovalInfo(appData);
      setApproving(false);

      // 3. Scenes
      setGeneratingScenes(true);
      const scRes = await fetch(`${API_BASE}/api/scenes/generate?provider=auto`, { method: "POST" });
      const scData = await scRes.json();
      setScenes(scData.scenes || []);
      setGeneratingScenes(false);

      // 4. Voice
      setGeneratingVoice(true);
      const vRes = await fetch(`${API_BASE}/api/voice/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script: sb.script, language: sb.language }),
      });
      const vData = await vRes.json();
      setVoiceData(vData);
      setGeneratingVoice(false);

      // 5. Captions
      setGeneratingCaptions(true);
      const capRes = await fetch(`${API_BASE}/api/captions/generate`, { method: "POST" });
      const capData = await capRes.json();
      setCaptionsData(capData);
      setGeneratingCaptions(false);

      // 6. Compose
      setComposingVideo(true);
      const compRes = await fetch(`${API_BASE}/api/compose`, { method: "POST" });
      const compData = await compRes.json();
      setVideoData(compData);
      setComposingVideo(false);

      // 7. Quality Gate
      setCheckingQuality(true);
      const qRes = await fetch(`${API_BASE}/api/quality/check`, { method: "POST" });
      const qData = await qRes.json();
      setQualityReport(qData);
      setCheckingQuality(false);
    } catch (err) {
      console.error(err);
      setError(err.message || "Pipeline execution failed");
    } finally {
      setRunningAll(false);
      setLoadingStoryboard(false);
      setApproving(false);
      setGeneratingScenes(false);
      setGeneratingVoice(false);
      setGeneratingCaptions(false);
      setComposingVideo(false);
      setCheckingQuality(false);
    }
  };

  // Storyboard editing helpers
  const updateField = (field, value) => {
    setStoryboard((prev) => ({ ...prev, [field]: value }));
    setIsApproved(false);
  };

  const updateScene = (sceneIndex, field, value) => {
    setStoryboard((prev) => {
      const newScenes = [...prev.scenes];
      newScenes[sceneIndex] = {
        ...newScenes[sceneIndex],
        [field]: field === "duration" ? parseInt(value, 10) || 1 : value,
      };
      const totalDuration = newScenes.reduce((acc, s) => acc + s.duration, 0);
      return { ...prev, duration: totalDuration, scenes: newScenes };
    });
    setIsApproved(false);
  };

  const getSceneTiming = (sceneList, targetIndex) => {
    let start = 0;
    for (let i = 0; i < targetIndex; i++) {
      start += sceneList[i].duration;
    }
    const end = start + sceneList[targetIndex].duration;
    return `${start}s – ${end}s (${sceneList[targetIndex].duration}s)`;
  };

  return (
    <main className="container">
      {/* Top Header */}
      <div className="header">
        <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.5rem" }}>
          <div className="badge">
            <Sparkles size={13} />
            Qoneqt × CTRL FREAK 2026
          </div>
          <div className="badge" style={{ background: "rgba(16, 185, 129, 0.15)", borderColor: "rgba(16, 185, 129, 0.3)", color: "#6ee7b7" }}>
            <Radio size={13} />
            Team Hackora • CHARUSAT
          </div>
        </div>
        <h1 className="title">AI-Powered Video Content Pipeline</h1>
        <p className="subtitle">
          Transform any topic, prompt, or trend into a broadcast-ready 9:16 vertical video for the Qoneqt Global Feed.
        </p>
      </div>

      {/* Global Interactive Pipeline Progress Bar */}
      <div className="pipeline-steps">
        <div className="step-chip done">
          <CheckCircle2 size={13} />
          1. Topic
        </div>
        <div className={`step-chip ${storyboard ? "done" : loadingStoryboard ? "active" : ""}`}>
          {storyboard ? <CheckCircle2 size={13} /> : <span>2</span>}
          2. Storyboard
        </div>
        <div className={`step-chip ${isApproved ? "done" : storyboard ? "active" : ""}`}>
          {isApproved ? <CheckCircle2 size={13} /> : <span>3</span>}
          3. Human Review
        </div>
        <div className={`step-chip ${scenes.length > 0 ? "done" : isApproved ? "active" : ""}`}>
          {scenes.length > 0 ? <CheckCircle2 size={13} /> : <span>4</span>}
          4. 9:16 Scenes
        </div>
        <div className={`step-chip ${voiceData ? "done" : scenes.length > 0 ? "active" : ""}`}>
          {voiceData ? <CheckCircle2 size={13} /> : <span>5</span>}
          5. Voice TTS
        </div>
        <div className={`step-chip ${captionsData ? "done" : voiceData ? "active" : ""}`}>
          {captionsData ? <CheckCircle2 size={13} /> : <span>6</span>}
          6. Captions
        </div>
        <div className={`step-chip ${videoData ? "done" : captionsData ? "active" : ""}`}>
          {videoData ? <CheckCircle2 size={13} /> : <span>7</span>}
          7. Composition
        </div>
        <div className={`step-chip ${qualityReport?.passed ? "done" : videoData ? "active" : ""}`}>
          {qualityReport?.passed ? <CheckCircle2 size={13} /> : <span>8</span>}
          8. Quality Gate
        </div>
        <div className={`step-chip ${publishReceipt ? "done" : qualityReport?.passed ? "active" : ""}`}>
          {publishReceipt ? <CheckCircle2 size={13} /> : <span>9</span>}
          9. Qoneqt Feed
        </div>
      </div>

      {/* PHASE 1 & 2: Topic & Generation Form */}
      <div className="card">
        <div className="card-title">
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <Sparkles size={20} color="var(--accent-primary)" />
            <span>Phase 1 & 2: Topic & Storyboard Engine</span>
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              id="run-all-button"
              type="button"
              className="btn-run-all"
              disabled={runningAll || loadingStoryboard}
              onClick={handleRunAll}
            >
              {runningAll ? (
                <>
                  <div className="spinner" />
                  <span>Executing Pipeline...</span>
                </>
              ) : (
                <>
                  <Zap size={16} />
                  <span>One-Click Full Run</span>
                </>
              )}
            </button>
          </div>
        </div>

        <form onSubmit={handleGenerateStoryboard}>
          <div className="form-group">
            <label className="label" htmlFor="topic-input">Content Topic or Trend</label>
            <input
              id="topic-input"
              type="text"
              className="input"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. AI in student life, Quantum Computing Breakthroughs..."
              required
            />
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="label" htmlFor="style-select">Content Style</label>
              <select
                id="style-select"
                className="select"
                value={style}
                onChange={(e) => setStyle(e.target.value)}
              >
                <option value="Educational">Educational & Insightful</option>
                <option value="Entertaining">Entertaining & Fast-Paced</option>
                <option value="Inspirational">Inspirational & Motivational</option>
                <option value="News & Trends">News & Emerging Tech</option>
              </select>
            </div>

            <div className="form-group">
              <label className="label" htmlFor="language-select">Regional Voice & Language</label>
              <select
                id="language-select"
                className="select"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="English">English (Neural)</option>
                <option value="Hindi">Hindi (Regional)</option>
                <option value="Gujarati">Gujarati (Regional)</option>
                <option value="Spanish">Spanish (Neural)</option>
                <option value="French">French (Neural)</option>
                <option value="German">German (Neural)</option>
              </select>
            </div>
          </div>

          <div style={{ display: "flex", gap: "1rem", marginTop: "1.25rem" }}>
            <button
              id="generate-button"
              type="submit"
              className="btn-primary"
              disabled={loadingStoryboard || runningAll}
            >
              {loadingStoryboard ? (
                <>
                  <div className="spinner" />
                  <span>Synthesizing Storyboard...</span>
                </>
              ) : (
                <>
                  <span>Generate Storyboard</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </div>
        </form>

        {loadingStoryboard && (
          <div className="progress-box">
            <div className="progress-title">
              <div className="spinner" />
              <span>AI Story Pipeline active...</span>
            </div>
            <div className="progress-steps-list">
              {progressSteps.map((step, idx) => {
                const isDone = idx < progressStep;
                const isCurrent = idx === progressStep;
                return (
                  <div
                    key={step}
                    className={`progress-step-item ${isDone ? "completed" : ""} ${isCurrent ? "active" : ""}`}
                  >
                    {isDone ? (
                      <CheckCircle2 size={16} color="var(--success)" />
                    ) : isCurrent ? (
                      <RefreshCw size={16} className="spinner" />
                    ) : (
                      <div style={{ width: 14, height: 14, borderRadius: "50%", border: "2px solid rgba(255,255,255,0.2)" }} />
                    )}
                    <span>{step}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {error && (
          <div
            style={{
              color: "#f87171",
              fontSize: "0.9rem",
              marginTop: "1.5rem",
              background: "rgba(239, 68, 68, 0.12)",
              padding: "1rem",
              borderRadius: "var(--radius-sm)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* PHASE 3: Storyboard & Human Review */}
      {storyboard && (
        <div className="card" id="storyboard-card">
          <div className="card-title">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Film size={20} color="var(--accent-primary)" />
              <span>Phase 3: Human Review & Storyboard Approval</span>
            </div>
            {isApproved && (
              <span className="meta-pill approved">
                <Lock size={12} /> Approved & Locked
              </span>
            )}
          </div>

          {isApproved && (
            <div className="approved-banner" id="approval-banner">
              <div className="approved-banner-text">
                <CheckCircle2 size={24} color="#10b981" />
                <div>
                  <div className="approved-banner-title">
                    STORYBOARD APPROVED & LOCKED FOR PRODUCTION
                  </div>
                  <div className="approved-banner-sub">
                    {approvalInfo?.message || "Human review complete. Proceed to Phase 4 Scene Generation."}
                  </div>
                </div>
              </div>
              <div className="meta-pill approved" style={{ background: "rgba(16, 185, 129, 0.25)" }}>
                <Lock size={12} /> State Preserved
              </div>
            </div>
          )}

          {/* Title and metadata */}
          <div className="storyboard-header">
            {isEditing ? (
              <div style={{ width: "100%", marginBottom: "1rem" }}>
                <label className="detail-label">Title (Editable)</label>
                <input
                  id="edit-title-input"
                  type="text"
                  className="input-edit"
                  style={{ fontSize: "1.3rem", fontWeight: 800 }}
                  value={storyboard.title}
                  onChange={(e) => updateField("title", e.target.value)}
                />
              </div>
            ) : (
              <h2 className="storyboard-title" id="storyboard-title" style={{ marginBottom: "0.75rem" }}>
                {storyboard.title}
              </h2>
            )}

            <div className="metadata-tags">
              <span className="meta-pill highlight">
                <Clock size={13} />
                {storyboard.duration}s Target Duration
              </span>
              <span className="meta-pill">
                <Film size={13} />
                {storyboard.scenes?.length || 0} Scenes Planned
              </span>
              <span className="meta-pill">Language: {storyboard.language}</span>
              {storyboard.keywords?.map((tag) => (
                <span key={tag} className="meta-pill">
                  <Tag size={12} />
                  #{tag}
                </span>
              ))}
            </div>
          </div>

          {/* Opening Hook */}
          <div className="hook-box">
            <div className="hook-label">
              <Sparkles size={13} />
              Opening Hook (0–3s Retention Seizer)
            </div>
            {isEditing ? (
              <input
                id="edit-hook-input"
                type="text"
                className="input-edit"
                style={{ fontStyle: "italic", fontWeight: 600 }}
                value={storyboard.hook}
                onChange={(e) => updateField("hook", e.target.value)}
              />
            ) : (
              <div className="hook-text" id="hook-text">"{storyboard.hook}"</div>
            )}
          </div>

          {/* Script */}
          <div className="script-section">
            <div className="detail-label" style={{ marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <FileText size={13} />
              Full Narration Script
            </div>
            {isEditing ? (
              <textarea
                id="edit-script-input"
                className="textarea-edit"
                value={storyboard.script}
                onChange={(e) => updateField("script", e.target.value)}
              />
            ) : (
              <p className="script-text">{storyboard.script}</p>
            )}
          </div>

          {/* Scene Breakdown */}
          <div className="scenes-container">
            <div className="scenes-header">
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 700, fontSize: "1.1rem" }}>
                <Film size={18} color="var(--accent-primary)" />
                <span>Scene Breakdown (9:16 Vertical Storyboard)</span>
              </div>
              <span style={{ fontSize: "0.82rem", color: "var(--text-dim)" }}>
                {storyboard.scenes?.length} Scenes
              </span>
            </div>

            <div className="scenes-list">
              {storyboard.scenes?.map((scene, idx) => (
                <div key={scene.id} className="scene-card" id={`scene-${scene.id}`}>
                  <div className="scene-top-bar">
                    <div className="scene-badge">
                      <span>Scene {scene.id}</span>
                    </div>
                    {isEditing ? (
                      <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                        <span style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>Duration (s):</span>
                        <input
                          type="number"
                          min="1"
                          max="20"
                          style={{ width: "60px", padding: "0.2rem 0.5rem" }}
                          className="input-edit"
                          value={scene.duration}
                          onChange={(e) => updateScene(idx, "duration", e.target.value)}
                        />
                      </div>
                    ) : (
                      <span className="scene-timing">{getSceneTiming(storyboard.scenes, idx)}</span>
                    )}
                  </div>

                  <div className="scene-detail-row">
                    <div className="detail-label">Narration (Voiceover)</div>
                    {isEditing ? (
                      <textarea
                        className="textarea-edit"
                        value={scene.narration}
                        onChange={(e) => updateScene(idx, "narration", e.target.value)}
                      />
                    ) : (
                      <div className="detail-content">{scene.narration}</div>
                    )}
                  </div>

                  <div className="scene-detail-row">
                    <div className="detail-label">Visual Prompt (9:16 Aspect)</div>
                    {isEditing ? (
                      <textarea
                        className="textarea-edit"
                        value={scene.visual_prompt}
                        onChange={(e) => updateScene(idx, "visual_prompt", e.target.value)}
                      />
                    ) : (
                      <div className="visual-prompt-box">{scene.visual_prompt}</div>
                    )}
                  </div>

                  <div className="scene-detail-row">
                    <div className="detail-label">On-Screen Caption</div>
                    {isEditing ? (
                      <input
                        type="text"
                        className="input-edit"
                        value={scene.caption}
                        onChange={(e) => updateScene(idx, "caption", e.target.value)}
                      />
                    ) : (
                      <div className="caption-box">"{scene.caption}"</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Phase 3 Action Buttons */}
          <div className="storyboard-actions">
            <button
              id="edit-toggle-button"
              className="btn-secondary"
              type="button"
              onClick={() => setIsEditing(!isEditing)}
            >
              {isEditing ? (
                <>
                  <Check size={16} />
                  <span>Done Editing</span>
                </>
              ) : (
                <>
                  <Edit3 size={16} />
                  <span>Edit Story</span>
                </>
              )}
            </button>

            <button
              id="approve-story-button"
              className="btn-approve"
              type="button"
              disabled={approving}
              onClick={handleApprove}
            >
              {approving ? (
                <>
                  <div className="spinner" />
                  <span>Locking Story...</span>
                </>
              ) : isApproved ? (
                <>
                  <CheckCircle2 size={16} />
                  <span>Approved ✓</span>
                </>
              ) : (
                <>
                  <Lock size={16} />
                  <span>Approve Story</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* PHASE 4: Scene Generation (9:16 Visuals) */}
      {isApproved && (
        <div className="card" id="phase4-card">
          <div className="card-title">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Film size={20} color="var(--accent-primary)" />
              <span>Phase 4: Scene Visuals Generation (9:16 Vertical)</span>
            </div>
            <button
              id="generate-scenes-button"
              type="button"
              className="btn-primary"
              style={{ padding: "0.6rem 1.2rem", fontSize: "0.85rem" }}
              disabled={generatingScenes}
              onClick={handleGenerateScenes}
            >
              {generatingScenes ? (
                <>
                  <div className="spinner" />
                  <span>Rendering Scenes...</span>
                </>
              ) : (
                <>
                  <RefreshCw size={14} />
                  <span>{scenes.length > 0 ? "Regenerate Scenes" : "Generate 9:16 Scenes"}</span>
                </>
              )}
            </button>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", marginBottom: "1rem" }}>
            Each approved scene prompt is rendered into high-resolution 1080x1920 vertical format. If any individual scene requires modification, use the isolated retry button without re-rendering the rest of the pipeline.
          </p>

          {scenes.length > 0 && (
            <div className="scenes-visual-grid">
              {scenes.map((scene) => (
                <div key={scene.scene_id} className="scene-visual-card">
                  <div className="scene-img-wrapper">
                    <img
                      src={`${API_BASE}/generated/images/${scene.filename}?t=${Date.now()}`}
                      alt={`Scene ${scene.scene_id}`}
                      className="scene-img"
                    />
                    <div className="scene-img-overlay">
                      <span className="scene-timing" style={{ background: "rgba(0,0,0,0.7)" }}>
                        Scene {scene.scene_id} ({scene.duration}s)
                      </span>
                      <span className="meta-pill approved" style={{ fontSize: "0.68rem", padding: "0.2rem 0.5rem" }}>
                        ✓ {scene.provider || "9:16 AI"}
                      </span>
                    </div>
                  </div>

                  <div className="scene-card-body">
                    <div style={{ fontSize: "0.8rem", color: "#f1f5f9", fontWeight: 600 }}>
                      "{scene.caption}"
                    </div>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-dim)", lineHeight: 1.35 }}>
                      {scene.visual_prompt?.substring(0, 100)}...
                    </div>
                    <button
                      type="button"
                      className="scene-retry-btn"
                      disabled={retryingSceneId === scene.scene_id}
                      onClick={() => handleRetryScene(scene.scene_id)}
                    >
                      {retryingSceneId === scene.scene_id ? (
                        <>
                          <div className="spinner" />
                          <span>Retrying...</span>
                        </>
                      ) : (
                        <>
                          <RotateCcw size={12} />
                          <span>Retry Scene {scene.scene_id}</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* PHASE 5: Voice Generation */}
      {scenes.length > 0 && (
        <div className="card" id="phase5-card">
          <div className="card-title">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Volume2 size={20} color="var(--accent-primary)" />
              <span>Phase 5: Neural Voiceover (TTS)</span>
            </div>
            <button
              id="generate-voice-button"
              type="button"
              className="btn-primary"
              style={{ padding: "0.6rem 1.2rem", fontSize: "0.85rem" }}
              disabled={generatingVoice}
              onClick={handleGenerateVoice}
            >
              {generatingVoice ? (
                <>
                  <div className="spinner" />
                  <span>Synthesizing Voice...</span>
                </>
              ) : (
                <>
                  <Volume2 size={14} />
                  <span>{voiceData ? "Regenerate Voice" : "Generate Narration Audio"}</span>
                </>
              )}
            </button>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", marginBottom: "1rem" }}>
            Generates high-fidelity neural narration matching target pacing (~{storyboard?.duration || 35} seconds).
          </p>

          {voiceData && (
            <div className="audio-player-card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <CheckCircle2 size={18} color="#10b981" />
                  <span style={{ fontWeight: 700, fontSize: "0.95rem" }}>
                    Narration Ready ({voiceData.provider})
                  </span>
                </div>
                <span className="meta-pill highlight">
                  Voice: {voiceData.voice || "Neural"}
                </span>
              </div>

              <div className="audio-controls-row">
                <audio controls src={`${API_BASE}/generated/audio/narration.mp3?t=${Date.now()}`} />
                <span style={{ fontSize: "0.8rem", color: "var(--text-dim)" }}>
                  Size: {(voiceData.file_size / 1024).toFixed(1)} KB
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* PHASE 6: Captions Generation */}
      {voiceData && (
        <div className="card" id="phase6-card">
          <div className="card-title">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Subtitles size={20} color="var(--accent-primary)" />
              <span>Phase 6: Aligned Captions (SRT / WebVTT / ASS)</span>
            </div>
            <button
              id="generate-captions-button"
              type="button"
              className="btn-primary"
              style={{ padding: "0.6rem 1.2rem", fontSize: "0.85rem" }}
              disabled={generatingCaptions}
              onClick={handleGenerateCaptions}
            >
              {generatingCaptions ? (
                <>
                  <div className="spinner" />
                  <span>Aligning Captions...</span>
                </>
              ) : (
                <>
                  <Subtitles size={14} />
                  <span>{captionsData ? "Re-align Captions" : "Generate Captions"}</span>
                </>
              )}
            </button>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", marginBottom: "1rem" }}>
            Generates millisecond-accurate subtitle streams synchronized to the scene durations and narration.
          </p>

          {captionsData && (
            <div className="captions-timeline">
              {captionsData.cues?.map((cue) => (
                <div key={cue.index} className="caption-cue-item">
                  <span className="caption-time-badge">
                    {cue.start_formatted} → {cue.end_formatted}
                  </span>
                  <div className="caption-cue-text">"{cue.text}"</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* PHASE 7: FFmpeg Video Composition */}
      {captionsData && (
        <div className="card" id="phase7-card">
          <div className="card-title">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Video size={20} color="var(--accent-primary)" />
              <span>Phase 7: FFmpeg Video Composition (1080x1920 9:16)</span>
            </div>
            <button
              id="compose-video-button"
              type="button"
              className="btn-primary"
              style={{ padding: "0.6rem 1.2rem", fontSize: "0.85rem" }}
              disabled={composingVideo}
              onClick={handleComposeVideo}
            >
              {composingVideo ? (
                <>
                  <div className="spinner" />
                  <span>Composing MP4 Video...</span>
                </>
              ) : (
                <>
                  <Film size={14} />
                  <span>{videoData ? "Re-compose Video" : "Compose Final MP4"}</span>
                </>
              )}
            </button>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", marginBottom: "1rem" }}>
            Combines 9:16 vertical visuals, narration voiceover audio, and synchronized captions into a web-optimized vertical video container.
          </p>

          {videoData && (
            <div className="video-showcase-container">
              {/* Vertical Mobile Player */}
              <div className="vertical-video-frame">
                <video
                  ref={videoRef}
                  controls
                  playsInline
                  src={`${API_BASE}/generated/videos/final.mp4?t=${Date.now()}`}
                  poster={`${API_BASE}/generated/images/scene_1.jpg`}
                >
                  <track
                    src={`${API_BASE}/generated/captions/captions.vtt`}
                    kind="subtitles"
                    srcLang="en"
                    label="Captions"
                    default
                  />
                </video>
              </div>

              {/* Render Specifications */}
              <div className="video-meta-panel">
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                  <CheckCircle2 size={20} color="#10b981" />
                  <h3 style={{ fontSize: "1.2rem", fontWeight: 800 }}>Broadcast-Ready Vertical Video</h3>
                </div>

                <div className="video-specs-grid">
                  <div className="spec-tile">
                    <div className="spec-tile-label">Resolution</div>
                    <div className="spec-tile-value">{videoData.resolution} (9:16)</div>
                  </div>
                  <div className="spec-tile">
                    <div className="spec-tile-label">Codec & Stream</div>
                    <div className="spec-tile-value">H.264 / AAC FastStart</div>
                  </div>
                  <div className="spec-tile">
                    <div className="spec-tile-label">File Size</div>
                    <div className="spec-tile-value">{(videoData.file_size / (1024 * 1024)).toFixed(2)} MB</div>
                  </div>
                  <div className="spec-tile">
                    <div className="spec-tile-label">Render Time</div>
                    <div className="spec-tile-value">{videoData.render_time_sec || 3.8}s</div>
                  </div>
                </div>

                <div style={{ display: "flex", gap: "1rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
                  <button
                    type="button"
                    onClick={handleFullscreen}
                    className="btn-secondary"
                    style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}
                  >
                    <Maximize2 size={15} />
                    <span>Full Screen (9:16 Fit)</span>
                  </button>

                  <a
                    href={`${API_BASE}/generated/videos/final.mp4`}
                    download="qoneqt_final.mp4"
                    className="btn-secondary"
                    style={{ textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "0.5rem" }}
                  >
                    <Download size={15} />
                    <span>Download MP4</span>
                  </a>
                </div>
              </div>

            </div>
          )}
        </div>
      )}

      {/* PHASE 8: Quality Gate */}
      {videoData && (
        <div className="card" id="phase8-card">
          <div className="card-title">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <ShieldCheck size={20} color="var(--accent-primary)" />
              <span>Phase 8: Automated Pre-Flight Quality Gate</span>
            </div>
            <button
              id="quality-gate-button"
              type="button"
              className="btn-primary"
              style={{ padding: "0.6rem 1.2rem", fontSize: "0.85rem" }}
              disabled={checkingQuality}
              onClick={handleRunQualityGate}
            >
              {checkingQuality ? (
                <>
                  <div className="spinner" />
                  <span>Verifying Video...</span>
                </>
              ) : (
                <>
                  <ShieldCheck size={14} />
                  <span>Run Pre-Flight Checks</span>
                </>
              )}
            </button>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", marginBottom: "1rem" }}>
            Automated verification verifying file integrity, H.264 playability, target duration, 9:16 aspect ratio, audio stream, and caption alignment before unlocking Qoneqt Feed distribution.
          </p>

          {qualityReport && (
            <div className="quality-gate-container">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
                <div
                  className={`quality-status-badge ${qualityReport.passed ? "passed" : "failed"}`}
                  id="quality-gate-status"
                >
                  {qualityReport.passed ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                  <span>STATUS: {qualityReport.status}</span>
                </div>
                <span style={{ fontSize: "0.85rem", color: "var(--text-dim)" }}>
                  {qualityReport.passed_checks} / {qualityReport.total_checks} Automated Checks Passed
                </span>
              </div>

              <div className="quality-checks-grid">
                {qualityReport.checks?.map((chk) => (
                  <div key={chk.name} className={`quality-check-item ${chk.passed ? "passed" : ""}`}>
                    {chk.passed ? (
                      <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0, marginTop: "2px" }} />
                    ) : (
                      <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: "2px" }} />
                    )}
                    <div>
                      <div className="quality-check-title">{chk.name}</div>
                      <div className="quality-check-details">{chk.details}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* PHASE 9: Qoneqt Publishing */}
      {videoData && (
        <div className="card" id="phase9-card">
          <div className="card-title">
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Globe size={20} color="var(--accent-primary)" />
              <span>Phase 9: Qoneqt Global Feed Distribution</span>
            </div>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", marginBottom: "1.25rem" }}>
            The publish button is strictly gated by the Phase 8 Quality Gate. Clicking publishes the sealed video package to the Qoneqt Global Feed with full cryptographic receipt and signed metadata.
          </p>

          <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
            <button
              id="publish-button"
              type="button"
              className="btn-publish"
              disabled={!qualityReport?.passed || publishing}
              onClick={handlePublish}
            >
              {publishing ? (
                <>
                  <div className="spinner" />
                  <span>Publishing to Qoneqt...</span>
                </>
              ) : publishReceipt ? (
                <>
                  <CheckCircle2 size={18} />
                  <span>Published to Global Feed ✓</span>
                </>
              ) : (
                <>
                  <Send size={18} />
                  <span>Publish to Qoneqt Global Feed</span>
                </>
              )}
            </button>

            {!qualityReport?.passed && (
              <span style={{ fontSize: "0.82rem", color: "var(--warning)", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Lock size={14} /> Locked until Quality Gate passes
              </span>
            )}
          </div>

          {publishReceipt && (
            <div style={{ marginTop: "1.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem", color: "#34d399", fontWeight: 700 }}>
                <CheckCircle2 size={18} />
                <span>OFFICIAL QONEQT GLOBAL FEED DELIVERY RECEIPT</span>
              </div>
              <pre className="publish-manifest-box">
                {JSON.stringify(publishReceipt, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
