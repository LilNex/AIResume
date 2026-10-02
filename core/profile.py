"""Construction et validation du profil candidat à partir du texte d'un CV."""
from litellm import completion
from pydantic import BaseModel 

# TODO (étudiant) : définir ici le modèle Pydantic du profil
# (champs attendus : firstName, lastName, phone, email, location, skills).

    

class Profil(BaseModel):
    first_name:str
    last_name:str
    phone:str
    location:str
    email:str | None = None
    skills : list[str] = []




def build_profile(cv_text: str) -> Profil | None:
    """Envoie le texte du CV au LLM et retourne sa réponse sous forme de dict.
    
    TODO (étudiant) :
    - charger la configuration (LLM_MODEL, clé API) depuis l'environnement ;
    - écrire le prompt demandant au LLM un JSON strict avec les champs du profil ;
    - appeler le modèle via `litellm.completion` ;
    - parser la réponse JSON (gérer une réponse mal formée).
    """
    schema = str(Profil.model_json_schema())
    reponse = completion(
            model="gemini/gemini-3.1-flash-lite",
            messages=[
              {
                "role":"system",
                "content": f"Extract moi depuis ce cv un json avec ce model {schema}\n Ta reponse doit etre formatté directement"
              },
              {
                  "role":"user",
                  "content":cv_text
              }
            ]
        )
    return  Profil.model_validate_json(reponse.choices[0].message.content)



def validate_profile(raw: dict):
    """Valide le dict produit par le LLM et retourne un profil typé.

    TODO (étudiant) :
    - valider `raw` avec le modèle Pydantic défini plus haut ;
    - décider quoi faire en cas d'erreur de validation (champ manquant,
      email invalide, skills qui n'est pas une liste...) : relancer le LLM,
      lever une erreur, ou marquer le profil comme incomplet.
    """
    raise NotImplementedError("validate_profile : à implémenter")
