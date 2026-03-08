from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("DB_PATH", ROOT / "data" / "voc_reviews.db"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", ROOT / "outputs"))
PRODUCT_CONFIG_PATH = Path(os.getenv("PRODUCT_CONFIG_PATH", ROOT / "data" / "products.json"))
CLAWDBOT_API_KEY = os.getenv("CLAWDBOT_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
CLAWDBOT_BASE_URL = os.getenv("CLAWDBOT_BASE_URL", "") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
CLAWDBOT_MODEL = os.getenv("CLAWDBOT_MODEL", "") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
REQUEST_TIMEOUT_SEC = int(os.getenv("REQUEST_TIMEOUT_SEC", "30"))
MAX_REVIEWS_PER_PRODUCT = int(os.getenv("MAX_REVIEWS_PER_PRODUCT", "600"))
PRODUCT_TEAM_WEBHOOK_URL = os.getenv("PRODUCT_TEAM_WEBHOOK_URL", "")
MARKETING_TEAM_WEBHOOK_URL = os.getenv("MARKETING_TEAM_WEBHOOK_URL", "")
SUPPORT_TEAM_WEBHOOK_URL = os.getenv("SUPPORT_TEAM_WEBHOOK_URL", "")
NOTIFY_ON_ZERO_DELTA = os.getenv("NOTIFY_ON_ZERO_DELTA", "false").lower() == "true"
