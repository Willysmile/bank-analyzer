#!/usr/bin/env python3
"""
Générateur de fichier CSV de test avec 100 transactions fictives
"""
import random
from datetime import datetime, timedelta

# Données fictives
MAGASINS = [
    "LIDL VILLE-A", "INTERMARCHE VILLE-B", "CARREFOUR VILLE-C", 
    "AUCHAN VILLE-A", "LECLERC VILLE-B", "CASINO VILLE-C",
    "MONOPRIX VILLE-A", "FRANPRIX VILLE-B", "SUPER U VILLE-C",
    "BIOCOOP VILLE-A", "AMAZON.FR", "FNAC.COM",
    "MC DONALD S VILLE-A", "BURGER KING VILLE-B", "KFC VILLE-C",
    "DECATHLON VILLE-A", "CULTURA VILLE-B", "BOULANGER VILLE-C",
    "PHARMACIE VILLE-A", "STATION SERVICE VILLE-B"
]

PRELEVEMENTS = [
    ("ORANGE SA", "Abonnement internet/mobile", 39.99),
    ("EDF", "Electricité", 87.50),
    ("VEOLIA EAU", "Eau", 42.30),
    ("NETFLIX", "Abonnement streaming", 15.99),
    ("SPOTIFY", "Abonnement musique", 9.99),
    ("OVH", "Hébergement web", 7.99),
    ("MUTUELLE SANTE", "Mutuelle santé", 125.00),
    ("ASSURANCE HABITATION", "Assurance habitation", 35.00),
    ("ASSURANCE AUTO", "Assurance auto", 68.50),
    ("AMAZON PRIME", "Abonnement Prime", 6.99),
    ("SALLE DE SPORT", "Abonnement fitness", 29.90),
]

VIREMENTS_RECUS = [
    ("Entreprise ABC", "Salaire", 2150.00),
    ("CAF", "Allocations familiales", 235.50),
    ("M. MARTIN JEAN", "Remboursement", 50.00),
    ("AMELI", "Remboursement santé", 45.80),
    ("Leboncoin", "Vente occasion", 120.00),
    ("Vinted", "Vente vêtements", 35.00),
]

