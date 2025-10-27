"""
Database module - SQLite database management
"""
import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """Transaction data class"""
    date: str
    description: str
    amount: float
    category: Optional[str] = None
    type: Optional[str] = None  # PAIEMENT, PRELEVEMENT, VIREMENT, etc.
    name: Optional[str] = None  # Nom du bénéficiaire/prestataire
    recurrence: bool = False  # Transaction récurrente
    vital: bool = False  # Transaction vitale
    savings: bool = False  # From savings (True) or external source (False)
    id: Optional[int] = None
    created_at: Optional[str] = None


class Database:
    """Manages SQLite database for transactions"""
    
    def __init__(self, db_path: str = "data/database.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.cursor = None
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        self.connection = sqlite3.connect(str(self.db_path))
        self.cursor = self.connection.cursor()
        
        # Create transactions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                type TEXT,
                name TEXT,
                recurrence INTEGER DEFAULT 0,
                vital INTEGER DEFAULT 0,
                savings INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create categories table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                parent_id INTEGER,
                description TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        """)
        
        # Create categorization_rules table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorization_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                case_sensitive INTEGER DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        self.connection.commit()
    
    def insert_transaction(self, transaction: Transaction) -> int:
        """Insert a transaction into the database"""
        self.cursor.execute("""
            INSERT INTO transactions (date, description, amount, category, type, name, recurrence, vital, savings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (transaction.date, transaction.description, transaction.amount, 
              transaction.category, transaction.type, transaction.name,
              int(transaction.recurrence), int(transaction.vital), int(transaction.savings)))
        
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_transactions(self, limit: Optional[int] = None) -> List[Transaction]:
        """Get all transactions"""
        query = """
            SELECT id, date, description, amount, category, type, name, recurrence, vital, savings, created_at
            FROM transactions
            ORDER BY date DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        
        results = []
        for row in self.cursor.fetchall():
            results.append(Transaction(
                id=row[0],
                date=row[1],
                description=row[2],
                amount=row[3],
                category=row[4],
                type=row[5],
                name=row[6],
                recurrence=bool(row[7]),
                vital=bool(row[8]),
                savings=bool(row[9]),
                created_at=row[10]
            ))
        return results
    
    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> List[Transaction]:
        """Get transactions within a date range"""
        self.cursor.execute("""
            SELECT id, date, description, amount, category, type, name, recurrence, vital, savings, created_at
            FROM transactions
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        """, (start_date, end_date))
        
        results = []
        for row in self.cursor.fetchall():
            results.append(Transaction(
                id=row[0],
                date=row[1],
                description=row[2],
                amount=row[3],
                category=row[4],
                type=row[5],
                name=row[6],
                recurrence=bool(row[7]),
                vital=bool(row[8]),
                savings=bool(row[9]),
                created_at=row[10]
            ))
        return results
    
    def get_transactions_by_category(self, category: str) -> List[Transaction]:
        """Get transactions by category"""
        self.cursor.execute("""
            SELECT id, date, description, amount, category, type, name, recurrence, vital, savings, created_at
            FROM transactions
            WHERE category = ?
            ORDER BY date DESC
        """, (category,))
        
        results = []
        for row in self.cursor.fetchall():
            results.append(Transaction(
                id=row[0],
                date=row[1],
                description=row[2],
                amount=row[3],
                category=row[4],
                type=row[5],
                name=row[6],
                recurrence=bool(row[7]),
                vital=bool(row[8]),
                savings=bool(row[9]),
                created_at=row[10]
            ))
        return results
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get a single transaction by its ID"""
        self.cursor.execute("""
            SELECT id, date, description, amount, category, type, name, recurrence, vital, savings, created_at
            FROM transactions
            WHERE id = ?
        """, (transaction_id,))
        
        row = self.cursor.fetchone()
        if row:
            return Transaction(
                id=row[0],
                date=row[1],
                description=row[2],
                amount=row[3],
                category=row[4],
                type=row[5],
                name=row[6],
                recurrence=bool(row[7]),
                vital=bool(row[8]),
                savings=bool(row[9]),
                created_at=row[10]
            )
        return None
    
    def update_transaction_category(self, transaction_id: int, category: Optional[str]) -> bool:
        """Update transaction category"""
        self.cursor.execute("""
            UPDATE transactions
            SET category = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (category, transaction_id))
        
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def update_transaction_flags(self, transaction_id: int, recurrence: bool = None, vital: bool = None, savings: bool = None) -> bool:
        """Update transaction recurrence, vital and savings flags"""
        updates = []
        params = []
        
        if recurrence is not None:
            updates.append("recurrence = ?")
            params.append(int(recurrence))
        
        if vital is not None:
            updates.append("vital = ?")
            params.append(int(vital))
        
        if savings is not None:
            updates.append("savings = ?")
            params.append(int(savings))
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(transaction_id)
        
        query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(query, params)
        
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def get_duplicate_check(self, date: str, description: str, amount: float) -> Optional[int]:
        """Check if transaction already exists (for duplicate detection)"""
        self.cursor.execute("""
            SELECT id FROM transactions
            WHERE date = ? AND description = ? AND amount = ?
            LIMIT 1
        """, (date, description, amount))
        
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def remove_duplicates(self) -> int:
        """Remove duplicate transactions, keeping the first occurrence
        
        Returns:
            Number of duplicate transactions removed
        """
        self.cursor.execute("""
            DELETE FROM transactions
            WHERE id NOT IN (
                SELECT MIN(id) FROM transactions
                GROUP BY date, description, amount
            )
        """)
        
        deleted_count = self.cursor.rowcount
        self.connection.commit()
        return deleted_count
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()
    
    # Budget Objectives Management
    def add_budget_objective(self, category: str, limit_amount: float) -> int:
        """Add a budget objective for a category"""
        self.cursor.execute("""
            INSERT INTO budget_objectives (category, limit_amount, period, active)
            VALUES (?, ?, 'monthly', 1)
        """, (category, limit_amount))
        
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_budget_objectives(self) -> List[Tuple]:
        """Get all active budget objectives"""
        self.cursor.execute("""
            SELECT id, category, limit_amount FROM budget_objectives
            WHERE active = 1
            ORDER BY category
        """)
        return self.cursor.fetchall()
    
    def update_budget_objective(self, objective_id: int, limit_amount: float) -> bool:
        """Update a budget objective"""
        self.cursor.execute("""
            UPDATE budget_objectives
            SET limit_amount = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (limit_amount, objective_id))
        
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def delete_budget_objective(self, objective_id: int) -> bool:
        """Delete a budget objective (soft delete)"""
        self.cursor.execute("""
            UPDATE budget_objectives
            SET active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (objective_id,))
        
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    # Tag management methods
    def add_tag(self, name: str, color: str = '#3498DB') -> int:
        """Add a new tag"""
        self.cursor.execute("""
            INSERT OR IGNORE INTO tags (name, color)
            VALUES (?, ?)
        """, (name, color))
        self.connection.commit()
        
        self.cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
        return self.cursor.fetchone()[0]
    
    def get_all_tags(self) -> List[Tuple[int, str, str]]:
        """Get all tags"""
        self.cursor.execute("SELECT id, name, color FROM tags ORDER BY name")
        return self.cursor.fetchall()
    
    def tag_transaction(self, transaction_id: int, tag_id: int) -> bool:
        """Add a tag to a transaction"""
        self.cursor.execute("""
            INSERT OR IGNORE INTO transaction_tags (transaction_id, tag_id)
            VALUES (?, ?)
        """, (transaction_id, tag_id))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def remove_tag_from_transaction(self, transaction_id: int, tag_id: int) -> bool:
        """Remove a tag from a transaction"""
        self.cursor.execute("""
            DELETE FROM transaction_tags
            WHERE transaction_id = ? AND tag_id = ?
        """, (transaction_id, tag_id))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def get_transaction_tags(self, transaction_id: int) -> List[Tuple[int, str, str]]:
        """Get all tags for a transaction"""
        self.cursor.execute("""
            SELECT t.id, t.name, t.color
            FROM tags t
            JOIN transaction_tags tt ON t.id = tt.tag_id
            WHERE tt.transaction_id = ?
            ORDER BY t.name
        """, (transaction_id,))
        return self.cursor.fetchall()
    
    def update_transaction_notes(self, transaction_id: int, notes: str) -> bool:
        """Update notes for a transaction"""
        self.cursor.execute("""
            UPDATE transactions
            SET notes = ?
            WHERE id = ?
        """, (notes, transaction_id))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def get_transaction_notes(self, transaction_id: int) -> str:
        """Get notes for a transaction"""
        self.cursor.execute("SELECT notes FROM transactions WHERE id = ?", (transaction_id,))
        result = self.cursor.fetchone()
        return result[0] if result else ""




