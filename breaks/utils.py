import yaml
from pathlib import Path
import logging
import requests
import random
from django.conf import settings

logger = logging.getLogger(__name__)


def get_reminder_content():
    file = Path(__file__).parent / "messages.yaml"
    try:
        with open(file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError) as e:
        logger.error(f"Failed to load or parse messages.yaml: {e}")
        raise

    try:
        subject = data["break_reminder"]["subject"]
        message = data["break_reminder"]["message"]
    except (KeyError, TypeError) as e:
        logger.error(f"Missing keys in messages.yaml: {e}")
        raise

    return subject, message


def fetch_inspirational_quote():
    try:
        response = requests.get(settings.ZEN_QUOTES_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data and isinstance(data, list):
            quote_data = random.choice(data)
            quote = quote_data.get("q")
            author = quote_data.get("a")

            if quote and author:
                return f'"{quote}" - {author}'

    except Exception as e:
        logger.error(f"Failed to fetch quote: {e}")

    return None
