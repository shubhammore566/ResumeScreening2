"""Resume parsing utilities — extract raw text from uploaded PDF resumes."""

from __future__ import annotations

from dataclasses import dataclass

import fitz  # PyMuPDF


@dataclass
class ParsedResume:
    """Holds the parsed output for a single uploaded resume."""
    filename: str
    text: str


def parse_uploaded_resume(uploaded_file) -> ParsedResume:
    """
    Streamlit ke `st.file_uploader` se aaye uploaded_file object se
    pura PDF text nikaalo (PyMuPDF/fitz ke through, page by page).
    """
    file_bytes = uploaded_file.read()
    text_parts: list[str] = []

    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())

    full_text = "\n".join(text_parts)
    return ParsedResume(filename=uploaded_file.name, text=full_text)
