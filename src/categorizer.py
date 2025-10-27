"""
Categorizer module - Handles transaction categorization
"""
from typing import List, Dict
from src.database import Database, Transaction


class Categorizer:
    """Manages transaction categorization"""
    
    # Parent categories for expenses
    DEFAULT_CATEGORIES_EXPENSES = {
        "Logement": [
            "Loyer/Hypothèque",
            "Charges",
            "Électricité/Gaz/Eau",
            "Internet/Téléphone",
            "Entretien/Réparations"
        ],
        "Alimentation": [
            "Courses",
            "Restaurants",
            "Café/Snacks",
            "Livraison de repas"
        ],
        "Transport": [
            "Carburant",
            "Transports en commun",
            "Parking",
            "Entretien voiture",
            "Péages",
            "Taxi/VTC"
        ],
        "Santé": [
            "Médecin/Dentiste",
            "Pharmacie",
            "Lunettes/Lentilles",
            "Sport/Fitness"
        ],
        "Loisirs": [
            "Cinéma/Théâtre",
            "Livres/Musique",
            "Jeux vidéo",
            "Hobbies",
            "Abonnements (streaming, etc.)"
        ],
        "Vêtements et accessoires": [
            "Vêtements",
            "Chaussures",
            "Bijoux",
            "Sacs"
        ],
        "Éducation": [
            "Cours",
            "Formation",
            "Livres scolaires",
            "Frais d'inscription"
        ],
        "Enfants": [
            "Garde d'enfants",
            "École",
            "Activités",
            "Jouets"
        ],
        "Animaux": [
            "Nourriture",
            "Vétérinaire",
            "Accessoires"
        ],
        "Beauté et bien-être": [
            "Coiffeur",
            "Cosmétiques",
            "Massage",
            "Soins"
        ],
        "Services et abonnements": [
            "Services numériques",
            "Adhésions"
        ],
        "Assurances": [
            "Assurance auto",
            "Assurance habitation",
            "Assurance santé",
            "Assurance vie",
            "Assurance prêt",
            "Assurance responsabilité civile",
            "Autres assurances"
        ],
        "Impôts et cotisations": [
            "Impôts",
            "Cotisations sociales"
        ],
        "Cadeaux et dons": [
            "Cadeaux",
            "Charité",
            "Donations"
        ],
        "Dépenses exceptionnelles": [
            "Voyages",
            "Gros achats",
            "Réparations importantes"
        ]
    }
    
    # Parent categories for income
    DEFAULT_CATEGORIES_INCOME = {
        "Salaire": [
            "Salaire principal",
            "Primes",
            "Bonus",
            "Commissions"
        ],
        "Revenus professionnels": [
            "Freelance",
            "Activité indépendante",
            "Honoraires"
        ],
        "Placements": [
            "Intérêts",
            "Dividendes",
            "Plus-values"
        ],
        "Aides sociales": [
            "Allocations familiales",
            "Allocation chômage",
            "Revenu minimum",
            "RSA",
            "Aides au logement",
            "Autres aides"
        ],
        "Autres revenus": [
            "Remboursements",
            "Ventes d'objets",
            "Location"
        ],
        "Revenus exceptionnels": [
            "Héritage",
            "Bonus exceptionnel"
        ]
    }
    
    # Keyword rules for auto-categorization
    AUTO_RULES = {
        "Alimentation": ["lidl", "carrefour", "intermarche", "restaurant", "mc donald", "pizza", "boulangerie", "boucherie"],
        "Transport": ["essence", "parking", "sncf", "bus", "metro", "uber", "taxi", "autolib", "carburant"],
        "Logement": ["loyer", "immobilier", "proprio", "syndic"],
        "Internet/Téléphone": ["edf", "orange", "water", "eau", "electricite", "gaz", "internet", "téléphone", "sfr", "bouygues"],
        "Loisirs": ["cinema", "theatre", "spotify", "netflix", "jeux", "flickr", "steam", "playstation"],
        "Santé": ["pharmacie", "docteur", "medical", "sante", "dentiste"],
        "Éducation": ["ecole", "universite", "formation", "cours"],
        "Salaire": ["salaire", "virement salaire", "paye", "traitement"],
    }
    
    DEFAULT_CATEGORIES = list(DEFAULT_CATEGORIES_EXPENSES.keys()) + list(DEFAULT_CATEGORIES_INCOME.keys())
    
    def __init__(self, db: Database = None):
        """Initialize categorizer"""
        self.db = db
    
    def init_categories(self):
        """Initialize default categories and subcategories in database"""
        if not self.db:
            return
        
        # Check if categories table is empty
        self.db.cursor.execute("SELECT COUNT(*) FROM categories WHERE parent_id IS NULL")
        parent_count = self.db.cursor.fetchone()[0]
        
        # Only reinitialize if no parent categories exist
        if parent_count > 0:
            return
        
        # Initialize expense categories with subcategories
        for parent_category, subcategories in self.DEFAULT_CATEGORIES_EXPENSES.items():
            try:
                self.db.cursor.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    (parent_category,)
                )
                parent_id = self.db.cursor.lastrowid
                
                # Add subcategories
                for subcategory in subcategories:
                    try:
                        self.db.cursor.execute(
                            "INSERT INTO categories (name, parent_id) VALUES (?, ?)",
                            (subcategory, parent_id)
                        )
                    except:
                        pass
            except Exception as e:
                pass
        
        # Initialize income categories with subcategories
        for parent_category, subcategories in self.DEFAULT_CATEGORIES_INCOME.items():
            try:
                self.db.cursor.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    (parent_category,)
                )
                parent_id = self.db.cursor.lastrowid
                
                # Add subcategories
                for subcategory in subcategories:
                    try:
                        self.db.cursor.execute(
                            "INSERT INTO categories (name, parent_id) VALUES (?, ?)",
                            (subcategory, parent_id)
                        )
                    except:
                        pass
            except Exception as e:
                pass
        
        self.db.connection.commit()
    
    def ensure_default_categories(self):
        """Ensure default categories exist without overwriting existing ones"""
        if not self.db:
            return
        
        # For each default category, check if it exists and add if not
        for parent_category, subcategories in self.DEFAULT_CATEGORIES_EXPENSES.items():
            try:
                self.db.cursor.execute(
                    "SELECT id FROM categories WHERE name = ? AND parent_id IS NULL",
                    (parent_category,)
                )
                result = self.db.cursor.fetchone()
                
                if not result:
                    # Add parent category
                    self.db.cursor.execute(
                        "INSERT INTO categories (name) VALUES (?)",
                        (parent_category,)
                    )
                    parent_id = self.db.cursor.lastrowid
                else:
                    parent_id = result[0]
                
                # Ensure all default subcategories exist
                for subcategory in subcategories:
                    try:
                        self.db.cursor.execute(
                            "SELECT id FROM categories WHERE name = ? AND parent_id = ?",
                            (subcategory, parent_id)
                        )
                        if not self.db.cursor.fetchone():
                            self.db.cursor.execute(
                                "INSERT INTO categories (name, parent_id) VALUES (?, ?)",
                                (subcategory, parent_id)
                            )
                    except:
                        pass
            except:
                pass
        
        # Same for income categories
        for parent_category, subcategories in self.DEFAULT_CATEGORIES_INCOME.items():
            try:
                self.db.cursor.execute(
                    "SELECT id FROM categories WHERE name = ? AND parent_id IS NULL",
                    (parent_category,)
                )
                result = self.db.cursor.fetchone()
                
                if not result:
                    # Add parent category
                    self.db.cursor.execute(
                        "INSERT INTO categories (name) VALUES (?)",
                        (parent_category,)
                    )
                    parent_id = self.db.cursor.lastrowid
                else:
                    parent_id = result[0]
                
                # Ensure all default subcategories exist
                for subcategory in subcategories:
                    try:
                        self.db.cursor.execute(
                            "SELECT id FROM categories WHERE name = ? AND parent_id = ?",
                            (subcategory, parent_id)
                        )
                        if not self.db.cursor.fetchone():
                            self.db.cursor.execute(
                                "INSERT INTO categories (name, parent_id) VALUES (?, ?)",
                                (subcategory, parent_id)
                            )
                    except:
                        pass
            except:
                pass
        
        self.db.connection.commit()
    
    def auto_categorize(self, transaction: Transaction) -> str:
        """Auto-categorize a transaction based on rules"""
        description = transaction.description.lower()
        
        for category, keywords in self.AUTO_RULES.items():
            for keyword in keywords:
                if keyword.lower() in description:
                    return category
        
        return "Autres"
    
    def categorize_transaction(self, transaction_id: int, category: str) -> bool:
        """Manually categorize a transaction"""
        if not self.db:
            return False
        
        return self.db.update_transaction_category(transaction_id, category)
    
    def get_uncategorized(self) -> List[Transaction]:
        """Get all uncategorized transactions"""
        if not self.db:
            return []
        
        self.db.cursor.execute("""
            SELECT id, date, description, amount, category, created_at
            FROM transactions
            WHERE category IS NULL
            ORDER BY date DESC
        """)
        
        results = []
        for row in self.db.cursor.fetchall():
            results.append(Transaction(
                id=row[0],
                date=row[1],
                description=row[2],
                amount=row[3],
                category=row[4],
                created_at=row[5]
            ))
        return results
    
    def categorize_all_auto(self):
        """Auto-categorize all uncategorized transactions"""
        if not self.db:
            return 0
        
        uncategorized = self.get_uncategorized()
        count = 0
        
        for transaction in uncategorized:
            category = self.auto_categorize(transaction)
            if self.categorize_transaction(transaction.id, category):
                count += 1
        
        return count
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        if not self.db:
            return self.DEFAULT_CATEGORIES
        
        try:
            self.db.cursor.execute("SELECT name FROM categories WHERE parent_id IS NULL ORDER BY name")
            results = self.db.cursor.fetchall()
            return [row[0] for row in results] if results else self.DEFAULT_CATEGORIES
        except:
            return self.DEFAULT_CATEGORIES
    
    def add_category(self, category_name: str, description: str = "") -> bool:
        """Add a new category"""
        if not self.db:
            return False
        
        try:
            self.db.cursor.execute(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (category_name, description)
            )
            self.db.connection.commit()
            return True
        except:
            return False
    
    def delete_category(self, category_name: str) -> bool:
        """Delete a category"""
        if not self.db:
            return False
        
        try:
            self.db.cursor.execute("DELETE FROM categories WHERE name = ?", (category_name,))
            deleted = self.db.cursor.rowcount > 0
            self.db.connection.commit()
            return deleted
        except:
            return False
    
    def add_rule(self, keyword: str, category: str) -> bool:
        """Add a categorization rule"""
        if not self.db:
            return False
        
        try:
            # Get category id, create category if it doesn't exist
            self.db.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
            result = self.db.cursor.fetchone()
            
            if not result:
                # Create the category first
                self.db.cursor.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    (category,)
                )
                category_id = self.db.cursor.lastrowid
            else:
                category_id = result[0]
            
            self.db.cursor.execute(
                "INSERT INTO categorization_rules (keyword, category_id) VALUES (?, ?)",
                (keyword.lower(), category_id)
            )
            self.db.connection.commit()
            return True
        except:
            return False
    
    def get_rules(self) -> List[dict]:
        """Get all categorization rules"""
        if not self.db:
            return []
        
        self.db.cursor.execute("""
            SELECT r.id, r.keyword, c.name FROM categorization_rules r
            JOIN categories c ON r.category_id = c.id
            ORDER BY c.name, r.keyword
        """)
        
        rules = []
        for row in self.db.cursor.fetchall():
            rules.append({
                'id': row[0],
                'keyword': row[1],
                'category': row[2]
            })
        return rules
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a categorization rule"""
        if not self.db:
            return False
        
        try:
            self.db.cursor.execute("DELETE FROM categorization_rules WHERE id = ?", (rule_id,))
            self.db.connection.commit()
            return True
        except:
            return False
    
    def get_all_categories_with_parent(self) -> List[Dict]:
        """Get all categories with their parent information"""
        if not self.db:
            return []
        
        self.db.cursor.execute("""
            SELECT c.id, c.name, c.parent_id, p.name as parent_name
            FROM categories c
            LEFT JOIN categories p ON c.parent_id = p.id
            ORDER BY c.parent_id, c.name
        """)
        
        categories = []
        for row in self.db.cursor.fetchall():
            categories.append({
                'id': row[0],
                'name': row[1],
                'parent_id': row[2],
                'parent': row[3] if row[3] else None
            })
        return categories
    
    def add_subcategory(self, subcategory_name: str, parent_category_name: str, description: str = "") -> bool:
        """Add a subcategory under a parent category"""
        if not self.db:
            return False
        
        try:
            # Get parent category id
            self.db.cursor.execute("SELECT id FROM categories WHERE name = ?", (parent_category_name,))
            parent_result = self.db.cursor.fetchone()
            if not parent_result:
                return False
            
            parent_id = parent_result[0]
            
            # Insert subcategory
            self.db.cursor.execute(
                "INSERT INTO categories (name, parent_id, description) VALUES (?, ?, ?)",
                (subcategory_name, parent_id, description)
            )
            self.db.connection.commit()
            return True
        except:
            return False
    
    def get_subcategories(self, parent_category_name: str) -> List[Dict]:
        """Get all subcategories of a parent category"""
        if not self.db:
            return []
        
        try:
            # Get parent category id
            self.db.cursor.execute("SELECT id FROM categories WHERE name = ?", (parent_category_name,))
            parent_result = self.db.cursor.fetchone()
            if not parent_result:
                return []
            
            parent_id = parent_result[0]
            
            # Get subcategories
            self.db.cursor.execute("""
                SELECT id, name FROM categories WHERE parent_id = ?
                ORDER BY name
            """, (parent_id,))
            
            subcategories = []
            for row in self.db.cursor.fetchall():
                subcategories.append({
                    'id': row[0],
                    'name': row[1]
                })
            return subcategories
        except:
            return []
    
    def get_parent_category(self, subcategory_name: str) -> str:
        """Get the parent category of a subcategory"""
        if not self.db:
            return ""
        
        try:
            self.db.cursor.execute("""
                SELECT parent.name FROM categories c
                JOIN categories parent ON c.parent_id = parent.id
                WHERE c.name = ?
            """, (subcategory_name,))
            
            result = self.db.cursor.fetchone()
            return result[0] if result else ""
        except:
            return ""
    
    def remove_duplicate_transactions(self) -> int:
        """Remove duplicate transactions from the database"""
        if not self.db:
            return 0
        
        return self.db.remove_duplicates()
