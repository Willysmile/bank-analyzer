"""
Database module - SQLite database management
"""
import sqlite3
from pathlib import Path
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create categories table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            INSERT INTO transactions (date, description, amount, category)
            VALUES (?, ?, ?, ?)
        """, (transaction.date, transaction.description, transaction.amount, transaction.category))
        
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions"""
        self.cursor.execute("""
            SELECT id, date, description, amount, category, created_at
            FROM transactions
            ORDER BY date DESC
        """)
        
        results = []
        for row in self.cursor.fetchall():
            results.append(Transaction(
                id=row[0],
                date=row[1],
                description=row[2],
                amount=row[3],
                category=row[4],
                created_at=row[5]
            ))
        return results
    
    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> List[Transaction]:
        """Get transactions within a date range"""
        self.cursor.execute("""
            SELECT id, date, description, amount, category, created_at
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
                created_at=row[5]
            ))
        return results
    
    def get_transactions_by_category(self, category: str) -> List[Transaction]:
        """Get transactions by category"""
        self.cursor.execute("""
            SELECT id, date, description, amount, category, created_at
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
                created_at=row[5]
            ))
        return results
    
    def update_transaction_category(self, transaction_id: int, category: str) -> bool:
        """Update transaction category"""
        self.cursor.execute("""
            UPDATE transactions
            SET category = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (category, transaction_id))
        
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
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()
