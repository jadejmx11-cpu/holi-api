# =========================================================
# HOLI - API DE GÉNÉRATION DE THÉRAPIES
# FastAPI + moteur de scoring personnalisé
# =========================================================

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from collections import defaultdict

# =========================================================
# INITIALISATION API
# =========================================================

app = FastAPI()

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
# TABLES DE RÈGLES (avec pondération intelligente)
# format: (besoin_principal, [ (besoin_secondaire, poids) ])
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

    "Plutôt bien": (
        "serenite",
        [("equilibre", 0.3)]
    ),

    "Je me réveille fatigué(e)": (
        "recuperation",
        [("ancrage", 0.4), ("serenite", 0.2)]
    ),

    "J'ai du mal à m'endormir": (
        "lacher_prise",
        [("serenite", 0.5)]
    ),

    "Je me réveille souvent": (
        "ancrage",
        [("recuperation", 0.4), ("lacher_prise", 0.3)]
    )
}

ENERGY_RULES = {
    "Très énergique": ("dynamisme", [("equilibre", 0.3)]),

    "Plutôt en forme": ("equilibre", [("dynamisme", 0.3)]),

    "Fatigue régulière": ("ancrage", [("recuperation", 0.5)]),

    "Très fatigué(e)": ("recuperation", [("ancrage", 0.4)])
}

DIGESTION_RULES = {
    "Tout va bien": ("equilibre", []),

    "Ballonnements": (
        "serenite",
        [("recuperation", 0.3)]
    ),

    "Digestion lente": (
        "lacher_prise",
        [("recuperation", 0.4)]
    ),

    "Fatigué(e) après le repas": (
        "recuperation",
        [("serenite", 0.3)]
    ),

    "Je ne souhaite pas répondre": ("NO_IMPACT", [])
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

    "Je ressens une certaine surcharge": (
        "ancrage",
        [("serenite", 0.5)]
    ),

    "Je me sens souvent débordé(e)": (
        "recuperation",
        [("serenite", 0.6), ("ancrage", 0.3)]
    ),

    "Je me sens constamment sous pression": (
        "lacher_prise",
        [("serenite", 0.7), ("recuperation", 0.4)]
    )
}

# =========================================================
# ASSOCIATION BESOINS -> THÉRAPIES
# =========================================================

BESOIN_THERAPIES = {
    "ancrage": ["yoga", "acupression", "meditation"],
    "lacher_prise": ["autohypnose", "respiration", "journaling"],
    "dynamisme": ["respiration", "qigong", "renforcement"],
    "recuperation": ["meditation", "autohypnose", "yoga"],
    "equilibre": ["renforcement", "journaling", "affirmation_positive"],
    "serenite": ["affirmation_positive", "acupression", "qigong"]
}

# =========================================================
# DOMAINES THÉRAPEUTIQUES
# =========================================================

THERAPY_DOMAINS = {
    "repos": ["respiration", "meditation", "autohypnose"],
    "mouvement": ["qigong", "yoga", "renforcement"],
    "emotion": ["acupression", "journaling", "affirmation_positive"]
}

# =========================================================
# MODÈLE UTILISATEUR (REQUÊTE API)
# =========================================================

class UserQuiz(BaseModel):
    firstname: str

    mood: List[str]

    sleepQuality: str

    energyLevel: str

    digestionQuality: str

    weeklySport: int

    mentalLoad: str

    mainGoal: str = None
    secondaryGoal: str = None

# =========================================================
# CALCUL DES BESOINS
# =========================================================

def calculate_needs(user: UserQuiz):

    needs_scores = defaultdict(int)

    # ---------------------------
    # MOOD (liste)
    # ---------------------------

    for mood_value in user.mood:

        if mood_value in MOOD_RULES:

            need = MOOD_RULES[mood_value]

            needs_scores[need] += QUESTION_SCORES["mood"]

    # ---------------------------
    # SOMMEIL
    # ---------------------------

    if user.sleepQuality in SLEEP_RULES:

        need = SLEEP_RULES[user.sleepQuality]

        needs_scores[need] += QUESTION_SCORES["sleepQuality"]

    # ---------------------------
    # ÉNERGIE
    # ---------------------------

    if user.energyLevel in ENERGY_RULES:

        need = ENERGY_RULES[user.energyLevel]

        needs_scores[need] += QUESTION_SCORES["energyLevel"]

    # ---------------------------
    # DIGESTION
    # ---------------------------

    if user.digestionQuality in DIGESTION_RULES:

        need = DIGESTION_RULES[user.digestionQuality]

        needs_scores[need] += QUESTION_SCORES["digestionQuality"]

    # ---------------------------
    # SPORT
    # ---------------------------

    sport_value = min(user.weeklySport, 5)

    if sport_value in SPORT_RULES:

        need = SPORT_RULES[sport_value]

        needs_scores[need] += QUESTION_SCORES["weeklySport"]

    # ---------------------------
    # CHARGE MENTALE
    # ---------------------------

    if user.mentalLoad in MENTAL_LOAD_RULES:

        need = MENTAL_LOAD_RULES[user.mentalLoad]

        needs_scores[need] += QUESTION_SCORES["mentalLoad"]

    return dict(needs_scores)

