"""One OpenRouter gateway, same pattern as FinLearn Guard."""
import os
from typing import Dict, Any


def analyze_with_llm(prompt: str, text: str, max_chars: int = 6000) -> Dict[str, Any]:
    key = os.getenv("OPENROUTER_API_KEY", "")
    model = os.getenv("OPENROUTER_MODEL", "mistralai/ministral-8b-2512")
    if not key:
        return {"ok": False, "verdict": "error", "error": "missing OPENROUTER_API_KEY"}
    try:
        import httpx
    except Exception as e:
        return {"ok": False, "verdict": "error", "error": f"httpx missing: {e}"}
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": (text or "")[:max_chars]},
            ],
            "temperature": 0.2,
        }
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        if r.status_code != 200:
            return {"ok": False, "verdict": "error", "error": f"HTTP {r.status_code}: {r.text[:300]}"}
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        return {"ok": True, "verdict": "ok", "text": content}
    except Exception as e:
        return {"ok": False, "verdict": "error", "error": str(e)}
