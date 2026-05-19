import { useState } from "react"
import { supabase } from "../supabase"

export default function Login({ onLogin }) {
  const [mode, setMode] = useState("login")
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function handleSubmit() {
    if (!email || !password) return setError("Please fill in all fields")
    if (mode === "signup" && !name) return setError("Please enter your name")
    setLoading(true)
    setError("")

    try {
      if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({
          email, password, options: { data: { name } }
        })
        if (error) throw error
        const res = await fetch("https://adaptive-test-engine-production.up.railway.app", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email })
        })
        const student = await res.json()
        onLogin({ ...student, authUser: data.user })
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        const res = await fetch(`"https://adaptive-test-engine-production.up.railway.app"/students/email/${email}`)
        const student = await res.json()
        onLogin({ ...student, authUser: data.user })
      }
    } catch (e) {
      setError(e.message || "Something went wrong")
    }
    setLoading(false)
  }

  function handleKey(e) {
    if (e.key === "Enter") handleSubmit()
  }

  return (
    <div className="login-wrapper">
      {/* Left decorative panel */}
      <div className="login-left">
        <div className="login-brand">
          <div className="login-brand-icon">⚡</div>
          <div className="login-brand-text">AdaptIQ</div>
        </div>
        <h2 className="login-tagline">Master JEE & NEET with AI-powered adaptive tests</h2>
        <div className="login-features">
          {[
            { icon: "🎯", text: "Adapts to your skill level" },
            { icon: "📊", text: "Detailed performance analytics" },
            { icon: "🤖", text: "AI explanations by Groq" },
            { icon: "🏆", text: "Compete on the leaderboard" },
          ].map(f => (
            <div key={f.text} className="login-feature-item">
              <span>{f.icon}</span>
              <span>{f.text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right form panel */}
      <div className="login-right">
        <div className="login-form-card">
          <h1 className="login-form-title">
            {mode === "login" ? "Welcome back 👋" : "Create account 🚀"}
          </h1>
          <p className="login-form-sub">
            {mode === "login" ? "Sign in to continue your practice" : "Start your JEE/NEET prep journey"}
          </p>

          {/* Mode toggle */}
          <div className="login-toggle">
            <button
              onClick={() => setMode("login")}
              className={`login-toggle-btn ${mode === "login" ? "login-toggle-active" : ""}`}
            >Login</button>
            <button
              onClick={() => setMode("signup")}
              className={`login-toggle-btn ${mode === "signup" ? "login-toggle-active" : ""}`}
            >Sign Up</button>
          </div>

          {/* Fields */}
          <div className="login-fields">
            {mode === "signup" && (
              <div className="login-field">
                <label className="login-label">Full Name</label>
                <input
                  className="login-input"
                  placeholder="e.g. Arjun Sharma"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  onKeyDown={handleKey}
                />
              </div>
            )}
            <div className="login-field">
              <label className="login-label">Email</label>
              <input
                className="login-input"
                placeholder="you@example.com"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                onKeyDown={handleKey}
              />
            </div>
            <div className="login-field">
              <label className="login-label">Password</label>
              <input
                className="login-input"
                placeholder="••••••••"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                onKeyDown={handleKey}
              />
            </div>
          </div>

          {error && (
            <div className="login-error">
              <span>⚠️</span> {error}
            </div>
          )}

          <button
            className="login-submit-btn"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading
              ? <span className="login-btn-loading"><span className="login-mini-spinner" /> Please wait...</span>
              : mode === "login" ? "Sign In →" : "Create Account →"
            }
          </button>

          <p className="login-switch">
            {mode === "login" ? "New here? " : "Already have an account? "}
            <span className="login-switch-link" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
              {mode === "login" ? "Create account" : "Sign in"}
            </span>
          </p>
        </div>
      </div>
    </div>
  )
}