#!/usr/bin/env python3
"""Check database status"""
from src.database import Database
from src.categorizer import Categorizer

db = Database()
cat = Categorizer(db)

# Count all transactions
db.cursor.execute("SELECT COUNT(*) FROM transactions")
total = db.cursor.fetchone()[0]

# Count uncategorized
db.cursor.execute("SELECT COUNT(*) FROM transactions WHERE category IS NULL")
uncategorized = db.cursor.fetchone()[0]

# Count categorized
db.cursor.execute("SELECT COUNT(*) FROM transactions WHERE category IS NOT NULL")
categorized = db.cursor.fetchone()[0]

print("📊 État de la base de données:")
print(f"   Total transactions: {total}")
print(f"   Non catégorisées: {uncategorized}")
print(f"   Catégorisées: {categorized}")

# Show breakdown by date
print(f"\n📅 Breakdown par date (derniers):")
db.cursor.execute("""
    SELECT date, COUNT(*) as count FROM transactions 
    GROUP BY date 
    ORDER BY date DESC 
    LIMIT 10
""")
for date, count in db.cursor.fetchall():
    print(f"   {date}: {count} transactions")

print(f"\n✅ Diagnostic complet affiché")
