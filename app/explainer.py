from groq import Groq
from app.database import GROQ_API_KEY
import json

client = Groq(api_key=GROQ_API_KEY)


def generate_explanation(question_text: str, correct_answer: str, selected_answer: str, options: dict) -> str:
    prompt = f"""A student answered a question wrong. Help them understand why.

Question: {question_text}
Options: A: {options.get('A')} | B: {options.get('B')} | C: {options.get('C')} | D: {options.get('D')}
Student answered: {selected_answer}
Correct answer: {correct_answer}

Give a clear, friendly, step-by-step explanation under 80 words."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content


def generate_test_report(attempts_data: list) -> str:
    questions_summary = ""
    for i, a in enumerate(attempts_data):
        status = "✅ Correct" if a["is_correct"] else "❌ Wrong"
        questions_summary += f"""
Q{i+1}: {a["question_text"]}
Your answer: {a["selected_answer"]} | Correct: {a["correct_answer"]}
Status: {status}
"""

    prompt = f"""A student just completed a JEE/NEET practice test. Here are their results:

{questions_summary}

Write a detailed, encouraging test report that:
1. Gives an overall performance summary
2. For each WRONG answer, explains the correct concept clearly in 2-3 sentences
3. Identifies which topics need more practice
4. Ends with 2-3 specific study tips

Be like a friendly, knowledgeable tutor. Use simple language."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content
def generate_question(subject: str, topic: str, difficulty: float, standard: str = "JEE") -> dict:
    level = "easy" if difficulty < 0.4 else "medium" if difficulty < 0.7 else "hard"
    exam_context = {
        "JEE": "JEE Main/Advanced Indian engineering entrance exam. Follow NTA pattern.",
        "NEET": "NEET Indian medical entrance exam. Follow NCERT syllabus and NTA pattern."
    }.get(standard, "JEE Main")

    prompt = f"""Generate a {level} difficulty MCQ for {standard} exam on topic "{topic}" in {subject}.
Context: {exam_context}
Rules: 4 options (A,B,C,D), one correct answer, accurate content, complete sentences only.
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