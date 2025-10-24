"""
Categorizer module - Handles transaction categorization
"""
from typing import List, Dict
from src.database import Database, Transaction


class Categorizer:
    """Manages transaction categorization"""
    
    DEFAULT_CATEGORIES = [
        "Alimentation",
        "Transport",
        "Logement",
        "Utilities",
        "Loisirs",
        "Santé",
        "Éducation",
        "Autres"
    ]
    
    # Keyword rules for auto-categorization
    AUTO_RULES = {
        "Alimentation": ["lidl", "carrefour", "intermarche", "restaurant", "mc donald", "pizza"],
        "Transport": ["essence", "parking", "sncf", "bus", "metro", "uber", "taxi"],
        "Logement": ["loyer", "immobilier", "proprio"],
        "Utilities": ["edf", "orange", "water", "eau", "electricite", "gaz", "internet"],
        "Loisirs": ["cinema", "theatre", "spotify", "netflix", "jeux", "flickr"],
        "Santé": ["pharmacie", "docteur", "medical", "sante"],
        "Éducation": ["ecole", "universite", "formation", "cours"],
    }
    
    def __init__(self, db: Database = None):
        """Initialize categorizer"""
        self.db = db
    
    def init_categories(self):
        """Initialize default categories in database"""
        if not self.db:
            return
        
        for category in self.DEFAULT_CATEGORIES:
            try:
                self.db.cursor.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    (category,)
                )
            except:
                # Category already exists
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
            self.db.connection.commit()
            return True
        except:
            return False
    
    def add_rule(self, keyword: str, category: str) -> bool:
        """Add a categorization rule"""
        if not self.db:
            return False
        
        try:
            # Get category id
            self.db.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
            result = self.db.cursor.fetchone()
            if not result:
                return False
            
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
