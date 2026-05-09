import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

def _parse_ids(env_var: str) -> list[int]:
    val = os.getenv(env_var, "")
    return [int(x.strip()) for x in val.split(",") if x.strip().lstrip('-').isdigit()]

ALLOWED_USER_IDS = _parse_ids("ALLOWED_USER_IDS")
if not ALLOWED_USER_IDS:
    raise ValueError("ALLOWED_TELEGRAM_USER_IDS is not set or invalid.")