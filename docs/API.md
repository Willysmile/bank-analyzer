# Documentation API - Bank Analyzer

## Vue d'ensemble

Bank Analyzer fournit une API modulaire pour l'analyse de relevés bancaires. L'architecture est composée de quatre modules principaux : Database, Importer, Categorizer et Analyzer.

## Architecture

```
Bank Analyzer API
├── Database      # Gestion SQLite et persistance
├── Importer      # Import et parsing CSV
├── Categorizer   # Catégorisation automatique/manuelle
└── Analyzer      # Statistiques et rapports
```

## Module Database

### Classe Database

Gestionnaire principal de la base de données SQLite.

#### Constructeur
```python
Database(db_path: str = "data/database.db")
```

#### Méthodes principales

##### Gestion des transactions
```python
insert_transaction(transaction: Transaction) -> int
```
Insère une nouvelle transaction en base.

```python
get_all_transactions(limit: Optional[int] = None) -> List[Transaction]
```
Récupère toutes les transactions (optionnellement limité).

```python
get_transactions_by_date_range(start_date: str, end_date: str) -> List[Transaction]
```
Récupère les transactions dans une plage de dates.

```python
get_transaction_by_id(transaction_id: int) -> Optional[Transaction]
```
Récupère une transaction par son ID.

```python
update_transaction_category(transaction_id: int, category: str) -> bool
```
Met à jour la catégorie d'une transaction.

##### Gestion des catégories
```python
add_budget_objective(category: str, limit_amount: float) -> int
```
Ajoute un objectif budgétaire pour une catégorie.

```python
get_budget_objectives() -> List[Tuple]
```
Récupère tous les objectifs budgétaires actifs.

## Module Importer

### Classe CSVImporter

Gestionnaire d'import de fichiers CSV bancaires.

#### Constructeur
```python
CSVImporter(config: dict = None)
```

#### Configuration par défaut
```python
DEFAULT_CONFIG = {
    'date_column': 'Date',
    'description_column': 'Libellé',
    'debit_column': 'Débit euros',
    'credit_column': 'Crédit euros',
    'encoding': 'utf-8',
    'delimiter': ',',
    'skip_rows': 0,
    'date_format': '%d/%m/%Y'
}
```

#### Méthodes principales

```python
import_file(filepath: str, db: Database = None) -> Tuple[List[Transaction], List[str], int]
```
Importe un fichier CSV et retourne (transactions, warnings, duplicates_skipped).

```python
_parse_csv(filepath: str) -> List[dict]
```
Parse le fichier CSV et retourne la liste des lignes.

```python
_parse_description(description: str) -> tuple
```
Extrait le type de transaction et le nom du bénéficiaire.

```python
_clean_amount(amount_str: str) -> float
```
Nettoie et convertit une chaîne de montant en float.

## Module Categorizer

### Classe Categorizer

Gestionnaire de catégorisation des transactions.

#### Constructeur
```python
Categorizer(db: Database = None)
```

#### Règles de catégorisation automatique
```python
AUTO_RULES = {
    "Alimentation": ["lidl", "carrefour", "intermarche", ...],
    "Transport": ["essence", "parking", "sncf", ...],
    "Logement": ["loyer", "immobilier", "proprio", ...],
    # ...
}
```

#### Méthodes principales

```python
auto_categorize(transaction: Transaction) -> str
```
Catégorise automatiquement une transaction basée sur les règles.

```python
categorize_transaction(transaction_id: int, category: str) -> bool
```
Catégorise manuellement une transaction.

```python
get_uncategorized() -> List[Transaction]
```
Récupère toutes les transactions non catégorisées.

```python
categorize_all_auto() -> int
```
Catégorise automatiquement toutes les transactions non catégorisées.

##### Gestion des catégories
```python
add_category(category_name: str, description: str = "") -> bool
```
Ajoute une nouvelle catégorie.

```python
get_categories() -> List[str]
```
Récupère toutes les catégories disponibles.

##### Gestion des règles
```python
add_rule(keyword: str, category: str) -> bool
```
Ajoute une règle de catégorisation automatique.

```python
get_rules() -> List[dict]
```
Récupère toutes les règles de catégorisation.

## Module Analyzer

### Classe Analyzer

Générateur de statistiques et rapports.

#### Constructeur
```python
Analyzer(db: Database)
```

#### Méthodes principales

```python
get_statistics(start_date: str = None, end_date: str = None, category: str = None) -> Dict
```
Génère des statistiques générales.

**Retour :**
```python
{
    'total_transactions': int,
    'total_income': float,
    'total_expenses': float,
    'net': float,
    'average_transaction': float,
    'largest_income': float,
    'largest_expense': float
}
```

```python
get_by_category(start_date: str = None, end_date: str = None) -> Dict[str, float]
```
Génère un rapport par catégorie.

```python
get_monthly_breakdown(year: int = None, month: int = None) -> Dict[str, Dict]
```
Génère une ventilation mensuelle des dépenses.

```python
get_daily_trend() -> Dict[str, float]
```
Génère la tendance quotidienne des transactions.

## Types de données

### Transaction
```python
@dataclass
class Transaction:
    date: str                    # YYYY-MM-DD
    description: str            # Libellé complet
    amount: float               # Montant (positif = revenu, négatif = dépense)
    category: Optional[str]     # Catégorie attribuée
    type: Optional[str]         # Type (PAIEMENT, PRELEVEMENT, VIREMENT, etc.)
    name: Optional[str]         # Nom du bénéficiaire/prestataire
    recurrence: bool = False    # Transaction récurrente
    vital: bool = False         # Transaction vitale
    savings: bool = False       # Provenant des économies
    id: Optional[int] = None    # ID en base (auto-généré)
    created_at: Optional[str] = None
```

## Gestion d'erreurs

### Exceptions communes

- **FileNotFoundError** : Fichier CSV introuvable
- **ValueError** : Format de données invalide
- **sqlite3.Error** : Erreur de base de données

### Codes de retour

- **True/False** : Succès/échec des opérations
- **int** : Nombre d'éléments affectés ou ID généré
- **List** : Collections d'objets
- **Dict** : Données structurées (statistiques, rapports)

## Exemples d'utilisation

### Workflow complet
```python
from src.database import Database
from src.importer import CSVImporter
from src.categorizer import Categorizer
from src.analyzer import Analyzer

# Initialisation
db = Database()
importer = CSVImporter()
categorizer = Categorizer(db)
analyzer = Analyzer(db)

# Import
transactions, warnings, duplicates = importer.import_file("releve.csv", db)

# Catégorisation
categorized_count = categorizer.categorize_all_auto()

# Analyse
stats = analyzer.get_statistics()
by_category = analyzer.get_by_category()

db.close()
```

### Catégorisation manuelle
```python
# Récupérer les transactions non catégorisées
uncategorized = categorizer.get_uncategorized()

# Catégoriser manuellement
for transaction in uncategorized:
    category = categorizer.auto_categorize(transaction)
    categorizer.categorize_transaction(transaction.id, category)
```</content>
<parameter name="filePath">/home/willysmile/Documents/bank/docs/API.md