"""Extraction du texte brut d'un CV PDF."""
import pymupdf
import pymupdf4llm

def extract_text(pdf_bytes: bytes) -> str:
    """Retourne le texte brut contenu dans un PDF.
    TODO (étudiant) :
    - ouvrir le PDF à partir des octets avec PyMuPDF (module `fitz`) ;
    - parcourir chaque page et concaténer son texte ;
    - gérer les cas limites : PDF vide, PDF scanné sans texte, fichier corrompu.
    """
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    md = pymupdf4llm.to_markdown(doc)
    return md
