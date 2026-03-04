from groq import Groq


def build_prompt(doc_type, text, target_job, depth):
    job_context = f"Le poste visé est : **{target_job}**." if target_job else "Aucun poste spécifique précisé."
    depth_instructions = {
        "Rapide": "Fais une analyse concise avec les points essentiels.",
        "Standard": "Fais une analyse équilibrée et détaillée.",
        "Approfondi": "Fais une analyse très complète, phrase par phrase si nécessaire.",
    }

    return f"""Tu es un expert en recrutement et en coaching professionnel francophone.
Analyse le {doc_type} suivant et fournis une réponse structurée en français.
{job_context}
{depth_instructions[depth]}

## Document à analyser :
---
{text}
---

## Format de ta réponse (respecte exactement cette structure) :

### Score global : X/10
Justification du score en 2-3 phrases.

###  Points forts
- (liste des points positifs)

###  Points à améliorer
- (liste des axes d'amélioration)

###  Suggestions concrètes
Pour chaque point faible, donne une suggestion précise et actionnable.

### Version reformulée et améliorée
Réécris intégralement le document de façon professionnelle, impactante et adaptée au poste visé.
Conserve les informations clés mais améliore le style, la structure et le vocabulaire.

### Conseils supplémentaires
3 à 5 conseils spécifiques pour maximiser les chances de succès.
"""


def call_groq(api_key, prompt):
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4096,
    )
    return response.choices[0].message.content