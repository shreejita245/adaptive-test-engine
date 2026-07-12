# Adaptive Mock Test Engine for JEE/NEET Preparation

An intelligent exam-preparation platform that adapts to each student's knowledge level in real time, powered by Bayesian Knowledge Tracing and AI-generated explanations.

---

## What It Does

- **Adaptive questioning** — Tracks student mastery per topic and adjusts question difficulty automatically using BKT
- **AI explanations** — Wrong answer? Get an instant explanation powered by Groq's Llama 3.3 70B
- **Real exam questions** — Database of ~7,700 actual JEE Mains previous-year questions
- **NTA-style interface** — Timed sections mirroring the real JEE/NEET experience
- **Secure sessions** — User authentication via Supabase Auth

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | Supabase (PostgreSQL) |
| AI Model | Groq — Llama 3.3 70B |
| Algorithm | Bayesian Knowledge Tracing (BKT) |
| Auth | Supabase Auth |

---

## ML Layer — In Progress

Currently implementing a faculty-facing analytics dashboard using:

- **XGBoost** — predict student performance and identify at-risk learners
- **SHAP** — explain which topics most influence a student's score
- **Isolation Forest** — detect anomalous answer patterns

---

## Roadmap

- [x] FastAPI backend
- [x] Supabase database with 7,700+ JEE PYQs
- [x] Bayesian Knowledge Tracing
- [x] Groq AI explanations
- [x] NTA-style exam simulation
- [x] User authentication
- [ ] XGBoost performance prediction
- [ ] SHAP explainability layer
- [ ] Isolation Forest anomaly detection
- [ ] Faculty analytics dashboard

---

## Author

**Shreejita Saha**  
B.Tech CSE (Data Science) — VIT Chennai  
[LinkedIn](https://www.linkedin.com/in/shreejita-saha-19053a315) • [GitHub](https://github.com/shreejita245)
