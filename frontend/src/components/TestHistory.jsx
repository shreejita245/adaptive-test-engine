import { useState, useEffect } from "react"
import axios from "axios"
import MathRenderer from "./MathRenderer"
import { API } from "../api"

function formatDate(iso) {
  if (!iso) return ""
  const d = new Date(iso)
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) +
    " · " + d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })
}

function ScoreBadge({ score, maxScore }) {
  const pct = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0
  const color = pct >= 75 ? "#22c55e" : pct >= 50 ? "#f97316" : "#ef4444"
  return (
    <div style={{ textAlign: "right" }}>
      <div style={{ fontSize: 20, fontWeight: 800, color }}>{score}</div>
      <div style={{ fontSize: 11, color: "#9ca3af" }}>/ {maxScore}</div>
    </div>
  )
}

export default function TestHistory({ student, onBack, onStartNew }) {
  const [sessions, setSessions] = useState(null)
  const [expanded, setExpanded] = useState(null)
  const [expandedQuestion, setExpandedQuestion] = useState(null)
  const [filterExam, setFilterExam] = useState("all")

  useEffect(() => {
    axios.get(`${API}/sessions/${student.id}`).then(r => setSessions(r.data))
  }, [])

  const examNames = sessions ? [...new Set(sessions.map(s => s.exam_name))] : []
  const filtered = sessions
    ? sessions.filter(s => filterExam === "all" || s.exam_name === filterExam)
    : []

  function toggleExpand(id) {
    setExpanded(e => e === id ? null : id)
    setExpandedQuestion(null)
  }

  return (
    <div className="history-page">
      {/* Header */}
      <div className="history-header">
        <div>
          <h2 style={{ color: "#fff", margin: 0, fontSize: 22, fontWeight: 800 }}>
            📂 Test History
          </h2>
          <p style={{ color: "#a5b4fc", fontSize: 14, margin: "4px 0 0" }}>
            {student.name} · All past tests
          </p>
        </div>
        <button className="history-back-btn" onClick={onBack}>← Back</button>
      </div>

      {/* Filter */}
      {examNames.length > 1 && (
        <div className="history-filters">
          {["all", ...examNames].map(name => (
            <button
              key={name}
              onClick={() => setFilterExam(name)}
              className={`history-filter-btn ${filterExam === name ? "history-filter-active" : ""}`}
            >
              {name === "all" ? `All Tests (${sessions.length})` : name}
            </button>
          ))}
        </div>
      )}

      {/* List */}
      {!sessions ? (
        <div className="history-loading">
          <div className="lb-spinner" />
          <p>Loading your tests...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="history-empty">
          <div style={{ fontSize: 56, marginBottom: 16 }}>📋</div>
          <h3 style={{ color: "#1f2937", marginBottom: 8 }}>No tests yet</h3>
          <p style={{ color: "#9ca3af", marginBottom: 24 }}>Complete a test to see it here.</p>
          <button className="score-btn-retry" onClick={onStartNew}>Start a Test →</button>
        </div>
      ) : (
        <div className="history-list">
          {filtered.map(session => {
            const isOpen = expanded === session.id
            const pct = session.max_score > 0 ? Math.round((session.score / session.max_score) * 100) : 0
            const gradeColor = pct >= 75 ? "#22c55e" : pct >= 50 ? "#f97316" : "#ef4444"

            return (
              <div key={session.id} className="history-card">
                {/* Card header — always visible */}
                <div className="history-card-top" onClick={() => toggleExpand(session.id)}>
                  {/* Left: exam info */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6, flexWrap: "wrap" }}>
                      <span className="history-exam-tag">{session.exam_name}</span>
                      <span className="history-mode-tag">
                        {session.mode === "full" ? "Full Test" : session.mode === "subject" ? session.subject : session.topic}
                      </span>
                    </div>
                    <div style={{ fontSize: 12, color: "#9ca3af" }}>{formatDate(session.completed_at)}</div>
                    {/* Mini stat row */}
                    <div className="history-mini-stats">
                      <span style={{ color: "#22c55e" }}>✅ {session.correct}</span>
                      <span style={{ color: "#ef4444" }}>❌ {session.wrong}</span>
                      <span style={{ color: "#9ca3af" }}>⏭ {session.unattempted}</span>
                      <span style={{ color: "#6366f1" }}>🎯 {session.accuracy}%</span>
                      <span style={{ color: "#6b7280" }}>⏱ {session.duration_mins}m</span>
                    </div>
                  </div>

                  {/* Right: score + chevron */}
                  <div style={{ display: "flex", alignItems: "center", gap: 12, flexShrink: 0 }}>
                    <ScoreBadge score={session.score} maxScore={session.max_score} />
                    {/* Progress arc */}
                    <div className="history-pct-ring" style={{ "--pct-color": gradeColor }}>
                      <svg viewBox="0 0 36 36" width="48" height="48">
                        <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f3f4f6" strokeWidth="3" />
                        <circle cx="18" cy="18" r="15.9" fill="none" stroke={gradeColor} strokeWidth="3"
                          strokeDasharray={`${pct} ${100 - pct}`}
                          strokeDashoffset="25"
                          strokeLinecap="round"
                          style={{ transition: "stroke-dasharray 0.5s ease" }}
                        />
                      </svg>
                      <div className="history-pct-label" style={{ color: gradeColor }}>{pct}%</div>
                    </div>
                    <div className={`history-chevron ${isOpen ? "history-chevron-open" : ""}`}>▾</div>
                  </div>
                </div>

                {/* Expanded question list */}
                {isOpen && (
                  <div className="history-questions">
                    <div className="history-questions-header">
                      Questions ({session.questions.length})
                    </div>
                    {session.questions.map((q, qi) => {
                      const isQOpen = expandedQuestion === `${session.id}-${qi}`
                      const statusColor = q.is_correct === null ? "#9ca3af"
                        : q.is_correct ? "#22c55e" : "#ef4444"
                      const statusIcon = q.is_correct === null ? "⏭" : q.is_correct ? "✅" : "❌"

                      return (
                        <div key={qi} className="history-question-item">
                          <div
                            className="history-question-row"
                            onClick={() => setExpandedQuestion(isQOpen ? null : `${session.id}-${qi}`)}
                          >
                            <span className="history-q-num" style={{ background: statusColor + "22", color: statusColor }}>
                              {statusIcon} Q{qi + 1}
                            </span>
                            <div className="history-q-text">
                              <MathRenderer
                                html={q.question_text}
                                style={{ fontSize: 13, color: "#374151", lineHeight: 1.5 }}
                              />
                            </div>
                            <span style={{ color: "#9ca3af", fontSize: 16, flexShrink: 0 }}>
                              {isQOpen ? "▴" : "▾"}
                            </span>
                          </div>

                          {isQOpen && (
                            <div className="history-question-detail">
                              {/* Options */}
                              <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 12 }}>
                                {q.options && Object.entries(q.options).map(([key, val]) => {
                                  const isCorrect = key === q.correct_answer
                                  const isSelected = key === q.selected_answer
                                  const isWrong = isSelected && !isCorrect
                                  return (
                                    <div key={key} style={{
                                      display: "flex", gap: 10, alignItems: "flex-start",
                                      padding: "8px 12px", borderRadius: 8, fontSize: 13,
                                      background: isCorrect ? "#f0fdf4" : isWrong ? "#fef2f2" : "#f9fafb",
                                      border: `1.5px solid ${isCorrect ? "#86efac" : isWrong ? "#fca5a5" : "#e5e7eb"}`,
                                      color: isCorrect ? "#15803d" : isWrong ? "#b91c1c" : "#374151"
                                    }}>
                                      <span style={{ fontWeight: 700, flexShrink: 0 }}>{key}.</span>
                                      <MathRenderer html={val} style={{ flex: 1, display: "inline" }} />
                                      {isCorrect && <span style={{ fontSize: 11, color: "#15803d", fontWeight: 700, flexShrink: 0 }}>✓ Correct</span>}
                                      {isWrong && <span style={{ fontSize: 11, color: "#b91c1c", fontWeight: 700, flexShrink: 0 }}>✗ Your Answer</span>}
                                    </div>
                                  )
                                })}
                              </div>
                              {/* Explanation */}
                              {q.explanation && (
                                <div style={{
                                  background: "linear-gradient(135deg, #f5f3ff, #ede9fe)",
                                  borderLeft: "3px solid #6366f1",
                                  borderRadius: 8, padding: 12
                                }}>
                                  <div style={{ fontWeight: 700, color: "#4338ca", fontSize: 12, marginBottom: 6 }}>
                                    💡 Explanation
                                  </div>
                                  <MathRenderer html={q.explanation} style={{ fontSize: 13, color: "#374151", lineHeight: 1.7 }} />
                                </div>
                              )}
                              <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 8 }}>
                                Topic: {q.topic} · Difficulty: {q.difficulty ? Math.round(q.difficulty * 100) + "%" : "—"}
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
