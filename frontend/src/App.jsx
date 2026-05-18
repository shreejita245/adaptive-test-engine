import { useState, useEffect } from "react"
import { supabase } from "./supabase"
import Login from "./components/Login"
import TestConfig from "./components/TestConfig"
import Test from "./components/Test"
import Dashboard from "./components/Dashboard"
import ExplanationPage from "./components/ExplanationPage"
import TestHistory from "./components/TestHistory"
import "./App.css"

export default function App() {
  const [student, setStudent] = useState(null)
  const [testSettings, setTestSettings] = useState(null)
  const [scoreData, setScoreData] = useState(null)
  const [page, setPage] = useState("login")
  const [showProfile, setShowProfile] = useState(false)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        fetch(`http://127.0.0.1:8000/students/email/${session.user.email}`)
          .then(r => r.json())
          .then(student => {
            if (student.id) {
              setStudent(student)
              setPage("config")
            }
          })
      }
    })
  }, [])

  async function handleLogout() {
    await supabase.auth.signOut()
    setStudent(null)
    setPage("login")
    setShowProfile(false)
  }

  const showTopbar = student && page !== "test" && page !== "login"

  return (
    <div className={page === "test" ? "app app-test-mode" : "app"}>
      {/* Top navigation bar */}
      {showTopbar && (
        <div className="topbar">
          {/* Brand */}
          <div className="topbar-brand" onClick={() => setPage("config")}>
            <div className="topbar-brand-icon">⚡</div>
            <span className="topbar-brand-name">AdaptIQ</span>
          </div>

          {/* Nav links */}
          <div className="topbar-nav">
            <button
              className={`topbar-nav-btn ${page === "config" ? "topbar-nav-active" : ""}`}
              onClick={() => setPage("config")}
            >
              🏠 Home
            </button>
            <button
              className={`topbar-nav-btn ${page === "history" ? "topbar-nav-active" : ""}`}
              onClick={() => setPage("history")}
            >
              📂 Test History
            </button>
          </div>

          {/* Profile */}
          <div style={{ position: "relative" }}>
            <div
              className="topbar-avatar"
              onClick={() => setShowProfile(p => !p)}
              title={student.name}
            >
              {student.name?.[0]?.toUpperCase()}
            </div>

            {showProfile && (
              <div className="topbar-dropdown">
                <div className="topbar-dropdown-name">{student.name}</div>
                <div className="topbar-dropdown-email">{student.email}</div>
                <hr style={{ border: "none", borderTop: "1px solid #f3f4f6", margin: "10px 0" }} />
                <button
                  onClick={() => { setPage("history"); setShowProfile(false) }}
                  className="topbar-dropdown-item"
                >
                  📂 Test History
                </button>
                <button
                  onClick={() => { setPage("config"); setShowProfile(false) }}
                  className="topbar-dropdown-item"
                >
                  🏠 Home
                </button>
                <button
                  onClick={handleLogout}
                  className="topbar-dropdown-item topbar-dropdown-logout"
                >
                  🚪 Logout
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Pages */}
      {page === "login" && (
        <Login onLogin={(s) => { setStudent(s); setPage("config") }} />
      )}

      {page === "config" && (
        <TestConfig
          student={student}
          onStart={(settings) => { setTestSettings(settings); setPage("test") }}
        />
      )}

      {page === "test" && (
        <Test
          student={student}
          settings={testSettings}
          onFinish={(data) => {
            setScoreData({ ...data, examName: testSettings?.examName })
            setPage("dashboard")
          }}
        />
      )}

      {page === "dashboard" && (
        <Dashboard
          student={student}
          scoreData={scoreData}
          onRetry={() => setPage("config")}
          onViewExplanations={() => setPage("explanations")}
          onViewHistory={() => setPage("history")}
        />
      )}

      {page === "explanations" && (
        <ExplanationPage
          questionsData={scoreData?.questionsData || []}
          onBack={() => setPage("dashboard")}
        />
      )}

      {page === "history" && (
        <TestHistory
          student={student}
          onBack={() => setPage(scoreData ? "dashboard" : "config")}
          onStartNew={() => setPage("config")}
        />
      )}
    </div>
  )
}