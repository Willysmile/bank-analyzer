# Bank Analyzer 🏦

Un outil complet d'analyse de relevés bancaires avec interface graphique moderne et rapports détaillés.

**Version** : 1.0.0

## ✨ Fonctionnalités

### 📥 Import & Gestion
- **Import CSV** : Compatible avec les exports bancaires français (Crédit Agricole, etc.)
- **Détection automatique** : Encodage UTF-8/ISO-8859-1, format de colonnes
- **Extraction intelligente** : Type de transaction et nom du bénéficiaire
- **Détection de doublons** : Évite les imports multiples

### 🏷️ Catégorisation
- **21 catégories parentes** : 15 dépenses + 6 revenus
- **81 sous-catégories** : Classification fine et précise
- **Catégorisation manuelle** : Clic-droit dans l'onglet Transactions
- **Sélection hiérarchique** : Interface en arbre pour faciliter le choix

### � Gestion avancée
- **Transactions récurrentes** : Marquez vos abonnements et charges fixes
- **Transactions vitales** : Identifiez vos dépenses essentielles
- **Menu contextuel** : Clic-droit pour catégoriser, marquer récurrent/vital

### 📊 Rapports & Analyses
- **4 graphiques en camembert** :
  - Revenus vs Dépenses
  - Dépenses récurrentes vs ponctuelles
  - Dépenses vitales vs non-vitales
  - Top 10 catégories
- **Statistiques détaillées** :
  - Vue d'ensemble (revenus, dépenses, bilan)
  - Analyse récurrence (charges fixes vs variables)
  - Analyse vital (essentiel vs superflu)
  - Répartition par catégorie

### � Sécurité & Confidentialité
- **Stockage local** : Base SQLite, vos données restent sur votre machine
- **Aucun cloud** : Aucune connexion internet requise
- **Script d'anonymisation** : Protégez vos données sensibles

## 🚀 Installation

### Prérequis

- Python 3.9+
- Bibliothèques système : `python3-chardet`, `python3-tk`

### Installation rapide

```bash
# Clone le projet
git clone <votre-repo>
cd bank

# Installation des dépendances système (Debian/Ubuntu)
sudo apt-get install python3-chardet python3-tk python3-pil python3-matplotlib

# OU avec pip (dans un venv)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 💻 Utilisation

### Interface Graphique (Recommandée)

```bash
python3 gui.py
```

**Navigation dans l'interface :**

1. **📥 Import** : Sélectionnez et importez votre fichier CSV
2. **📋 Transactions** : 
   - Visualisez toutes vos transactions
   - Clic-droit → Catégoriser / Marquer récurrent / Marquer vital
   - Filtrez par limite d'affichage
3. **📂 Catégories** : Gérez vos catégories personnalisées
4. **📊 Rapports** : 
   - Cliquez sur "🔄 Générer le Rapport"
   - Consultez les graphiques et statistiques
5. **⚙️ Paramètres** :
   - Consultez les statistiques de la base
   - Supprimez les doublons
   - Videz la base (conserve les catégories)

### Ligne de Commande

```bash
# Importer un fichier
python main.py import-csv data/mon_releve.csv

# Générer un rapport
python main.py report

