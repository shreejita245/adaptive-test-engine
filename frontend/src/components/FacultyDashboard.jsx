import { useState, useEffect } from "react"
import axios from "axios"
import { API } from "../api"

// Risk is always shown with both a color AND a text label/icon — never
// color alone — per the existing app's badge pattern (badge-weak/badge-strong)
// and standard accessibility practice for status colors.
const RISK_STYLE = {
  High:   { color: "#ef4444", bg: "#fef2f2", border: "#fecaca", icon: "🔴" },
  Medium: { color: "#f97316", bg: "#fff7ed", border: "#fed7aa", icon: "🟠" },
  Low:    { color: "#22c55e", bg: "#f0fdf4", border: "#bbf7d0", icon: "🟢" },
}

function RiskPill({ level }) {
  const s = RISK_STYLE[level] || RISK_STYLE.Medium
  return (
    <span
      style={{
        display: "inline-flex", alignItems: "center", gap: 4,
        fontSize: 12, fontWeight: 700, padding: "3px 10px", borderRadius: 999,
        color: s.color, background: s.bg, border: `1.5px solid ${s.border}`,
      }}
    >
      {s.icon} {level}
    </span>
  )
}

function PipelineNotRunState({ what }) {
  return (
    <div style={{
      textAlign: "center", padding: "48px 20px", color: "#6b7280",
      background: "#f9fafb", borderRadius: 14, border: "1.5px dashed #e5e7eb",
    }}>
      <div style={{ fontSize: 32, marginBottom: 10 }}>⚙️</div>
      <div style={{ fontWeight: 700, color: "#374151", marginBottom: 6 }}>
        No {what} yet
      </div>
      <div style={{ fontSize: 13, maxWidth: 420, margin: "0 auto" }}>
        Run the analytics pipeline first: <code>build_features.py</code> →{" "}
        <code>train_models.py</code> → <code>shap_analysis.py</code> →{" "}
        <code>anomaly_detection.py</code> → <code>aggregate_insights.py</code>,
        then reload this page.
      </div>
    </div>
  )
}

