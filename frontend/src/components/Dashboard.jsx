import { useState, useEffect } from "react"
import axios from "axios"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { API } from "../api"

export default function Dashboard({ student, scoreData, onRetry, onViewExplanations, onViewHistory }) {
  const [data, setData] = useState(null)
  const [progress, setProgress] = useState([])
  const [tab, setTab] = useState("score")

  useEffect(() => {
    axios.get(`${API}/analytics/${student.id}`).then(r => setData(r.data))
    axios.get(`${API}/analytics/progress/${student.id}`).then(r => setProgress(r.data))
  }, [])

  const { score, correct, wrong, unattempted, maxScore, questionsData } = scoreData || {}
  const total = (correct || 0) + (wrong || 0) + (unattempted || 0)
  const accuracy = total > 0 ? Math.round((correct / total) * 100) : 0
  const percentage = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0

  const grade = percentage >= 85 ? { label: "Excellent!", color: "#22c55e", emoji: "🏆" }
    : percentage >= 65 ? { label: "Good job!", color: "#f97316", emoji: "🎯" }
    : percentage >= 40 ? { label: "Keep going!", color: "#6366f1", emoji: "💪" }
    : { label: "Need practice", color: "#ef4444", emoji: "📚" }

  return (
    <div className="dashboard-wrapper">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h2 style={{ color: "#fff", margin: 0, fontSize: 22, fontWeight: 800 }}>
            {grade.emoji} Test Complete!
          </h2>
          <p style={{ color: "#a5b4fc", fontSize: 14, margin: "4px 0 0" }}>
            {student.name} · {scoreData?.examName || "Practice Test"}
          </p>
        </div>
        <span className="dashboard-grade-tag" style={{ background: grade.color }}>
          {grade.label}
        </span>
      </div>

      {/* Tab bar */}
      <div className="dashboard-tabs">
        {[
          { key: "score", label: "📊 Score" },
          { key: "overview", label: "📈 Analytics" },
          { key: "progress", label: "📉 Progress" }
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`dashboard-tab ${tab === t.key ? "dashboard-tab-active" : ""}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="dashboard-body">
        {/* ── SCORE TAB ── */}
        {tab === "score" && (
          <div>
            {/* Big score circle */}
            <div className="score-circle-wrap">
              <div className="score-circle" style={{ borderColor: grade.color }}>
                <div className="score-circle-num" style={{ color: grade.color }}>{score}</div>
                <div className="score-circle-denom">/ {maxScore}</div>
                <div className="score-circle-pct" style={{ color: grade.color }}>{percentage}%</div>
              </div>
            </div>

            {/* Stats row */}
            <div className="score-stats">
              {[
                { label: "Correct", val: correct, color: "#22c55e", bg: "#f0fdf4", icon: "✅" },
                { label: "Wrong", val: wrong, color: "#ef4444", bg: "#fef2f2", icon: "❌" },
                { label: "Skipped", val: unattempted, color: "#6b7280", bg: "#f9fafb", icon: "⏭" },
                { label: "Accuracy", val: `${accuracy}%`, color: "#6366f1", bg: "#ede9fe", icon: "🎯" }
              ].map(s => (
                <div key={s.label} className="score-stat-card" style={{ background: s.bg }}>
                  <div style={{ fontSize: 18, marginBottom: 4 }}>{s.icon}</div>
                  <div style={{ fontSize: 22, fontWeight: 800, color: s.color }}>{s.val}</div>
                  <div style={{ fontSize: 12, color: "#6b7280" }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Marking scheme note */}
            <div className="score-marking-note">
              <span>+4 per correct</span>
              <span>·</span>
              <span style={{ color: "#ef4444" }}>
                -{scoreData?.negativeMarks || 1} per wrong
              </span>
              <span>·</span>
              <span>0 for skipped</span>
            </div>

            {/* Action buttons */}
            <div className="score-actions">
              <button className="score-btn-explain" onClick={onViewExplanations}>
                📝 View Explanations
              </button>
              <button className="score-btn-history" onClick={onViewHistory}>
                📂 Test History
              </button>
              <button className="score-btn-retry" onClick={onRetry}>
                🔄 Practice Again
              </button>
            </div>
          </div>
        )}

        {/* ── ANALYTICS TAB ── */}
        {tab === "overview" && (
          <>
            {!data ? (
              <div style={{ textAlign: "center", padding: 40, color: "#9ca3af" }}>Loading analytics...</div>
            ) : (
              <>
                <div className="analytics-cards">
                  <div className="analytics-card" style={{ background: "#f5f3ff" }}>
                    <div style={{ fontSize: 28, fontWeight: 800, color: "#6366f1" }}>{data.overall_accuracy}%</div>
                    <div style={{ fontSize: 13, color: "#888", marginTop: 4 }}>Overall Accuracy</div>
                  </div>
                  <div className="analytics-card" style={{ background: "#f0fdf4" }}>
                    <div style={{ fontSize: 28, fontWeight: 800, color: "#22c55e" }}>{data.total_attempts}</div>
                    <div style={{ fontSize: 13, color: "#888", marginTop: 4 }}>Total Questions</div>
                  </div>
                  <div className="analytics-card" style={{ background: "#fff7ed" }}>
                    <div style={{ fontSize: 28, fontWeight: 800, color: "#f97316" }}>{data.avg_time_per_question}s</div>
                    <div style={{ fontSize: 13, color: "#888", marginTop: 4 }}>Avg Time/Q</div>
                  </div>
                </div>

                <h3 style={{ marginBottom: 16, marginTop: 4 }}>Topic Breakdown</h3>
                {data.topic_breakdown.map(t => (
                  <div key={t.topic} style={{ marginBottom: 16 }}>
                    <div className="row">
                      <span style={{ fontWeight: 500, fontSize: 14 }}>{t.topic}</span>
                      <span className={`badge ${t.mastered ? "badge-strong" : "badge-weak"}`}>
                        {t.mastered ? "Mastered" : "Needs work"}
                      </span>
                    </div>
                    <div className="skill-bar-bg">
                      <div className="skill-bar" style={{ width: `${t.skill_level * 100}%` }} />
                    </div>
                    <div style={{ fontSize: 12, color: "#888", marginTop: 4 }}>
                      {Math.round(t.skill_level * 100)}% skill · {t.accuracy}% accuracy
                    </div>
                  </div>
                ))}

                {data.weak_topics.length > 0 && (
                  <div style={{ marginTop: 12, padding: 16, background: "#fef2f2", borderRadius: 12 }}>
                    <strong>Focus on: </strong>{data.weak_topics.map(t => t.topic).join(", ")}
                  </div>
                )}
              </>
            )}
            <div style={{ marginTop: 20, display: "flex", gap: 10 }}>
              <button className="score-btn-explain" onClick={onViewExplanations}>📝 Explanations</button>
              <button className="score-btn-retry" onClick={onRetry}>🔄 Practice Again</button>
            </div>
          </>
        )}

        {/* ── PROGRESS TAB ── */}
        {tab === "progress" && (
          <>
            <h3>Accuracy Over Time</h3>
            {progress.length < 2
              ? <p style={{ color: "#888", marginBottom: 20 }}>Answer more questions to see your chart.</p>
              : (
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={progress}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="attempt_number" />
                    <YAxis domain={[0, 100]} unit="%" />
                    <Tooltip formatter={(v) => `${v}%`} />
                    <Line type="monotone" dataKey="running_accuracy"
                      stroke="#6366f1" strokeWidth={2.5} dot={{ r: 3 }} name="Accuracy" />
                  </LineChart>
                </ResponsiveContainer>
              )}

            <h3 style={{ marginTop: 24, marginBottom: 12 }}>Recent Attempts</h3>
            <div style={{ maxHeight: 240, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
              {progress.slice(-20).reverse().map((p, i) => (
                <div key={i} style={{
                  display: "flex", justifyContent: "space-between",
                  padding: "10px 14px", borderRadius: 10,
                  background: p.is_correct ? "#f0fdf4" : "#fef2f2",
                  border: `1.5px solid ${p.is_correct ? "#bbf7d0" : "#fecaca"}`
                }}>
                  <span style={{ fontSize: 14 }}>{p.is_correct ? "✅" : "❌"} Q{p.attempt_number} · {p.topic}</span>
                  <span style={{ fontSize: 13, color: "#888" }}>{p.time_taken}s</span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 20, display: "flex", gap: 10 }}>
              <button className="score-btn-history" onClick={onViewHistory}>📂 Test History</button>
              <button className="score-btn-retry" onClick={onRetry}>🔄 Practice Again</button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}