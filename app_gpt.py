import streamlit as st
from gpt_analyse import analyse_document_gpt, detecter_nom_prenom_par_gpt
from extract_documents import extraire_donnees
import json
from io import BytesIO

st.set_page_config(page_title="Analyse Documentaire Azure OpenAI", layout="wide")

st.title("📑 Analyse documentaire intelligente avec Azure OpenAI")

fiche_paie_file = st.file_uploader("📄 Téléversez la fiche de paie", type=["pdf", "jpg", "png"], key="fiche")
releve_bancaire_file = st.file_uploader("🏦 Téléversez le relevé bancaire", type=["pdf", "jpg", "png"], key="releve")

if fiche_paie_file and releve_bancaire_file:
    with st.spinner("Extraction des données depuis Azure Document Intelligence..."):
        fiche_paie_data = extraire_donnees(fiche_paie_file)
        releve_bancaire_data = extraire_donnees(releve_bancaire_file)

    st.success("Extraction terminée ✅")

    st.markdown("### 📄 Données extraites de la fiche de paie")
    st.json(fiche_paie_data)

    st.markdown("### 🏦 Données extraites du relevé bancaire")
    st.json(releve_bancaire_data)

    nom_paie = detecter_nom_prenom_par_gpt(fiche_paie_data)
    nom_releve = detecter_nom_prenom_par_gpt(releve_bancaire_data)

    st.write(f"👤 Nom détecté (fiche de paie - GPT) : {nom_paie}")
    st.write(f"👤 Nom détecté (relevé bancaire - GPT) : {nom_releve}")

    if st.button("Analyser avec GPT"):
        with st.spinner("Analyse en cours avec Azure OpenAI..."):
            result = analyse_document_gpt(fiche_paie_data, releve_bancaire_data)
        st.success("Analyse terminée")
        st.markdown("## 🧠 Verdict de l'analyse :")
        st.markdown(result)
else:
    st.info("Veuillez téléverser les deux documents pour lancer l'analyse.")

