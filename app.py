import os
import re
import streamlit as st
from dotenv import load_dotenv

from extractor import extract_text
from llm import build_prompt, call_groq
from pdf_report import generate_pdf_report
from cv_builder import call_groq_ats, generate_cv_docx, generate_cv_pdf
from ui_components import inject_css, render_header, render_empty_state, render_score, render_footer

# ─── Chargement de la clé API ─────────────────────────────────────────────────

load_dotenv()
cle_env = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

# ─── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CoachIA",
    page_icon=None,
    layout="wide",
)

inject_css()
render_header()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:

    if cle_env:
        api_key = cle_env
    else:
        st.warning("Aucun fichier .env détecté")
        api_key = st.text_input(
            "Clé API Groq",
            type="password",
            help="Obtenez votre clé sur console.groq.com ou créez un fichier .env"
        )

    st.divider()
    doc_type = st.selectbox("Type de document", ["CV", "Lettre de motivation"])
    target_job = st.text_input(
        "Poste visé (optionnel)",
        placeholder="Ex : Développeur Python, Marketing Manager..."
    )
    analysis_depth = st.select_slider(
        "Niveau d'analyse",
        options=["Rapide", "Standard", "Approfondi"],
        value="Standard"
    )

    st.divider()
    st.markdown("**Formats acceptés**")
    st.markdown("PDF, Word (.docx), Texte (.txt)")

    st.divider()
    st.markdown("**A propos**")
    st.markdown("Powered by Groq — LLaMA 3.3 70B")

# ─── Interface principale ─────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Importer votre document")

    input_method = st.radio("Méthode d'import", ["Fichier", "Texte direct"], horizontal=True)
    text_content = ""

    if input_method == "Fichier":
        uploaded = st.file_uploader(
            "Déposez votre fichier ici",
            type=["pdf", "docx", "txt"],
            help="Formats acceptés : PDF, DOCX, TXT"
        )
        if uploaded:
            with st.spinner("Extraction du texte..."):
                text_content = extract_text(uploaded)
            if text_content:
                st.success(f"Document chargé — {len(text_content)} caractères")
                with st.expander("Aperçu du texte extrait"):
                    st.text_area("", text_content[:1500] + ("..." if len(text_content) > 1500 else ""),
                                 height=200, disabled=True)
            else:
                st.error("Impossible d'extraire le texte. Vérifiez le fichier.")
    else:
        text_content = st.text_area(
            "Collez votre texte ici",
            placeholder="Copiez-collez votre CV ou lettre de motivation...",
            height=300
        )

    analyze_btn = st.button("Analyser et améliorer", type="primary", use_container_width=True)

