import streamlit as st
from extract_par_gpt import extraire_texte_pdf, extraire_texte_image, analyser_fiche_paie_par_gpt
import tempfile
import pandas as pd
import re
import json
import matplotlib.pyplot as plt
from gpt_analyse import analyse_document_gpt

st.set_page_config(page_title="Extraction de Données Salariales", layout="wide")
st.title("💼 Extraction et Analyse de Données Salariales")

st.markdown("""
Bienvenue sur la plateforme d'extraction intelligente de documents financiers.
Téléversez plusieurs fiches de paie ou documents similaires (PDF, JPEG, PNG) pour obtenir une analyse complète de la situation financière.
""")

fichiers = st.file_uploader(
    "Téléversez un ou plusieurs fichiers PDF ou image (JPEG/PNG)",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

textes_extraits = []
noms_fichiers = []

if fichiers:
    for fichier in fichiers:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(fichier.read())
            chemin_temp = tmp_file.name

        if fichier.name.endswith(".pdf"):
            texte = extraire_texte_pdf(chemin_temp)
        else:
            texte = extraire_texte_image(chemin_temp)

        textes_extraits.append(texte)
        noms_fichiers.append(fichier.name)

    # Affichage des textes extraits
    for nom, texte in zip(noms_fichiers, textes_extraits):
        st.markdown(f"#### Texte extrait de **{nom}** :")
        with st.expander("Afficher/Masquer le texte extrait"):
            st.text(texte)

    # Bouton pour analyser tous les fichiers d'un coup
    if st.button("Analyser tous les fichiers avec GPT"):
        resultats = []
        with st.spinner("🔎 Analyse de tous les documents en cours..."):
            for texte in textes_extraits:
                resultat_json = analyser_fiche_paie_par_gpt(texte)
                resultats.append(resultat_json)
        st.success("✅ Analyse terminée")

        # Parsing JSON
        donnees = []
        for r in resultats:
            try:
                donnees.append(json.loads(r))
            except Exception:
                pass  # Ignore les JSON invalides

        if not donnees:
            st.warning("Aucune donnée exploitable n'a été extraite.")
        else:
            df = pd.DataFrame(donnees)

            # Nettoyage des colonnes numériques
            def extract_number(val):
                if isinstance(val, str):
                    match = re.search(r"[\d]+([.,][\d]+)?", val.replace(" ", ""))
                    if match:
                        return float(match.group(0).replace(",", "."))
                elif isinstance(val, (int, float)):
                    return float(val)
                return None

            for col in ["salaire brut", "net à payer", "net imposable"]:
                if col in df.columns:
                    df[col + "_num"] = df[col].apply(extract_number)

            st.dataframe(df)

            # Indicateurs financiers globaux
            col1, col2, col3 = st.columns(3)
            if "salaire brut_num" in df.columns:
                col1.metric("Salaire brut moyen", f"{df['salaire brut_num'].mean():,.2f} €")
                col2.metric("Salaire brut total", f"{df['salaire brut_num'].sum():,.2f} €")
            if "net à payer_num" in df.columns:
                col3.metric("Net à payer moyen", f"{df['net à payer_num'].mean():,.2f} €")

            # Analyse d'évolution du salaire (stabilité)
            if "période de paie" in df.columns and "salaire brut_num" in df.columns:
                st.markdown("### 📈 Évolution du salaire brut")
                # Tenter de parser la période comme date, sinon afficher brute
                try:
                    df_sorted = df.copy()
                    df_sorted["période_dt"] = pd.to_datetime(df_sorted["période de paie"], errors="coerce")
                    df_sorted = df_sorted.sort_values("période_dt")
                    st.line_chart(
                        data=df_sorted,
                        x="période_dt",
                        y="salaire brut_num",
                        use_container_width=True
                    )
                    # Analyse simple de stabilité
                    if df_sorted["salaire brut_num"].std() < 0.05 * df_sorted["salaire brut_num"].mean():
                        st.success("Le salaire brut est stable sur la période analysée (écart-type faible).")
                    else:
                        st.warning("Le salaire brut varie significativement sur la période analysée.")
                except Exception:
                    st.info("Impossible d'analyser l'évolution du salaire (format de date non reconnu).")

            # Analyse croisée GPT sur toutes les paires de documents
            if len(df) >= 2:
                st.markdown("## 🤖 Analyse croisée GPT sur toutes les paires de documents")
                for i in range(len(df)):
                    for j in range(i + 1, len(df)):
                        fiche_paie = df.iloc[i].to_dict()
                        releve_bancaire = df.iloc[j].to_dict()
                        nom_fiche = noms_fichiers[i]
                        nom_releve = noms_fichiers[j]
                        with st.expander(f"Analyse fiche : {nom_fiche} / relevé : {nom_releve}"):
                            with st.spinner(f"Analyse GPT {nom_fiche} vs {nom_releve}..."):
                                try:
                                    analyse = analyse_document_gpt(fiche_paie, releve_bancaire)
                                    st.write(analyse)
                                except Exception as e:
                                    st.error(f"Erreur GPT : {e}")

            # Export CSV
            st.download_button(
                "📥 Télécharger les résultats (CSV)",
                df.to_csv(index=False).encode("utf-8"),
                file_name="synthese_salariale.csv",
                mime="text/csv"
            )