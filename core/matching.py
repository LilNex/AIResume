"""Matching entre une description de projet et les profils candidats."""


def match_candidates(project_description: str, profiles: list) -> list:
    """Classe les candidats selon leur adéquation avec le projet.

    TODO (étudiant) :
    - écrire le prompt qui fournit au LLM la description du projet
      et les profils validés ;
    - appeler le modèle via `litellm.completion` ;
    - parser et valider la réponse (ex. liste de {candidat, score, justification}) ;
    - retourner les candidats triés par pertinence.
    """
    raise NotImplementedError("match_candidates : à implémenter")
