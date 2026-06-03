import json
import logging
import os
import re

from groq import Groq, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, before_sleep_log

logger = logging.getLogger(__name__)

_MODEL = "llama-3.3-70b-versatile"
_MAX_TOKENS = 2048


def _is_rate_limit(exc: BaseException) -> bool:
    return isinstance(exc, RateLimitError)


class LLMClient:
    def __init__(self, api_key: str | None = None):
        # LLM_PROVIDER=groq2 uses the second Groq account key
        provider = os.getenv("LLM_PROVIDER", "groq").lower()
        if provider == "groq2":
            key = api_key or os.environ["GROQ_API_KEY_2"]
        else:
            key = api_key or os.environ["GROQ_API_KEY"]
        self._client = Groq(api_key=key)
        logger.info(f"LLMClient using Groq ({provider})")

    @retry(
        retry=retry_if_exception(_is_rate_limit),
        wait=wait_exponential(multiplier=1, min=15, max=120),
        stop=stop_after_attempt(6),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def complete(self, system: str, user_message: str, max_tokens: int = _MAX_TOKENS) -> str:
        response = self._client.chat.completions.create(
            model=_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
        )
        text = response.choices[0].message.content
        logger.debug(
            f"LLM call — input_tokens={response.usage.prompt_tokens} "
            f"output_tokens={response.usage.completion_tokens}"
        )
        return text

    def complete_json(self, system: str, user_message: str) -> dict:
        raw = self.complete(system, user_message)
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.DOTALL)
        return json.loads(cleaned)
