import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from workflow.pipeline import run_pipeline
from sentence_transformers import SentenceTransformer
from db.vector_store import search
from utils.logger import get_logger

app = FastAPI()
logger = get_logger("api")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

class DocumentInput(BaseModel):
    document: str

@app.post("/process")
def process_document(body: DocumentInput):
    if not body.document.strip():
        raise HTTPException(status_code=400, detail="Document is empty")

    logger.info(f"POST /process received | doc_length={len(body.document)}")
    state = run_pipeline(body.document)

    if state["errors"]:
        raise HTTPException(status_code=422, detail=state["errors"])

    val = state["validation_result"]
    status = "success" if val["status"] == "pass" else "partial"

    return {
        "status": status,
        "document_id": state["vector_id"],
        "data": val["data"],
        "warnings": val["warnings"],
        "latency_ms": state.get("total_ms", 0)
    }

@app.get("/search")
def search_documents(q: str, top_k: int = 5):
    start = time.time()
    query_embedding = embed_model.encode(q).tolist()
    results = search(query_embedding, top_k)

    formatted = []
    for i, meta in enumerate(results["metadatas"][0]):
        formatted.append({
            "document_id": meta.get("document_id"),
            "score": round(1 - results["distances"][0][i], 4),
            "data": meta
        })

    latency = int((time.time() - start) * 1000)
    return {"query": q, "results": formatted, "latency_ms": latency}

@app.get("/health")
def health():
    return {"status": "ok"}