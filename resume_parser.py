"""PDF parsing helpers for uploaded resumes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO

import pdfplumber


@dataclass
class ParsedResume:
    """Stores the original filename and extracted resume text."""

    filename: str
    text: str


def extract_text_from_pdf(file: BinaryIO) -> str:
    """Extract text from an uploaded PDF file.

    Streamlit uploads are file-like objects, so pdfplumber can read them
    directly without saving the resume to disk.
    """
    text_parts: list[str] = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def parse_uploaded_resume(uploaded_file: BinaryIO) -> ParsedResume:
    """Parse one uploaded PDF resume."""
    filename = getattr(uploaded_file, "name", "uploaded_resume.pdf")
    text = extract_text_from_pdf(uploaded_file)
    return ParsedResume(filename=filename, text=text)
