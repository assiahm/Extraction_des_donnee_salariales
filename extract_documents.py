from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Charger .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

endpoint = os.getenv("AZURE_FORM_ENDPOINT")
key = os.getenv("AZURE_FORM_KEY")

client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def extraire_donnees(file):
    poller = client.begin_analyze_document("prebuilt-document", document=file)
    result = poller.result()

    donnees = {}
    for kv in result.key_value_pairs:
        if kv.key and kv.value:
            donnees[kv.key.content.lower().strip()] = kv.value.content.strip()
    return donnees