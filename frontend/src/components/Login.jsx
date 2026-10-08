import { useState } from "react"
import { supabase } from "../supabase"
import { API } from "../api"

const FACULTY_SECRET = "ADAPTIQ_FACULTY_2024"

export default function Login({ onLogin }) {
  const [role, setRole] = useState(null)
  const [mode, setMode] = useState("login")
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [secretCode, setSecretCode] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  function selectRole(r) {
    setRole(r); setMode("login"); setError("")
    setName(""); setEmail(""); setPassword(""); setSecretCode("")
  }

  async function handleSubmit() {
    if (!email || !password) return setError("Please fill in all fields")
    if (mode === "signup" && !name) return setError("Please enter your name")
    if (role === "faculty" && mode === "signup" && secretCode !== FACULTY_SECRET)
      return setError("Invalid faculty invite code")
    setLoading(true); setError("")
    try {
      if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({ email, password, options: { data: { name, role } } })
        if (error) throw error
        if (role === "faculty") {
          onLogin({ name, email, role: "faculty" }, data.user)
        } else {
          const res = await fetch(`${API}/students/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, email }) })
          const student = await res.json()
          onLogin({ ...student, role: "student" }, data.user)
        }
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        const userRole = data.user?.user_metadata?.role || "student"
        if (role === "faculty" && userRole !== "faculty") throw new Error("This account is not a faculty account. Please use Student Login.")
        if (role === "student" && userRole === "faculty") throw new Error("This is a faculty account. Please use Faculty Login.")
        if (userRole === "faculty") {
          onLogin({ name: data.user.user_metadata?.name || email, email, role: "faculty" }, data.user)
        } else {
          const res = await fetch(`${API}/students/email/${email}`)
          const student = await res.json()
          onLogin({ ...student, role: "student" }, data.user)
        }
      }
    } catch (e) { setError(e.message || "Something went wrong") }
    setLoading(false)
  }

  function handleKey(e) { if (e.key === "Enter") handleSubmit() }

  if (!role) {
    return (
      <div className="login-wrapper">
        <div className="login-left">
          <div className="login-brand"><div className="login-brand-icon">⚡</div><div className="login-brand-text">AdaptIQ</div></div>
          <h2 className="login-tagline">Master JEE &amp; NEET with AI-powered adaptive tests</h2>
          <div className="login-features">
            {[{icon:"🎯",text:"Adapts to your skill level"},{icon:"📊",text:"Detailed performance analytics"},{icon:"🤖",text:"AI explanations by Groq"},{icon:"🏆",text:"Track cohort performance"}].map(f=>(
              <div key={f.text} className="login-feature-item"><span>{f.icon}</span><span>{f.text}</span></div>
            ))}
          </div>
        </div>
        <div className="login-right">
          <div className="login-form-card">
            <h1 className="login-form-title">Welcome to AdaptIQ 👋</h1>
            <p className="login-form-sub">How are you accessing the platform?</p>
            <div style={{display:"flex",flexDirection:"column",gap:"16px",marginTop:"32px"}}>
              <button className="login-submit-btn" onClick={()=>selectRole("student")} style={{fontSize:"1.1rem",padding:"18px"}}>🎓 I'm a Student</button>
              <button className="login-submit-btn" onClick={()=>selectRole("faculty")} style={{fontSize:"1.1rem",padding:"18px",background:"linear-gradient(135deg,#6366f1,#4f46e5)"}}>🧑‍🏫 I'm Faculty</button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const isFaculty = role === "faculty"
  return (
    <div className="login-wrapper">
      <div className="login-left">
        <div className="login-brand"><div className="login-brand-icon">{isFaculty?"🧑‍🏫":"⚡"}</div><div className="login-brand-text">AdaptIQ</div></div>
        <h2 className="login-tagline">{isFaculty?"Monitor student performance & flag at-risk learners":"Master JEE & NEET with AI-powered adaptive tests"}</h2>
        <div className="login-features">
          {(isFaculty?[{icon:"📊",text:"Cohort risk analysis"},{icon:"🔍",text:"SHAP explainability"},{icon:"⚠️",text:"Anomaly detection"},{icon:"🗺️",text:"Topic weakness heatmap"}]:[{icon:"🎯",text:"Adapts to your skill level"},{icon:"📊",text:"Detailed performance analytics"},{icon:"🤖",text:"AI explanations by Groq"},{icon:"🏆",text:"Compete on the leaderboard"}]).map(f=>(
            <div key={f.text} className="login-feature-item"><span>{f.icon}</span><span>{f.text}</span></div>
          ))}
        </div>
        <button onClick={()=>setRole(null)} style={{marginTop:"32px",background:"none",border:"1px solid rgba(255,255,255,0.3)",color:"white",padding:"8px 16px",borderRadius:"8px",cursor:"pointer"}}>← Back</button>
      </div>
      <div className="login-right">
        <div className="login-form-card">
          <div style={{display:"inline-block",background:isFaculty?"#eef2ff":"#f0fdf4",color:isFaculty?"#4f46e5":"#16a34a",padding:"4px 12px",borderRadius:"20px",fontSize:"0.8rem",fontWeight:600,marginBottom:"12px"}}>{isFaculty?"🧑‍🏫 Faculty Portal":"🎓 Student Portal"}</div>
          <h1 className="login-form-title">{mode==="login"?"Welcome back 👋":"Create account 🚀"}</h1>
          <p className="login-form-sub">{mode==="login"?(isFaculty?"Sign in to view student insights":"Sign in to continue your practice"):(isFaculty?"Register with your faculty invite code":"Start your JEE/NEET prep journey")}</p>
          <div className="login-toggle">
            <button onClick={()=>{setMode("login");setError("")}} className={`login-toggle-btn ${mode==="login"?"login-toggle-active":""}`}>Login</button>
            <button onClick={()=>{setMode("signup");setError("")}} className={`login-toggle-btn ${mode==="signup"?"login-toggle-active":""}`}>Sign Up</button>
          </div>
          <div className="login-fields">
            {mode==="signup"&&<div className="login-field"><label className="login-label">Full Name</label><input className="login-input" placeholder={isFaculty?"e.g. Dr. Priya Sharma":"e.g. Arjun Sharma"} value={name} onChange={e=>setName(e.target.value)} onKeyDown={handleKey}/></div>}
            <div className="login-field"><label className="login-label">Email</label><input className="login-input" placeholder="you@example.com" type="email" value={email} onChange={e=>setEmail(e.target.value)} onKeyDown={handleKey}/></div>
            <div className="login-field"><label className="login-label">Password</label><input className="login-input" placeholder="••••••••" type="password" value={password} onChange={e=>setPassword(e.target.value)} onKeyDown={handleKey}/></div>
            {isFaculty&&mode==="signup"&&<div className="login-field"><label className="login-label">Faculty Invite Code</label><input className="login-input" placeholder="Enter code provided by admin" value={secretCode} onChange={e=>setSecretCode(e.target.value)} onKeyDown={handleKey}/></div>}
          </div>
          {error&&<div className="login-error"><span>⚠️</span> {error}</div>}
          <button className="login-submit-btn" onClick={handleSubmit} disabled={loading} style={isFaculty?{background:"linear-gradient(135deg,#6366f1,#4f46e5)"}:{}}>{loading?<span className="login-btn-loading"><span className="login-mini-spinner"/> Please wait...</span>:mode==="login"?"Sign In →":"Create Account →"}</button>
          <p className="login-switch">{mode==="login"?"New here? ":"Already have an account? "}<span className="login-switch-link" onClick={()=>{setMode(mode==="login"?"signup":"login");setError("")}}>{mode==="login"?"Create account":"Sign in"}</span></p>
        </div>
      </div>
    </div>
  )
}
