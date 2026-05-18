import sys, os, json, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, GROQ_API_KEY
from app import models
from groq import Groq

client = Groq(api_key=GROQ_API_KEY)
db = SessionLocal()

QUESTIONS_TO_GENERATE = [
    # (subject, topic, difficulty, exam)
    ("mathematics", "quadratic equations", 0.3, "JEE"),
    ("mathematics", "quadratic equations", 0.5, "JEE"),
    ("mathematics", "quadratic equations", 0.7, "JEE"),
    ("mathematics", "trigonometry", 0.3, "JEE"),
    ("mathematics", "trigonometry", 0.5, "JEE"),
    ("mathematics", "trigonometry", 0.7, "JEE"),
    ("mathematics", "calculus", 0.3, "JEE"),
    ("mathematics", "calculus", 0.5, "JEE"),
    ("mathematics", "calculus", 0.7, "JEE"),
    ("mathematics", "probability", 0.3, "JEE"),
    ("mathematics", "probability", 0.5, "JEE"),
    ("mathematics", "matrices", 0.4, "JEE"),
    ("mathematics", "matrices", 0.6, "JEE"),
    ("mathematics", "complex numbers", 0.4, "JEE"),
    ("mathematics", "complex numbers", 0.7, "JEE"),
    ("mathematics", "coordinate geometry", 0.4, "JEE"),
    ("mathematics", "coordinate geometry", 0.6, "JEE"),
    ("mathematics", "binomial theorem", 0.4, "JEE"),
    ("mathematics", "binomial theorem", 0.6, "JEE"),
    ("physics", "laws of motion", 0.3, "JEE"),
    ("physics", "laws of motion", 0.5, "JEE"),
    ("physics", "laws of motion", 0.7, "JEE"),
    ("physics", "electrostatics", 0.3, "JEE"),
    ("physics", "electrostatics", 0.5, "JEE"),
    ("physics", "electrostatics", 0.7, "JEE"),
    ("physics", "optics", 0.3, "JEE"),
    ("physics", "optics", 0.5, "JEE"),
    ("physics", "optics", 0.7, "JEE"),
    ("physics", "thermodynamics", 0.4, "JEE"),
    ("physics", "thermodynamics", 0.6, "JEE"),
    ("physics", "waves", 0.4, "JEE"),
    ("physics", "waves", 0.6, "JEE"),
    ("physics", "gravitation", 0.4, "JEE"),
    ("physics", "gravitation", 0.6, "JEE"),
    ("physics", "modern physics", 0.5, "JEE"),
    ("physics", "modern physics", 0.7, "JEE"),
    ("physics", "current electricity", 0.4, "JEE"),
    ("physics", "current electricity", 0.6, "JEE"),
    ("chemistry", "atomic structure", 0.3, "JEE"),
    ("chemistry", "atomic structure", 0.5, "JEE"),
    ("chemistry", "chemical bonding", 0.3, "JEE"),
    ("chemistry", "chemical bonding", 0.5, "JEE"),
    ("chemistry", "chemical bonding", 0.7, "JEE"),
    ("chemistry", "equilibrium", 0.4, "JEE"),
    ("chemistry", "equilibrium", 0.6, "JEE"),
    ("chemistry", "organic chemistry", 0.4, "JEE"),
    ("chemistry", "organic chemistry", 0.6, "JEE"),
    ("chemistry", "organic chemistry", 0.8, "JEE"),
    ("chemistry", "electrochemistry", 0.4, "JEE"),
    ("chemistry", "electrochemistry", 0.6, "JEE"),
    ("chemistry", "thermodynamics", 0.4, "JEE"),
    ("chemistry", "thermodynamics", 0.6, "JEE"),
    ("chemistry", "solutions", 0.4, "JEE"),
    ("chemistry", "solutions", 0.6, "JEE"),
    ("chemistry", "coordination compounds", 0.5, "JEE"),
    ("chemistry", "coordination compounds", 0.7, "JEE"),
    ("biology", "cell biology", 0.3, "NEET"),
    ("biology", "cell biology", 0.5, "NEET"),
    ("biology", "cell biology", 0.7, "NEET"),
    ("biology", "genetics", 0.3, "NEET"),
    ("biology", "genetics", 0.5, "NEET"),
    ("biology", "genetics", 0.7, "NEET"),
    ("biology", "evolution", 0.3, "NEET"),
    ("biology", "evolution", 0.5, "NEET"),
    ("biology", "human physiology", 0.3, "NEET"),
    ("biology", "human physiology", 0.5, "NEET"),
    ("biology", "human physiology", 0.7, "NEET"),
    ("biology", "plant physiology", 0.3, "NEET"),
    ("biology", "plant physiology", 0.5, "NEET"),
    ("biology", "reproduction", 0.4, "NEET"),
    ("biology", "reproduction", 0.6, "NEET"),
    ("biology", "ecology", 0.4, "NEET"),
    ("biology", "ecology", 0.6, "NEET"),
    ("biology", "biotechnology", 0.5, "NEET"),
    ("biology", "biotechnology", 0.7, "NEET"),
]

def generate_question(subject, topic, difficulty, exam):
    level = "easy" if difficulty < 0.4 else "medium" if difficulty < 0.7 else "hard"
    prompt = f"""Generate a {level} difficulty MCQ for {exam} exam on topic "{topic}" in {subject}.
Rules: 4 options (A,B,C,D), one correct answer, accurate content, complete sentences.
Respond ONLY with valid JSON, no markdown:
{{"question_text": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "A", "explanation": "..."}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

inserted = 0
failed = 0

for i, (subject, topic, difficulty, exam) in enumerate(QUESTIONS_TO_GENERATE):
    try:
        print(f"[{i+1}/{len(QUESTIONS_TO_GENERATE)}] Generating: {subject} - {topic} ({difficulty})...")
        generated = generate_question(subject, topic, difficulty, exam)

        question = models.Question(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            question_text=generated["question_text"],
            options=generated["options"],
            correct_answer=generated["correct_answer"],
            explanation=generated["explanation"]
        )
        db.add(question)
        db.commit()
        inserted += 1
        print(f"  ✅ Done")
        time.sleep(1)  # avoid rate limiting

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        failed += 1
        time.sleep(2)

db.close()
print(f"\nDone! Inserted {inserted}, Failed {failed}")
print(f"Your DB now has plenty of questions for full JEE/NEET tests!")