def generate_csv():
    """Génère un fichier CSV avec 100 transactions"""
    
    # En-tête
    lines = [
        "Téléchargement du 25/10/2025,,,",
        ",,,",
        ",,,",
        "M. DUPONT JEAN,,,",
        "Compte de Dépôt n° 12345678901,,,",
        ",,,",
        ",Solde au 25/10/2025,\" 1 245,67 €\",",
        ",,,",
        "Liste des opérations du compte entre le 25/07/2025 et le 25/10/2025,,,",
        "Date,Libellé,Débit euros,Crédit euros"
    ]
    
    # Date de départ
    current_date = datetime(2025, 10, 25)
    
    # Génération des transactions
    transactions = []
    
    # 1. Un salaire par mois (3 salaires)
    for month_offset in [0, 1, 2]:
        date = current_date - timedelta(days=30 * month_offset + 20)
        date_str = date.strftime("%d/%m/%Y")
        transactions.append((
            date,
            f'{date_str},"VIREMENT EN VOTRE FAVEUR\nEntreprise ABC Salaire {date.strftime("%m/%Y")} ",,"2 150,00"'
        ))
    
    # 2. Allocations CAF mensuelles
    for month_offset in [0, 1, 2]:
        date = current_date - timedelta(days=30 * month_offset + 5)
        date_str = date.strftime("%d/%m/%Y")
        transactions.append((
            date,
            f'{date_str},"VIREMENT EN VOTRE FAVEUR\nCAF Allocations familiales ",,"235,50"'
        ))
    
    # 3. Prélèvements mensuels récurrents (tout le mois)
    for month_offset in [0, 1, 2]:
        for prel_name, prel_desc, prel_amount in PRELEVEMENTS:
            # Jour aléatoire du mois
            day_offset = random.randint(1, 28)
            date = current_date - timedelta(days=30 * month_offset + day_offset)
            date_str = date.strftime("%d/%m/%Y")
            amount_str = f'"{prel_amount:.2f}"'.replace('.', ',')
            transactions.append((
                date,
                f'{date_str},"PRELEVEMENT             \n{prel_name} {prel_desc} ",{amount_str},'
            ))
    
    # 4. Achats en magasin (50 achats aléatoires pour atteindre 100)
    for i in range(50):
        days_ago = random.randint(1, 90)
        date = current_date - timedelta(days=days_ago)
        date_str = date.strftime("%d/%m/%Y")
        magasin = random.choice(MAGASINS)
        montant = random.uniform(5.0, 150.0)
        amount_str = f'"{montant:.2f}"'.replace('.', ',')
        
        transactions.append((
            date,
            f'{date_str},"PAIEMENT PAR CARTE      \nX1234 {magasin} {(date - timedelta(days=1)).strftime("%d/%m")} ",{amount_str},'
        ))
    
    # 5. Quelques virements reçus aléatoires
    for i in range(5):
        days_ago = random.randint(5, 80)
        date = current_date - timedelta(days=days_ago)
        date_str = date.strftime("%d/%m/%Y")
        emetteur, motif, montant = random.choice(VIREMENTS_RECUS)
        amount_str = f'"{montant:.2f}"'.replace('.', ',')
        
        transactions.append((
            date,
            f'{date_str},"VIREMENT EN VOTRE FAVEUR\n{emetteur} {motif} ",,{amount_str}'
        ))
    
    # 6. Retraits DAB (5 retraits)
    for i in range(5):
        days_ago = random.randint(5, 85)
        date = current_date - timedelta(days=days_ago)
        date_str = date.strftime("%d/%m/%Y")
        montant = random.choice([20, 30, 40, 50, 60, 80, 100])
        amount_str = f'"{montant:.2f}"'.replace('.', ',')
        
        transactions.append((
            date,
            f'{date_str},"RETRAIT AU DISTRIBUTEUR \nVILLE-A CENTRE {date_str} 12H{random.randint(10,59)} ",{amount_str},'
        ))
    
    # 7. Virements émis (loyer, etc.)
    virements_emis = [
        ("AGENCE IMMOBILIERE", "Loyer", 750.00),
        ("M. BERNARD PAUL", "Remboursement", 30.00),
        ("EDF ENERGY", "Facture", 120.00),
    ]
    
    for month_offset in [0, 1, 2]:
        for dest, motif, montant in virements_emis[:1]:  # Juste le loyer chaque mois
            date = current_date - timedelta(days=30 * month_offset + 1)
            date_str = date.strftime("%d/%m/%Y")
            amount_str = f'"{montant:.2f}"'.replace('.', ',')
            
            transactions.append((
                date,
                f'{date_str},"VIREMENT EMIS           \nWEB {dest} {motif} ",{amount_str},'
            ))
    
    # 8. Frais bancaires
    date = current_date - timedelta(days=3)
    date_str = date.strftime("%d/%m/%Y")
    transactions.append((
        date,
        f'{date_str},"COTISATION              \nOffre Compte bancaire ","5,60",'
    ))
    
    # Trier par date décroissante
    transactions.sort(key=lambda x: x[0], reverse=True)
    
    # Ajouter au fichier
    for _, line in transactions[:100]:  # Limiter à 100
        lines.append(line)
    
    # Écrire le fichier
    output_file = "data/test_100_transactions.csv"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Fichier CSV généré : {output_file}")
    print(f"📊 {len(transactions[:100])} transactions créées")
    print(f"📅 Période : {(current_date - timedelta(days=90)).strftime('%d/%m/%Y')} - {current_date.strftime('%d/%m/%Y')}")

if __name__ == "__main__":
    generate_csv()
