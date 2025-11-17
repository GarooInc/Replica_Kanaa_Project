# main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import json  # Para encoding JSON de tokens
import logging
from app.streaming.streaming import ask_streaming

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lifespan(app: FastAPI):
    @asynccontextmanager
    async def lifespan_context(app: FastAPI):
        try: # rag retriever setup
            from app.rag.rag_store import get_retriever, set_global_retriever
            retriever = get_retriever(k=5)
            app.state.hotel_retriever = retriever
            set_global_retriever(retriever)
            logger.info("SUCCESS: Retriever global configurado en lifespan.")
        except Exception as e:
            logger.error(f"ERROR al configurar el retriever en lifespan: {e}")

        yield
    return lifespan_context(app)

app = FastAPI(
    title="Itzana Agent Streaming API",
    description="API para el hotel Itzana con streaming real de tokens.",
    version="3.0.0",
    lifespan=lifespan
)

@app.put("/contextrebuild")
async def update_vector_index(files: List[UploadFile] = File(...)):
    try:
        from app.rag.rag_indexer import index_markdown_contents
        from app.rag.rag_store import get_retriever, set_global_retriever

        file_contents = [await f.read() for f in files]
        filenames = [f.filename for f in files]

        result = index_markdown_contents(file_contents, filenames, rebuild=True)
        logging.info("SUCCESS: Reindexación completada.")

        retriever = get_retriever(k=3)
        app.state.hotel_retriever = retriever
        set_global_retriever(retriever)
        logging.info("SUCCESS: Retriever global actualizado tras reindexar.")

        return {"message": "Índice reconstruido y retriever actualizado.", "details": result}

    except Exception as e:
        return {"error": str(e)}

class AskRequest(BaseModel):
    question: str
    message_history: List[Dict] = []

@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    generator = ask_streaming(request.question, request.message_history)

    return StreamingResponse(
        generator,
        status_code=200,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
