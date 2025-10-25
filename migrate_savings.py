#!/usr/bin/env python3
"""
Migration script - Add savings column to transactions table
"""
import sqlite3
from pathlib import Path

def migrate_savings():
    """Add savings column if it doesn't exist"""
    db_path = Path("data/database.db")
    
    if not db_path.exists():
        print("❌ Database not found. Run the application first to create it.")
        return False
    
    connection = sqlite3.connect(str(db_path))
    cursor = connection.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'savings' in columns:
            print("✅ Column 'savings' already exists in transactions table.")
            connection.close()
            return True
        
        # Add savings column (0 = external, 1 = from savings)
        cursor.execute("""
            ALTER TABLE transactions 
            ADD COLUMN savings INTEGER DEFAULT 0
        """)
        
        connection.commit()
        print("✅ Successfully added 'savings' column to transactions table.")
        print("   Values: 0 = external source, 1 = from savings")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        connection.close()
    
    return True

if __name__ == "__main__":
    success = migrate_savings()
    exit(0 if success else 1)
