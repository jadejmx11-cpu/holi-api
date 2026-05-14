# =========================================================
# HOLI - API SIMPLE ET STABLE (MOOD = STRING)
# =========================================================

import random

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
    "Tout va bien": "equilibre",
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
    "serenite": ["Meditation", "Respiration", "Affirmation Positive"],
    "recuperation": ["Yoga", "Autohypnose", "Meditation"],
    "lacher_prise": ["Journaling", "Respiration", "Autohypnose"],
    "equilibre": ["Renforcement", "Affirmation Positive", "Journaling"],
    "dynamisme": ["Qi Gong", "Respiration", "Renforcement"],
    "ancrage": ["Yoga", "Meditation", "Acupression"]
}

THERAPY_DOMAINS = {
    "Qi Gong": "mouvement",
    "Yoga": "mouvement",
    "Renforcement": "mouvement",

    "Acupression": "emotion",
    "Journaling": "emotion",
    "Affirmation Positive": "emotion",

    "Respiration": "repos",
    "Meditation": "repos",
    "Autohypnose": "repos"
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

def select_domain_therapies(therapy_scores):
    
    domain_best = {
        "mouvement": None,
        "emotion": None,
        "repos": None
    }

    domain_scores = {
        "mouvement": -1,
        "emotion": -1,
        "repos": -1
    }

    # -------------------------
    # 1. meilleure thérapie par domaine
    # -------------------------
    
    for therapy, score in therapy_scores.items():

        domain = THERAPY_DOMAINS.get(therapy)

        if domain:

            if score > domain_scores[domain]:
                domain_scores[domain] = score
                domain_best[domain] = therapy

    # -------------------------
    # 2. récupérer les thérapies déjà sélectionnées
    # -------------------------

    selected = set(domain_best.values())

    # -------------------------
    # 3. thérapie bonus (meilleur score restant)
    # -------------------------

    remaining = {
        t: s for t, s in therapy_scores.items()
        if t not in selected
    }

    bonus = None

    if remaining:
        bonus = max(remaining.items(), key=lambda x: x[1])[0]

    # -------------------------
    # 4. résultat final (ordre structuré)
    # -------------------------

    final = [
        domain_best["mouvement"],
        domain_best["emotion"],
        domain_best["repos"],
        bonus
    ]

    return [t for t in final if t is not None]

# =========================================================
# FORMATAGE BESOINS
# =========================================================

NEED_LABELS = {
    "serenite": "de sérénité",
    "equilibre": "d'équilibre",
    "energie": "d'énergie",
    "ancrage": "d'ancrage",
    "lacher_prise": "de lâcher prise",
    "confiance": "de confiance",
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
    top_needs = select_top_needs(needs_scores)
    print("TOP NEEDS:", top_needs)

    # CALCUL THÉRAPIES
    therapy_scores = calculate_therapy_scores(needs_scores)

    # TOP THÉRAPIES
    final_therapies = select_domain_therapies(therapy_scores)

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
# =========================================================
# SUITE - GENERATE USER PROGRAM
# =========================================================

REPEAT_COOLDOWN_DAYS = 3

# =========================================================
# MODULES (TEST LOCAL - PLUS TARD FIRESTORE)
# =========================================================

MODULES = [

    {
        "id": "yoga_sleep_1",
        "title": "Yoga du sommeil",
        "therapy": "yoga",
        "goals": ["mieux_dormir"],
        "duration": 10,
        "level": "beginner"
    },
  
    {
        "id": "yoga_sleep_11",
        "title": "Yoga 11",
        "therapy": "yoga",
        "goals": ["mieux_dormir"],
        "duration":5,
        "level": "beginner"
    },

    {
        "id": "yoga_sleep_12",
        "title": "Yoga 12",
        "therapy": "yoga",
        "goals": ["mieux_dormir"],
        "duration": 10,
        "level": "beginner"
    },

    {
        "id": "yoga_stress_1",
        "title": "Yoga anti-stress",
        "therapy": "yoga",
        "goals": ["stress"],
        "duration": 15,
        "level": "beginner"
    },

    {
        "id": "meditation_sleep_1",
        "title": "Méditation sommeil profond",
        "therapy": "meditation",
        "goals": ["mieux_dormir"],
        "duration": 10,
        "level": "beginner"
    },

    {
        "id": "meditation_sleep_11",
        "title": "Méditation 11 profond",
        "therapy": "meditation",
        "goals": ["mieux_dormir"],
        "duration": 5,
        "level": "beginner"
    },

    {
        "id": "respiration_stress_1",
        "title": "Respiration relaxante",
        "therapy": "respiration",
        "goals": ["stress"],
        "duration": 5,
        "level": "beginner"
    },

    {
        "id": "journaling_stress_1",
        "title": "Journaling émotionnel",
        "therapy": "journaling",
        "goals": ["stress"],
        "duration": 10,
        "level": "beginner"
    },

]

# =========================================================
# MODEL API
# =========================================================

class ProgramGenerationRequest(BaseModel):
    mainGoal: str
    secondaryGoal: str
    selectedTherapies: list[str]
    dailyDuration: int
    experienceLevel: str

# =========================================================
# DURÉE PROGRAMME
# =========================================================

def get_program_duration(daily_duration):

    if daily_duration < 20:
        weeks = 12
    elif daily_duration <= 30:
        weeks = 8
    elif daily_duration <= 45:
        weeks = 5
    else:
        weeks = 3

    return {
        "weeks": weeks,
        "days": weeks * 7
    }

# =========================================================
# LEVEL ACCESS
# =========================================================

LEVEL_ACCESS = {
    "beginner": ["beginner"],
    "intermediate": ["beginner", "intermediate"],
    "advanced": ["beginner", "intermediate", "advanced"]
}

# =========================================================
# FILTRE MODULES
# =========================================================

def filter_modules(user, modules):

    allowed_levels = LEVEL_ACCESS[user["experienceLevel"]]
    valid_modules = []

    for module in modules:

        if module["therapy"] not in user["selectedTherapies"]:
            continue

        goals_match = (
            user["mainGoal"] in module["goals"]
            or user["secondaryGoal"] in module["goals"]
        )

        if not goals_match:
            continue

        if module["level"] not in allowed_levels:
            continue

        valid_modules.append(module)

    return valid_modules

# =========================================================
# GENERATION JOUR
# =========================================================

def generate_day_program(available_modules, daily_duration, recent_modules):

    selected = []
    total_time = 0

    shuffled = available_modules.copy()
    random.shuffle(shuffled)

    for module in shuffled:

        if module["id"] in recent_modules:
            continue

        if total_time + module["duration"] > daily_duration:
            continue

        selected.append(module)
        total_time += module["duration"]

        if total_time == daily_duration:
            break

    return selected

# =========================================================
# GENERATION PROGRAMME GLOBAL
# =========================================================

def generate_full_program(user, modules):

    duration = get_program_duration(user["dailyDuration"])
    valid_modules = filter_modules(user, modules)

    program = []
    recent_modules = defaultdict(int)

    for day in range(duration["days"]):

        # cooldown
        to_remove = []
        for mid in recent_modules:
            recent_modules[mid] -= 1
            if recent_modules[mid] <= 0:
                to_remove.append(mid)

        for mid in to_remove:
            del recent_modules[mid]

        # génération jour
        day_modules = generate_day_program(
            valid_modules,
            user["dailyDuration"],
            recent_modules
        )

        for m in day_modules:
            recent_modules[m["id"]] = REPEAT_COOLDOWN_DAYS

        program.append({
            "day": day + 1,
            "modules": day_modules
        })

    return program

# =========================================================
# ENDPOINT API
# =========================================================

@app.post("/generate-user-program")
def generate_user_program(user: ProgramGenerationRequest):

    user_dict = user.dict()

    program = generate_full_program(user_dict, MODULES)

    return {
        "success": True,
        "days": len(program),
        "program": program
    }

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port)