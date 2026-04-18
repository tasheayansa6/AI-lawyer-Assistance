"""
AI Legal Assistant - Groq API interface.
Fixes: thread-safe cache, stronger PII filtering, removed unused imports.
"""

import requests
import os
import re
import time
import logging
import hashlib
import datetime
import threading
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Query file logger ──────────────────────────────────────────────────────────
query_logger = logging.getLogger("query_logger")
query_logger.setLevel(logging.INFO)
if not query_logger.handlers:
    _fh = logging.FileHandler("query_log.log")
    _fh.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    query_logger.addHandler(_fh)

# ── Content filtering ──────────────────────────────────────────────────────────
INAPPROPRIATE_KEYWORDS = [
    "evade tax", "hide assets", "fake document", "lie in court", "bribe",
    "commit fraud", "money laundering", "perjury", "obstruct justice",
    "witness tampering", "false evidence", "stalk", "harass", "hack",
    "steal", "blackmail",
]

# Pre-compiled PII patterns for performance
_PII_PATTERNS = [
    (re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"), "[EMAIL REDACTED]"),
    (re.compile(r"\b\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}\b"), "[PHONE REDACTED]"),
    (re.compile(r"\b\+?[\d\s\-\(\)]{10,15}\b"), "[PHONE REDACTED]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN REDACTED]"),
    (re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"), "[CC REDACTED]"),
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "[IP REDACTED]"),
    (re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b", re.I), "[DATE REDACTED]"),
    (re.compile(r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b"), "[DATE REDACTED]"),
]


def is_inappropriate(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in INAPPROPRIATE_KEYWORDS)


def filter_pii(text: str) -> str:
    if not text:
        return text
    try:
        for pattern, replacement in _PII_PATTERNS:
            text = pattern.sub(replacement, text)
    except Exception as e:
        logger.error("PII filter error: %s", e)
    return text


def log_query(query: str, response: str, jurisdiction: str = "US"):
    try:
        entry = f"Query: {query[:100]} | Response: {response[:100]} | Jurisdiction: {jurisdiction}"
        query_logger.info(entry)
        with open("query_log.txt", "a", encoding="utf-8") as f:
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{ts}|{jurisdiction}|{query[:100]}|{response[:100]}\n")
    except Exception as e:
        logger.error("log_query failed: %s", e)


# ── Thread-safe response cache ─────────────────────────────────────────────────
_cache_lock = threading.Lock()
_response_cache: dict = {}
_CACHE_TTL = int(os.getenv("RESPONSE_CACHE_TTL", "300"))
_CACHE_MAX_SIZE = int(os.getenv("RESPONSE_CACHE_MAX_SIZE", "500"))


def _cache_key(query: str, jurisdiction: str, max_tokens: int) -> str:
    raw = f"{query.strip().lower()}|{jurisdiction}|{max_tokens}"
    return hashlib.md5(raw.encode()).hexdigest()


def _get_cached(key: str) -> Optional[str]:
    with _cache_lock:
        entry = _response_cache.get(key)
        if entry and (time.time() - entry["ts"]) < _CACHE_TTL:
            return entry["value"]
        if entry:
            del _response_cache[key]
    return None


def _set_cached(key: str, value: str):
    with _cache_lock:
        # Evict oldest entries if over size limit
        if len(_response_cache) >= _CACHE_MAX_SIZE:
            oldest = min(_response_cache.items(), key=lambda x: x[1]["ts"])
            del _response_cache[oldest[0]]
        _response_cache[key] = {"value": value, "ts": time.time()}


def clear_cache():
    with _cache_lock:
        _response_cache.clear()


# ── Jurisdiction info ──────────────────────────────────────────────────────────
JURISDICTION_INFO = {
    "US":        "United States federal and state law",
    "UK":        "United Kingdom law (England and Wales, Scotland, Northern Ireland)",
    "India":     "Indian law (common law system with constitutional framework)",
    "Canada":    "Canadian law (federal and provincial)",
    "Australia": "Australian law (federal and state/territory)",
    "Ethiopia":  "Ethiopian law (civil law system based on civil code and customary law)",
}

VALID_JURISDICTIONS = set(JURISDICTION_INFO.keys())


# ── LegalAssistant ─────────────────────────────────────────────────────────────
class LegalAssistant:
    """Groq-backed legal Q&A with retry, backoff, and thread-safe caching."""

    MAX_RETRIES = 3
    BACKOFF_BASE = 2

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY or GROQ_API_KEY in .env")

    def _make_api_request(self, messages: list, max_tokens: int = 800) -> Optional[str]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model, "messages": messages,
            "temperature": 0.7, "max_tokens": max_tokens,
            "top_p": 0.9, "frequency_penalty": 0.1, "presence_penalty": 0.1,
        }
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                resp = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                if resp.status_code == 429:
                    wait = self.BACKOFF_BASE ** attempt
                    logger.warning("Rate limited, retrying in %ss", wait)
                    time.sleep(wait)
                    continue
                logger.error("API error %s: %s", resp.status_code, resp.text[:200])
                return None
            except requests.exceptions.Timeout:
                logger.warning("Timeout attempt %d/%d", attempt, self.MAX_RETRIES)
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.BACKOFF_BASE ** attempt)
            except requests.exceptions.RequestException as e:
                logger.error("Request failed: %s", e)
                return None
        return None

    def ask_legal(self, query: str, jurisdiction: str = "US", max_tokens: int = 500) -> str:
        if not query or not query.strip():
            return "Please provide a valid legal question."
        if jurisdiction not in VALID_JURISDICTIONS:
            jurisdiction = "US"
        if is_inappropriate(query):
            return "I cannot answer that question. I am designed to provide legal information only."

        filtered_query = filter_pii(query)
        key = _cache_key(filtered_query, jurisdiction, max_tokens)
        cached = _get_cached(key)
        if cached:
            return cached

        messages = [
            {"role": "system", "content": (
                f"You are a professional AI legal assistant specialising in {JURISDICTION_INFO[jurisdiction]}. "
                "Provide accurate general legal information. Never give specific legal advice. "
                "Always recommend consulting a licensed attorney. Include a disclaimer in every response."
            )},
            {"role": "user", "content": filtered_query},
        ]
        response = self._make_api_request(messages, max_tokens)
        if response:
            if "disclaimer" not in response.lower():
                response += ("\n\n---\n**Disclaimer**: General information only — not legal advice. "
                             "Consult a qualified attorney for your specific situation.")
            _set_cached(key, response)
            log_query(query, response, jurisdiction)
            return response

        err = "Unable to process your request. Please try again or consult a qualified attorney."
        log_query(query, err, jurisdiction)
        return err

    def explain_term(self, term: str, jurisdiction: str = "US", max_tokens: int = 300) -> str:
        if not term or not term.strip():
            return "Please provide a valid legal term."
        return self.ask_legal(f"Explain the legal term '{term}' simply with a practical example.", jurisdiction, max_tokens)

    def legal_process(self, process_name: str, jurisdiction: str = "US", max_tokens: int = 500) -> str:
        if not process_name or not process_name.strip():
            return "Please provide a valid legal process name."
        return self.ask_legal(f"Explain step-by-step: {process_name} with key requirements and timelines.", jurisdiction, max_tokens)

    def get_service_status(self) -> dict:
        try:
            result = self._make_api_request([{"role": "user", "content": "ping"}], max_tokens=5)
            return {"status": "online" if result else "offline", "model": self.model}
        except Exception:
            return {"status": "error", "model": self.model}
