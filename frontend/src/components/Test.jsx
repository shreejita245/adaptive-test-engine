import { useState, useEffect, useRef } from "react"
import axios from "axios"
import MathRenderer from "./MathRenderer"

const API = "http://127.0.0.1:8000"

const STATUS = {
  NOT_VISITED: "not_visited",
  ANSWERED: "answered",
  SKIPPED: "skipped",
  MARKED: "marked",
  ANSWERED_MARKED: "answered_marked"
}

const STATUS_STYLES = {
  not_visited: { bg: "#2a2d3e", color: "#9ca3af", label: "Not Visited" },
  answered: { bg: "#22c55e", color: "white", label: "Answered" },
  skipped: { bg: "#ef4444", color: "white", label: "Not Answered" },
  marked: { bg: "#a855f7", color: "white", label: "Marked for Review" },
  answered_marked: { bg: "#f97316", color: "white", label: "Answered & Marked" }
}

export default function Test({ student, settings, onFinish }) {
  const { exam, mode, subjects, subject, topic, numQuestions, duration, marking } = settings

  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [questionStatuses, setQuestionStatuses] = useState({})
  const [selectedAnswers, setSelectedAnswers] = useState({})
  const [submitted, setSubmitted] = useState({})
  const [results, setResults] = useState({})
  const [timeLeft, setTimeLeft] = useState(duration * 60)
  const [testOver, setTestOver] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [loadedCount, setLoadedCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const timerRef = useRef(null)
  const questionIdsRef = useRef([])

  const totalTime = duration * 60
  const negativeMarks = marking.includes("-2") ? 2 : 1
  const positiveMarks = 4
  const maxScore = numQuestions * positiveMarks

  useEffect(() => {
    fetchAllQuestions()
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          clearInterval(timerRef.current)
          setTestOver(true)
          return 0
        }
        return t - 1
      })
    }, 1000)
    return () => clearInterval(timerRef.current)
  }, [])

  useEffect(() => { if (testOver) finishTest() }, [testOver])

  function getSubjectForIndex(i) {
    if (mode === "full") {
      const perSubject = Math.ceil(numQuestions / subjects.length)
      const si = Math.min(Math.floor(i / perSubject), subjects.length - 1)
      return subjects[si].toLowerCase()
    }
    return subject?.toLowerCase() || subjects[0].toLowerCase()
  }

  async function fetchAllQuestions() {
    setLoading(true)
    const fetched = []
    const statuses = {}
    const fetchedIds = []

    for (let i = 0; i < numQuestions; i++) {
      const currentSubject = getSubjectForIndex(i)
      const currentTopic = mode === "topic" ? topic.toLowerCase() : "all"

      try {
        const res = await axios.get(`${API}/attempts/next-question`, {
          params: {
            student_id: student.id,
            subject: currentSubject,
            topic: currentTopic,
            standard: exam,
            exclude_ids: fetchedIds.join(",")
          }
        })
        if (res.data.question) {
          fetched.push(res.data.question)
          statuses[i] = STATUS.NOT_VISITED
          fetchedIds.push(res.data.question.id)
          questionIdsRef.current.push(res.data.question.id)
          setLoadedCount(fetched.length)
        }
      } catch (e) { console.error(e) }
    }

    setQuestions(fetched)
    setQuestionStatuses(statuses)
    setLoading(false)
  }

  // Prevent double-call (timer expiry + button click)
  const finishedRef = useRef(false)

  async function finishTest() {
    if (finishedRef.current) return
    finishedRef.current = true
    clearInterval(timerRef.current)
    setGeneratingReport(true)

    // 12 second hard deadline — spinner WILL stop no matter what
    let timeoutId
    const deadline = new Promise(resolve => { timeoutId = setTimeout(() => resolve("timeout"), 12000) })

    const doWork = async () => {
      const localResults = { ...results }

      // Fire all pending submissions IN PARALLEL
      const jobs = []
      for (let i = 0; i < questions.length; i++) {
        const answer = selectedAnswers[i]
        if (answer && !submitted[i] && questions[i]) {
          const idx = i
          jobs.push(
            axios.post(`${API}/attempts/`, {
              student_id: student.id,
              question_id: questions[idx].id,
              selected_answer: answer,
              time_taken_seconds: 30
            }, { timeout: 7000 })
              .then(res => { localResults[idx] = res.data })
              .catch(() => {})
          )
        }
      }
      await Promise.allSettled(jobs)

      // Calculate score from server responses
      let finalScore = 0, correct = 0, wrong = 0, unattempted = 0
      const questionsData = questions.map((q, i) => {
        const answer = selectedAnswers[i]
        const result = localResults[i]
        if (!answer) {
          unattempted++
          return { question_text: q.question_text, options: q.options, correct_answer: result?.correct_answer || null, selected_answer: null, is_correct: null, topic: q.topic, explanation: result?.explanation || null }
        }
        const isCorrect = result ? Boolean(result.is_correct) : false
        if (isCorrect) { correct++; finalScore += positiveMarks }
        else { wrong++; finalScore -= negativeMarks }
        return { question_text: q.question_text, options: q.options, correct_answer: result?.correct_answer || null, selected_answer: answer, is_correct: isCorrect, topic: q.topic, explanation: result?.explanation || null }
      })

      // Save session in background — doesn't block
      axios.post(`${API}/sessions/`, {
        student_id: student.id, exam_name: settings.examName, mode: settings.mode,
        subject: settings.subject || null, topic: settings.topic || null,
        num_questions: questions.length, correct, wrong, unattempted,
        score: finalScore, max_score: maxScore, duration_mins: settings.duration,
        question_ids: questionIdsRef.current
      }, { timeout: 6000 }).catch(e => console.error("Session save:", e))

      return { score: finalScore, correct, wrong, unattempted, maxScore, questionsData, examName: settings.examName }
    }

    // Whichever resolves first — work done or deadline
    const result = await Promise.race([doWork().catch(() => null), deadline])
    clearTimeout(timeoutId)

    if (!result || result === "timeout") {
      console.warn("finishTest: timed out or failed, showing empty results")
      onFinish({ score: 0, correct: 0, wrong: 0, unattempted: questions.length, maxScore, questionsData: [], examName: settings.examName })
    } else {
      onFinish(result)
    }
  }




  function handleSelect(key) {
    if (submitted[currentIndex]) return
    setSelectedAnswers(prev => ({ ...prev, [currentIndex]: key }))
    setQuestionStatuses(prev => ({
      ...prev,
      [currentIndex]: prev[currentIndex] === STATUS.MARKED
        ? STATUS.ANSWERED_MARKED : STATUS.ANSWERED
    }))
  }

  async function handleSaveNext() {
    const answer = selectedAnswers[currentIndex]
    if (answer && !submitted[currentIndex]) {
      try {
        const res = await axios.post(`${API}/attempts/`, {
          student_id: student.id,
          question_id: questions[currentIndex].id,
          selected_answer: answer,
          time_taken_seconds: 30
        })
        setResults(prev => ({ ...prev, [currentIndex]: res.data }))
        setSubmitted(prev => ({ ...prev, [currentIndex]: true }))
      } catch (e) { console.error(e) }
    } else if (!answer) {
      setQuestionStatuses(prev => ({ ...prev, [currentIndex]: STATUS.SKIPPED }))
    }
    if (currentIndex < questions.length - 1) goTo(currentIndex + 1)
  }

  function handleMarkReview() {
    setQuestionStatuses(prev => ({
      ...prev,
      [currentIndex]: selectedAnswers[currentIndex]
        ? STATUS.ANSWERED_MARKED : STATUS.MARKED
    }))
    if (currentIndex < questions.length - 1) goTo(currentIndex + 1)
  }

  function handleClear() {
    if (submitted[currentIndex]) return
    setSelectedAnswers(prev => { const n = { ...prev }; delete n[currentIndex]; return n })
    setQuestionStatuses(prev => ({ ...prev, [currentIndex]: STATUS.NOT_VISITED }))
  }

  function goTo(index) {
    if (index < 0 || index >= questions.length) return
    setCurrentIndex(index)
  }

  const mins = Math.floor(timeLeft / 60)
  const secs = timeLeft % 60
  const timerColor = timeLeft > totalTime * 0.3 ? "#22c55e" : timeLeft > totalTime * 0.1 ? "#f97316" : "#ef4444"
  const q = questions[currentIndex]
  const currentAnswer = selectedAnswers[currentIndex]

  const answeredCount = Object.values(questionStatuses).filter(s => s === STATUS.ANSWERED || s === STATUS.ANSWERED_MARKED).length
  const markedCount = Object.values(questionStatuses).filter(s => s === STATUS.MARKED || s === STATUS.ANSWERED_MARKED).length
  const skippedCount = Object.values(questionStatuses).filter(s => s === STATUS.SKIPPED).length
  const notVisitedCount = Object.values(questionStatuses).filter(s => s === STATUS.NOT_VISITED).length

  if (generatingReport) return (
    <div className="generating-report-screen">
      <div className="generating-report-card">
        <div className="report-spinner"></div>
        <h2 style={{ color: "#fff", marginBottom: 8 }}>Saving Your Results</h2>
        <p style={{ color: "#a5b4fc", fontSize: 14 }}>Just a moment...</p>
      </div>
    </div>
  )

  if (loading) return (
    <div className="generating-report-screen">
      <div className="generating-report-card">
        <div className="report-spinner"></div>
        <h2 style={{ color: "#fff", marginBottom: 8 }}>Loading Questions</h2>
        <p style={{ color: "#a5b4fc", fontSize: 14, marginBottom: 16 }}>{loadedCount} / {numQuestions} loaded</p>
        <div style={{ height: 6, background: "#1e1b4b", borderRadius: 99, width: 200, margin: "0 auto" }}>
          <div style={{ height: 6, borderRadius: 99, background: "linear-gradient(90deg, #6366f1, #a855f7)", width: `${(loadedCount / numQuestions) * 100}%`, transition: "width 0.3s" }} />
        </div>
      </div>
    </div>
  )

  return (
    <div className="test-layout">
      {/* Main Content Area */}
      <div className="test-main">
        {/* Question header */}
        <div className="test-question-header">
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span className="question-number-badge">Q{currentIndex + 1}</span>
            <div>
              <div style={{ fontWeight: 600, fontSize: 15, color: "#1e1b4b" }}>
                Question {currentIndex + 1} of {questions.length}
              </div>
              <div style={{ fontSize: 12, color: "#6b7280", marginTop: 2 }}>
                {q?.topic} · {settings.examName}
              </div>
            </div>
          </div>
          {/* Mobile sidebar toggle */}
          <button className="sidebar-toggle-btn" onClick={() => setSidebarCollapsed(c => !c)}>
            ☰
          </button>
        </div>

        {/* Question card */}
        <div className="test-question-card">
          <MathRenderer
            html={q?.question_text}
            style={{ fontWeight: 500, fontSize: 15, lineHeight: 1.8, marginBottom: 20 }}
          />

          <div className="test-options">
            {q && Object.entries(q.options).map(([key, val]) => {
              const isSelected = currentAnswer === key
              return (
                <button
                  key={key}
                  onClick={() => handleSelect(key)}
                  className={`test-option ${isSelected ? "test-option-selected" : ""}`}
                >
                  <span className={`option-letter ${isSelected ? "option-letter-selected" : ""}`}>
                    {key}
                  </span>
                  <MathRenderer html={val} style={{ display: "inline" }} />
                </button>
              )
            })}
          </div>
        </div>

        {/* Action buttons */}
        <div className="test-actions">
          <button onClick={handleMarkReview} className="test-btn test-btn-mark">
            🔖 Mark & Next
          </button>
          <button onClick={handleClear} className="test-btn test-btn-clear">
            🗑 Clear
          </button>
          <button onClick={handleSaveNext} className="test-btn test-btn-save">
            {currentIndex < questions.length - 1 ? "Save & Next →" : "Save"}
          </button>
        </div>

        {/* Prev / Next nav */}
        <div className="test-nav-buttons">
          <button
            onClick={() => goTo(currentIndex - 1)}
            disabled={currentIndex === 0}
            className="test-btn test-btn-nav"
          >← Previous</button>
          <button
            onClick={() => goTo(currentIndex + 1)}
            disabled={currentIndex === questions.length - 1}
            className="test-btn test-btn-nav"
          >Next →</button>
        </div>
      </div>

      {/* Sidebar */}
      <div className={`test-sidebar ${sidebarCollapsed ? "test-sidebar-collapsed" : ""}`}>
        {/* Timer */}
        <div className="sidebar-timer">
          <div style={{ fontSize: 12, color: "#a5b4fc", marginBottom: 4, fontWeight: 600, letterSpacing: 1 }}>
            TIME REMAINING
          </div>
          <div style={{ fontWeight: 800, fontSize: 32, color: timerColor, fontFamily: "monospace" }}>
            {mins}:{secs.toString().padStart(2, "0")}
          </div>
          <div style={{ height: 4, background: "#1e1b4b", borderRadius: 99, marginTop: 8 }}>
            <div style={{
              height: 4, borderRadius: 99, background: timerColor,
              width: `${(timeLeft / totalTime) * 100}%`, transition: "width 1s linear"
            }} />
          </div>
        </div>

        {/* Stats */}
        <div className="sidebar-stats">
          {[
            { label: "Answered", count: answeredCount, color: "#22c55e", icon: "✅" },
            { label: "Marked", count: markedCount, color: "#a855f7", icon: "🔖" },
            { label: "Skipped", count: skippedCount, color: "#ef4444", icon: "⏭" },
            { label: "Remaining", count: notVisitedCount, color: "#6b7280", icon: "📋" }
          ].map(s => (
            <div key={s.label} className="sidebar-stat-item">
              <span style={{ fontSize: 11 }}>{s.icon}</span>
              <span style={{ fontWeight: 700, fontSize: 16, color: s.color }}>{s.count}</span>
              <span style={{ fontSize: 10, color: "#9ca3af" }}>{s.label}</span>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="sidebar-legend">
          {Object.entries(STATUS_STYLES).map(([status, style]) => (
            <div key={status} className="sidebar-legend-item">
              <div style={{ width: 12, height: 12, borderRadius: 3, background: style.bg, flexShrink: 0 }} />
              <span>{style.label}</span>
            </div>
          ))}
        </div>

        {/* Question Grid */}
        <div className="sidebar-grid-label">QUESTION NAVIGATOR</div>
        <div className="sidebar-grid">
          {questions.map((_, i) => {
            const status = questionStatuses[i] || STATUS.NOT_VISITED
            const s = STATUS_STYLES[status]
            const isCurrent = currentIndex === i
            return (
              <button
                key={i}
                onClick={() => goTo(i)}
                className={`sidebar-grid-btn ${isCurrent ? "sidebar-grid-btn-active" : ""}`}
                style={{ background: s.bg, color: s.color }}
              >
                {i + 1}
              </button>
            )
          })}
        </div>

        {/* Submit button */}
        <button onClick={finishTest} className="sidebar-submit-btn">
          🏁 Submit Test
        </button>
      </div>

      {/* Mobile overlay backdrop */}
      {!sidebarCollapsed && (
        <div className="sidebar-mobile-backdrop" onClick={() => setSidebarCollapsed(true)} />
      )}
    </div>
  )
}