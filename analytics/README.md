# Mastery Insights — Analytics Layer

Cohort-level risk analytics built on top of the Adaptive Mock Test Engine.
Rather than only showing each student their own adaptive progress, this
layer looks across the whole cohort's attempt history and tells faculty
*which* students are struggling, *on which topics*, and *why* — using a
gradient-boosted risk model (XGBoost), SHAP explanations, and Isolation
Forest anomaly detection.

## Why attempt-level, not student-level

The original plan was a student-level model (one row per student, predict
who's at risk). The real data — ~25 students, most with under 15 attempts,
278 attempts total — isn't enough to support that: 25 rows is too few to
train or validate anything. The project pivoted to attempt-level prediction
(one row per question attempt, predict correct/incorrect), which gives 278
rows to work with. Deep learning was also dropped from the core scope for
the same reason and kept only as a stretch comparison (see
`train_nn_comparison.py`).

## Pipeline — run in this order

```
python build_features.py          # pulls Supabase data -> feature_table.csv
python train_models.py            # trains + evaluates the core XGBoost model
python shap_analysis.py           # explainability layer -> per-attempt SHAP values
python anomaly_detection.py       # Isolation Forest -> per-attempt anomaly flags
python aggregate_insights.py      # rolls both up into per-student/per-topic JSON
python verify_pipeline.py         # end-to-end sanity check on all of the above
```

Each script prints what it did and writes its output as a file in
`analytics/`, so you can inspect intermediate results at any stage. Install
dependencies first: `pip install -r analytics/requirements.txt` (separate
from the root `requirements.txt`, which only covers the FastAPI app).

### What each stage produces

| Stage | Script | Output | Feeds into |
|---|---|---|---|
| Feature engineering | `build_features.py` | `feature_table.csv` (278 rows) | everything downstream |
| Core model | `train_models.py` | printed metrics only | (validates the modeling approach) |
| Explainability | `shap_analysis.py` | `shap_attempt_explanations.csv`, `shap_feature_importance.csv`, `shap_summary_bar.png`, `xgb_model_final.pkl` | `aggregate_insights.py` |
| Anomaly detection | `anomaly_detection.py` | `anomaly_scores.csv`, `anomaly_counts_by_student.csv` | `aggregate_insights.py` |
| Aggregation | `aggregate_insights.py` | `student_insights.json`, `topic_insights.json` | the `/insights` API |
| Verification | `verify_pipeline.py` | pass/fail report | — |

Stretch additions (synthetic data + NN comparison), documented separately:
`simulate_students.py` → `synthetic_feature_table.csv`, `combine_datasets.py`
→ `combined_feature_table.csv`, `train_combined.py` and
`train_nn_comparison.py` for the XGBoost-vs-NN comparison on the combined
dataset.

## Serving layer

`app/routers/insights.py` (mounted at `/insights` in `app/main.py`) reads
`student_insights.json` and `topic_insights.json` directly off disk and
serves them as JSON. It's deliberately simple: no retraining on request, no
background jobs, no database write-back. Re-run the pipeline whenever you
want fresh numbers, restart the API (or just let it re-read the files — it
loads fresh on every request since they're small), and the endpoints pick
up the new numbers automatically.

Endpoints:

- `GET /insights/cohort-summary` — headline numbers (student/attempt/topic counts, overall accuracy, overall risk, anomaly count)
- `GET /insights/students/at-risk?risk_level=High&limit=50` — risk-sorted student list, optionally filtered
- `GET /insights/students/{student_id}` — one student's full explanation (weak topics, SHAP-driven mistake factors, anomaly flags)
- `GET /insights/topics/heatmap` — every topic's accuracy/risk for the cohort heatmap
- `GET /insights/topics/{topic}` — one topic's detail

This is separate from the existing `app/routers/analytics.py`, which serves
live per-student BKT progress from the database — that one answers "how is
this one student doing right now," this one answers "which students/topics
need faculty attention, and why."

## Frontend

`frontend/src/components/FacultyDashboard.jsx`, reachable via the
"🧭 Insights" tab in the topbar (and profile dropdown) once logged in. Two
views: an at-risk student list with expandable per-student detail (weak
topics, SHAP factors, anomaly flags), and a topic risk heatmap (grid or
table view). Shows a friendly empty state if the pipeline hasn't been run
yet, rather than a raw fetch error.

**Known limitation:** there's no faculty-specific role or access control —
any logged-in student can currently open the Insights tab. The existing app
has no role system at all, so adding one is out of scope for the current
submission, but it should be the first thing added before any real
deployment (which is explicitly out of scope for this project anyway).

## Honest findings — read this before presenting results

This project deliberately documents what the data actually supports, rather
than only the flattering numbers:

- **XGBoost, real data only:** single-split accuracy 53–62% depending on
  config; 5-fold CV mean 58.6% (± 9.7%) — *below* the 71.4% naive baseline
  (majority class = "incorrect"). This is a small-data and class-imbalance
  finding, not a bug — flagged clearly rather than hidden.
- **XGBoost, combined real + synthetic data:** single-split 63% (above the
  56.9% baseline here), but 5-fold CV only 52.6% — lower than real-data-only.
  Likely synthetic/real domain shift; documented, not resolved.
- **Feedforward NN vs. XGBoost, combined data:** NN edges out XGBoost
  slightly (64.2% vs 63.0% single-split, 57.9% vs 52.6% CV), but the margin
  is well within noise at this sample size. Neither model reliably clears
  baseline under cross-validation — the binding constraint is data volume,
  not model architecture.
- **Isolation Forest:** `contamination=0.1` is a starting assumption, not a
  measured rate — there's no ground truth for "how many attempts are
  actually anomalous" with 278 rows. The flagged attempts look sane on
  manual inspection (e.g. a student answering much slower than their own
  norm and getting it wrong), which is reassuring but not proof.
- **Risk banding (High/Medium/Low):** computed as tertiles across whoever
  is currently in the cohort — a *relative* ranking within this specific
  group of ~25–30 students, not a calibrated absolute risk score. It will
  need re-deriving as the student count grows.

The right way to present this: XGBoost was chosen as the production model
over the NN not because it's dramatically more accurate (it isn't), but
because it performs equal-or-better, trains faster, and has native,
well-supported explainability tooling (SHAP) — which matters more for a
project literally named "Explainable Cohort Analytics" than a marginal
accuracy gain would.

## Security note

While building the aggregation layer, a hardcoded Supabase database
password and Groq API key were found still present as a fallback default in
`app/database.py` — despite being reported fixed earlier — and `.env`
(containing both as live values) was found tracked in git since the initial
commit, meaning both credentials have been visible on the public GitHub repo.
`app/database.py` has been corrected to require the environment variables
with no fallback, `.gitignore` now excludes `.env`, and `.env` has been
untracked from git locally. **This is not complete until:** both credentials
are rotated (again, regardless of any earlier rotation) and the fix is
committed and pushed — neither has been done automatically; both need
explicit confirmation before touching the public repository's history.
