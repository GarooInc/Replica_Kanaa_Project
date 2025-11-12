# main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import json  # Para encoding JSON de tokens

from app.streaming.streaming import ask_streaming

app = FastAPI(
    title="Kaana Agent Streaming API",
    description="API para el hotel Kaana con streaming real de tokens.",
    version="2.0.0",
    #lifespan=lifespan
)


class AskRequest(BaseModel):
    question: str
    message_history: List[Dict] = []

@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    generator = ask_streaming(request.question, request.message_history)
    return StreamingResponse(generator, media_type="text/event-stream")



if __name__ == "__main__":
    uvicorn.run("app.streaming.streaming:app", host="0.0.0.0", port=8000)