import requests
import json
import time
import os
from utils.logger import get_logger

logger = get_logger("extractor")

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"

PROMPT_TEMPLATE = """Extract fields from this document and return ONLY a valid JSON object with these exact keys:
vendor_name, document_number, total_amount, date, document_type

Document:
{text}

Return ONLY the JSON object, nothing else. Use null for missing fields.
Example: {{"vendor_name": "ABC Ltd", "document_number": "INV-001", "total_amount": 1200.0, "date": "2024-01-15", "document_type": "Invoice"}}"""

def extract(raw_text: str) -> dict:
    logger.info(f"Extraction started | method=llm | doc_length={len(raw_text)}")
    start = time.time()
    default = {"vendor_name": None, "document_number": None, "total_amount": None, "date": None, "document_type": None}

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "phi3:mini",
            "prompt": PROMPT_TEMPLATE.format(text=raw_text),
            "stream": False
        }, timeout=180)

        logger.info(f"Ollama status: {response.status_code}")
        raw = response.json()
        logger.info(f"Ollama keys: {list(raw.keys())}")

        result_text = raw.get("response", "")
        if not result_text:
            logger.error("Empty response from Ollama")
            return default

        start_idx = result_text.find("{")
        end_idx = result_text.rfind("}") + 1
        if start_idx == -1:
            logger.error(f"No JSON found in response: {result_text[:200]}")
            return default

        json_str = result_text[start_idx:end_idx]
        extracted = json.loads(json_str)

    except Exception as e:
        logger.error(f"Extraction failed | error={e}")
        extracted = default

    duration = int((time.time() - start) * 1000)
    fields_found = sum(1 for v in extracted.values() if v is not None)
    logger.info(f"Extraction complete | fields={fields_found} | duration_ms={duration}")
    return extracted