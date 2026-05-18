import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models

db = SessionLocal()

questions = [
    # ─── JEE MATHEMATICS ───────────────────────────────────────────
    {
        "subject": "mathematics", "topic": "quadratic equations",
        "difficulty": 0.4, "exam": "JEE",
        "question_text": "If the roots of the equation x² - 5x + 6 = 0 are α and β, then α² + β² equals:",
        "options": {"A": "13", "B": "25", "C": "11", "D": "7"},
        "correct_answer": "A",
        "explanation": "α + β = 5, αβ = 6. α² + β² = (α+β)² - 2αβ = 25 - 12 = 13"
    },
    {
        "subject": "mathematics", "topic": "quadratic equations",
        "difficulty": 0.6, "exam": "JEE",
        "question_text": "The number of real solutions of the equation |x|² - 3|x| + 2 = 0 is:",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "correct_answer": "D",
        "explanation": "Let |x| = t, so t² - 3t + 2 = 0 → (t-1)(t-2) = 0 → t=1 or t=2. Since t=|x|, x = ±1 or x = ±2. Total 4 real solutions."
    },
    {
        "subject": "mathematics", "topic": "trigonometry",
        "difficulty": 0.4, "exam": "JEE",
        "question_text": "The value of sin 30° × cos 60° + cos 30° × sin 60° is:",
        "options": {"A": "0", "B": "1/2", "C": "√3/2", "D": "1"},
        "correct_answer": "D",
        "explanation": "This is sin(30° + 60°) = sin 90° = 1 using the addition formula sin(A+B) = sinA cosB + cosA sinB."
    },
    {
        "subject": "mathematics", "topic": "trigonometry",
        "difficulty": 0.6, "exam": "JEE",
        "question_text": "If sin θ + cos θ = √2, then tan θ equals:",
        "options": {"A": "0", "B": "1", "C": "-1", "D": "√2"},
        "correct_answer": "B",
        "explanation": "Squaring: 1 + 2sinθcosθ = 2 → sin2θ = 1 → θ = 45°. So tan 45° = 1."
    },
    {
        "subject": "mathematics", "topic": "calculus",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "The derivative of sin²x with respect to x is:",
        "options": {"A": "2sinx", "B": "sin2x", "C": "2cosx", "D": "cos2x"},
        "correct_answer": "B",
        "explanation": "d/dx(sin²x) = 2sinx · cosx = sin2x using chain rule and double angle formula."
    },
    {
        "subject": "mathematics", "topic": "calculus",
        "difficulty": 0.7, "exam": "JEE",
        "question_text": "The value of ∫₀^π sin x dx is:",
        "options": {"A": "0", "B": "1", "C": "2", "D": "-2"},
        "correct_answer": "C",
        "explanation": "∫₀^π sin x dx = [-cos x]₀^π = -cos π + cos 0 = -(-1) + 1 = 2."
    },
    {
        "subject": "mathematics", "topic": "probability",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "Two dice are thrown simultaneously. The probability of getting a sum of 7 is:",
        "options": {"A": "1/6", "B": "1/4", "C": "5/36", "D": "7/36"},
        "correct_answer": "A",
        "explanation": "Favorable: (1,6),(2,5),(3,4),(4,3),(5,2),(6,1) = 6. Total = 36. P = 6/36 = 1/6."
    },
    {
        "subject": "mathematics", "topic": "matrices",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "If A = [[1,2],[3,4]], then det(A) equals:",
        "options": {"A": "10", "B": "-10", "C": "-2", "D": "2"},
        "correct_answer": "C",
        "explanation": "det(A) = (1×4) - (2×3) = 4 - 6 = -2."
    },
    {
        "subject": "mathematics", "topic": "complex numbers",
        "difficulty": 0.6, "exam": "JEE",
        "question_text": "The modulus of the complex number (3 + 4i) is:",
        "options": {"A": "3", "B": "4", "C": "5", "D": "7"},
        "correct_answer": "C",
        "explanation": "|3 + 4i| = √(3² + 4²) = √(9 + 16) = √25 = 5."
    },
    {
        "subject": "mathematics", "topic": "coordinate geometry",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "The distance between points (3, 4) and (0, 0) is:",
        "options": {"A": "3", "B": "4", "C": "5", "D": "7"},
        "correct_answer": "C",
        "explanation": "Distance = √((3-0)² + (4-0)²) = √(9+16) = √25 = 5."
    },

    # ─── JEE PHYSICS ────────────────────────────────────────────────
    {
        "subject": "physics", "topic": "laws of motion",
        "difficulty": 0.4, "exam": "JEE",
        "question_text": "A block of mass 5 kg is placed on a smooth surface. A force of 20 N is applied. The acceleration is:",
        "options": {"A": "2 m/s²", "B": "4 m/s²", "C": "100 m/s²", "D": "0.25 m/s²"},
        "correct_answer": "B",
        "explanation": "F = ma → a = F/m = 20/5 = 4 m/s²"
    },
    {
        "subject": "physics", "topic": "laws of motion",
        "difficulty": 0.6, "exam": "JEE",
        "question_text": "A 2 kg body moving at 10 m/s collides and sticks to a stationary 3 kg body. The combined velocity is:",
        "options": {"A": "6 m/s", "B": "4 m/s", "C": "5 m/s", "D": "2 m/s"},
        "correct_answer": "B",
        "explanation": "Conservation of momentum: 2×10 = 5×v → v = 4 m/s."
    },
    {
        "subject": "physics", "topic": "electrostatics",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "The electric field at distance r from a point charge Q is proportional to:",
        "options": {"A": "r", "B": "1/r", "C": "1/r²", "D": "r²"},
        "correct_answer": "C",
        "explanation": "By Coulomb's law, E = kQ/r². Field is inversely proportional to square of distance."
    },
    {
        "subject": "physics", "topic": "optics",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "A convex lens of focal length 20 cm forms an image of an object placed 30 cm from it. The image distance is:",
        "options": {"A": "30 cm", "B": "60 cm", "C": "12 cm", "D": "120 cm"},
        "correct_answer": "B",
        "explanation": "1/v - 1/u = 1/f → 1/v + 1/30 = 1/20 → 1/v = 1/60 → v = 60 cm."
    },
    {
        "subject": "physics", "topic": "thermodynamics",
        "difficulty": 0.6, "exam": "JEE",
        "question_text": "In an isothermal process for an ideal gas, which quantity remains constant?",
        "options": {"A": "Pressure", "B": "Volume", "C": "Temperature", "D": "Entropy"},
        "correct_answer": "C",
        "explanation": "Isothermal means constant temperature (iso = same, thermal = temperature)."
    },
    {
        "subject": "physics", "topic": "modern physics",
        "difficulty": 0.7, "exam": "JEE",
        "question_text": "The de Broglie wavelength of a particle of mass m moving with velocity v is:",
        "options": {"A": "h/mv", "B": "mv/h", "C": "h/m", "D": "hmv"},
        "correct_answer": "A",
        "explanation": "λ = h/p = h/mv where h is Planck's constant and p is momentum."
    },
    {
        "subject": "physics", "topic": "gravitation",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "The escape velocity from Earth's surface is approximately:",
        "options": {"A": "7.9 km/s", "B": "11.2 km/s", "C": "3.0 km/s", "D": "9.8 km/s"},
        "correct_answer": "B",
        "explanation": "Escape velocity = √(2gR) = √(2 × 9.8 × 6.4×10⁶) ≈ 11.2 km/s."
    },
    {
        "subject": "physics", "topic": "current electricity",
        "difficulty": 0.4, "exam": "JEE",
        "question_text": "The SI unit of electric resistance is:",
        "options": {"A": "Ampere", "B": "Volt", "C": "Ohm", "D": "Watt"},
        "correct_answer": "C",
        "explanation": "Resistance is measured in Ohms (Ω), named after Georg Simon Ohm. V = IR."
    },

    # ─── JEE CHEMISTRY ──────────────────────────────────────────────
    {
        "subject": "chemistry", "topic": "atomic structure",
        "difficulty": 0.4, "exam": "JEE",
        "question_text": "The number of electrons in the outermost shell of sodium (Na, Z=11) is:",
        "options": {"A": "1", "B": "2", "C": "3", "D": "11"},
        "correct_answer": "A",
        "explanation": "Na has configuration 2,8,1. The outermost shell has 1 electron."
    },
    {
        "subject": "chemistry", "topic": "chemical bonding",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "The hybridization of carbon in CO₂ is:",
        "options": {"A": "sp³", "B": "sp²", "C": "sp", "D": "dsp²"},
        "correct_answer": "C",
        "explanation": "CO₂ is linear (O=C=O). Carbon forms 2 sigma bonds with no lone pairs → sp hybridization."
    },
    {
        "subject": "chemistry", "topic": "organic chemistry",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "Which of the following is the IUPAC name of CH₃-CH₂-OH?",
        "options": {"A": "Methanol", "B": "Ethanol", "C": "Propanol", "D": "Ethanoic acid"},
        "correct_answer": "B",
        "explanation": "CH₃-CH₂-OH has 2 carbons with an OH group. IUPAC: Ethanol."
    },
    {
        "subject": "chemistry", "topic": "electrochemistry",
        "difficulty": 0.6, "exam": "JEE",
        "question_text": "In electrolysis of water, the gas produced at the cathode is:",
        "options": {"A": "Oxygen", "B": "Hydrogen", "C": "Ozone", "D": "Water vapor"},
        "correct_answer": "B",
        "explanation": "At cathode (reduction): 2H₂O + 2e⁻ → H₂ + 2OH⁻. Hydrogen produced at cathode."
    },
    {
        "subject": "chemistry", "topic": "thermodynamics",
        "difficulty": 0.6, "exam": "JEE",
        "question_text": "A reaction is spontaneous at all temperatures when:",
        "options": {"A": "ΔH > 0, ΔS > 0", "B": "ΔH < 0, ΔS < 0", "C": "ΔH < 0, ΔS > 0", "D": "ΔH > 0, ΔS < 0"},
        "correct_answer": "C",
        "explanation": "ΔG = ΔH - TΔS. For spontaneous ΔG < 0 at all T: need ΔH < 0 and ΔS > 0."
    },
    {
        "subject": "chemistry", "topic": "solutions",
        "difficulty": 0.5, "exam": "JEE",
        "question_text": "Which colligative property is used to determine molecular mass of polymers?",
        "options": {"A": "Boiling point elevation", "B": "Osmotic pressure", "C": "Freezing point depression", "D": "Vapour pressure lowering"},
        "correct_answer": "B",
        "explanation": "Osmotic pressure is most sensitive and used for high molecular mass substances like polymers."
    },

    # ─── NEET BIOLOGY ───────────────────────────────────────────────
    {
        "subject": "biology", "topic": "cell biology",
        "difficulty": 0.3, "exam": "NEET",
        "question_text": "The powerhouse of the cell is:",
        "options": {"A": "Nucleus", "B": "Ribosome", "C": "Mitochondria", "D": "Golgi apparatus"},
        "correct_answer": "C",
        "explanation": "Mitochondria produce ATP through cellular respiration, hence called the powerhouse of the cell."
    },
    {
        "subject": "biology", "topic": "cell biology",
        "difficulty": 0.5, "exam": "NEET",
        "question_text": "Which organelle is responsible for protein synthesis?",
        "options": {"A": "Mitochondria", "B": "Ribosome", "C": "Lysosome", "D": "Vacuole"},
        "correct_answer": "B",
        "explanation": "Ribosomes are the sites of protein synthesis — they translate mRNA into polypeptide chains."
    },
    {
        "subject": "biology", "topic": "genetics",
        "difficulty": 0.5, "exam": "NEET",
        "question_text": "In a monohybrid cross TT × tt, the ratio of tall to dwarf plants in F2 is:",
        "options": {"A": "1:1", "B": "1:2:1", "C": "3:1", "D": "2:1"},
        "correct_answer": "C",
        "explanation": "F1 = Tt. F2 = TT:Tt:tt = 1:2:1. Phenotypically tall:dwarf = 3:1."
    },
    {
        "subject": "biology", "topic": "human physiology",
        "difficulty": 0.5, "exam": "NEET",
        "question_text": "Which of the following is NOT a function of the liver?",
        "options": {"A": "Detoxification", "B": "Bile production", "C": "Insulin secretion", "D": "Glycogen storage"},
        "correct_answer": "C",
        "explanation": "Insulin is secreted by beta cells of islets of Langerhans in the pancreas, not the liver."
    },
    {
        "subject": "biology", "topic": "human physiology",
        "difficulty": 0.6, "exam": "NEET",
        "question_text": "Normal RBC count in adult human males is approximately:",
        "options": {"A": "2-3 million/mm³", "B": "4.5-5.5 million/mm³", "C": "7-8 million/mm³", "D": "1-2 million/mm³"},
        "correct_answer": "B",
        "explanation": "Normal RBC count in adult males is 4.5-5.5 million per mm³."
    },
    {
        "subject": "biology", "topic": "plant physiology",
        "difficulty": 0.5, "exam": "NEET",
        "question_text": "Photosynthesis takes place in:",
        "options": {"A": "Mitochondria", "B": "Nucleus", "C": "Chloroplast", "D": "Ribosome"},
        "correct_answer": "C",
        "explanation": "Chloroplasts contain chlorophyll and are the sites where light energy is converted to chemical energy."
    },
    {
        "subject": "biology", "topic": "evolution",
        "difficulty": 0.4, "exam": "NEET",
        "question_text": "The theory of Natural Selection was proposed by:",
        "options": {"A": "Lamarck", "B": "Mendel", "C": "Darwin", "D": "Hugo de Vries"},
        "correct_answer": "C",
        "explanation": "Charles Darwin proposed Natural Selection in 'On the Origin of Species' (1859)."
    },
    {
        "subject": "biology", "topic": "ecology",
        "difficulty": 0.5, "exam": "NEET",
        "question_text": "Which of the following is a greenhouse gas?",
        "options": {"A": "Nitrogen", "B": "Oxygen", "C": "Carbon dioxide", "D": "Argon"},
        "correct_answer": "C",
        "explanation": "CO₂ is a major greenhouse gas that traps heat in the atmosphere, contributing to global warming."
    },
    {
        "subject": "biology", "topic": "biotechnology",
        "difficulty": 0.6, "exam": "NEET",
        "question_text": "The enzyme used to cut DNA at specific sequences in recombinant DNA technology is:",
        "options": {"A": "DNA polymerase", "B": "Restriction endonuclease", "C": "Ligase", "D": "RNA polymerase"},
        "correct_answer": "B",
        "explanation": "Restriction endonucleases (restriction enzymes) cut DNA at specific palindromic sequences. They are molecular scissors."
    },
    {
        "subject": "biology", "topic": "reproduction",
        "difficulty": 0.5, "exam": "NEET",
        "question_text": "The site of fertilization in the human female reproductive system is:",
        "options": {"A": "Uterus", "B": "Ovary", "C": "Fallopian tube", "D": "Vagina"},
        "correct_answer": "C",
        "explanation": "Fertilization normally occurs in the ampulla region of the fallopian tube (oviduct)."
    },
]

# Insert all questions
inserted = 0
skipped = 0
for q in questions:
    exists = db.query(models.Question).filter(
        models.Question.question_text == q["question_text"]
    ).first()
    if exists:
        skipped += 1
        continue

    question = models.Question(
        subject=q["subject"],
        topic=q["topic"],
        difficulty=q["difficulty"],
        question_text=q["question_text"],
        options=q["options"],
        correct_answer=q["correct_answer"],
        explanation=q["explanation"]
    )
    db.add(question)
    inserted += 1

db.commit()
db.close()

print(f"Done! Inserted {inserted} questions, skipped {skipped} duplicates.")
print(f"Total: {len(questions)} questions across JEE Math, Physics, Chemistry + NEET Biology")
