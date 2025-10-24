# Cahier des Charges - Analyseur de Relevés Bancaires

**Version :** 1.0  
**Date :** 24 octobre 2025  
**Statut :** En cours de développement

## 1. Contexte et Objectifs

### 1.1 Contexte
Le projet vise à créer un outil d'analyse personnelle des dépenses bancaires, permettant à l'utilisateur de :
- Importer automatiquement ses relevés bancaires au format CSV
- Catégoriser ses dépenses de manière flexible
- Analyser ses dépenses sur des périodes ajustables
- Générer des rapports et statistiques

### 1.2 Objectifs Principaux
- **Importer des CSV** : Supporter les exports de relevés bancaires
- **Catégoriser** : Permettre une catégorisation facile et flexible des transactions
- **Analyser** : Générer des statistiques par période (jour, semaine, mois, année)
- **Visualiser** : Créer des graphiques et tableaux de synthèse
- **Exporter** : Générer des rapports en différents formats

## 2. Fonctionnalités

### 2.1 Phase 1 - MVP (Minimum Viable Product)

#### 2.1.1 Import CSV
- **Description** : Importer un fichier CSV provenant de la banque
- **Format actuellement supporté** : Export de relevés bancaires avec colonnes :
  - `Date` : Date de la transaction (format DD/MM/YYYY)
  - `Libellé` : Description/Type de transaction
  - `Débit euros` : Montants débités
  - `Crédit euros` : Montants crédités
  - Gestion des en-têtes multiples (en-têtes personnalisés en haut du fichier)
  - Encodage : ISO-8859-1
  - Séparateur : virgule
- **Traitement** :
  - Détection et suppression des lignes d'en-tête et de métadonnées
  - Conversion des dates au format standard ISO (YYYY-MM-DD)
  - Normalisation des montants (suppression des séparateurs de milliers)
  - Combinaison Débit/Crédit pour obtenir un montant signé
  - Détecter les doublons
- **Validation** : 
  - Vérifier la présence des colonnes obligatoires
  - Valider les dates et montants
  - Avertir si des lignes ne peuvent pas être parsées
- **Stockage** : Sauvegarder les transactions dans une base de données locale (SQLite)

#### 2.1.2 Catégorisation des Transactions
- **Catégories prédéfinies** :
  - Alimentation
  - Transport
  - Logement
  - Utilities (eau, électricité, gaz)
  - Loisirs
  - Santé
  - Éducation
  - Autres
  
- **Règles de catégorisation** :
  - Catégorisation manuelle par transaction
  - Création de règles basées sur des mots-clés automatiques
  - Mémorisation des catégorisations antérieures
  - Interface pour modifier/corriger les catégories

#### 2.1.3 Filtrage par Période
- **Fonctionnalités** :
  - Sélection d'une plage de dates (début - fin)
  - Filtrage par mois/année
  - Filtrage par catégorie
  - Filtrage par montant (min - max)
  
- **Options** :
  - Afficher les dépenses seulement
  - Afficher les revenus seulement
  - Afficher les deux

#### 2.1.4 Statistiques et Rapports
- **Statistiques disponibles** :
  - Total des dépenses par période
  - Total par catégorie
  - Moyenne des transactions
  - Transaction la plus importante
  - Nombre de transactions
  
- **Formats de rapports** :
  - Tableau texte dans le terminal
  - Export en CSV
  - Export en PDF (future)

### 2.2 Interface Graphique (Phase 1+)
- **Plateforme** : Tkinter (built-in, multiplateforme)
- **Design** : Interface par onglets pour une meilleure ergonomie
- **Onglets** :
  - 📥 Import : Upload de fichiers CSV
  - 📋 Transactions : Visualisation du catalogue complet
  - 🏷️ Catégorisation : Auto-catégorisation et gestion
  - 📊 Rapports : Génération de rapports et statistiques

### 2.3 Phase 2 - Améliorations Futures
- Visualisations graphiques (diagrammes en camembert, courbes)
- Support de plusieurs banques avec auto-détection du format
- Budget prévisionnel et alertes de dépassement
- Synchronisation avec les API des banques
- Export en fichiers Excel avec formatage avancé
- Amélioration de la GUI (filtres avancés, graphiques intégrés)

## 3. Architecture Technique

### 3.1 Stack Technologique
- **Langage** : Python 3.9+
- **Base de données** : SQLite3
- **Dépendances principales** :
  - `pandas` : Manipulation des données CSV
  - `sqlite3` : Gestion de la base de données
  - `click` : Interface CLI
  - `tabulate` : Affichage des tableaux
  - `pytest` : Tests unitaires

