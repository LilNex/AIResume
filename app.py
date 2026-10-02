"""Interface Streamlit d'AI_TalentMatcher (interface uniquement, sans logique métier)."""

import streamlit as st
import core.extraction as ex
import core.profile as profiler
import core.matching as matcher
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="AI TalentMatcher", page_icon="📄", layout="wide")
if "uploaded_cvs" not in st.session_state:
    st.session_state.uploaded_cvs = {}  # nom de fichier -> octets du PDF
if "profiles" not in st.session_state:
    st.session_state.profiles = []  # profils validés (dicts)
if "matches" not in st.session_state:
    st.session_state.matches = []

st.title("AI TalentMatcher")

# --- 1. Upload des CV -------------------------------------------------------
st.header(f"1. CV des candidats")
files = st.file_uploader(
    "Déposer un ou plusieurs CV (PDF)",
    type=["pdf"],
    accept_multiple_files=True,
)
for f in files or []:
    st.session_state.uploaded_cvs[f.name] = f.getvalue()

if st.session_state.uploaded_cvs:
    st.write(f"{len(st.session_state.uploaded_cvs)} fichier(s) reçu(s) :")
    for name, data in st.session_state.uploaded_cvs.items():
        st.write(f"- {name} ({len(data) / 1024:.1f} Ko)")
    col1, col2 = st.columns(2)
    if col1.button("Analyser les CV", type="primary"):
        for cv in st.session_state.uploaded_cvs:
            # TODO (étudiant) : brancher ici extraction PDF -> LLM -> validation.
            md = ex.extract_text(st.session_state.uploaded_cvs[cv])
            profile = profiler.build_profile(md)
            st.session_state.profiles.append(profile)
            st.info(profile.skills)

    if col2.button("Vider la liste"):
        st.session_state.uploaded_cvs = {}
        st.session_state.profiles = []
        st.rerun()
else:
    st.caption("Aucun fichier reçu pour l'instant.")

# --- 2. Profils extraits ----------------------------------------------------
st.header("2. Profils extraits")

# Les profils peuvent être des dicts ou des modèles Pydantic : on affiche des dicts.
profiles = [
    p.model_dump() if hasattr(p, "model_dump") else p
    for p in st.session_state.profiles
]
if not profiles:
    st.caption("Aucun profil pour l'instant.")
else:
    view = st.radio("Affichage", ["Cartes", "Tableau"], horizontal=True)
    if view == "Tableau":
        st.dataframe(profiles, use_container_width=True)
    else:
        cols = st.columns(3)
        for i, p in enumerate(profiles):
            with cols[i % 3].container(border=True):
                st.subheader(f"{p.get('first_name', '')} {p.get('last_name', '')}")
                st.write(f"📧 {p.get('email', '-')}")
                st.write(f"📞 {p.get('phone', '-')}")
                st.write(f"📍 {p.get('location', '-')}")
                st.write("**Compétences :** " + ", ".join(p.get("skills", [])))

# --- 3. Matching ------------------------------------------------------------
st.header("3. Matching projet")

description = st.text_area(
    "Description du projet",
    placeholder="Ex. : application mobile React Native avec backend Node.js...",
    height=150,
)
if st.button("Trouver les meilleurs candidats"):
    # TODO (étudiant) : brancher ici le matching LLM.
    
    st.info(matcher.match_candidates(description, profiles))
if st.session_state.matches:
    st.dataframe(st.session_state.matches, use_container_width=True)