# Lister les transactions
python main.py list-transactions --limit 50
```

## 📁 Structure du Projet

```
bank/
├── src/                          # Code source
│   ├── database.py              # Gestion SQLite + Transaction dataclass
│   ├── importer.py              # Parser CSV bancaire français
│   ├── categorizer.py           # 21 catégories + 81 sous-catégories
│   ├── analyzer.py              # Stats + Graphiques matplotlib
│   ├── gui.py                   # Interface Tkinter (5 onglets)
│   └── cli.py                   # Interface ligne de commande
├── data/                         # Base de données (auto-créé)
│   ├── database.db              # SQLite
│   └── test_100_transactions.csv # Fichier de test
├── tests/                        # Tests et fichiers de test
├── docs/                         # Documentation
│   ├── CAHIER_DES_CHARGES.md    # Spécifications complètes
│   └── GUI_GUIDE.md             # Guide interface graphique
├── gui.py                        # Point d'entrée GUI
├── main.py                       # Point d'entrée CLI
├── generate_test_csv.py          # Générateur de données test
├── anonymize.py                  # Script d'anonymisation
├── migrate_db.py                 # Migration base de données
└── requirements.txt              # Dépendances Python
```

## 🎨 Fonctionnalités Avancées

### Anonymisation des données

```bash
python3 anonymize.py
```

Remplace automatiquement :
- Noms et prénoms
- Numéros de compte et cartes
- Références bancaires
- Adresses et villes

### Génération de données de test

```bash
python3 generate_test_csv.py
```

Crée un fichier avec 100 transactions fictives pour tester l'application.

### Migration de base de données

```bash
python3 migrate_db.py
```

Ajoute les colonnes `recurrence` et `vital` si elles n'existent pas.

## 📋 Catégories Disponibles

### 💸 Dépenses (15 catégories + 54 sous-catégories)

- **🛒 Alimentation** : Supermarché, Boulangerie, Restaurants, Livraison repas
- **🚗 Transport** : Essence, Péage, Parking, Transports publics, Taxi/VTC, Entretien véhicule
- **🏠 Logement** : Loyer, Charges, Ameublement, Électroménager, Décoration, Travaux
- **⚡ Factures** : Électricité, Gaz, Eau, Internet, Téléphone, Assurances
- **🎬 Loisirs** : Streaming, Jeux vidéo, Sport, Sorties, Livres
- **👕 Vêtements** : Mode, Chaussures, Accessoires
- **🏥 Santé** : Pharmacie, Médecin, Dentiste, Mutuelle
- **📚 Éducation** : Frais scolaires, Fournitures, Formation
- **🎁 Shopping** : Cosmétiques, High-tech, Cadeaux
- **💰 Banque** : Frais bancaires, Agios, Cotisations
- **🚬 Vices** : Cigarettes, Alcool, Paris
- **✈️ Voyages** : Billets, Hébergement, Activités
- **🐕 Animaux** : Vétérinaire, Nourriture, Accessoires
- **👨‍👩‍👧 Famille** : Garde enfants, Aide parents, Pension
- **❓ Autres** : Divers

### 💰 Revenus (6 catégories + 27 sous-catégories)

- **� Salaire** : Salaire net, Primes, 13ème mois
- **🎯 Freelance** : Prestations, Commissions, Royalties
- **� Investissements** : Dividendes, Plus-values, Intérêts
- **�️ Aides sociales** : CAF, Pôle emploi, Retraite
- **� Remboursements** : Santé, Impôts, Frais professionnels
- **🎁 Autres revenus** : Ventes, Cadeaux, Pension

## 🗄️ Base de Données

Structure SQLite (`data/database.db`) :

**transactions**
- `id`, `date`, `description`, `amount`, `category`
- `type`, `name` (extraction depuis libellé)
- `recurrence` (BOOLEAN) - Transaction récurrente
- `vital` (BOOLEAN) - Transaction vitale
- `created_at`, `updated_at`

**categories**
- `id`, `name`, `parent_id` (hiérarchie), `description`, `color`
- `created_at`

**categorization_rules**
- `id`, `keyword`, `category_id`, `case_sensitive`

## 🧪 Tests

```bash
# Générer un fichier de test
python3 generate_test_csv.py

# Importer le fichier de test
python3 gui.py
# Puis : Import → Sélectionner data/test_100_transactions.csv
```

## 📊 Formats CSV Supportés

### Crédit Agricole (testé)
```
Date,Libellé,Débit euros,Crédit euros
24/10/2025,"PAIEMENT PAR CARTE X3573 LIDL","13,38",
24/10/2025,"VIREMENT EN VOTRE FAVEUR LBC",,"110,00"
```

**Caractéristiques détectées :**
- Encodage : UTF-8 ou ISO-8859-1 (auto-détecté)
- Séparateur : Virgule
- Format date : JJ/MM/YYYY
- Montants : Virgule comme décimale, guillemets optionnels
- Libellés multi-lignes supportés

## 🚀 Roadmap

### Version 1.0 ✅
- [x] Import CSV avec détection intelligente
- [x] 21 catégories + 81 sous-catégories
- [x] Interface graphique complète (5 onglets)
- [x] Transactions récurrentes et vitales
- [x] Rapports avec graphiques matplotlib
- [x] Statistiques détaillées
- [x] Menu contextuel pour actions rapides
- [x] Gestion des doublons

### Version 2.0 (Futur)
- [ ] Export PDF des rapports
- [ ] Graphiques interactifs (plotly)
- [ ] Prévisions budgétaires
- [ ] Alertes personnalisées
- [ ] Support multi-comptes
- [ ] Import automatique par API bancaire
- [ ] Application mobile (Flask + React Native)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Ajouter des tests

## 📄 License

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## 👨‍💻 Auteur

Développé avec ❤️ pour une meilleure gestion de ses finances personnelles.

---

**Note** : Vos données bancaires restent privées et locales. Aucune donnée n'est envoyée sur Internet.
- [ ] API bancaire
- [ ] Synchronisation cloud
- [ ] Application web
- [ ] Dashboard en temps réel

## Limitations Actuelles

- Support d'un seul format de CSV (à adapter)
- Pas d'interface graphique
- Pas de synchronisation avec les APIs bancaires
- Toutes les données sont stockées localement

## Dépannage

### "Module introuvable : src"

Assure-toi que tu es dans le répertoire du projet et que tu utilises :
```bash
python main.py [command]
# et non
python -m src.cli [command]
```

### Erreur d'encodage lors de l'import

Vérifie l'encodage de ton fichier CSV. Par défaut, on utilise ISO-8859-1. Si tu dois utiliser UTF-8, mets à jour la configuration.

### La base de données n'existe pas

Initialise d'abord la base :
```bash
python main.py init
```

## Contribution

Les contributions sont bienvenues ! N'hésite pas à :
1. Signaler des bugs
2. Proposer des améliorations
3. Soumettre des pull requests

## Licence

MIT License - Voir LICENSE pour plus de détails

## Contacts

**Auteur** : [Ton Nom]  
**Email** : [Ton Email]

---

**Dernière mise à jour** : 24 octobre 2025
