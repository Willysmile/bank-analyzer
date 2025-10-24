# Bank Analyzer 🏦

Un outil simple et efficace pour analyser vos relevés bancaires au format CSV.

**Statut** : En cours de développement (v0.1.0)

## Fonctionnalités

- ✅ **Import CSV** : Importe tes relevés bancaires directement
- 🏷️ **Catégorisation** : Catégorise automatiquement tes transactions
- 📊 **Rapports** : Génère des statistiques par période et catégorie
- 📈 **Tendances** : Visualise tes dépenses sur le temps
- 🛢️ **Stockage local** : Toutes tes données restent sur ton ordinateur (SQLite)

## Installation

### Prérequis

- Python 3.9+
- pip

### Étapes

```bash
# Clone ou télécharge le projet
cd bank

# Crée un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installe les dépendances
pip install -r requirements.txt

# Initialise la base de données
python -m src.cli init
```

## Utilisation Rapide

### 1. Importer un fichier CSV

```bash
python main.py import-csv /chemin/vers/ton/relevé.csv
```

### 2. Catégoriser automatiquement

```bash
python main.py categorize
```

### 3. Générer un rapport

```bash
# Rapport global
python main.py report

# Rapport pour une période
python main.py report --start 2025-01-01 --end 2025-12-31

# Rapport pour une catégorie
python main.py report --category Alimentation
```

### 4. Lister les dernières transactions

```bash
python main.py list-transactions --limit 50
```

## Structure du Projet

```
bank/
├── src/                      # Code source
│   ├── cli.py               # Interface ligne de commande
│   ├── database.py          # Gestion base de données
│   ├── importer.py          # Import CSV
│   ├── categorizer.py       # Catégorisation
│   └── analyzer.py          # Analyses
├── tests/                    # Tests unitaires
├── docs/                     # Documentation
│   └── CAHIER_DES_CHARGES.md # Cahier des charges complet
├── data/                     # Données (généré automatiquement)
│   └── database.db
├── config/                   # Configuration
├── main.py                  # Point d'entrée
├── requirements.txt         # Dépendances Python
├── setup.py                 # Configuration d'installation
└── README.md               # Ce fichier
```

## Formats Supportés

### Format CSV Actuellement Supporté

- **Colonnes** : `Date`, `Libellé`, `Débit euros`, `Crédit euros`
- **Encodage** : ISO-8859-1
- **Séparateur** : Virgule
- **Format de date** : JJ/MM/YYYY

Exemple :
```
Date,Libellé,Débit euros,Crédit euros
24/10/2025,PAIEMENT PAR CARTE X3573 LIDL 0780,13.38,
24/10/2025,VIREMENT EN VOTRE FAVEUR LBC France,,"110,00"
```

## Catégories Disponibles

- 🛒 Alimentation
- 🚗 Transport
- 🏠 Logement
- ⚡ Utilities (eau, gaz, électricité, Internet)
- 🎬 Loisirs
- 🏥 Santé
- 📚 Éducation
- ❓ Autres

Les transactions sont catégorisées automatiquement en fonction de mots-clés dans la description.

## Base de Données

Les transactions sont stockées dans une base SQLite locale (`data/database.db`) avec la structure suivante :

- **transactions** : Les transactions importées
  - `id`, `date`, `description`, `amount`, `category`, `created_at`, `updated_at`

- **categories** : Les catégories disponibles
  - `id`, `name`, `description`, `color`

- **categorization_rules** : Les règles de catégorisation automatiques
  - `id`, `keyword`, `category_id`, `case_sensitive`

## Configuration

Les paramètres de configuration se trouvent dans les fichiers :

- `pyproject.toml` : Configuration du projet
- `requirements.txt` : Dépendances Python

## Développement

### Installer les dépendances de développement

```bash
pip install -e ".[dev]"
```

### Lancer les tests

```bash
pytest tests/
```

### Couverture des tests

```bash
pytest --cov=src tests/
```

## Roadmap

### Phase 1 - MVP ✅
- [x] Import CSV
- [x] Catégorisation automatique
- [x] Rapports basiques
- [ ] Tests complets

### Phase 2 - Améliorations
- [ ] GUI avec Tkinter
- [ ] Support de plusieurs formats de banques
- [ ] Export en PDF
- [ ] Budget et alertes
- [ ] Graphiques

### Phase 3 - Avancé
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
