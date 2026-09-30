"""Construction et validation du profil candidat à partir du texte d'un CV."""


# TODO (étudiant) : définir ici le modèle Pydantic du profil
# (champs attendus : firstName, lastName, phone, email, location, skills).


def build_profile(cv_text: str) -> dict:
    """Envoie le texte du CV au LLM et retourne sa réponse sous forme de dict.

    TODO (étudiant) :
    - charger la configuration (LLM_MODEL, clé API) depuis l'environnement ;
    - écrire le prompt demandant au LLM un JSON strict avec les champs du profil ;
    - appeler le modèle via `litellm.completion` ;
    - parser la réponse JSON (gérer une réponse mal formée).
    """
    raise NotImplementedError("build_profile : à implémenter")


def validate_profile(raw: dict):
    """Valide le dict produit par le LLM et retourne un profil typé.

    TODO (étudiant) :
    - valider `raw` avec le modèle Pydantic défini plus haut ;
    - décider quoi faire en cas d'erreur de validation (champ manquant,
      email invalide, skills qui n'est pas une liste...) : relancer le LLM,
      lever une erreur, ou marquer le profil comme incomplet.
    """
    raise NotImplementedError("validate_profile : à implémenter")
