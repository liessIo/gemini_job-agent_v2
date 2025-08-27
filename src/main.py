# src/main.py

import yaml
from pathlib import Path
import sys # Import sys to exit the script
from src.scraper.indeed_scraper import search_indeed, scrape_job_details
from src.knowledge_base.query_engine import query_knowledge_base
from src.analysis.scoring_engine import calculate_relevance_score
from src.analysis.llm_analyzer import analyze_job_with_llm
from sentence_transformers import SentenceTransformer

# ... (Konstanten und Pfade bleiben gleich) ...
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config"
SCORE_THRESHOLD_FOR_LLM = 60

def load_config(file_path: Path) -> dict:
    """Lädt eine spezifische YAML-Konfigurationsdatei."""
    # NEU: Prüfen, ob die Datei existiert
    if not file_path.is_file():
        template_name = file_path.name.replace('.yaml', '.template.yaml')
        print(f"❌ FEHLER: Konfigurationsdatei nicht gefunden: {file_path}")
        print(f"   Bitte kopieren Sie '{template_name}' nach '{file_path.name}' und füllen Sie sie mit Ihren Daten.")
        sys.exit(1) # Beendet das Skript

    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_job_agent():
    """Die Hauptfunktion, die den Job-Agenten ausführt."""
    # Lädt jetzt sicher die Konfigurationen
    config = load_config(CONFIG_PATH / "config.yaml")
    profile_de = load_config(CONFIG_PATH / "profil_de.yaml")
    profile_en = load_config(CONFIG_PATH / "profil_en.yaml")
    profiles = {'de': profile_de, 'en': profile_en}
    
    # ... (Rest des Skripts bleibt unverändert) ...
    print("=============================================")
    print(f"🤖 Starte Gemini Job Agent v2 (Reasoning Mode)")
    
    print("Lade KI-Modell in den Speicher...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Modell erfolgreich geladen.")
    
    print(f"Lese Suchparameter aus der Konfiguration...")
    print("=============================================")

    scraped_jobs = search_indeed()

    if not scraped_jobs:
        print("Keine Jobs gefunden. Der Agent wird beendet.")
        return

    print(f"\n✅ {len(scraped_jobs)} Jobs gefunden. Beginne mit der Detail-Analyse...")
    
    analyzed_jobs = []
    for i, job in enumerate(scraped_jobs):
        print("\n---------------------------------------------")
        print(f"Analysiere Job {i+1}/{len(scraped_jobs)}: {job.get('title')}")
        
        description = scrape_job_details(job.get("link", ""))
        job['description'] = description
        
        if not description:
            print("   -> Konnte keine Beschreibung extrahieren. Job wird übersprungen.")
            continue
        
        try:
            lang = detect(description)
            if lang not in ['de', 'en']:
                print(f"   -> Sprache '{lang}' wird nicht unterstützt. Job wird übersprungen.")
                continue
            print(f"   -> Sprache erkannt: '{lang}'")
        except Exception:
            print("   -> Sprache konnte nicht erkannt werden. Job wird übersprungen.")
            continue
        
        query_results = query_knowledge_base(query=description, model=model, language=lang, n_results=3)
        
        if query_results:
            scoring_config = config.get('scoring_logic', {})
            score_details = calculate_relevance_score(job.get('title', ''), query_results, scoring_config, lang)
            job['relevance'] = score_details
            
            if score_details['score'] >= SCORE_THRESHOLD_FOR_LLM:
                profile_for_llm = profiles.get(lang)
                if profile_for_llm:
                    llm_analysis = analyze_job_with_llm(job, profile_for_llm)
                    job['llm_analysis'] = llm_analysis
            
            analyzed_jobs.append(job)

    analyzed_jobs.sort(key=lambda x: x.get('relevance', {}).get('score', 0), reverse=True)

    print("\n\n=== Finale Analyse-Ergebnisse (sortiert nach Relevanz) ===")
    for job in analyzed_jobs:
        relevance = job.get('relevance', {})
        score = relevance.get('score', 0)
        reason = relevance.get('reason', 'N/A')
        print("\n---------------------------------------------")
        print(f" Titel: {job.get('title')}")
        print(f" Firma: {job.get('company')}")
        print(f" Relevanz: {score}/100")
        print(f" Begründung: {reason}")
        print(f" Link: {job.get('link')}")
        
        if 'llm_analysis' in job:
            print(f"\n--- Gemini Analyse ---")
            print(job['llm_analysis'])

if __name__ == "__main__":
    from langdetect import detect
    run_job_agent()
