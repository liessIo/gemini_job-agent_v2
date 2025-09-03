# Gemini Job Agent v2

## 1. Projektvision & Ziel

Der **Gemini Job Agent v2** ist ein KI-gestützter Assistent, der den Prozess der Jobsuche und -bewerbung automatisiert. Er durchsucht autonom Jobportale (z.B. Indeed), analysiert die Stellenanforderungen und gleicht diese mit einem hinterlegten Bewerberprofil ab. Ziel ist es, passende Stellen zu identifizieren, die Bewerbungschancen zu bewerten und perspektivisch auch Bewerbungsentwürfe zu erstellen.

---

## 2. Architektur & Technologiestack

Das Projekt ist in Python entwickelt und nutzt eine modulare Architektur, um die verschiedenen Aufgabenbereiche sauber zu trennen.

* **Sprache:** Python 3.x
* **Kern-Bibliotheken:** (Details in `requirements.txt`)
* **Wissensbasis:** Vektordatenbanken (`ChromaDB`) zur Speicherung und Abfrage von Jobdaten und Profilinformationen (`data/vector_stores/`).
* **Konfiguration:** YAML-Dateien im `config`-Ordner. Es wird strikt zwischen privaten Profilen (z.B. `config.yaml`) und öffentlichen Vorlagen (`config.template.yaml`) getrennt.
* **Code-Struktur:**
    * `src/scraper`: Module zum Scrapen von Job-Plattformen.
    * `src/knowledge_base`: Verwaltung der Vektordatenbanken.
    * `src/analysis`: Module zur Analyse und Bewertung der Jobs mittels LLM.
    * `main.py`: Haupteinstiegspunkt der Anwendung.

---

## 3. Setup & Konfiguration

Um das Projekt lokal aufzusetzen, sind folgende Schritte nötig:

1.  **Repository klonen:**
    ```bash
    git clone [https://github.com/liessIo/gemini_job-agent_v2.git](https://github.com/liessIo/gemini_job-agent_v2.git)
    cd gemini_job-agent_v2
    ```
2.  **Virtuelle Umgebung erstellen & aktivieren:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Konfiguration erstellen:**
    Kopiere alle `.template.yaml`-Dateien aus dem `config/`-Ordner und benenne die Kopien ohne das `.template`-Suffix (z.B. `config.template.yaml` -> `config.yaml`). Fülle diese neuen Dateien mit deinen privaten Daten (API-Keys, Profile etc.). Diese Dateien werden durch die `.gitignore` bewusst ignoriert, um deine Daten zu schützen.

---

## 4. Gedächtnisprotokoll: Entwicklungs-Historie & Kernentscheidungen

Dieses Projekt durchlief einen initialen Setup-Prozess, um eine saubere und sichere Codebasis auf GitHub zu gewährleisten. Die folgenden Herausforderungen wurden gemeistert:

1.  **Problem: Private Daten im öffentlichen Repository:**
    * **Herausforderung:** Beim ersten `git push` wurden versehentlich private Konfigurationsdateien (API-Keys, Profile) in das öffentliche GitHub-Repository geladen.
    * **Lösung:**
        1.  Die `.gitignore`-Datei wurde um die entsprechenden Pfade (`config/*.yaml`, `data/` etc.) erweitert.
        2.  Bereits versionierte Dateien wurden mit `git rm -r --cached <ordnername>` aus der Git-Verfolgung entfernt, ohne sie lokal zu löschen. Ein neuer Commit hat diese Entfernung festgehalten.

2.  **Problem: Konfigurationsvorlagen konnten nicht hinzugefügt werden:**
    * **Herausforderung:** Die `.gitignore`-Regel `config/` war zu pauschal und verhinderte, dass öffentliche Template-Dateien (z.B. `config.template.yaml`) zum Repository hinzugefügt werden konnten.
    * **Lösung:** Die `.gitignore`-Regel wurde verfeinert. Anstatt den ganzen Ordner zu ignorieren, werden nun gezielt Dateien ignoriert, aber Ausnahmen für Templates erlaubt:
        ```gitignore
        # Ignoriere alle .yaml Dateien im config Ordner...
        config/*.yaml
        # ... ABER mache eine Ausnahme für Dateien, die auf '.template.yaml' enden.
        !config/*.template.yaml
        ```

3.  **Problem: Unsaubere Git-Commit-Historie:**
    * **Herausforderung:** Die ersten Commits bestanden aus vielen kleinen Korrektur-Schritten ("Fix", "Add gitignore", "Remove config"). Für ein sauberes, öffentliches Projekt sollte dies zu einem einzigen, klaren "Initial Commit" zusammengefasst werden.
    * **Lösung:** Ein **interaktiver Rebase** (`git rebase -i HEAD~5`) wurde durchgeführt, um die letzten 5 Commits zu einem einzigen zu verschmelzen (`squash`).
    * **Schwierigkeiten dabei:** Der Rebase schlug mehrfach fehl, weil lokale, unversionierte Dateien im Arbeitsverzeichnis im Weg waren. Weder `git stash` noch einfache Lösungsansätze funktionierten.
    * **Finale, robuste Lösung:** Die blockierenden Ordner (`config/`, `data/`) wurden manuell aus dem Projektverzeichnis herausverschoben, der Rebase wurde im sauberen Verzeichnis durchgeführt, und danach wurden die Ordner wieder zurückgeschoben. Abschließend wurde die neue, saubere Historie mit `git push --force` auf GitHub erzwungen.

---