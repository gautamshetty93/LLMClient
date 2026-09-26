import asyncio
import json

import httpx
import pytest

from llm_clients.llm_clients import OpenAIClient


def test_ask_posts_request_and_extracts_output_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == "https://api.openai.com/v1/responses"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert json.loads(request.content) == {
            "model": "gpt-test",
            "input": "Say hello",
            "max_output_tokens": 500,
        }
        return httpx.Response(
            200,
            json={
                "output": [
                    {"content": [{"type": "output_text", "text": "Hello there!"}]}
                ]
            },
        )

    async def run() -> str:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            client = OpenAIClient(http, api_key="test-key")
            return await client.ask("Say hello", model="gpt-test")

    assert asyncio.run(run()) == "Hello there!"


def test_stream_yields_text_deltas() -> None:
    events = "\n\n".join(
        [
            'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"Hello "}',
            'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"there!"}',
            'event: response.completed\ndata: {"type":"response.completed"}',
            "data: [DONE]",
        ]
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-key"
        request_json = json.loads(request.content)
        assert request_json["stream"] is True
        assert request_json["model"] == "gpt-test"
        return httpx.Response(200, text=events)

    async def run() -> list[str]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            client = OpenAIClient(http, api_key="test-key")
            return [chunk async for chunk in client.stream("Say hello", "gpt-test")]

    assert asyncio.run(run()) == ["Hello ", "there!"]


def test_ask_raises_for_http_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "Invalid API key"}})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            client = OpenAIClient(http, api_key="bad-key")
            await client.ask("Say hello", model="gpt-test")

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(run())
