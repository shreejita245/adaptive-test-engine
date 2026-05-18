import { useState, useEffect } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

const RANK_STYLES = [
  { bg: "linear-gradient(135deg, #f59e0b, #d97706)", shadow: "rgba(245,158,11,0.4)", medal: "🥇", label: "1st" },
  { bg: "linear-gradient(135deg, #94a3b8, #64748b)", shadow: "rgba(148,163,184,0.4)", medal: "🥈", label: "2nd" },
  { bg: "linear-gradient(135deg, #cd7c2e, #a85f1f)", shadow: "rgba(205,124,46,0.4)", medal: "🥉", label: "3rd" },
]

export default function Leaderboard({ onClose, currentStudentId }) {
  const [data, setData] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const [confirmId, setConfirmId] = useState(null)

  function load() {
    axios.get(`${API}/analytics/leaderboard/all`).then(r => setData(r.data))
  }

  useEffect(() => { load() }, [])

  async function handleDelete(studentId) {
    if (confirmId !== studentId) {
      setConfirmId(studentId)
      return
    }
    setDeletingId(studentId)
    try {
      await axios.delete(`${API}/students/${studentId}`)
      setConfirmId(null)
      load()
    } catch (e) {
      console.error(e)
    }
    setDeletingId(null)
  }

  return (
    <div className="lb-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="lb-modal">
        {/* Header */}
        <div className="lb-header">
          <div>
            <div className="lb-header-title">🏆 Leaderboard</div>
            <div className="lb-header-sub">Top performers ranked by score</div>
          </div>
          <button className="lb-close-btn" onClick={onClose}>✕</button>
        </div>

        {/* Content */}
        <div className="lb-body">
          {!data ? (
            <div className="lb-loading">
              <div className="lb-spinner" />
              <p>Loading rankings...</p>
            </div>
          ) : data.length === 0 ? (
            <div className="lb-empty">
              <div style={{ fontSize: 48, marginBottom: 12 }}>🎯</div>
              <p>No students yet. Be the first!</p>
            </div>
          ) : (
            <>
              {/* Top 3 podium */}
              {data.length >= 1 && (
                <div className="lb-podium">
                  {data.slice(0, Math.min(3, data.length)).map((entry, i) => {
                    const rs = RANK_STYLES[i]
                    return (
                      <div key={entry.student_id} className="lb-podium-item" style={{ order: i === 1 ? 0 : i === 0 ? 1 : 2 }}>
                        <div className="lb-podium-medal" style={{ background: rs.bg, boxShadow: `0 4px 16px ${rs.shadow}` }}>
                          {rs.medal}
                        </div>
                        <div className="lb-podium-name">{entry.name.split(" ")[0]}</div>
                        <div className="lb-podium-score" style={{ background: rs.bg }}>{entry.score}</div>
                        <div className="lb-podium-bar" style={{
                          height: i === 0 ? 80 : i === 1 ? 100 : 60,
                          background: rs.bg, opacity: 0.3
                        }} />
                      </div>
                    )
                  })}
                </div>
              )}

              {/* Full list */}
              <div className="lb-list">
                {data.map((entry, i) => {
                  const isTop3 = i < 3
                  const isCurrentUser = entry.student_id === currentStudentId
                  const isConfirming = confirmId === entry.student_id
                  const isDeleting = deletingId === entry.student_id

                  return (
                    <div
                      key={entry.student_id}
                      className={`lb-row ${isCurrentUser ? "lb-row-me" : ""} ${isTop3 ? "lb-row-top" : ""}`}
                    >
                      {/* Rank */}
                      <div className="lb-rank">
                        {i < 3
                          ? <span style={{ fontSize: 20 }}>{RANK_STYLES[i].medal}</span>
                          : <span className="lb-rank-num">#{i + 1}</span>
                        }
                      </div>

                      {/* Avatar */}
                      <div className="lb-avatar" style={{
                        background: isTop3
                          ? RANK_STYLES[Math.min(i, 2)].bg
                          : "linear-gradient(135deg, #6366f1, #8b5cf6)"
                      }}>
                        {entry.name[0].toUpperCase()}
                      </div>

                      {/* Info */}
                      <div className="lb-info">
                        <div className="lb-name">
                          {entry.name}
                          {isCurrentUser && <span className="lb-you-tag">You</span>}
                        </div>
                        <div className="lb-meta">
                          {entry.total_attempts} questions · {entry.accuracy}% accuracy · {entry.avg_skill}% skill
                        </div>
                      </div>

                      {/* Score */}
                      <div className="lb-score-block">
                        <div className="lb-score">{entry.score}</div>
                        <div className="lb-score-label">score</div>
                      </div>

                      {/* Delete */}
                      {!isCurrentUser && (
                        <button
                          className={`lb-delete-btn ${isConfirming ? "lb-delete-confirm" : ""}`}
                          onClick={() => handleDelete(entry.student_id)}
                          disabled={isDeleting}
                          title={isConfirming ? "Click again to confirm" : "Remove student"}
                        >
                          {isDeleting ? "..." : isConfirming ? "Sure?" : "✕"}
                        </button>
                      )}
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}