#!/usr/bin/env python3
"""
Migration script to add recurrence and vital columns to existing database
"""
import sqlite3
from pathlib import Path

def migrate():
    db_path = Path("data/database.db")
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Colonnes actuelles: {columns}")
    
    # Add recurrence column if not exists
    if 'recurrence' not in columns:
        print("✅ Ajout de la colonne 'recurrence'...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN recurrence INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Colonne 'recurrence' ajoutée")
    else:
        print("ℹ️ Colonne 'recurrence' déjà présente")
    
    # Add vital column if not exists
    if 'vital' not in columns:
        print("✅ Ajout de la colonne 'vital'...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN vital INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Colonne 'vital' ajoutée")
    else:
        print("ℹ️ Colonne 'vital' déjà présente")
    
    # Verify
    cursor.execute("PRAGMA table_info(transactions)")
    new_columns = [col[1] for col in cursor.fetchall()]
    print(f"\n✅ Colonnes après migration: {new_columns}")
    
    conn.close()
    print("\n✅ Migration terminée!")

if __name__ == "__main__":
    migrate()
