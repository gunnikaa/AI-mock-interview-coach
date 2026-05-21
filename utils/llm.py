import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)

_client = None

_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY is not set in .env")
        print(f"[LLM] Loaded API key: {api_key[:10]}...{api_key[-4:]}")
        _client = genai.Client(api_key=api_key)
    return _client


def call_llm(prompt: str, max_tokens: int = 1024) -> str:
    """Call Gemini — try each model once, fail fast on rate limit."""
    client = _get_client()
    last_error = None

    for model in _MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=max_tokens,
                ),
            )
            return response.text.strip() if response.text else ""
        except Exception as e:
            err_str = str(e)
            last_error = e
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                print(f"[LLM] {model} → rate limit, trying next")
                continue
            if "404" in err_str or "NOT_FOUND" in err_str:
                print(f"[LLM] {model} → not found, trying next")
                continue
            raise RuntimeError(f"Gemini API call failed: {e}") from e

    raise RuntimeError(
        f"All Gemini models are rate-limited or unavailable. "
        f"Your free-tier quota is exhausted — wait until daily reset (midnight US Pacific) "
        f"or use a different Google account. Last error: {last_error}"
    )
