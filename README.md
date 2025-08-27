Gemini Job Agent v2
This is an autonomous AI agent designed to assist with job hunting. It scrapes job portals, analyzes listings against a personalized profile, ranks them by relevance, and uses an LLM to provide a qualitative analysis for the best matches.

Setup
Clone the repository:

git clone <your-repo-url>
cd gemini_job-agent_v2

Create and activate a virtual environment:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Install browser binaries for Playwright:

playwright install

Configuration
Before running the agent, you must configure your personal data and API keys. This data is kept local and is not committed to Git.

API Keys & Credentials:

Create a file named .env in the project root. You can copy the structure from .env.template if one is provided.

Add your API keys to this file:

GEMINI_API_KEY="your-google-ai-studio-key"
BRIGHTDATA_USERNAME="your-brightdata-username"
BRIGHTDATA_PASSWORD="your-brightdata-password"
BRIGHTDATA_HOST="brd.superproxy.io"
BRIGHTDATA_PORT="22225"

Personal Profiles (Crucial Step):

The agent needs your professional profile to work.

Copy config/profil_de.template.yaml to config/profil_de.yaml.

Copy config/profil_en.template.yaml to config/profil_en.yaml.

Open these new files and fill them with your detailed personal and professional information.

Search & Scoring Parameters:

Open config/config.yaml to adjust search terms, keywords for scoring, and other settings.

Usage
Build the Knowledge Base:

Any time you update your profil_de.yaml or profil_en.yaml, you must rebuild the vector databases.

python3 src/knowledge_base/builder.py

Run the Agent:

Execute the main script from the project's root directory.

TOKENIZERS_PARALLELISM=false python3 -m src.main

The agent will then start scraping, analyzing, and ranking jobs based on your configuration.