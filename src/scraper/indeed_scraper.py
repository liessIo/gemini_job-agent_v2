# src/scraper/indeed_scraper.py

import yaml
import time
import random
import os
from dotenv import load_dotenv
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth.stealth import stealth_sync
from urllib.parse import urljoin, urlencode
from typing import List, Dict, Any

# --- Pfad-Konfiguration ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
BASE_URL = "https://de.indeed.com"

# Lade .env Datei explizit aus dem Projektstammverzeichnis
dotenv_path = BASE_DIR / ".env"
if dotenv_path.is_file():
    load_dotenv(dotenv_path=dotenv_path)

# --- Bright Data Konfiguration ---
BRIGHTDATA_USERNAME = os.getenv("BRIGHTDATA_USERNAME")
BRIGHTDATA_PASSWORD = os.getenv("BRIGHTDATA_PASSWORD")
BRIGHTDATA_HOST = os.getenv("BRIGHTDATA_HOST")
BRIGHTDATA_PORT = os.getenv("BRIGHTDATA_PORT")

if not all([BRIGHTDATA_USERNAME, BRIGHTDATA_PASSWORD, BRIGHTDATA_HOST, BRIGHTDATA_PORT]):
    raise ValueError("Bright Data credentials not found in .env file.")

proxy_settings = {
    "server": f"http://{BRIGHTDATA_HOST}:{BRIGHTDATA_PORT}",
    "username": BRIGHTDATA_USERNAME,
    "password": BRIGHTDATA_PASSWORD
}

def build_indeed_search_url() -> str:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    params = config.get('indeed_search_params', {})
    params['from'] = 'searchOnHP'
    return f"{BASE_URL}/jobs?" + urlencode(params)

def search_indeed() -> List[Dict[str, Any]]:
    search_url = build_indeed_search_url()
    print(f"🚀 Starte getarnten Scraper für Indeed (via Bright Data)...")
    all_jobs = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, proxy=proxy_settings) # type: ignore
            # --- MODIFIED: Ignore SSL errors for the proxy connection ---
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                ignore_https_errors=True
            )
            page = context.new_page()
            stealth_sync(page)
            
            page.goto(search_url, timeout=120000, wait_until="networkidle")

            job_list_container_selector = 'div#mosaic-provider-jobcards'
            page.wait_for_selector(job_list_container_selector, timeout=60000)
            job_cards = page.locator('div.job_seen_beacon').all()
            print(f"{len(job_cards)} Jobs auf der Seite gefunden.")

            for card in job_cards:
                title_element = card.locator('h2.jobTitle a').first
                company_element = card.locator('[data-testid="company-name"]').first
                url_suffix = title_element.get_attribute('href')
                if url_suffix:
                    title = title_element.inner_text()
                    url = urljoin(BASE_URL, str(url_suffix))
                    company = company_element.inner_text() if company_element.count() > 0 else "N/A"
                    all_jobs.append({"title": title, "company": company, "link": url})
            
            browser.close()
        
        print("✅ Suche beendet.")
        return all_jobs

    except TimeoutError:
        print("❌ Timeout-Fehler. Selbst mit Bright Data konnte die Seite nicht geladen werden.")
        return []
    except Exception as e:
        print(f"❌ Fehler beim Scrapen der Indeed-Ergebnisseite: {e}")
        return []

def scrape_job_details(job_url: str) -> str:
    print(f"  -> Lade Details von: {job_url[:70]}...")
    description = ""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, proxy=proxy_settings) # type: ignore
            # --- MODIFIED: Ignore SSL errors for the proxy connection ---
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                ignore_https_errors=True
            )
            page = context.new_page()
            stealth_sync(page)
            
            page.goto(job_url, timeout=90000, wait_until="domcontentloaded")

            try:
                iframe_selector = 'iframe#vjs-container-iframe'
                page.wait_for_selector(iframe_selector, timeout=7000)
                frame = page.frame_locator(iframe_selector)
                description_selector = 'div#jobDescriptionText'
                frame.locator(description_selector).wait_for(timeout=20000)
                description = frame.locator(description_selector).inner_text()
            except Exception:
                description_selector = 'div#jobDescriptionText'
                if page.locator(description_selector).count() > 0:
                    description = page.locator(description_selector).first.inner_text()
                else:
                    description = page.locator('body').inner_text()
            
            browser.close()
            
    except Exception as e:
        print(f"     -> Fehler beim Scrapen der Job-Details: {e}")

    if description:
        return "\n".join(line.strip() for line in description.splitlines() if line.strip())
    return ""

if __name__ == '__main__':
    jobs = search_indeed()
    if jobs:
        first_job_url = jobs[0].get("link")
        if first_job_url:
            description_text = scrape_job_details(first_job_url)
            print("\n--- Extrahierte Beschreibung (erste 500 Zeichen) ---")
            print(description_text[:500] + "...")

