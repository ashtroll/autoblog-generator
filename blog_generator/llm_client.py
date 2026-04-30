import json
import logging
import os
import re

from groq import Groq

logger = logging.getLogger(__name__)

_MODEL = "llama-3.3-70b-versatile"
_MAX_TOKENS = 4096


class LLMClient:
    def __init__(self, api_key: str | None = None):
        self._client = Groq(
            api_key=api_key or os.environ["GROQ_API_KEY"]
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
