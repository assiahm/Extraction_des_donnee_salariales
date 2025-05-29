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
    system_message = "Tu es un expert bancaire. Ton rôle est de vérifier la cohérence entre une fiche de paie et un relevé bancaire."

    user_prompt = f"""
Voici les données extraites d'une fiche de paie :
{json.dumps(fiche_paie, indent=2)}

Et voici les données extraites d'un relevé bancaire :
{json.dumps(releve_bancaire, indent=2)}

Analyse :
1. Est-ce que le nom/prénom du salarié correspond au titulaire du compte ?
2. Le montant 'net à payer' est-il présent dans les virements ?
3. La période de paie est-elle cohérente avec la date du virement ?
4. Le nom de l’entreprise est-il mentionné comme émetteur du virement ?

Donne une analyse détaillée, puis un verdict clair : COHÉRENT ou INCOHÉRENT.
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
