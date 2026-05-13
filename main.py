# =========================================================
# HOLI - API DE GÉNÉRATION DE THÉRAPIES
# FastAPI + moteur de scoring personnalisé
# =========================================================

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from collections import defaultdict
import os

# =========================================================
# INITIALISATION API
# =========================================================

app = FastAPI()

# =========================================================
# USER MODEL (FIX 1)
# =========================================================

class UserQuiz(BaseModel):
    firstname: str
    mainGoal: str
    mood: List[str]
    sleepQuality: str
    energyLevel: str
    digestionQuality: str
    weeklySport: int
    mentalLoad: str

# =========================================================
# CONFIGURATION DES SCORES PAR QUESTION
# =========================================================

QUESTION_SCORES = {
    "mood": 9,
    "sleepQuality": 10,
    "energyLevel": 4,
    "digestionQuality": 6,
    "weeklySport": 3,
    "mentalLoad": 7
}

# =========================================================
# TABLES DE RÈGLES
# =========================================================

MOOD_RULES = {
    "Stressé(e)": ("serenite", [("lacher_prise", 0.5)]),
    "Fatigué(e)": ("recuperation", [("ancrage", 0.3)]),
    "Anxieux(se)": ("lacher_prise", [("serenite", 0.5)]),
    "Surchargé(e)": ("ancrage", [("recuperation", 0.4), ("serenite", 0.3)]),
    "Bien": ("equilibre", [])
}

SLEEP_RULES = {
    "Très bien": ("equilibre", []),
    "Plutôt bien": ("serenite", [("equilibre", 0.3)]),
    "Je me réveille fatigué(e)": ("recuperation", [("ancrage", 0.4), ("serenite", 0.2)]),
    "J'ai du mal à m'endormir": ("lacher_prise", [("serenite", 0.5)]),
    "Je me réveille souvent": ("ancrage", [("recuperation", 0.4), ("lacher_prise", 0.3)])
}

ENERGY_RULES = {
    "Très énergique": ("dynamisme", [("equilibre", 0.3)]),
    "Plutôt en forme": ("equilibre", [("dynamisme", 0.3)]),
    "Fatigue régulière": ("ancrage", [("recuperation", 0.5)]),
    "Très fatigué(e)": ("recuperation", [("ancrage", 0.4)])
}

DIGESTION_RULES = {
    "Tout va bien": ("equilibre", []),
    "Ballonnements": ("serenite", [("recuperation", 0.3)]),
    "Digestion lente": ("lacher_prise", [("recuperation", 0.4)]),
    "Fatigué(e) après le repas": ("recuperation", [("serenite", 0.3)]),
    "Je ne souhaite pas répondre": "NO_IMPACT"
}

SPORT_RULES = {
    0: ("dynamisme", []),
    1: ("dynamisme", []),
    2: ("equilibre", []),
    3: ("equilibre", [("dynamisme", 0.2)]),
    4: ("recuperation", []),
    5: ("recuperation", [("ancrage", 0.2)]),
    6: ("recuperation", [("ancrage", 0.3), ("serenite", 0.2)]),
    7: ("recuperation", [("ancrage", 0.4), ("serenite", 0.3)]),
}

MENTAL_LOAD_RULES = {
    "Je me sens plutôt léger(e)": ("dynamisme", []),
    "Ça reste gérable": ("equilibre", []),
    "Je ressens une certaine surcharge": ("ancrage", [("serenite", 0.5)]),
    "Je me sens souvent débordé(e)": ("recuperation", [("serenite", 0.6), ("ancrage", 0.3)]),
    "Je me sens constamment sous pression": ("lacher_prise", [("serenite", 0.7), ("recuperation", 0.4)])
}

# =========================================================
# THÉRAPIES
# =========================================================

BESOIN_THERAPIES = {
    "ancrage": ["yoga", "acupression", "meditation"],
    "lacher_prise": ["autohypnose", "respiration", "journaling"],
    "dynamisme": ["respiration", "qigong", "renforcement"],
    "recuperation": ["meditation", "autohypnose", "yoga"],
    "equilibre": ["renforcement", "journaling", "affirmation_positive"],
    "serenite": ["affirmation_positive", "acupression", "qigong"]
}

THERAPY_DOMAINS = {
    "repos": ["respiration", "meditation", "autohypnose"],
    "mouvement": ["qigong", "yoga", "renforcement"],
    "emotion": ["acupression", "journaling", "affirmation_positive"]
}

# =========================================================
# CALCUL DES BESOINS
# =========================================================

