# Async LLM Chat API

Small FastAPI app that calls OpenAI with `httpx.AsyncClient`.

## Setup

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -e .
```

Set your OpenAI API key in the same terminal before launching the app:

```powershell
$env:OPENAI_API_KEY = "your-key"
```

## Run

```bash
python -m uvicorn llm_clients.main:app --app-dir src --reload
```

Open `http://127.0.0.1:8000/docs` to try `POST /chat` interactively.

Example body:

```json
{
  "model": "gpt-5",
  "prompt": "Explain async I/O in one sentence."
}
```

# Async LLM Chat API

Small FastAPI app that calls OpenAI with `httpx.AsyncClient`.

## Setup

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -e .
```

Set your OpenAI API key in the same terminal before launching the app:

```powershell
$env:OPENAI_API_KEY = "your-key"
```

## Run

```bash
python -m uvicorn llm_client.main:app --app-dir src --reload
```

Open `http://127.0.0.1:8000/docs` to try `POST /chat` interactively.

Example body:

```json
{
  "model": "gpt-5",
  "prompt": "Explain async I/O in one sentence."
}
```
