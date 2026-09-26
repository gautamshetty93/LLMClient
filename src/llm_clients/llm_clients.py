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