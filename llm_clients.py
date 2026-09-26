import httpx


class OpenAIClient:
    def __init__(self, api_key: str, timeout: float = 30.0) -> None:
        self._api_key = api_key
        self._http = httpx.AsyncClient(timeout=timeout)

    async def ask(self, prompt: str, model: str) -> str:
        response = await self._http.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": model,
                "input": prompt,
                "max_output_tokens": 500,
            },
        )
        response.raise_for_status()
        data = response.json()

        return "".join(
            block["text"]
            for item in data["output"]
            for block in item.get("content", [])
            if block.get("type") == "output_text"
        )

    async def close(self) -> None:
        await self._http.aclose()


# class AnthropicClient:
#     def __init__(self, api_key: str, timeout: float = 30.0) -> None:
#         self._api_key = api_key
#         self._http = httpx.AsyncClient(timeout=timeout)

#     async def ask(self, prompt: str, model: str) -> str:
#         response = await self._http.post(
#             "https://api.anthropic.com/v1/messages",
#             headers={
#                 "x-api-key": self._api_key,
#                 "anthropic-version": "2023-06-01",
#             },
#             json={
#                 "model": model,
#                 "max_tokens": 500,
#                 "messages": [{"role": "user", "content": prompt}],
#             },
#         )
#         response.raise_for_status()
#         data = response.json()

#         return "".join(
#             block["text"]
#             for block in data["content"]
#             if block.get("type") == "text"
#         )

#     async def close(self) -> None:
#         await self._http.aclose()