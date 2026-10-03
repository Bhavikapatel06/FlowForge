"use client";

import { useState, useEffect } from "react";
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
} from "lucide-react";

export default function Home() {
  const [topic, setTopic] = useState("AI in student life");
  const [style, setStyle] = useState("Educational");
  const [language, setLanguage] = useState("English");

  const [loading, setLoading] = useState(false);
  const [approving, setApproving] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [error, setError] = useState(null);
  
  // Storyboard state
  const [storyboard, setStoryboard] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isApproved, setIsApproved] = useState(false);
  const [approvalInfo, setApprovalInfo] = useState(null);

  // Progressive feedback simulation while generating
  const progressSteps = [
    "Understanding topic & research context",
    "Creating high-retention opening hook",
    "Writing full narrative script",
    "Planning 9:16 vertical scenes & visual prompts",
  ];

  useEffect(() => {
    let interval;
    if (loading) {
      setProgressStep(0);
      interval = setInterval(() => {
        setProgressStep((prev) => (prev < progressSteps.length - 1 ? prev + 1 : prev));
      }, 700);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    setError(null);
    setStoryboard(null);
    setIsApproved(false);
    setApprovalInfo(null);
    setIsEditing(false);

    try {
      const res = await fetch("http://localhost:8000/api/storyboard", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          style,
          language,
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
      setStoryboard(data);
    } catch (err) {
      console.error("API error:", err);
      setError(err.message || "Failed to connect to FastAPI backend");
    } finally {
      setLoading(false);
    }
  };

  // Phase 3: Approve Storyboard
  const handleApprove = async () => {
    if (!storyboard) return;
    setApproving(true);
    setError(null);

    try {
      const res = await fetch("http://localhost:8000/api/storyboard/approve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(storyboard),
      });

      if (!res.ok) {
        throw new Error(`Approval failed with HTTP ${res.status}`);
      }

      const data = await res.json();
      setIsApproved(true);
      setApprovalInfo(data);
      setIsEditing(false);
    } catch (err) {
      console.error("Approval error:", err);
      setError(err.message || "Failed to approve storyboard");
    } finally {
      setApproving(false);
    }
  };

  // Updaters for human review editing
  const updateField = (field, value) => {
    setStoryboard((prev) => ({
      ...prev,
      [field]: value,
    }));
    setIsApproved(false); // require re-approval if modified
  };

  const updateScene = (sceneIndex, field, value) => {
    setStoryboard((prev) => {
      const newScenes = [...prev.scenes];
      newScenes[sceneIndex] = {
        ...newScenes[sceneIndex],
        [field]: field === "duration" ? parseInt(value, 10) || 1 : value,
      };
      
      // Recalculate total duration if scene duration changed
      const totalDuration = newScenes.reduce((acc, s) => acc + s.duration, 0);
      return {
        ...prev,
        duration: totalDuration,
        scenes: newScenes,
      };
    });
    setIsApproved(false);
  };

  const getSceneTiming = (scenes, targetIndex) => {
    let start = 0;
    for (let i = 0; i < targetIndex; i++) {
      start += scenes[i].duration;
    }
    const end = start + scenes[targetIndex].duration;
    return `${start}s – ${end}s (${scenes[targetIndex].duration}s)`;
  };

  return (
    <main className="container">
      {/* Header */}
      <div className="header">
        <div className="badge">
          <Sparkles size={14} />
          Qoneqt × CTRL FREAK 2026
        </div>
        <h1 className="title">Qoneqt AI Content Engine</h1>
        <p className="subtitle">
          Transform raw ideas into broadcast-ready vertical videos for the Qoneqt Global Feed.
        </p>
      </div>

      {/* Pipeline Navigation / Progress */}
      <div className="pipeline-steps">
        <div className="step-chip done">
          <CheckCircle2 size={13} />
          Phase 1: Foundation
        </div>
        <div className={`step-chip ${storyboard ? "done" : "active"}`}>
          {storyboard ? <CheckCircle2 size={13} /> : <span>2</span>}
          Phase 2: Storyboard
        </div>
        <div className={`step-chip ${isApproved ? "done" : storyboard ? "active" : ""}`}>
          {isApproved ? <CheckCircle2 size={13} /> : <span>3</span>}
          Phase 3: Human Review
        </div>
        <div className={`step-chip ${isApproved ? "active" : ""}`}>
          <span>4</span> Scenes
        </div>
        <div className="step-chip">
          <span>5</span> Voice & Captions
        </div>
        <div className="step-chip">
          <span>6</span> Composition
        </div>
        <div className="step-chip">
          <span>7</span> Quality Gate
        </div>
        <div className="step-chip">
          <span>8</span> Publish
        </div>
      </div>

      {/* Generator Input Form */}
      <div className="card">
        <div className="card-title">
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <Sparkles size={20} color="var(--accent-primary)" />
            <span>AI Storyboard Generation</span>
          </div>
          {isApproved && (
            <span className="meta-pill approved">
              <Lock size={12} /> Approved & Locked
            </span>
          )}
        </div>

        <form onSubmit={handleGenerate}>
          <div className="form-group">
            <label className="label" htmlFor="topic-input">Enter your topic</label>
            <input
              id="topic-input"
              type="text"
              className="input"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. AI in student life, Future of Quantum Computing..."
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
                <option value="Educational">Educational</option>
                <option value="Entertaining">Entertaining</option>
                <option value="Inspirational">Inspirational</option>
                <option value="News & Trends">News & Trends</option>
              </select>
            </div>

            <div className="form-group">
              <label className="label" htmlFor="language-select">Language</label>
              <select
                id="language-select"
                className="select"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="English">English</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="German">German</option>
                <option value="Hindi">Hindi</option>
              </select>
            </div>
          </div>

          <button
            id="generate-button"
            type="submit"
            className="btn-primary"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="spinner" />
                <span>Generating AI Storyboard...</span>
              </>
            ) : (
              <>
                <span>Generate Storyboard</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        {/* Live Pipeline Step Progress */}
        {loading && (
          <div className="progress-box">
            <div className="progress-title">
              <div className="spinner" />
              <span>Generating story & scene plans...</span>
            </div>
            <div className="progress-steps-list">
              {progressSteps.map((step, idx) => {
                const isDone = idx < progressStep;
                const isCurrent = idx === progressStep;
                return (
                  <div
                    key={step}
                    className={`progress-step-item ${isDone ? "completed" : ""} ${
                      isCurrent ? "active" : ""
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 size={16} color="var(--success)" />
                    ) : isCurrent ? (
                      <RefreshCw size={16} className="spinner" />
                    ) : (
                      <div
                        style={{
                          width: 14,
                          height: 14,
                          borderRadius: "50%",
                          border: "2px solid rgba(255,255,255,0.2)",
                        }}
                      />
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

      {/* Rendered Storyboard Output (Phase 2 & Phase 3) */}
      {storyboard && (
        <div className="card" id="storyboard-card">
          {/* Phase 3 Approval Banner */}
          {isApproved && (
            <div className="approved-banner" id="approval-banner">
              <div className="approved-banner-text">
                <CheckCircle2 size={24} color="#10b981" />
                <div>
                  <div className="approved-banner-title">
                    STORYBOARD APPROVED & LOCKED FOR PRODUCTION
                  </div>
                  <div className="approved-banner-sub">
                    {approvalInfo?.message || "Human review complete. Ready for Phase 4 Scene Generation."}
                  </div>
                </div>
              </div>
              <div className="meta-pill approved" style={{ background: "rgba(16, 185, 129, 0.25)" }}>
                <Lock size={12} /> State Preserved
              </div>
            </div>
          )}

          {/* Storyboard Header */}
          <div className="storyboard-header">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
              {isEditing ? (
                <div style={{ width: "100%", marginRight: "1rem" }}>
                  <label className="detail-label">Title (Editable)</label>
                  <input
                    id="edit-title-input"
                    type="text"
                    className="input-edit"
                    style={{ fontSize: "1.4rem", fontWeight: 800 }}
                    value={storyboard.title}
                    onChange={(e) => updateField("title", e.target.value)}
                  />
                </div>
              ) : (
                <h2 className="storyboard-title" id="storyboard-title">{storyboard.title}</h2>
              )}
            </div>

            <div className="metadata-tags">
              <span className="meta-pill highlight">
                <Clock size={13} />
                {storyboard.duration}s Target Duration
              </span>
              <span className="meta-pill">
                <Film size={13} />
                {storyboard.scenes?.length || 0} Scenes Planned
              </span>
              <span className="meta-pill">
                Language: {storyboard.language}
              </span>
              {storyboard.keywords?.map((tag) => (
                <span key={tag} className="meta-pill">
                  <Tag size={12} />
                  #{tag}
                </span>
              ))}
            </div>
          </div>

          {/* Hook Box */}
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

          {/* Script Section */}
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

          {/* Scene by Scene Structure */}
          <div className="scenes-container">
            <div className="scenes-header">
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 700, fontSize: "1.1rem" }}>
                <Film size={18} color="var(--accent-primary)" />
                <span>Scene Breakdown (9:16 Vertical Assets)</span>
              </div>
              <span style={{ fontSize: "0.82rem", color: "var(--text-dim)" }}>
                {storyboard.scenes?.length} Total Scenes
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
                      <span className="scene-timing">
                        {getSceneTiming(storyboard.scenes, idx)}
                      </span>
                    )}
                  </div>

                  {/* Narration */}
                  <div className="scene-detail-row">
                    <div className="detail-label">Narration (Spoken Voiceover)</div>
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

                  {/* Visual Prompt */}
                  <div className="scene-detail-row">
                    <div className="detail-label">Visual Prompt (9:16 Composition)</div>
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

                  {/* On-Screen Caption */}
                  <div className="scene-detail-row">
                    <div className="detail-label">On-Screen Caption</div>
                    {isEditing ? (
                      <input
                        id={`edit-caption-input-${scene.id}`}
                        type="text"
                        className="input-edit"
                        value={scene.caption}
                        onChange={(e) => updateScene(idx, "caption", e.target.value)}
                      />
                    ) : (
                      <div className="caption-box" id={`caption-box-${scene.id}`}>
                        "{scene.caption}"
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Footer for Phase 3 Human Review */}
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
    </main>
  );
}
