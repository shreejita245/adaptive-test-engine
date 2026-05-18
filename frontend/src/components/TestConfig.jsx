import { useState } from "react"

const EXAM_PATTERNS = {
  "JEE Mains": {
    exam: "JEE",
    subjects: ["Mathematics", "Physics", "Chemistry"],
    topics: {
      "Mathematics": [
        "Sets and Relations", "Quadratic Equations", "Sequence and Series",
        "Binomial Theorem", "Permutation and Combination", "Complex Numbers",
        "Matrices and Determinants", "Probability", "Statistics",
        "Limits Continuity and Differentiability", "Application of Derivatives",
        "Indefinite Integration", "Definite Integration", "Differential Equations",
        "Straight Lines", "Circles", "Conic Sections", "3D Geometry",
        "Vector Algebra", "Trigonometry"
      ],
      "Physics": [
        "Units and Dimensions", "Kinematics", "Laws of Motion",
        "Work Power and Energy", "Rotational Motion", "Gravitation",
        "Properties of Matter", "Thermodynamics", "Kinetic Theory of Gases",
        "Simple Harmonic Motion", "Waves", "Electrostatics",
        "Current Electricity", "Magnetic Effects of Current", "Magnetism",
        "Electromagnetic Induction", "Alternating Current", "Optics",
        "Dual Nature of Radiation", "Atoms and Nuclei", "Semiconductors"
      ],
      "Chemistry": [
        "Atomic Structure", "Chemical Bonding", "Periodic Table",
        "States of Matter", "Thermodynamics", "Equilibrium",
        "Redox Reactions", "Electrochemistry", "Chemical Kinetics",
        "Solutions", "Surface Chemistry", "Hydrogen",
        "s Block Elements", "p Block Elements", "d and f Block Elements",
        "Coordination Compounds", "Metallurgy", "General Organic Chemistry",
        "Hydrocarbons", "Haloalkanes and Haloarenes",
        "Alcohols Phenols and Ethers", "Aldehydes and Ketones",
        "Carboxylic Acids", "Amines", "Biomolecules", "Polymers"
      ]
    },
    full: { questions: 75, duration: 180, marking: "+4 / -1" },
    subject: { questions: 25, duration: 60, marking: "+4 / -1" },
    topic: { questions: 10, duration: 20, marking: "+4 / -1" }
  },
  "JEE Advanced": {
    exam: "JEE",
    subjects: ["Mathematics", "Physics", "Chemistry"],
    topics: {
      "Mathematics": [
        "Sets Relations and Functions", "Quadratic Equations", "Sequence and Series",
        "Binomial Theorem", "Permutation and Combination", "Complex Numbers",
        "Matrices", "Probability and Statistics", "Trigonometry",
        "Differential Calculus", "Integral Calculus", "Differential Equations",
        "Analytical Geometry 2D", "Analytical Geometry 3D", "Vectors"
      ],
      "Physics": [
        "Kinematics", "Laws of Motion", "Work Power and Energy",
        "Rotational Motion", "Gravitation", "Properties of Matter",
        "Thermal Physics", "Waves and Sound", "Electrostatics",
        "Current Electricity", "Magnetic Fields", "Electromagnetic Induction",
        "Optics", "Modern Physics", "Nuclear Physics"
      ],
      "Chemistry": [
        "Atomic Structure", "Chemical Bonding", "Thermodynamics",
        "Chemical Equilibrium", "Electrochemistry", "Chemical Kinetics",
        "Solutions", "Nuclear Chemistry", "Isolation of Metals",
        "p Block Elements", "Transition Elements", "Coordination Compounds",
        "General Organic Chemistry", "Stereochemistry", "Reaction Mechanisms",
        "Hydrocarbons", "Functional Group Chemistry", "Biomolecules"
      ]
    },
    full: { questions: 54, duration: 180, marking: "+4 / -2" },
    subject: { questions: 18, duration: 60, marking: "+4 / -2" },
    topic: { questions: 8, duration: 16, marking: "+4 / -2" }
  },
  "NEET": {
    exam: "NEET",
    subjects: ["Biology", "Physics", "Chemistry"],
    topics: {
      "Biology": [
        "The Living World", "Biological Classification", "Plant Kingdom",
        "Animal Kingdom", "Morphology of Flowering Plants",
        "Anatomy of Flowering Plants", "Structural Organisation in Animals",
        "Cell Structure and Function", "Biomolecules", "Cell Division",
        "Transport in Plants", "Mineral Nutrition", "Photosynthesis",
        "Respiration in Plants", "Plant Growth and Development",
        "Digestion and Absorption", "Breathing and Gas Exchange",
        "Body Fluids and Circulation", "Excretory Products",
        "Locomotion and Movement", "Neural Control and Coordination",
        "Chemical Coordination", "Reproduction in Organisms",
        "Sexual Reproduction in Plants", "Human Reproduction",
        "Reproductive Health", "Principles of Inheritance",
        "Molecular Basis of Inheritance", "Evolution",
        "Human Health and Disease", "Strategies for Food Production",
        "Microbes in Human Welfare", "Biotechnology Principles",
        "Biotechnology Applications", "Organisms and Populations",
        "Ecosystem", "Biodiversity and Conservation"
      ],
      "Physics": [
        "Physical World and Measurement", "Kinematics", "Laws of Motion",
        "Work Energy and Power", "Rotational Motion", "Gravitation",
        "Properties of Bulk Matter", "Thermodynamics",
        "Kinetic Theory of Gases", "Oscillations", "Waves",
        "Electrostatics", "Current Electricity",
        "Magnetic Effects of Current", "Magnetism",
        "Electromagnetic Induction", "Alternating Current",
        "Electromagnetic Waves", "Optics",
        "Dual Nature of Matter", "Atoms and Nuclei", "Electronic Devices"
      ],
      "Chemistry": [
        "Atomic Structure", "Chemical Bonding", "Classification of Elements",
        "States of Matter", "Thermodynamics", "Equilibrium",
        "Redox Reactions", "Hydrogen", "s Block Elements",
        "p Block Elements", "Organic Chemistry Basics", "Hydrocarbons",
        "Environmental Chemistry", "Solid State", "Solutions",
        "Electrochemistry", "Chemical Kinetics", "Surface Chemistry",
        "Isolation of Elements", "d and f Block Elements",
        "Coordination Compounds", "Haloalkanes and Haloarenes",
        "Alcohols Phenols Ethers", "Aldehydes Ketones Carboxylic Acids",
        "Amines", "Biomolecules", "Polymers", "Chemistry in Everyday Life"
      ]
    },
    full: { questions: 180, duration: 200, marking: "+4 / -1" },
    subject: { questions: 45, duration: 60, marking: "+4 / -1" },
    topic: { questions: 10, duration: 20, marking: "+4 / -1" }
  }
}

