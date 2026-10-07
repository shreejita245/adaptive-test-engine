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

## ML Layer — Mastery Insights

A cohort-level analytics layer on top of the same attempt data, giving faculty an explainable view of student risk — not just per-student adaptive practice, but which students are struggling, on which topics, and why:

- **XGBoost** — predicts per-attempt risk, evaluated via 5-fold cross-validation
- **SHAP** — explains which factors (mastery level, recent accuracy, topic difficulty) drove each prediction
- **Isolation Forest** — flags attempts that look statistically unusual for a given student
- **Faculty dashboard** — cohort weak-topic heatmap and at-risk student list, served via a `/insights` API

See [`analytics/README.md`](analytics/README.md) for the full pipeline, the honest findings on what the modeling results do and don't support at this data scale (~280 attempts, ~25 students), and how to run it.

---

## Roadmap

- [x] FastAPI backend
- [x] Supabase database with 7,700+ JEE PYQs
- [x] Bayesian Knowledge Tracing
- [x] Groq AI explanations
- [x] NTA-style exam simulation
- [x] User authentication
- [x] XGBoost performance prediction
- [x] SHAP explainability layer
- [x] Isolation Forest anomaly detection
- [x] Faculty analytics dashboard
- [ ] Faculty-specific role/access control on the Insights tab

---

## Author

**Shreejita Saha**   
B.Tech CSE (Data Science) — VIT Chennai  
[LinkedIn](https://www.linkedin.com/in/shreejita-saha-19053a315) • [GitHub](https://github.com/shreejita245)
