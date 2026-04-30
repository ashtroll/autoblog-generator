import json
import logging
import os
import re

import anthropic

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 4096


class LLMClient:
    def __init__(self, api_key: str | None = None):
        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ["ANTHROPIC_API_KEY"]
        )

    def complete(self, system: str, user_message: str, max_tokens: int = _MAX_TOKENS) -> str:
        response = self._client.messages.create(
            model=_MODEL,
            max_tokens=max_tokens,
            system=[
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text
        logger.debug(
            f"LLM call — input_tokens={response.usage.input_tokens} "
            f"output_tokens={response.usage.output_tokens}"
        )
        return text

    def complete_json(self, system: str, user_message: str) -> dict:
        raw = self.complete(system, user_message)
        # Strip markdown fences if the model added them despite instructions
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.DOTALL)
        return json.loads(cleaned)
