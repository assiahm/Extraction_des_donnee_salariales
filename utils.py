from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_API_KEY")

def analyser_document(file):
    client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))
    poller = client.begin_analyze_document("prebuilt-document", file)
    result = poller.result()

    extracted_data = {}
    for kv_pair in result.key_value_pairs:
        if kv_pair.key and kv_pair.value:
            extracted_data[kv_pair.key.content.lower()] = kv_pair.value.content.lower()

    return extracted_data

def classifier_document(donnees):
    texte_total = " ".join(donnees.keys()).lower()

    # Vérifier pour fiche de paie
    if any(mot in texte_total for mot in ["bulletin de salaire", "salaire net", "net à payer", "rémunération", "fiche de paie"]):
        return "fiche_paie"
    
    # Vérifier pour relevé bancaire
    elif any(mot in texte_total for mot in ["relevé bancaire", "virement salaire", "crédit (eur)", "iban", "bic", "solde initial"]):
        return "releve_bancaire"
    
    else:
        return "autre"