const MODE_INFO = {
  full: { label: "Full Test", icon: "📋", desc: "All subjects, real pattern" },
  subject: { label: "Subject Wise", icon: "📚", desc: "One subject at a time" },
  topic: { label: "Topic Wise", icon: "🎯", desc: "One specific topic" }
}

export default function TestConfig({ student, onStart }) {
  const [examName, setExamName] = useState("JEE Mains")
  const [mode, setMode] = useState("full")
  const [subject, setSubject] = useState("Mathematics")
  const [topic, setTopic] = useState("Quadratic Equations")

  const pattern = EXAM_PATTERNS[examName]

  function handleExamChange(name) {
    setExamName(name)
    const newPattern = EXAM_PATTERNS[name]
    const firstSubject = newPattern.subjects[0]
    setSubject(firstSubject)
    setTopic(newPattern.topics[firstSubject][0])
    setMode("full")
  }

  function handleSubjectChange(s) {
    setSubject(s)
    setTopic(pattern.topics[s][0])
  }

  function getConfig() {
    const p = pattern[mode]
    return {
      exam: pattern.exam,
      examName,
      mode,
      subjects: pattern.subjects,
      subject: mode === "full" ? null : subject,
      topic: mode === "topic" ? topic : null,
      numQuestions: p.questions,
      duration: p.duration,
      marking: p.marking
    }
  }

  const config = getConfig()
  const hours = Math.floor(config.duration / 60)
  const mins = config.duration % 60
  const timeStr = hours > 0 ? `${hours}h ${mins > 0 ? mins + "m" : ""}` : `${mins}m`

  return (
    <div className="card" style={{ marginTop: 32 }}>
      <h2>👋 Hi {student.name}!</h2>
      <p style={{ marginBottom: 24, color: "#666" }}>Set up your practice test.</p>

      {/* Exam */}
      <p style={{ fontWeight: 600, marginBottom: 10 }}>Exam</p>
      <div style={{ display: "flex", gap: 10, marginBottom: 24 }}>
        {Object.keys(EXAM_PATTERNS).map(name => (
          <button key={name} onClick={() => handleExamChange(name)}
            className={examName === name ? "btn-primary" : "btn-outline"}
            style={{ width: "auto", flex: 1, fontSize: 13, padding: "10px 6px" }}>
            {name === "JEE Mains" ? "🔬 JEE Mains" : name === "JEE Advanced" ? "⚡ JEE Advanced" : "🧬 NEET"}
          </button>
        ))}
      </div>

      {/* Mode */}
      <p style={{ fontWeight: 600, marginBottom: 10 }}>Test Mode</p>
      <div style={{ display: "flex", gap: 10, marginBottom: 24 }}>
        {Object.entries(MODE_INFO).map(([key, info]) => (
          <button key={key} onClick={() => setMode(key)}
            className={mode === key ? "btn-primary" : "btn-outline"}
            style={{ width: "auto", flex: 1, fontSize: 13, padding: "10px 6px" }}>
            {info.icon} {info.label}
          </button>
        ))}
      </div>

      {/* Subject */}
      {(mode === "subject" || mode === "topic") && (
        <>
          <p style={{ fontWeight: 600, marginBottom: 10 }}>Subject</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 24 }}>
            {pattern.subjects.map(s => (
              <button key={s} onClick={() => handleSubjectChange(s)}
                className={subject === s ? "btn-primary" : "btn-outline"}
                style={{ width: "auto", padding: "8px 16px", fontSize: 14 }}>
                {s}
              </button>
            ))}
          </div>
        </>
      )}

      {/* Topic */}
      {mode === "topic" && (
        <>
          <p style={{ fontWeight: 600, marginBottom: 10 }}>Topic</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 24 }}>
            {pattern.topics[subject].map(t => (
              <button key={t} onClick={() => setTopic(t)}
                className={topic === t ? "btn-primary" : "btn-outline"}
                style={{ width: "auto", padding: "7px 12px", fontSize: 12 }}>
                {t}
              </button>
            ))}
          </div>
        </>
      )}

      {/* Summary */}
      <div style={{ background: "#f5f3ff", borderRadius: 14, padding: 20, marginBottom: 24 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <div style={{ fontSize: 12, color: "#888" }}>Exam</div>
            <div style={{ fontWeight: 600 }}>{examName}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: "#888" }}>Mode</div>
            <div style={{ fontWeight: 600 }}>{MODE_INFO[mode].label}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: "#888" }}>Questions</div>
            <div style={{ fontWeight: 600 }}>{config.numQuestions}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: "#888" }}>Duration</div>
            <div style={{ fontWeight: 600, color: "#6366f1" }}>{timeStr}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: "#888" }}>Marking</div>
            <div style={{ fontWeight: 600 }}>{config.marking}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: "#888" }}>
              {mode === "topic" ? "Topic" : mode === "subject" ? "Subject" : "Subjects"}
            </div>
            <div style={{ fontWeight: 600, fontSize: 12 }}>
              {mode === "topic" ? topic : mode === "subject" ? subject : pattern.subjects.join(", ")}
            </div>
          </div>
        </div>
      </div>

      <button className="btn-primary" onClick={() => onStart(config)}>
        Start Test →
      </button>
    </div>
  )
}