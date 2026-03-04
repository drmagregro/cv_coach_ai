import json
import subprocess
import re
import os
from groq import Groq


# ─── Chemin vers le script JS (copié à côté de cv_builder.py au premier appel) ─

_DIR = os.path.dirname(os.path.abspath(__file__))
_JS_TEMPLATE = os.path.join(_DIR, "cv_builder_node.js")


# ─── Prompt ATS ───────────────────────────────────────────────────────────────

def build_ats_prompt(cv_text, target_job, analysis_result):
    job_context = f"Le poste visé est : {target_job}." if target_job else ""
    return f"""Tu es un expert ATS (Applicant Tracking System) et en rédaction de CV professionnels.

À partir du CV ci-dessous et de l'analyse fournie, génère un CV entièrement revu et optimisé pour les systèmes ATS.

{job_context}

CV original :
---
{cv_text}
---

Analyse et suggestions :
---
{analysis_result}
---

Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ou après, sans balises markdown.
Structure exacte :

{{
  "nom": "Prénom Nom",
  "titre": "Titre professionnel",
  "contact": {{
    "email": "email@exemple.com",
    "telephone": "+33 6 00 00 00 00",
    "localisation": "Ville, Pays",
    "linkedin": "linkedin.com/in/profil"
  }},
  "profil": "Résumé professionnel percutant de 3-4 lignes, orienté résultats.",
  "experience": [
    {{
      "poste": "Titre du poste",
      "entreprise": "Nom de l'entreprise",
      "periode": "Jan 2022 – Présent",
      "missions": [
        "Mission ou réalisation concrète avec chiffre si possible",
        "Deuxième mission clé"
      ]
    }}
  ],
  "formation": [
    {{
      "diplome": "Nom du diplôme",
      "etablissement": "Nom de l'établissement",
      "annee": "2020"
    }}
  ],
  "competences": {{
    "techniques": ["Compétence 1", "Compétence 2"],
    "soft_skills": ["Qualité 1", "Qualité 2"],
    "langues": ["Français (natif)", "Anglais (courant)"]
  }},
  "certifications": ["Certification 1 (année)"],
  "projets": [
    {{
      "nom": "Nom du projet",
      "description": "Description courte orientée impact"
    }}
  ]
}}

Règles importantes :
- Intègre toutes les suggestions de l'analyse dans la version améliorée
- Utilise des verbes d'action forts (développé, optimisé, géré, créé...)
- Quantifie les résultats quand possible
- Si une section est vide dans le CV original, mets un tableau vide []
- Corrige l'orthographe et améliore le style
- Ne garde que les informations pertinentes et véridiques
"""


def call_groq_ats(api_key, cv_text, target_job, analysis_result):
    """Appelle Groq pour obtenir le CV restructuré en JSON."""
    client = Groq(api_key=api_key)
    prompt = build_ats_prompt(cv_text, target_job, analysis_result)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4096,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# ─── Génération DOCX ──────────────────────────────────────────────────────────

