"""Extraction du texte brut d'un CV PDF."""


def extract_text(pdf_bytes: bytes) -> str:
    """Retourne le texte brut contenu dans un PDF.

    TODO (étudiant) :
    - ouvrir le PDF à partir des octets avec PyMuPDF (module `fitz`) ;
    - parcourir chaque page et concaténer son texte ;
    - gérer les cas limites : PDF vide, PDF scanné sans texte, fichier corrompu.
    """
    raise NotImplementedError("extract_text : à implémenter")
