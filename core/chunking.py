"""Découpage du markdown d'un CV en passages indexables."""
import re

_HEADING = re.compile(r"^#{1,3} ", re.MULTILINE)


def chunk_markdown(markdown: str, size: int = 800, overlap: int = 100) -> list[dict]:
    """Découpe un CV en sections, puis en fenêtres si une section est trop longue.

    Chaque passage contient `section` (titre) et `text`.
    """
    text = (markdown or "").strip()
    if not text:
        return []

    matches = list(_HEADING.finditer(text))
    if not matches:
        return [{"section": "CV", "text": window} for window in _windows(text, size, overlap)]

    sections: list[tuple[str, str]] = []
    if matches[0].start() > 0:
        intro = text[: matches[0].start()].strip()
        if intro:
            sections.append(("CV", intro))

    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start() : end].strip()
        if not block:
            continue
        first_line = block.splitlines()[0]
        section = first_line.lstrip("#").strip() or "CV"
        sections.append((section, block))

    chunks = []
    for section, block in sections:
        for window in _windows(block, size, overlap):
            chunks.append({"section": section, "text": window})
    return chunks


def _windows(text: str, size: int, overlap: int) -> list[str]:
    if len(text) <= size:
        return [text]
    step = max(1, size - overlap)
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        if start + size >= len(text):
            break
        start += step
    return chunks
