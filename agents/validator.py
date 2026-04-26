from utils.logger import get_logger
from dateutil import parser as dateparser

logger = get_logger("validator")

def validate(extracted: dict) -> dict:
    warnings = []
    data = extracted.copy()

    # Check if all fields are None
    if all(v is None for v in data.values()):
        return {"status": "fail", "data": data, "warnings": ["No fields extracted"]}

    # Critical fields check
    if not data.get("vendor_name") or not data.get("total_amount"):
        warnings.append("Critical fields missing: vendor_name or total_amount")

    # Date normalization
    if data.get("date"):
        try:
            parsed = dateparser.parse(str(data["date"]))
            data["date"] = parsed.strftime("%Y-%m-%d")
        except:
            warnings.append("date is non-ISO format")

    # total_amount parsing
    if data.get("total_amount"):
        try:
            amount_str = str(data["total_amount"]).replace(",", "").replace("USD", "").replace("INR", "").strip()
            data["total_amount"] = float(amount_str)
        except:
            warnings.append("total_amount could not be parsed as number")

    status = "pass" if not warnings else "warn"
    logger.info(f"Validation {status} | warnings={len(warnings)}")
    return {"status": status, "data": data, "warnings": warnings}