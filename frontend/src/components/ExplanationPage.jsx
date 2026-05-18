import { useState } from "react"
import MathRenderer from "./MathRenderer"

export default function ExplanationPage({ questionsData, onBack }) {
  const [filter, setFilter] = useState("all") // all, correct, incorrect

  const filtered = questionsData.filter(q => {
    if (filter === "correct") return q.is_correct
    if (filter === "incorrect") return !q.is_correct
    return true
  })

  const correctCount = questionsData.filter(q => q.is_correct).length
  const incorrectCount = questionsData.filter(q => !q.is_correct).length

  return (
    <div className="explanation-page">
      {/* Header */}
      <div className="explanation-header">
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "#fff", marginBottom: 4 }}>
            📝 Detailed Explanations
          </h1>
          <p style={{ color: "#a5b4fc", fontSize: 14 }}>
            AI-powered breakdown of every question
          </p>
        </div>
        <button onClick={onBack} className="explanation-back-btn">
          ← Back to Results
        </button>
      </div>

      {/* Summary bar */}
      <div className="explanation-summary">
        <div className="explanation-summary-stat">
          <span style={{ fontSize: 24, fontWeight: 700, color: "#22c55e" }}>{correctCount}</span>
          <span style={{ fontSize: 12, color: "#6b7280" }}>Correct</span>
        </div>
        <div className="explanation-summary-stat">
          <span style={{ fontSize: 24, fontWeight: 700, color: "#ef4444" }}>{incorrectCount}</span>
          <span style={{ fontSize: 12, color: "#6b7280" }}>Incorrect</span>
        </div>
        <div className="explanation-summary-stat">
          <span style={{ fontSize: 24, fontWeight: 700, color: "#6366f1" }}>{questionsData.length}</span>
          <span style={{ fontSize: 12, color: "#6b7280" }}>Total</span>
        </div>
        <div className="explanation-summary-stat">
          <span style={{ fontSize: 24, fontWeight: 700, color: "#f97316" }}>
            {questionsData.length > 0 ? Math.round((correctCount / questionsData.length) * 100) : 0}%
          </span>
          <span style={{ fontSize: 12, color: "#6b7280" }}>Accuracy</span>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="explanation-filters">
        {[
          { key: "all", label: `All (${questionsData.length})` },
          { key: "incorrect", label: `❌ Incorrect (${incorrectCount})` },
          { key: "correct", label: `✅ Correct (${correctCount})` }
        ].map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`explanation-filter-btn ${filter === f.key ? "explanation-filter-active" : ""}`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Questions list */}
      <div className="explanation-list">
        {filtered.map((q, i) => {
          const originalIndex = questionsData.indexOf(q)
          return (
            <div key={i} className={`explanation-card ${q.is_correct ? "explanation-card-correct" : "explanation-card-incorrect"}`}>
              {/* Question number & status */}
              <div className="explanation-card-header">
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span className={`explanation-q-badge ${q.is_correct ? "badge-correct" : "badge-incorrect"}`}>
                    Q{originalIndex + 1}
                  </span>
                  <span style={{ fontSize: 12, color: "#6b7280", background: "#f3f4f6", padding: "3px 10px", borderRadius: 20 }}>
                    {q.topic}
                  </span>
                </div>
                <span style={{ fontSize: 20 }}>{q.is_correct ? "✅" : "❌"}</span>
              </div>

              {/* Question text */}
              <div className="explanation-question-text">
                <MathRenderer html={q.question_text} style={{ lineHeight: 1.8 }} />
              </div>

              {/* Options */}
              <div className="explanation-options">
                {q.options && Object.entries(q.options).map(([key, val]) => {
                  const isCorrect = key === q.correct_answer
                  const isSelected = key === q.selected_answer
                  const isWrongSelection = isSelected && !isCorrect

                  let className = "explanation-option"
                  if (isCorrect) className += " explanation-option-correct"
                  if (isWrongSelection) className += " explanation-option-wrong"

                  return (
                    <div key={key} className={className}>
                      <span className="explanation-option-key">{key}</span>
                      <MathRenderer html={val} style={{ display: "inline", flex: 1 }} />
                      {isCorrect && <span className="explanation-option-tag correct-tag">✓ Correct</span>}
                      {isWrongSelection && <span className="explanation-option-tag wrong-tag">✗ Your Answer</span>}
                      {isSelected && isCorrect && <span className="explanation-option-tag correct-tag">✓ Your Answer</span>}
                    </div>
                  )
                })}
              </div>

              {/* Explanation */}
              {q.explanation && (
                <div className="explanation-detail">
                  <div className="explanation-detail-header">
                    <span>💡</span>
                    <strong>Explanation</strong>
                  </div>
                  <MathRenderer html={q.explanation} style={{ lineHeight: 1.8, fontSize: 14, color: "#374151" }} />
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Bottom back button */}
      <div style={{ textAlign: "center", marginTop: 24, paddingBottom: 32 }}>
        <button onClick={onBack} className="explanation-back-btn" style={{ display: "inline-flex" }}>
          ← Back to Results
        </button>
      </div>
    </div>
  )
}
