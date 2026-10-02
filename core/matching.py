"""Matching entre une description de projet et les profils candidats."""
from litellm import completion


def match_candidates(project_description: str, profiles: list) -> list:
    """Classe les candidats selon leur adéquation avec le projet.

    TODO (étudiant) :
    - écrire le prompt qui fournit au LLM la description du projet
      et les profils validés ;
    - appeler le modèle via `litellm.completion` ;
    - parser et valider la réponse (ex. liste de {candidat, score, justification}) ;
    - retourner les candidats triés par pertinence.
    """
    reponse = completion(
                model="gemini/gemini-3.1-flash-lite",
                messages=[
                  {
                    "role":"system",
                    "content": f"""Voici les profiles des candidats {profiles}\n
                      La description du poste est {project_description}\n
                      Affiche moi les meilleurs candidats pour ce poste"""
                  }
                  # ,
                  # {
                  #     "role":"user",
                  #     "content":cv_text
                  # }
                ]
            )
    return reponse.choices[0].message.content
