#!/usr/bin/env python3
"""
Migration script - Add budget objectives table
"""
import sqlite3
from pathlib import Path

def migrate_budget_objectives():
    """Add budget objectives table if it doesn't exist"""
    db_path = Path("data/database.db")
    
    if not db_path.exists():
        print("❌ Database not found. Run the application first to create it.")
        return False
    
    connection = sqlite3.connect(str(db_path))
    cursor = connection.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='budget_objectives'")
        if cursor.fetchone():
            print("✅ Table 'budget_objectives' already exists.")
            connection.close()
            return True
        
        # Create budget objectives table
        cursor.execute("""
            CREATE TABLE budget_objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                limit_amount REAL NOT NULL,
                period TEXT DEFAULT 'monthly',
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        print("✅ Successfully created 'budget_objectives' table.")
        print("   Columns: id, category, limit_amount, period (monthly), active, created_at, updated_at")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        connection.close()
    
    return True

if __name__ == "__main__":
    success = migrate_budget_objectives()
    exit(0 if success else 1)