### 3.2 Structure des Fichiers
```
bank/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée de l'application
│   ├── database.py             # Gestion SQLite
│   ├── importer.py             # Import CSV
│   ├── categorizer.py          # Catégorisation
│   ├── analyzer.py             # Analyses et statistiques
│   └── utils.py                # Fonctions utilitaires
├── tests/
│   ├── __init__.py
│   ├── test_importer.py
│   ├── test_categorizer.py
│   ├── test_analyzer.py
│   └── test_integration.py
├── config/
│   ├── categories.yaml         # Définition des catégories
│   └── rules.yaml              # Règles de catégorisation
├── docs/
│   ├── CAHIER_DES_CHARGES.md   # Ce fichier
│   ├── INSTALL.md              # Installation
│   ├── API.md                  # Documentation API
│   └── EXAMPLES.md             # Exemples d'utilisation
├── data/
│   ├── database.db             # Base de données SQLite (généré)
│   └── .gitkeep
├── requirements.txt            # Dépendances Python
├── setup.py                    # Configuration installation
├── pyproject.toml              # Métadonnées du projet
├── .gitignore                  # Exclusions Git
├── .github/
│   ├── workflows/
│   └── copilot-instructions.md
└── README.md                   # Documentation principale
```

#### Table : transactions
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    balance REAL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table : categories
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table : categorization_rules
```sql
CREATE TABLE categorization_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    case_sensitive BOOLEAN DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

## 4. Cas d'Usage Principaux

### 4.1 Cas d'Usage 1 : Import d'un relevé bancaire
**Acteur** : Utilisateur
**Préconditions** : Avoir un fichier CSV d'une banque
**Flux** :
1. Lancer la commande `python -m bank import <chemin_fichier.csv>`
2. L'application valide le fichier
3. Les transactions sont importées en base de données
4. Un rapport de synthèse est affiché

### 4.2 Cas d'Usage 2 : Catégoriser les transactions
**Acteur** : Utilisateur
**Préconditions** : Des transactions importées
**Flux** :
1. Lancer `python -m bank categorize`
2. Affichage des transactions non catégorisées
3. L'utilisateur choisit une catégorie pour chaque transaction
4. Les catégorisations sont sauvegardées

### 4.3 Cas d'Usage 3 : Générer un rapport
**Acteur** : Utilisateur
**Préconditions** : Des transactions catégorisées
**Flux** :
1. Lancer `python -m bank report --start 2025-01-01 --end 2025-12-31`
2. L'application génère les statistiques
3. Un rapport formaté est affiché/exporté

## 5. Spécifications Fonctionnelles Détaillées

### 5.1 Module Importer (importer.py)
**Responsabilités** :
- Valider le format CSV
- Parser les colonnes
- Détecter les doublons
- Insérer en base de données

**Interfaces** :
```python
def import_csv(filepath: str, bank: str = 'auto') -> dict
def validate_csv(filepath: str) -> tuple[bool, str]
def detect_encoding(filepath: str) -> str
```

### 5.2 Module Catégoriser (categorizer.py)
**Responsabilités** :
- Appliquer les règles de catégorisation automatiques
- Fournir une interface pour catégorisation manuelle
- Gérer les règles de catégorisation

**Interfaces** :
```python
def auto_categorize(transaction: Transaction) -> str
def add_rule(keyword: str, category: str) -> bool
def get_uncategorized() -> list[Transaction]
def categorize_manual(transaction_id: int, category: str) -> bool
```

### 5.3 Module Analyseur (analyzer.py)
**Responsabilités** :
- Générer des statistiques
- Filtrer les transactions
- Créer des rapports

**Interfaces** :
```python
def get_statistics(start: date, end: date, category: str = None) -> dict
def get_by_category(start: date, end: date) -> dict[str, float]
def get_monthly_trend() -> dict[str, float]
```

## 6. Contraintes et Limitations

- **Sécurité** : Les données financières sont sensibles, elles doivent rester locales
- **Performance** : Support initial pour < 10 000 transactions
- **Formats** : CSV uniquement en phase 1
- **Confidentialité** : Pas de synchronisation cloud

## 7. Critères d'Acceptation

### Phase 1 MVP
- [x] Structure du projet créée
- [ ] Importer un CSV fonctionnel
- [ ] Catégoriser des transactions
- [ ] Générer un rapport basique
- [ ] Tests unitaires (80% couverture)
- [ ] Documentation utilisateur
- [ ] Fonctionnalité "hello world" testée

## 8. Planning

| Phase | Fonctionnalité | Durée Estimée |
|-------|---|---|
| 1 | Setup projet + structure | 1-2 heures |
| 2 | Module importer CSV | 2-3 heures |
| 3 | Module base de données | 2 heures |
| 4 | Module catégorisation | 3 heures |
| 5 | Module analyseur | 2-3 heures |
| 6 | Tests et refactoring | 2 heures |
| 7 | Documentation | 1-2 heures |
| 8 | Déploiement | 1 heure |

**Total estimé** : 14-17 heures

## 9. Glossaire

- **CSV** : Format de fichier texte pour stocker des données tabulaires
- **Transaction** : Opération financière (débit ou crédit)
- **Catégorie** : Classification d'une transaction (ex: Alimentation)
- **Règle** : Association automatique entre un mot-clé et une catégorie
- **Relevé** : Document bancaire listant les transactions

## 10. Notes et Remarques

- La base de données SQLite sera stockée dans `/data/database.db`
- Les fichiers CSV importés seront stockés dans un dossier `/data/imports/`
- Toutes les dates utiliseront le format ISO (YYYY-MM-DD)
- Les montants seront stockés en EUR (€)

---

**Approuvé par** : [À compléter]  
**Date d'approbation** : [À compléter]
