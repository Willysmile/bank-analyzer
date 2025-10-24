#!/usr/bin/env python3
"""
Test script to verify CSV parsing
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.importer import CSVImporter

def test_import(filepath):
    """Test importing a CSV file"""
    importer = CSVImporter()
    
    try:
        transactions, warnings = importer.import_file(filepath)
        
        print(f"✅ Success!\n")
        print(f"📊 {len(transactions)} transactions parsed")
        print(f"⚠️ {len(warnings)} warnings\n")
        
        if warnings:
            print("Warnings:")
            for w in warnings[:5]:  # Show first 5
                print(f"  • {w}")
            if len(warnings) > 5:
                print(f"  ... and {len(warnings) - 5} more\n")
        
        if transactions:
            print("Sample transactions:")
            for t in transactions[:3]:
                print(f"  {t.date} | {t.description[:40]:40} | €{t.amount:8.2f}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_import.py <csv_file>")
        sys.exit(1)
    
    test_import(sys.argv[1])
