import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    anthropic_api_key: str
    newsapi_key: str
    wp_url: str
    wp_user: str
    wp_app_password: str
    telegram_bot_token: str
    telegram_chat_id: str

    @classmethod
    def from_env(cls) -> "Settings":
        missing = []
        required = [
            "ANTHROPIC_API_KEY",
            "NEWSAPI_KEY",
            "WP_URL",
            "WP_USER",
            "WP_APP_PASSWORD",
        ]
        for key in required:
            if not os.getenv(key):
                missing.append(key)
        if missing:
            raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")

        return cls(
            anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
            newsapi_key=os.environ["NEWSAPI_KEY"],
            wp_url=os.environ["WP_URL"].rstrip("/"),
            wp_user=os.environ["WP_USER"],
            wp_app_password=os.environ["WP_APP_PASSWORD"],
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        )


settings = Settings.from_env()
