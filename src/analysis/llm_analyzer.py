# src/analysis/llm_analyzer.py

import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=GEMINI_API_KEY) # type: ignore


def analyze_job_with_llm(job_data: Dict[str, Any], profile_data: Dict[str, Any]) -> str:
    """
    Sends job and profile data to the Gemini LLM for a qualitative analysis.
    """
    print("   -> Sende Daten zur qualitativen Analyse an das LLM (Gemini)...")
    
    profile_summary = profile_data.get('identity', {}).get('profile_summary', '')
    semantic_anchors_list = profile_data.get('semantic_anchors', []) or profile_data.get('semantische_anker', [])
    semantic_anchors = "\n- ".join(semantic_anchors_list)
    
    prompt = f"""
    Du bist ein erfahrener Karriereberater für Tech-Führungskräfte. Analysiere die folgende Stellenbeschreibung im Abgleich mit dem Profil des Kandidaten.

    **Kandidatenprofil:**
    - Zusammenfassung: {profile_summary}
    - Kernkompetenzen und Erfolge:
    - {semantic_anchors}

    **Stellenbeschreibung:**
    - Titel: {job_data.get('title')}
    - Firma: {job_data.get('company')}
    - Beschreibung: {job_data.get('description')}

    **Deine Aufgaben:**
    1.  **Zusammenfassung:** Fasse die 3 wichtigsten Anforderungen der Stelle in Stichpunkten zusammen.
    2.  **Passung (Fit):** Bewerte kurz, wie gut der Kandidat zu diesen 3 Anforderungen passt.
    3.  **Potenzielle Lücke:** Identifiziere eine mögliche Schwäche oder ein Thema, das im Interview angesprochen werden könnte.
    4.  **Urteil:** Gib eine finale Empfehlung in einem Satz (z.B., "Hervorragende Übereinstimmung", "Gute Übereinstimmung mit kleinen Lücken", "Kein klarer Match").
    """
    
    try:
        # Initialize the model and ignore the incorrect Pylance warning
        model = genai.GenerativeModel( # type: ignore
            model_name='models/gemini-1.5-flash',
            generation_config={"temperature": 0.5}
        ) # type: ignore
        
        response = model.generate_content(prompt)
        print("   -> LLM-Analyse erfolgreich empfangen.")
        return response.text.strip()
    except Exception as e:
        print(f"   -> Fehler bei der LLM-Analyse: {e}")
        return "Die LLM-Analyse konnte nicht durchgeführt werden."