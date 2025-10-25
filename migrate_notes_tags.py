#!/usr/bin/env python3
"""
Migration script to add notes and tags support to transactions
"""
import sqlite3
from pathlib import Path

def migrate_notes_tags():
    """Add notes and tags columns and create tags table"""
    db_path = Path(__file__).parent / "data" / "database.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if notes column exists
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'notes' not in columns:
            print("Adding 'notes' column to transactions...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN notes TEXT DEFAULT ''")
        
        # Create tags table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#3498DB',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create transaction_tags junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY(transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE,
                UNIQUE(transaction_id, tag_id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Migration completed successfully")
        return True
    
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    migrate_notes_tags()
