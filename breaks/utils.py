import yaml
from pathlib import Path
import logging

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
