"""Matching entre une description de projet et les profils candidats."""
from litellm import completion


def match_candidates(project_description: str, profiles: list, passages: list | None = None) -> str:
    """Classe les candidats selon leur adéquation avec le projet.

    Sans `passages`, tous les profils sont envoyés au LLM (flux linéaire).
    Avec `passages`, le prompt ne contient que les extraits retrouvés par le RAG.
    """
    if passages:
        excerpts = "\n\n".join(
            f"[{p.get('candidate')} | {p.get('section')} | fichier {p.get('filename')} | similarité {p.get('score')}]\n{p.get('text')}"
            for p in passages
        )
        system_content = (
            "Tu classes des candidats à partir d'extraits de CV récupérés par recherche sémantique.\n"
            f"Extraits :\n{excerpts}\n\n"
            f"Profils structurés des candidats concernés : {profiles}\n\n"
            "Affiche les meilleurs candidats pour la description. "
            "Pour chaque candidat retenu, donne un score sur 100 et une justification qui cite les extraits."
        )
    else:
        system_content = f"""Voici les profiles des candidats {profiles}\n\n
                      Affiche moi les meilleurs candidats pour cette description"""

 
     reponse = completion(
                model="gemini/gemini-3.1-flash-lite",
                messages=[
                  {
                    "role":"system",
                    "content": system_content
                  },
                  {
                      "role":"user",
                      "content": project_description
                  }
                ]
            )
    return reponse.choices[0].message.content
