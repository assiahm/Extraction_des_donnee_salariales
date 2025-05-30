import streamlit as st
from utils import analyser_document, classifier_document
from analyse import verifier_coherence
from io import BytesIO
import pandas as pd

st.title("🔎 Vérification de cohérence des documents financiers")

uploaded_files = st.file_uploader("Déposez plusieurs fichiers (PDF/Image)", type=['pdf', 'jpg', 'png'], accept_multiple_files=True)

if uploaded_files:
    fiches_paie, releves_bancaires = [], []

    with st.spinner("Extraction et classification en cours..."):
        for uploaded_file in uploaded_files:
            file_bytes = BytesIO(uploaded_file.read())
            donnees = analyser_document(file_bytes)
            
            # Affiche toutes les clés extraites pour le débogage
            st.write(f"🔑 **Clés extraites pour {uploaded_file.name} :**")
            st.json(donnees)

            type_doc = classifier_document(donnees)

            if type_doc == 'fiche_paie':
                fiches_paie.append(donnees)
            elif type_doc == 'releve_bancaire':
                releves_bancaires.append(donnees)

    if fiches_paie and releves_bancaires:
        st.success("✅ Documents traités avec succès!")
        resultats = verifier_coherence(fiches_paie, releves_bancaires)
        df = pd.DataFrame(resultats)
        st.write("## Résultats d'analyse :")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger en CSV", csv, "resultats_analyse.csv", "text/csv")
    else:
        st.error("⚠️ Veuillez fournir au moins une fiche de paie et un relevé bancaire.")
