from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import ollama
import time
from typing import Annotated, List
from sqlalchemy.orm import Session
from database import get_db
from repository import RequestLogRepository

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
async def root(db: Session = Depends(get_db)) -> dict:
    start_time = time.time()
    response_data = {"message": "Hello World"}
    end_time = time.time()
    
    repo = RequestLogRepository(db)
    repo.create_request_log(
        endpoint="/",
        request_data={},
        response_data=response_data,
        response_time_ms=(end_time - start_time) * 1000
    )
    return response_data

@app.get("/api/llm/model", response_model=ModelsResponse)
async def list_models(db: Session = Depends(get_db)) -> ModelsResponse:
    start_time = time.time()
    try:
        models = ollama.list()
        response = ModelsResponse(
            models=[model['model'] for model in models['models']]
        )
        end_time = time.time()
        
        repo = RequestLogRepository(db)
        repo.create_request_log(
            endpoint="/api/llm/model",
            request_data={},
            response_data=dict(response),
            response_time_ms=(end_time - start_time) * 1000
        )
        return response
    except Exception as e:
        end_time = time.time()
        error_msg = f"Failed to list models: {str(e)}"
        repo = RequestLogRepository(db)
        repo.create_request_log(
            endpoint="/api/llm/model",
            request_data={},
            response_data={"error": error_msg},
            status_code=500,
            error_message=error_msg,
            response_time_ms=(end_time - start_time) * 1000
        )
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/llm/inference", response_model=InferenceResponse)
async def inference(request: InferenceRequest, db: Session = Depends(get_db)) -> InferenceResponse:
    start_time = time.time()
    try:
        response = ollama.generate(
            model=request.model,
            prompt=request.prompt
        )
        
        tokens = len(response['response'].split())  # Simple token count approximation
        tokens_per_second = tokens / (time.time() - start_time) if time.time() - start_time > 0 else 0
        
        inference_response = InferenceResponse(
            model=request.model,
            response=response['response'],
            tokens=tokens,
            token_per_second=round(tokens_per_second, 6)
        )

        end_time = time.time()
        repo = RequestLogRepository(db)
        repo.create_request_log(
            endpoint="/api/llm/inference",
            request_data=dict(request),
            response_data=dict(inference_response),
            model=request.model,
            response_time_ms=(end_time - start_time) * 1000
        )
        
        return inference_response
    except ollama.ResponseError as e:
        end_time = time.time()
        error_msg = f"Ollama error: {str(e)}"
        repo = RequestLogRepository(db)
        repo.create_request_log(
            endpoint="/api/llm/inference",
            request_data=dict(request),
            response_data={"error": error_msg},
            status_code=400,
            error_message=error_msg,
            model=request.model,
            response_time_ms=(end_time - start_time) * 1000
        )
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        end_time = time.time()
        error_msg = f"Internal server error: {str(e)}"
        repo = RequestLogRepository(db)
        repo.create_request_log(
            endpoint="/api/llm/inference",
            request_data=dict(request),
            response_data={"error": error_msg},
            status_code=500,
            error_message=error_msg,
            model=request.model,
            response_time_ms=(end_time - start_time) * 1000
        )
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