with col2:
    st.subheader("Résultats de l'analyse")

    if analyze_btn:
        if not api_key:
            st.error("Aucune clé API trouvée. Créez un fichier .env ou saisissez-la dans la sidebar.")
        elif not text_content.strip():
            st.warning("Veuillez importer un document ou saisir du texte.")
        else:
            with st.spinner("Analyse en cours..."):
                try:
                    prompt = build_prompt(doc_type, text_content, target_job, analysis_depth)
                    result = call_groq(api_key, prompt)

                    st.session_state["analysis_result"] = result
                    st.session_state["original_text"] = text_content
                    st.session_state["doc_type"] = doc_type
                    st.session_state["target_job"] = target_job
                    # Réinitialiser le CV ATS si nouvelle analyse
                    st.session_state.pop("cv_ats_data", None)
                    st.session_state.pop("cv_ats_docx", None)
                    st.session_state.pop("cv_ats_pdf", None)

                except Exception as e:
                    st.error(f"Erreur API : {str(e)}")

    if "analysis_result" in st.session_state:
        result = st.session_state["analysis_result"]

        # 3 onglets si CV, 2 si lettre de motivation
        if st.session_state.get("doc_type") == "CV":
            tab1, tab2, tab3 = st.tabs(["Analyse complète", "Version améliorée", "CV ATS"])
        else:
            tab1, tab2 = st.tabs(["Analyse complète", "Version améliorée"])
            tab3 = None

        with tab1:
            score_match = re.search(r'Score global\s*:\s*(\d+)/10', result)
            if score_match:
                render_score(int(score_match.group(1)))
            st.markdown(result)

        with tab2:
            reformulated = re.search(
                r'Version reformulée.*?\n(.*?)(?=###|\Z)', result, re.DOTALL | re.IGNORECASE
            )
            if reformulated:
                st.markdown(reformulated.group(1).strip())
            else:
                st.markdown(result)

        if tab3 is not None:
            with tab3:
                st.markdown("#### CV optimisé pour les systèmes ATS")
                st.markdown(
                    "Les suggestions de l'analyse ont été intégrées directement dans ce CV restructuré.",
                    help="Structure sobre, mots-clés optimisés, format lisible par les logiciels de recrutement."
                )

                generate_ats_btn = st.button(
                    "Générer le CV ATS",
                    type="primary",
                    use_container_width=True,
                    disabled="cv_ats_data" in st.session_state
                )

                if generate_ats_btn:
                    with st.spinner("Restructuration du CV en cours..."):
                        try:
                            cv_data = call_groq_ats(
                                api_key,
                                st.session_state["original_text"],
                                st.session_state.get("target_job", ""),
                                result
                            )
                            st.session_state["cv_ats_data"] = cv_data
                            st.session_state["cv_ats_docx"] = generate_cv_docx(cv_data)
                            st.session_state["cv_ats_pdf"] = generate_cv_pdf(cv_data)
                        except Exception as e:
                            st.error(f"Erreur lors de la génération : {str(e)}")

                if "cv_ats_data" in st.session_state:
                    cv = st.session_state["cv_ats_data"]

                    # ─── Aperçu du CV ─────────────────────────────────────
                    with st.container():
                        st.markdown(f"## {cv.get('nom', '')}")
                        if cv.get("titre"):
                            st.markdown(f"*{cv['titre']}*")

                        c = cv.get("contact", {})
                        contact_parts = [c.get("email"), c.get("telephone"), c.get("localisation"), c.get("linkedin")]
                        contact_str = "  |  ".join([p for p in contact_parts if p])
                        if contact_str:
                            st.caption(contact_str)

                        st.divider()

                        if cv.get("profil"):
                            st.markdown("**Profil**")
                            st.markdown(cv["profil"])
                            st.divider()

                        if cv.get("experience"):
                            st.markdown("**Expérience professionnelle**")
                            for exp in cv["experience"]:
                                st.markdown(f"**{exp.get('poste', '')}** — {exp.get('entreprise', '')}")
                                if exp.get("periode"):
                                    st.caption(exp["periode"])
                                for m in exp.get("missions", []):
                                    st.markdown(f"– {m}")
                            st.divider()

                        if cv.get("formation"):
                            st.markdown("**Formation**")
                            for f in cv["formation"]:
                                annee = f" ({f['annee']})" if f.get("annee") else ""
                                st.markdown(f"**{f.get('diplome', '')}** — {f.get('etablissement', '')}{annee}")
                            st.divider()

                        comp = cv.get("competences", {})
                        if any([comp.get("techniques"), comp.get("soft_skills"), comp.get("langues")]):
                            st.markdown("**Compétences**")
                            if comp.get("techniques"):
                                st.markdown(f"Techniques : {', '.join(comp['techniques'])}")
                            if comp.get("soft_skills"):
                                st.markdown(f"Qualités : {', '.join(comp['soft_skills'])}")
                            if comp.get("langues"):
                                st.markdown(f"Langues : {', '.join(comp['langues'])}")
                            st.divider()

                        if cv.get("certifications"):
                            st.markdown("**Certifications**")
                            for cert in cv["certifications"]:
                                st.markdown(f"– {cert}")
                            st.divider()

                        if cv.get("projets"):
                            st.markdown("**Projets**")
                            for p in cv["projets"]:
                                st.markdown(f"**{p.get('nom', '')}** — {p.get('description', '')}")

                    # ─── Téléchargements ──────────────────────────────────
                    st.divider()
                    st.markdown("**Télécharger le CV ATS**")
                    dcol1, dcol2 = st.columns(2)
                    with dcol1:
                        st.download_button(
                            "Télécharger (.docx)",
                            data=st.session_state["cv_ats_docx"],
                            file_name="cv_ats.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    with dcol2:
                        st.download_button(
                            "Télécharger (.pdf)",
                            data=st.session_state["cv_ats_pdf"],
                            file_name="cv_ats.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

        st.divider()
        st.subheader("Télécharger le rapport d'analyse")

        dcol1, dcol2 = st.columns(2)

        with dcol1:
            st.download_button(
                "Télécharger (.txt)",
                data=(f"RAPPORT COACH IA - {st.session_state['doc_type']}\n" +
                      "=" * 50 + "\n\n" +
                      "DOCUMENT ORIGINAL:\n" + st.session_state['original_text'] +
                      "\n\n" + "=" * 50 + "\n\nANALYSE:\n" + result).encode("utf-8"),
                file_name=f"rapport_coach_ia_{doc_type.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with dcol2:
            try:
                pdf_bytes = generate_pdf_report(
                    st.session_state["original_text"],
                    result,
                    st.session_state["doc_type"],
                    st.session_state.get("target_job", "")
                )
                st.download_button(
                    "Télécharger (.pdf)",
                    data=pdf_bytes,
                    file_name=f"rapport_coach_ia_{doc_type.lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"PDF non disponible : {e}")
    else:
        render_empty_state()

render_footer()