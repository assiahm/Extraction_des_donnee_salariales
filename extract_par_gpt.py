import os
import fitz  # PyMuPDF pour PDF
import time
from PIL import Image
import openai
from dotenv import load_dotenv

import os
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
# ...existing code...
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Chargement des variables d'environnement
load_dotenv()

client = openai.AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def extraire_texte_pdf(path):
    """Extraction de texte depuis un fichier PDF."""
    texte = ""
    doc = fitz.open(path)
    for page in doc:
        texte += page.get_text()
    return texte

def extraire_texte_image(fichier_image):
    # Configuration Tesseract

    """Extraction OCR depuis une image (JPEG/PNG)."""
    image = Image.open(fichier_image)
    texte = pytesseract.image_to_string(image, lang='fra')
    return texte


def analyser_fiche_paie_par_gpt(texte_brut):
    prompt = f'''
Tu es un expert en extraction de données de documents financiers.

Voici le contenu texte extrait d'une fiche de paie :

"""
{texte_brut}
"""

Ta mission : extraire les informations structurées suivantes :
- nom
- prénom
- entreprise
- période de paie
- salaire brut
- net imposable
- net à payer
- date de paiement (si présente)
- adresse (si présente)

Réponds uniquement avec un objet JSON clair et valide.
    '''

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(60)  # attendre 60 secondes avant de réessayer
            else:
                raise e