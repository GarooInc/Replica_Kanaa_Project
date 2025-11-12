import json
from typing import Any, AsyncIterator, Dict, Optional
import datetime

def _encode(data: Any) -> str:
    """Codifica el dato como JSON válido para SSE."""
    if isinstance(data, str):
        return json.dumps({"content": data, "timestamp": datetime.datetime.utcnow().isoformat()})
    try:
        payload = dict(data)
        payload["timestamp"] = datetime.datetime.utcnow().isoformat()
        return json.dumps(payload, ensure_ascii=False)
    except Exception:
        return json.dumps({"content": str(data), "timestamp": datetime.datetime.utcnow().isoformat()})


async def send_event(event_type: str, data: Any) -> AsyncIterator[str]:
    """Genera un evento SSE con tipo y datos."""
    yield f"event: {event_type}\n"
    yield f"data: {_encode(data)}\n\n"


async def send_error(message: str, code: Optional[int] = None) -> AsyncIterator[str]:
    """Evento de error estándar."""
    error_data: Dict[str, Any] = {"error": message}
    if code:
        error_data["code"] = code
    async for chunk in send_event("error", error_data):
        yield chunk


async def send_done() -> AsyncIterator[str]:
    """Evento final."""
    yield "event: done\n"
    yield "data: {}\n\n"
