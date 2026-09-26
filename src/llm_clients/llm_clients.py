import json
from collections.abc import AsyncIterator

import httpx


class OpenAIClient:
    """Minimal async client for OpenAI's Responses API."""

    def __init__(self, http: httpx.AsyncClient, api_key: str) -> None:
        self._http = http
        self._api_key = api_key

    async def ask(self, prompt: str, model: str) -> str:
        response = await self._http.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"model": model, "input": prompt, "max_output_tokens": 500},
        )
        response.raise_for_status()
        data = response.json()
        return "".join(
            block["text"]
            for item in data.get("output", [])
            for block in item.get("content", [])
            if block.get("type") == "output_text"
        )

    async def stream(self, prompt: str, model: str) -> AsyncIterator[str]:
        """Yield text deltas from an OpenAI Responses API stream."""
        async with self._http.stream(
            "POST",
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": model,
                "input": prompt,
                "max_output_tokens": 500,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue

                data = line.removeprefix("data:").strip()
                if not data or data == "[DONE]":
                    continue

                event = json.loads(data)
                event_type = event.get("type")

                if event_type == "response.output_text.delta":
                    yield event["delta"]
                elif event_type in {"error", "response.failed"}:
                    raise RuntimeError("OpenAI returned an error while generating the response")
