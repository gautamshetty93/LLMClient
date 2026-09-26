import os
import json
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

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

@app.post("/chat/stream")
async def chat_stream(body: ChatRequest, request: Request) -> StreamingResponse:
    """Stream generated text as Server-Sent Events (SSE)."""
    http: httpx.AsyncClient = request.app.state.http
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    client = OpenAIClient(http, api_key)

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for text_delta in client.stream(body.prompt, body.model):
                yield f"data: {json.dumps({'text': text_delta})}\n\n"
        except httpx.HTTPStatusError as exc:
            error = {"detail": f"OpenAI API returned HTTP {exc.response.status_code}"}
            yield f"event: error\ndata: {json.dumps(error)}\n\n"
            return
        except (httpx.RequestError, RuntimeError) as exc:
            detail = str(exc) if isinstance(exc, RuntimeError) else "Could not reach OpenAI API"
            error = {"detail": detail}
            yield f"event: error\ndata: {json.dumps(error)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
