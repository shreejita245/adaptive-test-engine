import sys, os, re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jee_data_base import DataBase, Filter
from app.database import SessionLocal
from app import models

db_session = SessionLocal()

ALL_CHAPTERS = {
    # Physics
    "communication-systems": ("physics", "modern physics"),
    "atoms-and-nuclei": ("physics", "atoms and nuclei"),
    "heat-and-thermodynamics": ("physics", "thermodynamics"),
    "electrostatics": ("physics", "electrostatics"),
    "motion-in-a-plane": ("physics", "kinematics"),
    "motion-in-a-straight-line": ("physics", "kinematics"),
    "dual-nature-of-radiation": ("physics", "dual nature of radiation"),
    "gravitation": ("physics", "gravitation"),
    "wave-optics": ("physics", "optics"),
    "capacitor": ("physics", "electrostatics"),
    "waves": ("physics", "waves"),
    "magnetics": ("physics", "magnetic effects of current"),
    "laws-of-motion": ("physics", "laws of motion"),
    "electromagnetic-induction": ("physics", "electromagnetic induction"),
    "rotational-motion": ("physics", "rotational motion"),
    "gaseous-state": ("physics", "kinetic theory of gases"),
    # Chemistry
    "hydrocarbons": ("chemistry", "organic chemistry"),
    "coordination-compounds": ("chemistry", "coordination compounds"),
    "ionic-equilibrium": ("chemistry", "equilibrium"),
    "structure-of-atom": ("chemistry", "atomic structure"),
    "electrochemistry": ("chemistry", "electrochemistry"),
    "chemical-bonding-and-molecular-structure": ("chemistry", "chemical bonding"),
    "thermodynamics": ("chemistry", "thermodynamics"),
    "solutions": ("chemistry", "solutions"),
    "chemical-equilibrium": ("chemistry", "equilibrium"),
    "p-block-elements": ("chemistry", "p block elements"),
    "d-and-f-block-elements": ("chemistry", "d and f block elements"),
    "aldehydes-ketones-and-carboxylic-acids": ("chemistry", "aldehydes and ketones"),
    "biomolecules": ("chemistry", "biomolecules"),
    # Math
    "probability": ("mathematics", "probability"),
    "trigonometric-ratio-and-identites": ("mathematics", "trigonometry"),
    "matrices-and-determinants": ("mathematics", "matrices"),
    "differentiation": ("mathematics", "calculus"),
    "definite-integration": ("mathematics", "definite integration"),
    "3d-geometry": ("mathematics", "3d geometry"),
    "vector-algebra": ("mathematics", "vector algebra"),
    "straight-lines-and-pair-of-straight-lines": ("mathematics", "coordinate geometry"),
}

DIFFICULTY_MAP = {"easy": 0.3, "medium": 0.6, "hard": 0.9}

def extract_img_url(html):
    match = re.search(r'src="(https://[^"]+)"', html)
    return match.group(1) if match else None

jee_db = DataBase()
f = Filter(jee_db.chapters_dict)

inserted = 0
skipped = 0

for chapter_slug, (subject, topic) in ALL_CHAPTERS.items():
    try:
        f.reset()
        f.by_chapter(chapter_slug)
        questions = f.current_set

        # only image questions this time
        img_questions = [q for q in questions if q.isImgQuestion and q.type == "mcq"]
        print(f"\n📚 {chapter_slug}: {len(img_questions)} image questions")

        for q in img_questions:
            if not q.correct_options:
                skipped += 1
                continue

            correct_answer = q.correct_options[0]
            if correct_answer not in ["A", "B", "C", "D"]:
                skipped += 1
                continue

            # extract image URL from question HTML
            img_url = extract_img_url(q.question)
            if not img_url:
                skipped += 1
                continue

            # build question text with image tag
            question_text = f'<img src="{img_url}" style="max-width:100%;margin:8px 0;" /><br/>{q.question}'
            # clean up nested img tags if already in text
            question_text = re.sub(r'<img[^>]+loading=[^>]+>', '', q.question)
            question_text = f'<img src="{img_url}" style="max-width:100%;border-radius:8px;margin:10px 0;" /><br/>{question_text}'

            # build options
            options = {}
            for opt in q.options:
                content = opt["content"]
                # handle image options
                if opt.get("isImgOption") or "<img" in content:
                    opt_url = extract_img_url(content)
                    if opt_url:
                        content = f'<img src="{opt_url}" style="max-height:60px;" />'
                options[opt["identifier"]] = content

            if len(options) != 4:
                skipped += 1
                continue

            # check duplicate
            exists = db_session.query(models.Question).filter(
                models.Question.question_text == question_text
            ).first()
            if exists:
                skipped += 1
                continue

            difficulty = DIFFICULTY_MAP.get(q.difficulty, 0.5)
            explanation = q.explanation if q.explanation else ""
            # extract explanation image if present
            if explanation and "<img" in explanation:
                exp_url = extract_img_url(explanation)
                if exp_url:
                    explanation = re.sub(r'<img[^>]+>', '', explanation)
                    explanation = f'<img src="{exp_url}" style="max-width:100%;margin:8px 0;" /><br/>{explanation}'

            question = models.Question(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                question_text=question_text,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation
            )
            db_session.add(question)
            inserted += 1

        db_session.commit()
        print(f"  ✅ Inserted so far: {inserted}")

    except Exception as e:
        print(f"  ❌ Error: {e}")

db_session.close()
print(f"\n🎉 Done! Inserted: {inserted}, Skipped: {skipped}")