import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, HTTPException, Request

from llm_clients.llm_clients import OpenAIClient
from llm_clients.schemas import ChatRequest, ChatResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # One connection pool is shared by both provider clients and closed on shutdown.
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as http:
        app.state.http = http
        yield


app = FastAPI(title="Async LLM Chat API", lifespan=lifespan)


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    http: httpx.AsyncClient = request.app.state.http

    # if body.provider == "openai":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    client = OpenAIClient(http, api_key)
    # else:
    #     api_key = os.getenv("ANTHROPIC_API_KEY")
    #     if not api_key:
    #         raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY is not configured")
    #     client = AnthropicClient(http, api_key)

    try:
        text = await client.ask(body.prompt, body.model)
    except httpx.HTTPStatusError as exc:
        # Avoid returning provider response bodies, which may include sensitive details.
        raise HTTPException(
            status_code=502,
            detail=f"API returned HTTP {exc.response.status_code}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach {body.provider} API") from exc

    return ChatResponse(model=body.model, text=text)
