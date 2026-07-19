import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

_REQUIRED = {
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "SERPER_API_KEY": SERPER_API_KEY,  # used by SerperDevTool (researcher)
    "GITHUB_TOKEN": GITHUB_TOKEN,  # used by the GitHub MCP server (Ritu)
}


def missing_config() -> list[str]:
    """Names of required env vars that are unset or empty."""
    return [name for name, value in _REQUIRED.items() if not value]
