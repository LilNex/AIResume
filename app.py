"""Interface Streamlit d'AI_TalentMatcher."""

import streamlit as st
import core.extraction as ex
import core.profile as profiler
import core.matching as matcher
import core.rag as rag
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="AI TalentMatcher", page_icon="📄", layout="wide")
if "uploaded_cvs" not in st.session_state:
    st.session_state.uploaded_cvs = {}  # nom de fichier -> octets du PDF
if "profiles" not in st.session_state:
    st.session_state.profiles = []  # profils validés (dicts)
if "matches" not in st.session_state:
    st.session_state.matches = []
if "cv_texts" not in st.session_state:
    st.session_state.cv_texts = {}  # fichier -> {markdown, profile}
if "cv_chunks" not in st.session_state:
    st.session_state.cv_chunks = []  # passages indexés pour le RAG
if "last_result" not in st.session_state:
    st.session_state.last_result = ""
if "last_mode" not in st.session_state:
    st.session_state.last_mode = ""
if "last_passages" not in st.session_state:
    st.session_state.last_passages = []

st.title("AI TalentMatcher")

# --- Mode -------------------------------------------------------------------
st.header("Mode de traitement")
with st.container(border=True):
    mode = st.radio(
        "Choisir comment les CV sont utilisés",
        ["Linéaire", "RAG"],
        horizontal=True,
        key="processing_mode",
    )
    if mode == "Linéaire":
        st.caption(
            "Flux actuel : chaque CV est envoyé en entier pour l'extraction, "
            "et tous les profils sont envoyés au matching."
        )
    else:
        st.caption(
            "Les CV sont découpés en passages et indexés. "
            "Au matching, seuls les passages proches de la description du projet sont envoyés au LLM. "
            f"Index actuel : {len(st.session_state.cv_chunks)} passage(s)."
        )

# --- 1. Upload des CV -------------------------------------------------------
st.header("1. CV des candidats")
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
        use_rag = st.session_state.processing_mode == "RAG"
        with st.spinner("Indexation RAG des CV..." if use_rag else "Analyse des CV..."):
            for cv in list(st.session_state.uploaded_cvs):
                try:
                    md = ex.extract_text(st.session_state.uploaded_cvs[cv])
                    profile = profiler.build_profile(md)
                    st.session_state.profiles.append(profile)
                    dumped = profile.model_dump() if hasattr(profile, "model_dump") else profile
                    st.session_state.cv_texts[cv] = {"markdown": md, "profile": dumped}
                    if use_rag:
                        st.session_state.cv_chunks = rag.upsert_document(
                            st.session_state.cv_chunks, cv, md, dumped
                        )
                except Exception as exc:
                    st.error(f"{cv} : {exc}")

    if col2.button("Vider la liste"):
        st.session_state.uploaded_cvs = {}
        st.session_state.profiles = []
        st.session_state.cv_texts = {}
        st.session_state.cv_chunks = []
        st.session_state.matches = []
        st.session_state.last_result = ""
        st.session_state.last_mode = ""
        st.session_state.last_passages = []
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
                st.subheader(f"{p.get('firstName', '')} {p.get('lastName', '')}")
                st.write(f"📧 {p.get('email', '-')}")
                st.write(f"📞 {p.get('phone', '-')}")
                st.write(f"📍 {p.get('location', '-')}")
                st.write("**Compétences :** " + ", ".join(p.get("skills", [])))

# --- 3. Matching ------------------------------------------------------------
st.header("3. Matching projet")
st.caption(f"Mode actif : {st.session_state.processing_mode}.")

description = st.text_area(
    "Description du projet",
    placeholder="Ex. : application mobile React Native avec backend Node.js...",
    height=150,
)
if st.button("Trouver les meilleurs candidats"):
    active_mode = st.session_state.processing_mode
    if not description.strip():
        st.warning("Renseigne la description du projet.")
    elif not profiles:
        st.warning("Analyse d'abord au moins un CV.")
    elif active_mode == "RAG":
        try:
            with st.spinner("Recherche des passages pertinents..."):
                chunks = list(st.session_state.cv_chunks)
                for name, doc in st.session_state.cv_texts.items():
                    if not any(chunk["filename"] == name for chunk in chunks):
                        chunks = rag.upsert_document(chunks, name, doc["markdown"], doc["profile"])
                st.session_state.cv_chunks = chunks
                passages = rag.search_chunks(description, chunks)
            st.session_state.last_passages = passages
            if not passages:
                st.session_state.last_result = ""
                st.warning("Aucun passage indexé pour cette recherche.")
            else:
                relevant = []
                seen = set()
                for passage in passages:
                    filename = passage["filename"]
                    if filename in seen:
                        continue
                    seen.add(filename)
                    doc = st.session_state.cv_texts.get(filename)
                    if doc:
                        relevant.append(doc["profile"])
                st.session_state.last_result = matcher.match_candidates(
                    description, relevant or profiles, passages
                )
                st.session_state.last_mode = "RAG"
        except Exception as exc:
            st.error(f"RAG : {exc}")
    else:
        try:
            st.session_state.last_passages = []
            st.session_state.last_result = matcher.match_candidates(description, profiles)
            st.session_state.last_mode = "Linéaire"
        except Exception as exc:
            st.error(f"Matching : {exc}")

if st.session_state.last_result:
    st.caption(f"Dernier résultat ({st.session_state.last_mode})")
    st.info(st.session_state.last_result)

if st.session_state.processing_mode == "RAG" and st.session_state.last_passages:
    st.subheader("Passages retenus")
    for passage in st.session_state.last_passages:
        label = f"{passage['candidate']} — {passage['section']} ({passage['score']})"
        with st.expander(label):
            st.write(passage["text"])

if st.session_state.matches:
    st.dataframe(st.session_state.matches, use_container_width=True)
