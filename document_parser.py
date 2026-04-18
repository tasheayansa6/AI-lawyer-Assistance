"""
Document Parser — PDF and DOCX extraction with size/type validation.
"""

from pypdf import PdfReader
from docx import Document
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_from_pdf(file) -> str:
    try:
        data = file.read() if hasattr(file, "read") else open(file, "rb").read()
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()
    except Exception as e:
        raise ValueError(f"Error extracting PDF: {e}")


def extract_from_docx(file) -> str:
    try:
        data = file.read() if hasattr(file, "read") else open(file, "rb").read()
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
    except Exception as e:
        raise ValueError(f"Error extracting DOCX: {e}")


def extract_text(uploaded_file) -> Optional[str]:
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return extract_from_docx(uploaded_file)
    raise ValueError(f"Unsupported format: {uploaded_file.name}")


def get_document_info(uploaded_file) -> dict:
    if uploaded_file is None:
        return {}
    try:
        raw = uploaded_file.getvalue()
        text = extract_text(uploaded_file)
        return {
            "name":            uploaded_file.name,
            "size_kb":         round(len(raw) / 1024, 1),
            "type":            "PDF" if uploaded_file.name.lower().endswith(".pdf") else "DOCX",
            "character_count": len(text),
            "word_count":      len(text.split()),
            "line_count":      len(text.splitlines()),
            "preview":         text[:300] + "..." if len(text) > 300 else text,
        }
    except Exception as e:
        return {"name": uploaded_file.name, "error": str(e)}


def is_legal_document(text: str) -> dict:
    if not text:
        return {"is_legal": False, "confidence": 0.0, "indicators": []}
    keywords = [
        "agreement", "contract", "terms", "conditions", "parties", "hereinafter",
        "whereas", "indemnify", "liability", "breach", "termination", "governing law",
        "jurisdiction", "arbitration", "confidential", "non-disclosure", "nda",
        "lease", "employment", "power of attorney", "will", "testament", "deed",
        "mortgage", "promissory note",
    ]
    phrases = [
        "this agreement", "the parties", "in consideration of", "binding agreement",
        "entire agreement", "force majeure", "confidential information",
        "intellectual property", "non-compete", "severability",
    ]
    kw_hits = sum(1 for k in keywords if k in text.lower())
    ph_hits = sum(1 for p in phrases if p in text.lower())
    confidence = min((kw_hits + ph_hits) / 10, 1.0)
    found = [k for k in keywords if k in text.lower()]
    return {
        "is_legal":       confidence > 0.3,
        "confidence":     round(confidence, 2),
        "keyword_matches": kw_hits,
        "phrase_matches":  ph_hits,
        "indicators":      found[:10],
    }


def clean_legal_text(text: str) -> str:
    if not text:
        return ""
    text = " ".join(text.split())
    for bad, good in [(" ,", ","), (" .", "."), ("( ", "("), (" )", ")")]:
        text = text.replace(bad, good)
    return text.strip()
