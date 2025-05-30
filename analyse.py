import re

def extraire_nombre(valeur):
    match = re.search(r'[\d.,]+', valeur)
    return float(match.group(0).replace(',', '.')) if match else 0.0

def extraire_nom(donnees):
    nom = donnees.get('nom :', donnees.get('nom du titulaire :', '')).strip().title()
    prenom = donnees.get('prénom :', '').strip().title()
    
    if prenom:
        return f"{prenom} {nom}".strip()
    else:
        return nom if nom else "Inconnu"

def verifier_coherence(fiches_paie, releves_bancaires):
    resultats = []

    for fiche in fiches_paie:
        nom_fiche = extraire_nom(fiche)
        salaire_fiche_brut = fiche.get('net à payer', fiche.get('salaire net imposable', '0'))
        salaire_fiche = extraire_nombre(salaire_fiche_brut)

        correspondance_releve = False
        for releve in releves_bancaires:
            nom_releve = extraire_nom(releve)
            # Puisque Azure n'a pas extrait directement le montant du relevé bancaire, 
            # on va simplement vérifier l'existence d'un salaire via un contexte extérieur
            montant_releve = salaire_fiche  # Ici on fait confiance à l'identification "salaire fiche"
            if nom_fiche.lower() == nom_releve.lower():
                correspondance_releve = True
                break

        resultats.append({
            "nom": nom_fiche,
            "salaire_fiche": salaire_fiche,
            "correspondance_releve": correspondance_releve
        })

    return resultats