function StudentCard({ s, expanded, onToggle }) {
  return (
    <div
      className="card"
      style={{ marginBottom: 12, cursor: "pointer", padding: 16 }}
      onClick={onToggle}
    >
      <div className="row">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ fontWeight: 700, fontSize: 15 }}>Student #{s.student_id}</div>
          <RiskPill level={s.risk_level} />
        </div>
        <div style={{ fontSize: 13, color: "#6b7280" }}>
          {expanded ? "▲ hide" : "▼ details"}
        </div>
      </div>

      <div style={{ display: "flex", gap: 20, marginTop: 10, fontSize: 13, color: "#6b7280", flexWrap: "wrap" }}>
        <span>📊 {(s.overall_accuracy * 100).toFixed(0)}% accuracy</span>
        <span>⚠️ {(s.avg_predicted_risk * 100).toFixed(0)}% avg risk</span>
        <span>🧮 {s.total_attempts} attempts</span>
        {s.anomaly_count > 0 && (
          <span style={{ color: "#a855f7", fontWeight: 600 }}>
            🔍 {s.anomaly_count} anomal{s.anomaly_count === 1 ? "y" : "ies"}
          </span>
        )}
      </div>

      {expanded && (
        <div style={{ marginTop: 16, borderTop: "1px solid #f3f4f6", paddingTop: 14 }}>
          {s.top_risk_topics?.length > 0 && (
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#374151", marginBottom: 6 }}>
                WEAKEST TOPICS
              </div>
              {s.top_risk_topics.map((t, i) => (
                <div key={i} className="row" style={{ fontSize: 13, padding: "4px 0" }}>
                  <span>{t.topic}</span>
                  <span style={{ color: "#6b7280" }}>
                    {(t.accuracy * 100).toFixed(0)}% acc · {(t.avg_risk * 100).toFixed(0)}% risk
                  </span>
                </div>
              ))}
            </div>
          )}

          {s.top_mistake_drivers?.length > 0 && (
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#374151", marginBottom: 6 }}>
                WHY (SHAP — most common factor behind wrong answers)
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {s.top_mistake_drivers.map((d, i) => (
                  <span key={i} style={{
                    fontSize: 12, padding: "4px 10px", borderRadius: 8,
                    background: "#ede9fe", color: "#5b21b6", fontWeight: 600,
                  }}>
                    {d.feature.replaceAll("_", " ")} ({d.count}×)
                  </span>
                ))}
              </div>
            </div>
          )}

          {s.anomaly_flags?.length > 0 && (
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#374151", marginBottom: 6 }}>
                ANOMALY FLAGS
              </div>
              {s.anomaly_flags.map((a, i) => (
                <div key={i} style={{
                  fontSize: 12, color: "#7c2d12", background: "#fff7ed",
                  border: "1px solid #fed7aa", borderRadius: 8,
                  padding: "6px 10px", marginBottom: 6,
                }}>
                  {a.topic} (attempt #{a.attempt_number}) — {a.anomaly_reason}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function TopicHeatmap({ topics, view, setView }) {
  return (
    <>
      <div className="row" style={{ marginBottom: 12 }}>
        <div style={{ display: "flex", gap: 14, fontSize: 12, color: "#6b7280" }}>
          {Object.entries(RISK_STYLE).map(([level, s]) => (
            <span key={level}>{s.icon} {level} risk</span>
          ))}
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          <button
            className={`topbar-nav-btn ${view === "grid" ? "topbar-nav-active" : ""}`}
            onClick={() => setView("grid")}
          >Grid</button>
          <button
            className={`topbar-nav-btn ${view === "table" ? "topbar-nav-active" : ""}`}
            onClick={() => setView("table")}
          >Table</button>
        </div>
      </div>

      {view === "grid" ? (
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: 10,
        }}>
          {topics.map((t) => {
            const s = RISK_STYLE[t.risk_level] || RISK_STYLE.Medium
            return (
              <div key={t.topic} style={{
                background: s.bg, border: `1.5px solid ${s.border}`, borderRadius: 12,
                padding: 12,
              }}>
                <div style={{ fontWeight: 700, fontSize: 13, color: "#1f2937", marginBottom: 6 }}>
                  {t.topic}
                </div>
                <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 4 }}>{t.subject}</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: s.color }}>
                  {(t.accuracy * 100).toFixed(0)}%
                </div>
                <div style={{ fontSize: 11, color: "#6b7280" }}>
                  {t.n_students} student{t.n_students === 1 ? "" : "s"} · {t.n_attempts} attempts
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "2px solid #f3f4f6", color: "#6b7280" }}>
                <th style={{ padding: "8px 6px" }}>Topic</th>
                <th style={{ padding: "8px 6px" }}>Subject</th>
                <th style={{ padding: "8px 6px" }}>Accuracy</th>
                <th style={{ padding: "8px 6px" }}>Avg risk</th>
                <th style={{ padding: "8px 6px" }}>Students</th>
                <th style={{ padding: "8px 6px" }}>Risk</th>
              </tr>
            </thead>
            <tbody>
              {topics.map((t) => (
                <tr key={t.topic} style={{ borderBottom: "1px solid #f9fafb" }}>
                  <td style={{ padding: "8px 6px", fontWeight: 600 }}>{t.topic}</td>
                  <td style={{ padding: "8px 6px", color: "#6b7280" }}>{t.subject}</td>
                  <td style={{ padding: "8px 6px" }}>{(t.accuracy * 100).toFixed(0)}%</td>
                  <td style={{ padding: "8px 6px" }}>{(t.avg_predicted_risk * 100).toFixed(0)}%</td>
                  <td style={{ padding: "8px 6px" }}>{t.n_students}</td>
                  <td style={{ padding: "8px 6px" }}><RiskPill level={t.risk_level} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}

export default function FacultyDashboard({ onBack }) {
  const [tab, setTab] = useState("students")
  const [cohort, setCohort] = useState(null)
  const [cohortError, setCohortError] = useState(false)
  const [students, setStudents] = useState(null)
  const [studentsError, setStudentsError] = useState(false)
  const [topics, setTopics] = useState(null)
  const [topicsError, setTopicsError] = useState(false)
  const [riskFilter, setRiskFilter] = useState("")
  const [expandedId, setExpandedId] = useState(null)
  const [topicView, setTopicView] = useState("grid")

  useEffect(() => {
    axios.get(`${API}/insights/cohort-summary`)
      .then(r => setCohort(r.data))
      .catch(() => setCohortError(true))
  }, [])

  useEffect(() => {
    const params = riskFilter ? { risk_level: riskFilter } : {}
    axios.get(`${API}/insights/students/at-risk`, { params })
      .then(r => setStudents(r.data.students))
      .catch(() => setStudentsError(true))
  }, [riskFilter])

  useEffect(() => {
    axios.get(`${API}/insights/topics/heatmap`)
      .then(r => setTopics(r.data.topics))
      .catch(() => setTopicsError(true))
  }, [])

  return (
    <div className="dashboard-wrapper">
      <div className="dashboard-header">
        <div>
          <h2 style={{ color: "#fff", margin: 0, fontSize: 22, fontWeight: 800 }}>
            🧭 Mastery Insights
          </h2>
          <p style={{ color: "#a5b4fc", fontSize: 14, margin: "4px 0 0" }}>
            Cohort risk & explainability — faculty view
          </p>
        </div>
        {onBack && (
          <button className="score-btn-history" onClick={onBack}>← Back</button>
        )}
      </div>

      {/* Cohort summary strip */}
      {cohort && (
        <div className="analytics-cards" style={{ margin: "16px 0" }}>
          <div className="analytics-card" style={{ background: "#f5f3ff" }}>
            <div style={{ fontSize: 24, fontWeight: 800, color: "#6366f1" }}>{cohort.n_students}</div>
            <div style={{ fontSize: 12, color: "#888", marginTop: 4 }}>Students</div>
          </div>
          <div className="analytics-card" style={{ background: "#f0fdf4" }}>
            <div style={{ fontSize: 24, fontWeight: 800, color: "#22c55e" }}>
              {(cohort.overall_accuracy * 100).toFixed(0)}%
            </div>
            <div style={{ fontSize: 12, color: "#888", marginTop: 4 }}>Cohort accuracy</div>
          </div>
          <div className="analytics-card" style={{ background: "#fff7ed" }}>
            <div style={{ fontSize: 24, fontWeight: 800, color: "#f97316" }}>
              {(cohort.overall_avg_risk * 100).toFixed(0)}%
            </div>
            <div style={{ fontSize: 12, color: "#888", marginTop: 4 }}>Avg risk</div>
          </div>
          <div className="analytics-card" style={{ background: "#faf5ff" }}>
            <div style={{ fontSize: 24, fontWeight: 800, color: "#a855f7" }}>{cohort.total_anomalies}</div>
            <div style={{ fontSize: 12, color: "#888", marginTop: 4 }}>Anomalies flagged</div>
          </div>
        </div>
      )}

      <div className="dashboard-tabs">
        {[
          { key: "students", label: "🎯 At-Risk Students" },
          { key: "topics", label: "🗺️ Topic Heatmap" },
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
        {tab === "students" && (
          <>
            {studentsError && <PipelineNotRunState what="student insights" />}
            {!studentsError && !students && (
              <div style={{ textAlign: "center", padding: 40, color: "#9ca3af" }}>Loading…</div>
            )}
            {!studentsError && students && (
              <>
                <div className="row" style={{ marginBottom: 14 }}>
                  <span style={{ fontSize: 13, color: "#6b7280" }}>{students.length} students shown</span>
                  <select
                    value={riskFilter}
                    onChange={e => setRiskFilter(e.target.value)}
                    style={{ fontSize: 13, padding: "6px 10px", borderRadius: 8, border: "1.5px solid #e5e7eb" }}
                  >
                    <option value="">All risk levels</option>
                    <option value="High">High only</option>
                    <option value="Medium">Medium only</option>
                    <option value="Low">Low only</option>
                  </select>
                </div>
                {students.length === 0 ? (
                  <div style={{ textAlign: "center", padding: 30, color: "#9ca3af" }}>
                    No students match this filter.
                  </div>
                ) : (
                  students.map(s => (
                    <StudentCard
                      key={s.student_id}
                      s={s}
                      expanded={expandedId === s.student_id}
                      onToggle={() => setExpandedId(expandedId === s.student_id ? null : s.student_id)}
                    />
                  ))
                )}
              </>
            )}
          </>
        )}

        {tab === "topics" && (
          <>
            {topicsError && <PipelineNotRunState what="topic insights" />}
            {!topicsError && !topics && (
              <div style={{ textAlign: "center", padding: 40, color: "#9ca3af" }}>Loading…</div>
            )}
            {!topicsError && topics && (
              <TopicHeatmap topics={topics} view={topicView} setView={setTopicView} />
            )}
          </>
        )}
      </div>
    </div>
  )
}
