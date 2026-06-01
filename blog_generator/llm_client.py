import json
import logging
import os
import re

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

logger = logging.getLogger(__name__)

_GROQ_MODEL = "llama-3.3-70b-versatile"
_GEMINI_MODEL = "gemini-2.0-flash"
_MAX_TOKENS = 4096


def _is_rate_limit(exc: BaseException) -> bool:
    from groq import RateLimitError as GroqRLE
    if isinstance(exc, GroqRLE):
        return True
    try:
        from google.api_core.exceptions import ResourceExhausted
        return isinstance(exc, ResourceExhausted)
    except ImportError:
        return False


class LLMClient:
    def __init__(self, api_key: str | None = None):
        self._provider = os.getenv("LLM_PROVIDER", "groq").lower()

        if self._provider == "gemini":
            import google.generativeai as genai
            key = api_key or os.environ["GEMINI_API_KEY"]
            genai.configure(api_key=key)
            self._gemini = genai.GenerativeModel(_GEMINI_MODEL)
            self._groq = None
        else:
            from groq import Groq
            self._groq = Groq(api_key=api_key or os.environ["GROQ_API_KEY"])
            self._gemini = None

        logger.info(f"LLMClient using provider: {self._provider}")

    @retry(
        retry=retry_if_exception_type(_is_rate_limit),
        wait=wait_exponential(multiplier=1, min=15, max=120),
        stop=stop_after_attempt(6),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def complete(self, system: str, user_message: str, max_tokens: int = _MAX_TOKENS) -> str:
        if self._provider == "gemini":
            return self._complete_gemini(system, user_message, max_tokens)
        return self._complete_groq(system, user_message, max_tokens)

    def _complete_groq(self, system: str, user_message: str, max_tokens: int) -> str:
        response = self._groq.chat.completions.create(
            model=_GROQ_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
        )
        text = response.choices[0].message.content
        logger.debug(
            f"Groq call — input_tokens={response.usage.prompt_tokens} "
            f"output_tokens={response.usage.completion_tokens}"
        )
        return text

    def _complete_gemini(self, system: str, user_message: str, max_tokens: int) -> str:
        from google.generativeai.types import GenerationConfig
        response = self._gemini.generate_content(
            f"{system}\n\n{user_message}",
            generation_config=GenerationConfig(max_output_tokens=max_tokens),
        )
        text = response.text
        logger.debug(f"Gemini call — finish_reason={response.candidates[0].finish_reason}")
        return text

    def complete_json(self, system: str, user_message: str) -> dict:
        raw = self.complete(system, user_message)
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.DOTALL)
        return json.loads(cleaned)
