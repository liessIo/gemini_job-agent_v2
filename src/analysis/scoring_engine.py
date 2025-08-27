# src/analysis/scoring_engine.py

from typing import Any, Dict, List
import statistics
from chromadb.api.types import QueryResult

# Konstanten für die Gewichtung
MAX_DISTANCE = 2.0
IDEAL_ROLE_BONUS = 30.0
EXCLUSION_ROLE_PENALTY = -100.0

def calculate_relevance_score(job_title: str, query_results: QueryResult | None, scoring_config: Dict[str, Any], language: str) -> Dict[str, Any]:
    """
    Berechnet einen ganzheitlichen Relevanz-Score für einen Job.
    """
    if not query_results:
        return {"score": 0, "reason": "Keine semantischen Ergebnisse gefunden."}

    semantic_score = 0.0
    
    # Schritt 1: Berechne den semantischen Basis-Score, falls möglich.
    distances_list = query_results.get('distances')
    if distances_list and distances_list[0]:
        distances = distances_list[0]
        avg_distance = statistics.mean(distances)
        semantic_score = ((MAX_DISTANCE - avg_distance) / MAX_DISTANCE) * 100
        semantic_score = max(0, semantic_score)

    # Schritt 2: Der finale Score startet IMMER mit dem semantischen Score.
    final_score = semantic_score
    reasons = []

    # Schritt 3: Wende Boni und Malusse an.
    ideal_roles_key = f"ideal_roles_{language}"
    ideal_roles = scoring_config.get(ideal_roles_key, [])
    for role in ideal_roles:
        if role.lower() in job_title.lower():
            final_score += IDEAL_ROLE_BONUS
            reasons.append(f"+{IDEAL_ROLE_BONUS:.0f} Pkt (Bonus: '{role}')")
            break

    exclusion_roles_key = f"exclusion_roles_{language}"
    exclusion_roles = scoring_config.get(exclusion_roles_key, [])
    for role in exclusion_roles:
        if role.lower() in job_title.lower():
            final_score += EXCLUSION_ROLE_PENALTY
            reasons.append(f"-{abs(EXCLUSION_ROLE_PENALTY):.0f} Pkt (Malus: '{role}')")
            break
            
    # Schritt 4: Begrenze den Score auf 0-100.
    final_score = max(0, min(100, final_score))

    # Schritt 5: Baue die finale Begründung zusammen.
    # Füge den Basis-Score immer an den Anfang, wenn er die Grundlage bildet.
    if semantic_score > 0:
        reasons.insert(0, f"Semantischer Basis-Score: {semantic_score:.0f}")

    return {
        "score": int(final_score),
        "reason": ", ".join(reasons) if reasons else "Keine spezifischen Übereinstimmungen"
    }