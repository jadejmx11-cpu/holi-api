# =========================================================
# HOLI - API SIMPLE ET STABLE (MOOD = STRING)
# =========================================================

from fastapi import FastAPI
from pydantic import BaseModel
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
    mood: str
    energyLevel: str
    sleepQuality: str
    digestionQuality: str
    weeklySport: int
    mentalLoad: str

# =========================================================
# SCORES
# =========================================================

QUESTION_SCORES = {
    "mood": 9,
    "sleep": 10,
    "energy": 4,
    "digestion": 6,
    "sport": 3,
    "mental": 7
}

# =========================================================
# RULES
# =========================================================

MOOD_RULES = {
    "Stressé(e)": "serenite",
    "Fatigué(e)": "recuperation",
    "Anxieux(se)": "lacher_prise",
    "Surchargé(e)": "ancrage",
    "Bien": "equilibre"
}

SLEEP_RULES = {
    "Très bien": "equilibre",
    "Plutôt bien": "serenite",
    "Je me réveille souvent": "ancrage",
    "Je me réveille fatigué(e)": "recuperation",
    "J'ai du mal à m'endormir": "lacher_prise"
}

ENERGY_RULES = {
    "Très énergique": "ancrage",
    "Plutôt en forme": "serenite",
    "Fatigue régulière": "lacher_prise",
    "Très fatigué": "recuperation"
}

DIGESTION_RULES = {
    "Très énergique": "ancrage",
    "Ballonnements": "lacher_prise",
    "Fatigue après les repas": "serenite",
    "Digestion lente": "recuperation",
    "Je ne souhaite pas répondre": " "
}

SPORT_RULES = {
    0: "dynamisme",
    1: "dynamisme",
    2: "equilibre",
    3: "equilibre",
    4: "ancrage",
    5: "ancrage",
    6: "recuperation",
    7: "recuperation"
}

MENTAL_RULES = {
    "Je me sens plutôt léger(ère)": "equilibre",
    "Ça reste gérable": "serenite",
    "Je sens une certaine surcharge": "lacher_prise",
    "Je me sens souvent débordé(e)": "ancrage",
    "Je me sens constamment sous pression": "recuperation"
}

# =========================================================
# THÉRAPIES
# =========================================================

BESOIN_THERAPIES = {
    "serenite": ["meditation", "respiration", "affirmation_positive"],
    "recuperation": ["yoga", "autohypnose", "meditation"],
    "lacher_prise": ["journaling", "respiration", "autohypnose"],
    "equilibre": ["renforcement", "affirmation_positive", "journaling"],
    "dynamisme": ["qigong", "respiration", "renforcement"],
    "ancrage": ["yoga", "meditation", "acupression"]
}

# =========================================================
# CALCUL DES BESOINS
# =========================================================

def calculate_needs(user: UserQuiz):

    needs_scores = defaultdict(int)

    # -------------------------
    # MOOD (STRING UNIQUE)
    # -------------------------

    if user.mood in MOOD_RULES:

        need = MOOD_RULES[user.mood]
        needs_scores[need] += QUESTION_SCORES["mood"]

    # -------------------------
    # SOMMEIL
    # -------------------------

    if user.sleepQuality in SLEEP_RULES:

        need = SLEEP_RULES[user.sleepQuality]
        needs_scores[need] += QUESTION_SCORES["sleep"]
        
    # -------------------------
    # ENERGY
    # -------------------------

    if user.energyLevel in ENERGY_RULES:

        need = ENERGY_RULES[user.energyLevel]
        needs_scores[need] += QUESTION_SCORES["energy"]

    # -------------------------
    # DIGESTION
    # -------------------------

    if user.digestionQuality in DIGESTION_RULES:

        need = DIGESTION_RULES[user.digestionQuality]
        needs_scores[need] += QUESTION_SCORES["digestion"]

    # -------------------------
    # SPORT
    # -------------------------

    sport_value = min(user.weeklySport, 7)

    if sport_value in SPORT_RULES:

        need = SPORT_RULES[sport_value]
        needs_scores[need] += QUESTION_SCORES["sport"]

    # -------------------------
    # MENTAL
    # -------------------------

    if user.mentalLoad in MENTAL_RULES:

        need = MENTAL_RULES[user.mentalLoad]
        needs_scores[need] += QUESTION_SCORES["mental"]

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
# FORMATAGE BESOINS
# =========================================================

NEED_LABELS = {
    "serenite": "sérénité",
    "equilibre": "équilibre",
    "energie": "énergie",
    "ancrage": "ancrage",
    "lacher_prise": "lâcher prise",
    "confiance": "confiance",
}

# =========================================================
# TOP BESOINS
# =========================================================

def select_top_needs(needs_scores):

    sorted_needs = sorted(
        needs_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_needs = sorted_needs[:2]

    return [
        NEED_LABELS.get(need, need.replace("_", " "))
        for need, score in top_needs
    ]

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

    print("=== RAW INPUT FROM FLUTTERFLOW ===")
    print(user.dict())
    print("===================================")

    # CALCUL BESOINS
    needs_scores = calculate_needs(user)
    
    # CALCUL TOP BESOINS
    print("TOP NEEDS:", top_needs)
    top_needs = select_top_needs(needs_scores)

    # CALCUL THÉRAPIES
    therapy_scores = calculate_therapy_scores(needs_scores)

    # TOP THÉRAPIES
    final_therapies = select_final_therapies(therapy_scores)

    # TEXTE
    analysis_text = build_analysis_text(user, final_therapies)

    return {
        "firstname": user.firstname,
        "needs_scores": needs_scores,
        "top_needs": top_needs,
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