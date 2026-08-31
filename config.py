import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
DATA = ROOT / "data"
CAMPAIGNS = ROOT / "campaigns"

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
# Gmail App Password (needs 2-step verification on), not the account password.
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")
# No LLM API key by design: drafting is done by Claude Code (the subscription),
# not the Anthropic API. See README "Drafting".


def data_dir(campaign):
    d = DATA / campaign
    d.mkdir(parents=True, exist_ok=True)
    return d
