"""
Case Summarizer — legal case summarization, comparison, metadata extraction.
URL fetching now validates against domain whitelist (auth.validate_url).
"""

from chat import LegalAssistant
import requests
from bs4 import BeautifulSoup
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)


def summarize_case(case_text: str) -> str:
    if not case_text or not case_text.strip():
        return "Please provide valid case text to summarize."
    assistant = LegalAssistant()
    prompt = (
        "Summarize this legal case with the following structure:\n"
        "- **Facts**: What happened\n"
        "- **Issue**: The legal question\n"
        "- **Holding**: The court's decision\n"
        "- **Reasoning**: Why the court decided this way\n"
        "- **Precedent**: Important precedents set\n\n"
        f"Case: {case_text[:4000]}"
    )
    try:
        return assistant.ask_legal(prompt, "US", 800)
    except Exception as e:
        logger.error("summarize_case error: %s", e)
        return f"Error summarizing case: {e}"


def fetch_case_from_url(url: str) -> Optional[str]:
    """Fetch case text from a URL. Validates URL before fetching."""
    from auth import validate_url
    ok, err = validate_url(url)
    if not ok:
        raise ValueError(f"URL validation failed: {err}")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; LegalAI/1.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = " ".join(soup.get_text().split())
        return text[:5000]
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}")
    except Exception as e:
        raise ValueError(f"Error processing URL: {e}")


def compare_cases(case1: str, case2: str) -> str:
    if not case1 or not case2:
        return "Please provide valid text for both cases."
    assistant = LegalAssistant()
    prompt = (
        "Compare these two legal cases:\n\n"
        f"Case A:\n{case1[:2000]}\n\n"
        f"Case B:\n{case2[:2000]}\n\n"
        "Analyse: Similarities, Differences, Outcomes, Legal Principles, Precedential Value."
    )
    try:
        return assistant.ask_legal(prompt, "US", 800)
    except Exception as e:
        return f"Error comparing cases: {e}"


def extract_case_metadata(text: str) -> dict:
    metadata: dict = {"court": None, "date": None, "parties": [], "citation": None, "judge": None}
    patterns = {
        "court":    [r"(?:Supreme Court|Court of Appeals|District Court|Circuit Court|\w+ Court)"],
        "date":     [r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
                     r"\b\d{1,2}/\d{1,2}/\d{4}\b"],
        "citation": [r"\b\d+\s+[A-Z]\.\w*\s+\d+\b", r"\b\d+\s+F\.\d+\b"],
        "judge":    [r"(?:Judge|Justice)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"],
    }
    for field, pats in patterns.items():
        for pat in pats:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                metadata[field] = m.group(0)
                break

    party_pat = r"([A-Z][a-zA-Z\s,\.]+?)\s+v\.\s+([A-Z][a-zA-Z\s,\.]+?)(?=\s*[,\.\(]|\Z)"
    metadata["parties"] = [f"{a.strip()} v. {b.strip()}"
                           for a, b in re.findall(party_pat, text)][:3]
    return metadata


def validate_case_text(text: str) -> dict:
    if not text or not text.strip():
        return {"valid": False, "error": "No text provided", "word_count": 0,
                "char_count": 0, "likely_case": False}
    indicators = ["v.", "versus", "plaintiff", "defendant", "court", "judge",
                  "appeal", "holding", "opinion", "majority", "dissent",
                  "precedent", "ruling", "judgment", "verdict"]
    count = sum(1 for i in indicators if i.lower() in text.lower())
    return {
        "valid": True, "error": None,
        "word_count": len(text.split()), "char_count": len(text),
        "likely_case": count >= 3, "indicator_count": count,
    }


def format_case_summary(summary: str) -> str:
    if not summary:
        return "No summary available."
    lines = []
    for line in summary.split("\n"):
        line = line.strip()
        if not line:
            continue
        if any(kw in line.lower() for kw in ["facts:", "issue:", "holding:", "reasoning:", "precedent:"]):
            if not line.startswith("**"):
                line = f"**{line}**"
        lines.append(line)
    return "\n\n".join(lines)
