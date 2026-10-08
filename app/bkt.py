# Bayesian Knowledge Tracing (BKT) Model
# Estimates probability that a student has mastered a topic
# based on their sequence of correct/incorrect answers.

# Default BKT parameters (can be tuned per topic later)
DEFAULT_PARAMS = {
    "p_l0": 0.30,   # Prior probability of knowing the topic
    "p_t":  0.09,   # Probability of learning after each attempt
    "p_g":  0.20,   # Probability of guessing correctly (without knowing)
    "p_s":  0.10,   # Probability of slipping (wrong despite knowing)
}


def update_mastery(p_mastered: float, correct: bool, params: dict = None) -> float:
    if params is None:
        params = DEFAULT_PARAMS

    p_l = p_mastered
    p_t = params["p_t"]
    p_g = params["p_g"]
    p_s = params["p_s"]

    if correct:
        numerator   = p_l * (1 - p_s)
        denominator = p_l * (1 - p_s) + (1 - p_l) * p_g
    else:
        numerator   = p_l * p_s
        denominator = p_l * p_s + (1 - p_l) * (1 - p_g)

    if denominator == 0:
        p_l_given_obs = p_l
    else:
        p_l_given_obs = numerator / denominator

    p_l_new = p_l_given_obs + (1 - p_l_given_obs) * p_t
    return max(0.0, min(1.0, p_l_new))


def compute_mastery_from_attempts(attempts: list, params: dict = None) -> float:
    if params is None:
        params = DEFAULT_PARAMS

    p_mastered = params["p_l0"]
    for correct in attempts:
        p_mastered = update_mastery(p_mastered, correct, params)
    return p_mastered


def compute_mastery_by_topic(questions_data: list, params: dict = None) -> dict:
    if params is None:
        params = DEFAULT_PARAMS

    topic_attempts: dict[str, list] = {}
    for q in questions_data:
        topic = q.get("topic", "Unknown")
        correct = bool(q.get("correct", False))
        topic_attempts.setdefault(topic, []).append(correct)

    mastery = {}
    for topic, attempts in topic_attempts.items():
        mastery[topic] = compute_mastery_from_attempts(attempts, params)

    return mastery
