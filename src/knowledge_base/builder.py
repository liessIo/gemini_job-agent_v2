# src/knowledge_base/builder.py

import yaml
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import shutil
import sys

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config"
VECTOR_STORE_PATH = BASE_DIR / "data" / "vector_stores"

def load_config(file_path: Path) -> dict:
    """Loads a specific YAML config file and handles errors."""
    if not file_path.is_file():
        template_name = file_path.name.replace('.yaml', '.template.yaml')
        print(f"❌ FEHLER: Konfigurationsdatei nicht gefunden: {file_path}")
        print(f"   Bitte kopieren Sie '{template_name}' nach '{file_path.name}' und füllen Sie sie mit Ihren Daten.")
        sys.exit(1)
    
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_vector_store(profile_data: dict, language: str):
    """Builds the vector database from the semantically rich parts of the profile."""
    print(f"Starte den Aufbau der Vektordatenbank für '{language}'...")

    documents = []
    
    # Robust Data Extraction
    impact_section = profile_data.get('impact')
    if impact_section:
        for station in impact_section:
            achievements = station.get('achievements', []) or station.get('erfolge', [])
            documents.extend(achievements)
    
    hard_facts_section = profile_data.get('hard_facts')
    if hard_facts_section:
        technologies = hard_facts_section.get('technologies', [])
        for tech in technologies:
            documents.append(tech.get('description', ''))
            
    style_section = profile_data.get('work_style') or profile_data.get('arbeitsweise')
    if style_section:
        documents.append(style_section.get('leadership_style') or style_section.get('fuehrungsstil', ''))
        documents.append(style_section.get('environment') or style_section.get('umfeld', ''))
        documents.append(style_section.get('mission', ''))
    
    semantic_anchors_de = profile_data.get('semantische_anker')
    if semantic_anchors_de:
        documents.extend(semantic_anchors_de)
        
    semantic_anchors_en = profile_data.get('semantic_anchors')
    if semantic_anchors_en:
        documents.extend(semantic_anchors_en)

    documents = [doc for doc in documents if doc and isinstance(doc, str)]
    
    print(f"{len(documents)} Dokumente zur Vektorisierung extrahiert.")

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(documents)

    db_path = str(VECTOR_STORE_PATH / language)
    persistent_client = chromadb.PersistentClient(path=db_path)
    
    collection_name = f"jobs_{language}"
    # Delete old collection if it exists to ensure a fresh build
    persistent_client.delete_collection(name=collection_name)
    collection = persistent_client.create_collection(name=collection_name)

    ids = [f"{language}_{i}" for i in range(len(documents))]

    collection.add(
        embeddings=embeddings.tolist(),
        documents=documents,
        ids=ids
    )
    print(f"✅ Vektordatenbank für '{language}' erfolgreich erstellt und gespeichert unter: {db_path}")


if __name__ == "__main__":
    main_config = load_config(CONFIG_PATH / "config.yaml")
    supported_languages = main_config.get('supported_languages', {})
    
    print("\n--- Starte den Aufbau der Wissensbasis(en) ---")
    
    if not supported_languages:
        print("Keine Sprachen in config.yaml konfiguriert. Abbruch.")
    else:
        for lang_code, lang_config in supported_languages.items():
            print("\n---------------------------------------------")
            if lang_config.get('enabled'):
                print(f"Verarbeite Sprache: '{lang_code}'")
                
                db_to_delete = VECTOR_STORE_PATH / lang_code
                if db_to_delete.exists() and db_to_delete.is_dir():
                    print(f"Lösche alte Vektordatenbank unter: {db_to_delete}")
                    shutil.rmtree(db_to_delete)
                
                profile_file = lang_config.get('profile_file')
                if profile_file:
                    profile = load_config(CONFIG_PATH / profile_file)
                    if profile:
                        build_vector_store(profile, lang_code)
                else:
                    print(f"Fehler: Kein 'profile_file' für '{lang_code}' in der Konfiguration gefunden.")
            else:
                print(f"Sprache '{lang_code}' ist in der Konfiguration deaktiviert. Wird übersprungen.")
    
    print("\n--- Aufbau der Wissensbasis(en) abgeschlossen ---")
