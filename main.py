# =========================================================
# HOLI - API SIMPLE ET STABLE
# =========================================================

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from collections import defaultdict
import os

# =========================================================
# INITIALISATION
# =========================================================

app = FastAPI()

# =========================================================
# USER MODEL
# =========================================================

class UserQuiz(BaseModel):
    firstname: str
    mainGoal: str
    mood: List[str]
    sleepQuality: str
    weeklySport: int

# =========================================================
# SCORES
# =========================================================

QUESTION_SCORES = {
    "mood": 10,
    "sleep": 10,
    "sport": 5
}

# =========================================================
# RULES
# =========================================================

MOOD_RULES = {
    "Stressé(e)": "serenite",
    "Fatigué(e)": "recuperation",
    "Anxieux(se)": "lacher_prise",
    "Bien": "equilibre"
}

SLEEP_RULES = {
    "Très bien": "equilibre",
    "Je me réveille fatigué(e)": "recuperation",
    "J'ai du mal à m'endormir": "lacher_prise"
}

SPORT_RULES = {
    0: "dynamisme",
    1: "dynamisme",
    2: "equilibre",
    3: "equilibre",
    4: "recuperation",
    5: "recuperation"
}

# =========================================================
# THÉRAPIES
# =========================================================

BESOIN_THERAPIES = {
    "serenite": ["meditation", "respiration"],
    "recuperation": ["yoga", "autohypnose"],
    "lacher_prise": ["journaling", "respiration"],
    "equilibre": ["renforcement", "affirmation_positive"],
    "dynamisme": ["qigong", "respiration"]
}

# =========================================================
# CALCUL DES BESOINS
# =========================================================

def calculate_needs(user: UserQuiz):

    needs_scores = defaultdict(int)

    # -------------------------
    # MOOD
    # -------------------------

    for mood in user.mood:

        if mood in MOOD_RULES:

            need = MOOD_RULES[mood]

            needs_scores[need] += QUESTION_SCORES["mood"]

    # -------------------------
    # SOMMEIL
    # -------------------------

    if user.sleepQuality in SLEEP_RULES:

        need = SLEEP_RULES[user.sleepQuality]

        needs_scores[need] += QUESTION_SCORES["sleep"]

    # -------------------------
    # SPORT
    # -------------------------

    sport_value = min(user.weeklySport, 5)

    if sport_value in SPORT_RULES:

        need = SPORT_RULES[sport_value]

        needs_scores[need] += QUESTION_SCORES["sport"]

    return dict(needs_scores)

# =========================================================
# CALCUL THÉRAPIES
# =========================================================

def calculate_therapy_scores(needs_scores):

    therapy_scores = defaultdict(int)

    for need, score in needs_scores.items():

        therapies = BESOIN_THERAPIES.get(need, [])

        for therapy in therapies:

            therapy_scores[therapy] += score

    return dict(therapy_scores)

# =========================================================
# TOP THÉRAPIES
# =========================================================

def select_final_therapies(therapy_scores):

    sorted_therapies = sorted(
        therapy_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_therapies = sorted_therapies[:4]

    return [therapy for therapy, score in top_therapies]

# =========================================================
# TEXTE ANALYSE
# =========================================================

def build_analysis_text(user, therapies):

    formatted = [
        therapy.replace("_", " ")
        for therapy in therapies
    ]

    return (
        f"{user.firstname}, "
        f"pour atteindre ton objectif '{user.mainGoal}', "
        f"nous te recommandons : "
        f"{', '.join(formatted)}."
    )

# =========================================================
# ENDPOINT API
# =========================================================

@app.post("/generate-program")

def generate_program(user: UserQuiz):

    # CALCUL BESOINS
    needs_scores = calculate_needs(user)

    # CALCUL THÉRAPIES
    therapy_scores = calculate_therapy_scores(
        needs_scores
    )

    # TOP THÉRAPIES
    final_therapies = select_final_therapies(
        therapy_scores
    )

    # TEXTE
    analysis_text = build_analysis_text(
        user,
        final_therapies
    )

    # RESPONSE
    return {

        "firstname": user.firstname,

        "needs_scores": needs_scores,

        "therapy_scores": therapy_scores,

        "recommended_therapies": final_therapies,

        "analysis_text": analysis_text
    }

# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )