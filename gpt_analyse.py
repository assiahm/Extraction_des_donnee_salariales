import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = openai.AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def analyse_document_gpt(fiche_paie, releve_bancaire):
    system_message = (
        "Tu es un conseiller en crédit qui analyse les revenus d’un individu à partir de deux documents financiers : "
        "- Une fiche de paie "
        "- Un relevé bancaire "
        "🎯 Ton objectif est de : "
        "- Évaluer la cohérence des revenus déclarés (salaire net à payer vs montant réellement reçu) "
        "- Vérifier si la personne a des revenus stables et vérifiables "
        "- Aider à estimer sa capacité à obtenir un crédit "
        "✅ Détail de ce que tu dois faire : "
        "- Compare les salaires nets : 'salaire_net' (fiche de paie) vs 'montant_recu' (relevé bancaire) "
        "- Vérifie que les périodes/mois concordent "
        "- Donne un avis sur la fiabilité des revenus "
        "- Fournis une conclusion claire : "
        "   - 'revenus cohérents et stables' "
        "   - ou 'revenus incohérents ou douteux' "
        "   - ou 'informations insuffisantes pour conclure'"
    )

    user_prompt = f"""
Voici les données extraites automatiquement :

Fiche de paie :
{json.dumps(fiche_paie, indent=2)}

Relevé bancaire :
{json.dumps(releve_bancaire, indent=2)}

Merci de fournir une analyse détaillée et une conclusion claire.
"""

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

def detecter_nom_prenom_par_gpt(donnees_extraites):
    prompt = f"""
Voici des données extraites d'un document (fiche de paie ou relevé bancaire). Trouve le nom complet (prénom + nom) de la personne à qui ce document appartient.

Données :
{json.dumps(donnees_extraites, indent=2)}

Réponds uniquement par le nom complet, sans explication.
"""

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content.strip()
