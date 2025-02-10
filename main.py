from ast import mod
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
import ollama
import time
from typing import Annotated, List

app = FastAPI(
    title="Jagad API",
    description="Just Another Generative AI Deployment",
    version="1.0.0"
)

class InferenceRequest(BaseModel):
    prompt: Annotated[str, Field(description="The prompt to send to the model")]
    model: Annotated[str, Field(description="The Ollama model to use for inference")]

    class Config:
        schema_extra = {
            "examples": [
                {
                    "prompt": "Hello, World!",
                    "model": "llama2"
                }
            ]
        }

class InferenceResponse(BaseModel):
    model: Annotated[str, Field(description="The model used for inference")]
    response: Annotated[str, Field(description="The model's response")]
    tokens: Annotated[int, Field(description="Number of tokens in the response")]
    token_per_second: Annotated[float, Field(description="Tokens processed per second")]

    class Config:
        schema_extra = {
            "examples": [
                {
                    "model": "llama2",
                    "response": "Hello! How can I assist you today?",
                    "tokens": 8,
                    "token_per_second": 0.123456
                }
            ]
        }

class ModelsResponse(BaseModel):
    models: Annotated[List[str], Field(description="List of available Ollama models")]

    class Config:
        schema_extra = {
            "examples": [
                {
                    "models": [
                        "llama2",
                        "codellama",
                        "mistral"
                    ]
                }
            ]
        }

@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}

@app.get("/api/llm/model", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    try:
        models = ollama.list()
        print(models)
        return ModelsResponse(
            models=[model['model'] for model in models['models']]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@app.post("/api/llm/inference", response_model=InferenceResponse)
async def inference(request: InferenceRequest) -> InferenceResponse:
    try:
        start_time = time.time()
        
        response = ollama.generate(
            model=request.model,
            prompt=request.prompt
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        tokens = len(response['response'].split())  # Simple token count approximation
        tokens_per_second = tokens / elapsed_time if elapsed_time > 0 else 0
        
        return InferenceResponse(
            model=request.model,
            response=response['response'],
            tokens=tokens,
            token_per_second=round(tokens_per_second, 6)
        )
    except ollama.ResponseError as e:
        raise HTTPException(status_code=400, detail=f"Ollama error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