def generate_cv_docx(cv_data: dict) -> bytes:
    """Génère un fichier DOCX ATS à partir des données structurées."""
    with open("/tmp/cv_data.json", "w", encoding="utf-8") as f:
        json.dump(cv_data, f, ensure_ascii=False)

    result = subprocess.run(
        ["node", _JS_TEMPLATE],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Erreur génération DOCX : {result.stderr}")

    with open("/tmp/cv_ats.docx", "rb") as f:
        return f.read()


# ─── Génération PDF ATS ───────────────────────────────────────────────────────

def generate_cv_pdf(cv_data: dict) -> bytes:
    """Génère un PDF ATS sobre avec reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors
    import io

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    def s(text):
        if not text:
            return ""
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    noir = colors.HexColor("#1a1a1a")
    gris  = colors.HexColor("#555555")
    gris2 = colors.HexColor("#888888")

    style_nom = ParagraphStyle("nom", fontName="Helvetica-Bold", fontSize=22, textColor=noir, spaceAfter=4)
    style_titre = ParagraphStyle("titre", fontName="Helvetica-Oblique", fontSize=12, textColor=gris, spaceAfter=4)
    style_contact = ParagraphStyle("contact", fontName="Helvetica", fontSize=9, textColor=gris, spaceAfter=10)
    style_section = ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=10, textColor=noir, spaceBefore=12, spaceAfter=4)
    style_poste = ParagraphStyle("poste", fontName="Helvetica-Bold", fontSize=10, textColor=noir, spaceBefore=8, spaceAfter=2)
    style_periode = ParagraphStyle("periode", fontName="Helvetica-Oblique", fontSize=9, textColor=gris2, spaceAfter=2)
    style_body = ParagraphStyle("body", fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#404040"), spaceAfter=3, leading=14)
    style_bullet = ParagraphStyle("bullet", fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#404040"), spaceAfter=2, leftIndent=12, firstLineIndent=0, leading=13)

    def hr():
        return HRFlowable(width="100%", thickness=0.8, color=noir, spaceAfter=6)

    story = []

    # NOM
    story.append(Paragraph(s(cv_data.get("nom", "")), style_nom))

    # TITRE
    if cv_data.get("titre"):
        story.append(Paragraph(s(cv_data["titre"]), style_titre))

    # CONTACT
    c = cv_data.get("contact", {})
    parts = [c.get("email"), c.get("telephone"), c.get("localisation"), c.get("linkedin")]
    contact_str = "  |  ".join([p for p in parts if p])
    if contact_str:
        story.append(Paragraph(s(contact_str), style_contact))

    # PROFIL
    if cv_data.get("profil"):
        story.append(Paragraph("PROFIL", style_section))
        story.append(hr())
        story.append(Paragraph(s(cv_data["profil"]), style_body))

    # EXPERIENCE
    if cv_data.get("experience"):
        story.append(Paragraph("EXPÉRIENCE PROFESSIONNELLE", style_section))
        story.append(hr())
        for exp in cv_data["experience"]:
            label = s(exp.get("poste", "")) + "  —  " + s(exp.get("entreprise", ""))
            story.append(Paragraph(label, style_poste))
            if exp.get("periode"):
                story.append(Paragraph(s(exp["periode"]), style_periode))
            for m in exp.get("missions", []):
                story.append(Paragraph("– " + s(m), style_bullet))
            story.append(Spacer(1, 4))

    # FORMATION
    if cv_data.get("formation"):
        story.append(Paragraph("FORMATION", style_section))
        story.append(hr())
        for f in cv_data["formation"]:
            annee = f" ({f['annee']})" if f.get("annee") else ""
            label = s(f.get("diplome", "")) + "  —  " + s(f.get("etablissement", "")) + annee
            story.append(Paragraph(label, style_poste))
        story.append(Spacer(1, 4))

    # COMPETENCES
    comp = cv_data.get("competences", {})
    if any([comp.get("techniques"), comp.get("soft_skills"), comp.get("langues")]):
        story.append(Paragraph("COMPÉTENCES", style_section))
        story.append(hr())
        if comp.get("techniques"):
            story.append(Paragraph("<b>Techniques :</b> " + s(", ".join(comp["techniques"])), style_body))
        if comp.get("soft_skills"):
            story.append(Paragraph("<b>Qualités :</b> " + s(", ".join(comp["soft_skills"])), style_body))
        if comp.get("langues"):
            story.append(Paragraph("<b>Langues :</b> " + s(", ".join(comp["langues"])), style_body))
        story.append(Spacer(1, 4))

    # CERTIFICATIONS
    if cv_data.get("certifications"):
        story.append(Paragraph("CERTIFICATIONS", style_section))
        story.append(hr())
        for cert in cv_data["certifications"]:
            story.append(Paragraph("– " + s(cert), style_bullet))
        story.append(Spacer(1, 4))

    # PROJETS
    if cv_data.get("projets"):
        story.append(Paragraph("PROJETS", style_section))
        story.append(hr())
        for p in cv_data["projets"]:
            story.append(Paragraph(s(p.get("nom", "")), style_poste))
            if p.get("description"):
                story.append(Paragraph(s(p["description"]), style_body))
        story.append(Spacer(1, 4))

    doc.build(story)
    return buf.getvalue()