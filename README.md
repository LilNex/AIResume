# AI TalentMatcher

CV PDF → LLM → profil JSON validé (firstName, lastName, phone, email, location, skills) → matching de candidats par LLM.

## Lancement

1. Copier `.env.example` en `.env` et renseigner `LLM_MODEL` et la clé API (Groq ou Gemini).
2. Lancer :

   ```bash
   docker compose up --build
   ```

3. Ouvrir http://localhost:8501

Le dossier est monté dans le conteneur : les modifications de code sont prises en compte en rechargeant la page.

## Structure

- `app.py` : interface Streamlit (upload, affichage des profils, matching).
- `core/extraction.py` : `extract_text` — texte brut d'un PDF (PyMuPDF).
- `core/profile.py` : `build_profile`, `validate_profile` — appel LLM et validation Pydantic.
- `core/matching.py` : `match_candidates` — classement des candidats par LLM.

Les fonctions de `core/` sont à implémenter (voir les TODO).
