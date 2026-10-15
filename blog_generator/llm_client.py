import json
import logging
import os
import re

from groq import Groq, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, before_sleep_log

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "llama-3.1-8b-instant"
_DEFAULT_FALLBACK_MODELS = ("llama-3.3-70b-versatile",)
_MAX_TOKENS = 2048


def _is_rate_limit(exc: BaseException) -> bool:
    return isinstance(exc, RateLimitError)


def _is_model_unavailable(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return (
        "model_not_found" in msg
        or "does not exist" in msg
        or "do not have access" in msg
        or "not found" in msg
    )


class LLMClient:
    def __init__(self, api_key: str | None = None):
        # LLM_PROVIDER=groq2 uses the second Groq account key
        provider = os.getenv("LLM_PROVIDER", "groq").lower()
        if provider == "groq2":
            key = api_key or os.environ["GROQ_API_KEY_2"]
        else:
            key = api_key or os.environ["GROQ_API_KEY"]
        self._client = Groq(api_key=key)

        primary_model = os.getenv("GROQ_MODEL", _DEFAULT_MODEL).strip() or _DEFAULT_MODEL
        fallback_raw = os.getenv("GROQ_MODEL_FALLBACKS", "")
        if fallback_raw.strip():
            fallback_models = [m.strip() for m in fallback_raw.split(",") if m.strip()]
        else:
            fallback_models = list(_DEFAULT_FALLBACK_MODELS)
        self._models = []
        for model in [primary_model, *fallback_models]:
            if model not in self._models:
                self._models.append(model)

        logger.info(f"LLMClient using Groq ({provider})")

    @retry(
        retry=retry_if_exception(_is_rate_limit),
        wait=wait_exponential(multiplier=1, min=15, max=120),
        stop=stop_after_attempt(6),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def complete(self, system: str, user_message: str, max_tokens: int = _MAX_TOKENS) -> str:
        last_exc: Exception | None = None
        for i, model in enumerate(self._models):
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_message},
                    ],
                )
                text = response.choices[0].message.content
                logger.debug(
                    f"LLM call ({model}) — input_tokens={response.usage.prompt_tokens} "
                    f"output_tokens={response.usage.completion_tokens}"
                )
                return text
            except Exception as exc:
                last_exc = exc
                has_more_models = i < len(self._models) - 1
                if has_more_models and _is_model_unavailable(exc):
                    logger.warning(f"Groq model unavailable ({model}), trying next model")
                    continue
                raise

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("No Groq model configured")

    def complete_json(self, system: str, user_message: str) -> dict:
        raw = self.complete(system, user_message)
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.DOTALL)
        return json.loads(cleaned)