# =========================================================
# CALCUL DES THÉRAPIES
# =========================================================

def calculate_therapy_scores(needs_scores):

    therapy_scores = defaultdict(int)

    for need, score in needs_scores.items():

        therapies = BESOIN_THERAPIES.get(need, [])

        for therapy in therapies:

            therapy_scores[therapy] += score

    return dict(therapy_scores)

# =========================================================
# SÉLECTION DES THÉRAPIES FINALES
# =========================================================

def select_final_therapies(therapy_scores):

    selected_therapies = []

    # ---------------------------------------
    # 1. MEILLEURE THÉRAPIE PAR DOMAINE
    # ---------------------------------------

    for domain, therapies in THERAPY_DOMAINS.items():

        best_therapy = None
        best_score = -1

        for therapy in therapies:

            score = therapy_scores.get(therapy, 0)

            if score > best_score:

                best_score = score
                best_therapy = therapy

        if best_therapy:

            selected_therapies.append(best_therapy)

    # ---------------------------------------
    # 2. 4ÈME THÉRAPIE = MEILLEUR SCORE RESTANT
    # ---------------------------------------

    remaining_therapies = {
        therapy: score
        for therapy, score in therapy_scores.items()
        if therapy not in selected_therapies
    }

    if remaining_therapies:

        fourth_therapy = max(
            remaining_therapies,
            key=remaining_therapies.get
        )

        selected_therapies.append(fourth_therapy)

    return selected_therapies

# =========================================================
# ANALYSE TEXTE PERSONNALISÉE
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

    formatted_needs = [
        need_labels.get(n, n)
        for n in top_needs
    ]

    formatted_therapies = [
        therapy.replace("_", " ").title()
        for therapy in therapies
    ]

    analysis = (
        f"{user.firstname}, ton objectif est de "
        f"{user.mainGoal}. "
        f"Mais tes réponses montrent surtout "
        f"un besoin de {', '.join(formatted_needs)}. "
        f"Nous allons d'abord aider ton corps "
        f"à retrouver un meilleur équilibre "
        f"avant de chercher à stimuler davantage ton énergie. "
        f"C'est pourquoi nous te proposons : "
        f"{', '.join(formatted_therapies)}."
    )

    return analysis

# =========================================================
# ENDPOINT API
# =========================================================

@app.post("/generate-program")

def generate_program(user: UserQuiz):

    print("========= USER RECEIVED =========")
    print(user)
    print("=================================")

    # ---------------------------------------
    # CALCUL DES BESOINS

    needs_scores = calculate_needs(user)

    # ---------------------------------------
    # TRI DES BESOINS
    # ---------------------------------------

    sorted_needs = sorted(
        needs_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_needs = [
        need for need, score in sorted_needs[:3]
    ]

    # ---------------------------------------
    # CALCUL DES THÉRAPIES
    # ---------------------------------------

    therapy_scores = calculate_therapy_scores(
        needs_scores
    )

    # ---------------------------------------
    # THÉRAPIES FINALES
    # ---------------------------------------

    final_therapies = select_final_therapies(
        therapy_scores
    )

    # ---------------------------------------
    # TEXTE PERSONNALISÉ
    # ---------------------------------------

    analysis_text = build_analysis_text(
        user,
        top_needs,
        final_therapies
    )

    # ---------------------------------------
    # RÉPONSE API
    # ---------------------------------------

    return {

        "firstname": user.firstname,

        "needs_scores": needs_scores,

        "top_needs": top_needs,

        "therapy_scores": therapy_scores,

        "recommended_therapies": final_therapies,

        "analysis_text": analysis_text
    }

import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# =========================================================
# FIN
# =========================================================