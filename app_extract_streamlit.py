import streamlit as st
from extract_par_gpt import extraire_texte_pdf, extraire_texte_image, analyser_fiche_paie_par_gpt
import tempfile
import pytesseract
import os


st.set_page_config(page_title="Extraction fiche de paie via GPT", layout="wide")
st.title("📤 Extraction intelligente de fiche de paie avec OpenAI")

fichier = st.file_uploader("Téléversez un fichier PDF ou image (JPEG/PNG)", type=["pdf", "jpg", "jpeg", "png"])

if fichier:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(fichier.read())
        chemin_temp = tmp_file.name

    with st.spinner("📄 Lecture du fichier et extraction du texte..."):
        if fichier.name.endswith(".pdf"):
            texte = extraire_texte_pdf(chemin_temp)
        else:
            texte = extraire_texte_image(chemin_temp)

        st.markdown("### 📄 Texte extrait :")
        st.text(texte)

    if st.button("Analyser avec GPT"):
        with st.spinner("🔎 Analyse par OpenAI en cours..."):
            resultat_json = analyser_fiche_paie_par_gpt(texte)
        st.success("✅ Analyse terminée")
        st.markdown("### 🧠 Résultat JSON structuré :")
        st.code(resultat_json, language="json")
