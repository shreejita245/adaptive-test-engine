import { useState, useEffect } from "react"
import { supabase } from "./supabase"
import { API } from "./api"
import Login from "./components/Login"
import TestConfig from "./components/TestConfig"
import Test from "./components/Test"
import Dashboard from "./components/Dashboard"
import ExplanationPage from "./components/ExplanationPage"
import TestHistory from "./components/TestHistory"
import FacultyDashboard from "./components/FacultyDashboard"
import "./App.css"

export default function App() {
  const [student, setStudent] = useState(null)
  const [isFaculty, setIsFaculty] = useState(false)
  const [testSettings, setTestSettings] = useState(null)
  const [scoreData, setScoreData] = useState(null)
  const [page, setPage] = useState("login")
  const [showProfile, setShowProfile] = useState(false)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        // Check Supabase user metadata for faculty role.
        // Set this once per faculty user in the Supabase dashboard:
        //   Auth → Users → [user] → Edit → user_metadata → { "role": "faculty" }
        const role = session.user?.user_metadata?.role
        setIsFaculty(role === "faculty")

        fetch(`${API}/students/email/${session.user.email}`)
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

  async function handleLogin(studentData, authUser) {
    // Read faculty flag from the auth user returned at login time
    const role = authUser?.user_metadata?.role
    setIsFaculty(role === "faculty")
    setStudent(studentData)
    setPage("config")
  }

  async function handleLogout() {
    await supabase.auth.signOut()
    setStudent(null)
    setIsFaculty(false)
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
            {/* Only faculty see the Insights tab */}
            {isFaculty && (
              <button
                className={`topbar-nav-btn ${page === "faculty" ? "topbar-nav-active" : ""}`}
                onClick={() => setPage("faculty")}
              >
                🧭 Insights
              </button>
            )}
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
                {isFaculty && (
                  <div style={{
                    fontSize: 11, fontWeight: 700, color: "#6366f1",
                    background: "#ede9fe", borderRadius: 6,
                    padding: "2px 8px", marginTop: 4, display: "inline-block"
                  }}>
                    Faculty
                  </div>
                )}
                <hr style={{ border: "none", borderTop: "1px solid #f3f4f6", margin: "10px 0" }} />
                <button
                  onClick={() => { setPage("history"); setShowProfile(false) }}
                  className="topbar-dropdown-item"
                >
                  📂 Test History
                </button>
                {isFaculty && (
                  <button
                    onClick={() => { setPage("faculty"); setShowProfile(false) }}
                    className="topbar-dropdown-item"
                  >
                    🧭 Insights
                  </button>
                )}
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
        <Login onLogin={(s, authUser) => handleLogin(s, authUser)} />
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

      {/* Faculty-only page: render an access-denied screen for non-faculty */}
      {page === "faculty" && (
        isFaculty
          ? <FacultyDashboard onBack={() => setPage("config")} />
          : (
            <div style={{
              display: "flex", flexDirection: "column", alignItems: "center",
              justifyContent: "center", minHeight: "60vh", gap: 12,
              color: "#6b7280", textAlign: "center", padding: 40,
            }}>
              <div style={{ fontSize: 48 }}>🔒</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: "#374151" }}>
                Faculty access only
              </div>
              <div style={{ fontSize: 14, maxWidth: 360 }}>
                The Insights tab is restricted to faculty accounts.
                Ask your administrator to grant faculty access.
              </div>
              <button
                className="score-btn-history"
                onClick={() => setPage("config")}
                style={{ marginTop: 8 }}
              >
                ← Back to Home
              </button>
            </div>
          )
      )}
    </div>
  )
}
