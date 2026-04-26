import uuid
import time
from sentence_transformers import SentenceTransformer
from db.vector_store import add_document
from utils.logger import get_logger

logger = get_logger("indexer")
model = SentenceTransformer("all-MiniLM-L6-v2")

def index(validated_data: dict) -> str:
    doc_id = str(uuid.uuid4())
    start = time.time()

    d = validated_data
    embedding_text = (
        f"{d.get('document_type','Document')} from {d.get('vendor_name','unknown')} "
        f"dated {d.get('date','unknown')} "
        f"for amount {d.get('total_amount','unknown')} "
        f"document number {d.get('document_number','unknown')}"
    )

    embedding = model.encode(embedding_text).tolist()
    metadata = {k: str(v) if v is not None else "" for k, v in d.items()}
    metadata["document_id"] = doc_id

    add_document(doc_id, embedding, metadata)

    duration = int((time.time() - start) * 1000)
    logger.info(f"Indexed document | id={doc_id} | duration_ms={duration}")
    return doc_id