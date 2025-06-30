import warnings
# Suppress unnecessary warnings from pydantic serializers used by LiteLLM
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

import logging

# Setup basic logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# === LiteLLM Configuration ===
LITELLM_MODEL = "meta-llama-3-70b-instruct"  # Replace if using a different model
LITELLM_API_BASE = "https://your-api-proxy.com/v1"  # Replace with actual proxy URL
LITELLM_API_KEY = "sk-your-api-key"  # Keep it secure — never commit this

# === General Project Paths ===
GUIDELINE_JSON_PATH = "guidelines/guidelines.json"
REVIEW_OUTPUT_JSON = "output/review.json"
REVIEW_OUTPUT_HTML = "output/report.html"

# === Prompting and Control ===
MAX_GUIDELINE_MATCHES = 5  # Number of top guidelines to inject per code chunk
CHUNK_LINE_LIMIT = 200     # Max lines per code chunk
