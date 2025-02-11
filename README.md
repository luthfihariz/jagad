# JAGAD

Yet, Just another Generative AI Deployment

## Prerequisites

1. Install Ollama:
   ```bash
   # For macOS
   curl -fsSL https://ollama.com/install.sh | sh
   ```
   For other operating systems, visit: https://ollama.ai/download

2. Start Ollama service:
   ```bash
   ollama serve
   ```

3. Pull at least one model (e.g., llama2):
   ```bash
   ollama pull llama2
   ```

4. Make sure you have pipenv installed:
   ```bash
   pip install pipenv
   ```

## Setup and Running

1. Make sure you have pipenv installed
2. Install dependencies:
   ```
   pipenv install
   ```
3. Run the application:
   ```
   pipenv run uvicorn main:app
   ```

The API will be available at http://localhost:8000

## Endpoints

- GET `/`: Returns a Hello World message
- GET `/docs`: OpenAPI documentation (provided by FastAPI)

### POST `/api/llm/inference`

Request body
```json
{
   "prompt": "Hello, World!"
   "model": "llama3.1-70b"
}
```

Response
```json
{
   "model": "llama3.1-70b"
   "response": "Hello, World!"
   "tokens": 9
   "token_per_second": 0.111111
}
```

### GET `/api/llm/model`
Response
```json
{
   "models": [
      "llama2",
      "codellama",
      "mistral",
      "gemma"
   ]
}
```

Note: The actual list of models will depend on which models you have pulled using the `ollama pull` command.

## Troubleshooting

1. If you get an error about Ollama not being available, make sure the Ollama service is running:
   ```bash
   ollama serve
   ```

2. To check available models:
   ```bash
   ollama list
   ```

3. To pull a new model:
   ```bash
   ollama pull <model-name>
   ```