def calculate_needs(user: UserQuiz):

    needs_scores = defaultdict(int)

    # FIX 5 MOOD SAFE
    moods = user.mood if isinstance(user.mood, list) else [user.mood]

    for mood_value in moods:
        if mood_value in MOOD_RULES:
            main_need, secondary = MOOD_RULES[mood_value]
            needs_scores[main_need] += QUESTION_SCORES["mood"]

            for sec_need, weight in secondary:
                needs_scores[sec_need] += QUESTION_SCORES["mood"] * weight

    # SOMMEIL
    if user.sleepQuality in SLEEP_RULES:
        main_need, secondary = SLEEP_RULES[user.sleepQuality]
        needs_scores[main_need] += QUESTION_SCORES["sleepQuality"]

        for sec_need, weight in secondary:
            needs_scores[sec_need] += QUESTION_SCORES["sleepQuality"] * weight

    # ÉNERGIE
    if user.energyLevel in ENERGY_RULES:
        main_need, secondary = ENERGY_RULES[user.energyLevel]
        needs_scores[main_need] += QUESTION_SCORES["energyLevel"]

        for sec_need, weight in secondary:
            needs_scores[sec_need] += QUESTION_SCORES["energyLevel"] * weight

    # DIGESTION (FIX 4)
    rule = DIGESTION_RULES.get(user.digestionQuality)

    if rule and rule != "NO_IMPACT":
        main_need, secondary = rule
        needs_scores[main_need] += QUESTION_SCORES["digestionQuality"]

        for sec_need, weight in secondary:
            needs_scores[sec_need] += QUESTION_SCORES["digestionQuality"] * weight

# SPORT

try:
    sport_value = int(user.weeklySport)
except:
    sport_value = 0

sport_value = min(sport_value, 7)

if sport_value in SPORT_RULES:

    main_need, secondary = SPORT_RULES[sport_value]

    needs_scores[main_need] += QUESTION_SCORES["weeklySport"]

    for sec_need, weight in secondary:
        needs_scores[sec_need] += (
            QUESTION_SCORES["weeklySport"] * weight
        )
        
    # MENTAL LOAD
    if user.mentalLoad in MENTAL_LOAD_RULES:
        main_need, secondary = MENTAL_LOAD_RULES[user.mentalLoad]
        needs_scores[main_need] += QUESTION_SCORES["mentalLoad"]

        for sec_need, weight in secondary:
            needs_scores[sec_need] += QUESTION_SCORES["mentalLoad"] * weight

    return dict(needs_scores)

# =========================================================
# THERAPIES SCORES
# =========================================================

def calculate_therapy_scores(needs_scores):

    therapy_scores = defaultdict(int)

    for need, score in needs_scores.items():
        for therapy in BESOIN_THERAPIES.get(need, []):
            therapy_scores[therapy] += score

    return dict(therapy_scores)

# =========================================================
# SELECTION THÉRAPIES (FIX 7)
# =========================================================

def select_final_therapies(therapy_scores):

    selected = sorted(
        therapy_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:4]

    return [therapy for therapy, _ in selected]

# =========================================================
# ANALYSE TEXTE
# =========================================================

def build_analysis_text(user, top_needs, therapies):

    need_labels = {
        "lacher_prise": "lâcher prise",
        "serenite": "sérénité",
        "dynamisme": "dynamisme",
        "ancrage": "ancrage",
        "recuperation": "récupération",
        "equilibre": "équilibre"
    }

    formatted_needs = [need_labels.get(n, n) for n in top_needs]
    formatted_therapies = [t.replace("_", " ").title() for t in therapies]

    return (
        f"{user.firstname}, ton objectif est de {user.mainGoal}. "
        f"Mais tes réponses montrent surtout un besoin de {', '.join(formatted_needs)}. "
        f"Nous allons d'abord aider ton corps à retrouver un meilleur équilibre "
        f"avant de chercher à stimuler davantage ton énergie. "
        f"C'est pourquoi nous te proposons : {', '.join(formatted_therapies)}."
    )

# =========================================================
# ENDPOINT
# =========================================================

@app.post("/generate-program")
def generate_program(user: UserQuiz):

    needs_scores = calculate_needs(user)

    sorted_needs = sorted(needs_scores.items(), key=lambda x: x[1], reverse=True)

    top_needs = [n for n, _ in sorted_needs[:3]]

    therapy_scores = calculate_therapy_scores(needs_scores)

    final_therapies = select_final_therapies(therapy_scores)

    analysis_text = build_analysis_text(user, top_needs, final_therapies)

    return {
        "firstname": user.firstname,
        "needs_scores": needs_scores,
        "top_needs": top_needs,
        "therapy_scores": therapy_scores,
        "recommended_therapies": final_therapies,
        "analysis_text": analysis_text
    }

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)