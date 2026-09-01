"""
Cohort-level risk/explainability endpoints for Mastery Insights.

Named "insights" (not "analytics") because app/routers/analytics.py already
exists and covers live per-student BKT progress from the database — this
router is deliberately separate: it serves the offline ML pipeline's output
(XGBoost risk + SHAP explanations + Isolation Forest anomalies), read from
the JSON files analytics/aggregate_insights.py produces, not the live DB.

That's a conscious simplification for the "no deployment" core scope: the
ML pipeline runs as a batch job (feature build -> train -> SHAP -> anomaly
detection -> aggregate) whenever you want fresh numbers, and this router
just serves whatever the last run produced. No retraining on request, no
background jobs. Re-run the analytics/ pipeline and restart the API (or
add a refresh endpoint later) to update the numbers.
"""

from pathlib import Path
from typing import Optional
import json

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/insights", tags=["insights"])

# app/routers/insights.py -> app/routers -> app -> project root -> analytics/
ANALYTICS_DIR = Path(__file__).resolve().parent.parent.parent / "analytics"
STUDENT_INSIGHTS_FILE = ANALYTICS_DIR / "student_insights.json"
TOPIC_INSIGHTS_FILE = ANALYTICS_DIR / "topic_insights.json"


def _load_json(path: Path):
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                f"{path.name} not found. Run the analytics pipeline first: "
                f"build_features.py -> train_models.py -> shap_analysis.py "
                f"-> anomaly_detection.py -> aggregate_insights.py"
            ),
        )
    with open(path) as f:
        return json.load(f)


# Loaded fresh on every request rather than cached: these files are small
# (tens of KB for ~30 students) and are only refreshed by manually re-running
# the batch pipeline, so a cache would just risk serving stale data after a
# re-run without adding meaningful performance benefit.


@router.get("/cohort-summary")
def get_cohort_summary():
    """High-level numbers for the dashboard header: student/attempt/topic
    counts, overall accuracy, overall risk, total anomalies flagged."""
    data = _load_json(STUDENT_INSIGHTS_FILE)
    return {
        "generated_at": data["generated_at"],
        **data["cohort_summary"],
    }


@router.get("/students/at-risk")
def get_at_risk_students(
    risk_level: Optional[str] = Query(
        None, description="Filter to 'High', 'Medium', or 'Low'"
    ),
    limit: int = Query(50, ge=1, le=500),
):
    """Cohort risk list, sorted highest-risk first — the core input for the
    dashboard's at-risk student list."""
    data = _load_json(STUDENT_INSIGHTS_FILE)
    students = data["students"]

    if risk_level:
        normalized = risk_level.strip().capitalize()
        if normalized not in ("High", "Medium", "Low"):
            raise HTTPException(
                status_code=400,
                detail="risk_level must be one of: High, Medium, Low",
            )
        students = [s for s in students if s["risk_level"] == normalized]

    return {
        "generated_at": data["generated_at"],
        "count": len(students[:limit]),
        "students": students[:limit],
    }


@router.get("/students/{student_id}")
def get_student_insight(student_id: int):
    """Full risk explanation for one student: weak topics, the SHAP factors
    behind their mistakes, and any anomaly flags."""
    data = _load_json(STUDENT_INSIGHTS_FILE)
    for student in data["students"]:
        if student["student_id"] == student_id:
            return student
    raise HTTPException(
        status_code=404,
        detail=f"No insights found for student_id={student_id}. Either this "
               f"student has no attempts, or the analytics pipeline hasn't "
               f"been re-run since they were added.",
    )


@router.get("/topics/heatmap")
def get_topic_heatmap():
    """Cohort weak-topic heatmap data: every topic with accuracy, avg risk,
    risk level, and the top factors driving mistakes on it."""
    data = _load_json(TOPIC_INSIGHTS_FILE)
    return {
        "generated_at": data["generated_at"],
        "topics": data["topics"],
    }


@router.get("/topics/{topic}")
def get_topic_insight(topic: str):
    """Detail for a single topic, matched case-insensitively since topic
    names come from free-text question metadata."""
    data = _load_json(TOPIC_INSIGHTS_FILE)
    for t in data["topics"]:
        if t["topic"].lower() == topic.lower():
            return t
    raise HTTPException(
        status_code=404, detail=f"No insights found for topic='{topic}'"
    )
