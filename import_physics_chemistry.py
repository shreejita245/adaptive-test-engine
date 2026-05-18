import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jee_data_base import DataBase, Filter
from app.database import SessionLocal
from app import models

db_session = SessionLocal()

PHYSICS_CHAPTERS = {
    "communication-systems": "modern physics",
    "atoms-and-nuclei": "atoms and nuclei",
    "heat-and-thermodynamics": "thermodynamics",
    "electrostatics": "electrostatics",
    "motion-in-a-plane": "kinematics",
    "motion-in-a-straight-line": "kinematics",
    "dual-nature-of-radiation": "dual nature of radiation",
    "magnetic-properties-of-matter": "magnetism",
    "gravitation": "gravitation",
    "wave-optics": "optics",
    "capacitor": "electrostatics",
    "waves": "waves",
    "magnetics": "magnetic effects of current",
    "laws-of-motion": "laws of motion",
    "electromagnetic-induction": "electromagnetic induction",
    "rotational-motion": "rotational motion",
    "gaseous-state": "kinetic theory of gases",
}

CHEMISTRY_CHAPTERS = {
    "hydrocarbons": "organic chemistry",
    "coordination-compounds": "coordination compounds",
    "ionic-equilibrium": "equilibrium",
    "structure-of-atom": "atomic structure",
    "periodic-table-and-periodicity": "periodic table",
    "hydrogen": "hydrogen",
    "solid-state": "solid state",
    "haloalkanes-and-haloarenes": "haloalkanes and haloarenes",
    "chemical-kinetics-and-nuclear-chemistry": "chemical kinetics",
    "surface-chemistry": "surface chemistry",
    "alcohols-phenols-and-ethers": "alcohols phenols and ethers",
    "practical-organic-chemistry": "organic chemistry",
    "redox-reactions": "redox reactions",
    "p-block-elements": "p block elements",
    "chemistry-in-everyday-life": "organic chemistry",
    "s-block-elements": "s block elements",
    "basics-of-organic-chemistry": "general organic chemistry",
    "thermodynamics": "thermodynamics",
    "salt-analysis": "equilibrium",
    "aldehydes-ketones-and-carboxylic-acids": "aldehydes and ketones",
    "some-basic-concepts-of-chemistry": "atomic structure",
    "isolation-of-elements": "metallurgy",
    "solutions": "solutions",
    "chemical-equilibrium": "equilibrium",
    "environmental-chemistry": "organic chemistry",
    "compounds-containing-nitrogen": "amines",
    "electrochemistry": "electrochemistry",
    "polymers": "organic chemistry",
    "d-and-f-block-elements": "d and f block elements",
    "chemical-bonding-and-molecular-structure": "chemical bonding",
    "biomolecules": "biomolecules",
}

DIFFICULTY_MAP = {
    "easy": 0.3,
    "medium": 0.6,
    "hard": 0.9
}

jee_db = DataBase()
f = Filter(jee_db.chapters_dict)

inserted = 0
skipped_img = 0
skipped_type = 0
skipped_dup = 0

def import_chapters(chapter_map, subject_name):
    global inserted, skipped_img, skipped_type, skipped_dup

    for chapter_slug, topic_name in chapter_map.items():
        try:
            f.reset()
            f.by_chapter(chapter_slug)
            questions = f.current_set
            print(f"\n📚 {chapter_slug} → {topic_name}: {len(questions)} questions")

            for q in questions:
                if q.isImgQuestion or any(q.isImgOption):
                    skipped_img += 1
                    continue

                if q.type != "mcq":
                    skipped_type += 1
                    continue

                if not q.correct_options:
                    skipped_type += 1
                    continue

                options = {}
                for opt in q.options:
                    options[opt["identifier"]] = opt["content"]

                if len(options) != 4:
                    skipped_type += 1
                    continue

                correct_answer = q.correct_options[0]
                if correct_answer not in ["A", "B", "C", "D"]:
                    skipped_type += 1
                    continue

                difficulty = DIFFICULTY_MAP.get(q.difficulty, 0.5)
                question_text = q.question.strip()

                exists = db_session.query(models.Question).filter(
                    models.Question.question_text == question_text
                ).first()
                if exists:
                    skipped_dup += 1
                    continue

                question = models.Question(
                    subject=subject_name,
                    topic=topic_name,
                    difficulty=difficulty,
                    question_text=question_text,
                    options=options,
                    correct_answer=correct_answer,
                    explanation=q.explanation if q.explanation else ""
                )
                db_session.add(question)
                inserted += 1

            db_session.commit()
            print(f"  ✅ Inserted so far: {inserted}")

        except Exception as e:
            print(f"  ❌ Error on {chapter_slug}: {e}")

print("=== Importing Physics ===")
import_chapters(PHYSICS_CHAPTERS, "physics")

print("\n=== Importing Chemistry ===")
import_chapters(CHEMISTRY_CHAPTERS, "chemistry")

db_session.close()
print(f"\n🎉 Done!")
print(f"✅ Inserted: {inserted}")
print(f"⏭ Skipped (image): {skipped_img}")
print(f"⏭ Skipped (non-MCQ): {skipped_type}")
print(f"⏭ Skipped (duplicate): {skipped_dup}")