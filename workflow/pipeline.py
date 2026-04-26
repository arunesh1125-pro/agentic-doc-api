import time
from agents.extractor import extract
from agents.validator import validate
from agents.indexer import index

def run_pipeline(raw_text: str) -> dict:
    state = {
        "raw_text": raw_text,
        "extracted_data": None,
        "validation_result": None,
        "vector_id": None,
        "errors": [],
        "start_time": time.time()
    }

    # Agent 1
    state["extracted_data"] = extract(raw_text)

    # Agent 2
    val_result = validate(state["extracted_data"])
    state["validation_result"] = val_result

    if val_result["status"] == "fail":
        state["errors"].append("Extraction returned no usable fields")
        return state

    # Agent 3
    state["vector_id"] = index(val_result["data"])
    state["total_ms"] = int((time.time() - state["start_time"]) * 1000)

    return state