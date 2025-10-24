"""
CLI module - Command line interface
"""
import click
from tabulate import tabulate
from datetime import datetime
from pathlib import Path
from src.database import Database
from src.importer import CSVImporter
from src.categorizer import Categorizer
from src.analyzer import Analyzer


@click.group()
def main():
    """Bank Analyzer - Analyze your bank statements"""
    pass


@main.command()
@click.argument('filepath', type=click.Path(exists=True))
def import_csv(filepath):
    """Import a CSV file from your bank"""
    click.echo(f"📥 Importing {filepath}...")
    
    db = Database()
    importer = CSVImporter()
    
    try:
        transactions, warnings = importer.import_file(filepath, db)
        
        # Display warnings
        if warnings:
            click.echo("\n⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"   {warning}")
        
        # Insert transactions
        imported_count = 0
        for transaction in transactions:
            db.insert_transaction(transaction)
            imported_count += 1
        
        click.echo(f"\n✅ Successfully imported {imported_count} transactions")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@main.command()
def categorize():
    """Categorize transactions"""
    db = Database()
    categorizer = Categorizer(db)
    
    click.echo("🏷️  Auto-categorizing transactions...")
    
    count = categorizer.categorize_all_auto()
    click.echo(f"✅ Categorized {count} transactions")
    
    db.close()


@main.command()
@click.option('--start', help='Start date (YYYY-MM-DD)')
@click.option('--end', help='End date (YYYY-MM-DD)')
@click.option('--category', help='Filter by category')
def report(start, end, category):
    """Generate a report"""
    db = Database()
    analyzer = Analyzer(db)
    
    try:
        stats = analyzer.get_statistics(start, end, category)
        
        click.echo("\n📊 Statistics")
        click.echo(f"   Period: {start or 'All'} to {end or 'All'}")
        if category:
            click.echo(f"   Category: {category}")
        click.echo(f"\n   Total Transactions: {stats['total_transactions']}")
        click.echo(f"   Total Income: €{stats['total_income']:.2f}")
        click.echo(f"   Total Expenses: €{stats['total_expenses']:.2f}")
        click.echo(f"   Net: €{stats['net']:.2f}")
        click.echo(f"   Average: €{stats['average_transaction']:.2f}")
        
        # Category breakdown
        if not category:
            by_cat = analyzer.get_by_category(start, end)
            if by_cat:
                click.echo("\n📈 By Category:")
                for cat, amount in by_cat.items():
                    click.echo(f"   {cat}: €{amount:.2f}")
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@main.command()
@click.option('--limit', default=20, help='Number of transactions to show')
def list_transactions(limit):
    """List recent transactions"""
    db = Database()
    
    try:
        transactions = db.get_all_transactions()[:limit]
        
        if not transactions:
            click.echo("No transactions found")
            return
        
        data = [
            [t.date, t.description[:40], f"€{t.amount:.2f}", t.category or "-"]
            for t in transactions
        ]
        
        click.echo(tabulate(data, headers=["Date", "Description", "Amount", "Category"]))
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@main.command()
def init():
    """Initialize the database"""
    click.echo("🔧 Initializing database...")
    db = Database()
    categorizer = Categorizer(db)
    categorizer.init_categories()
    db.close()
    click.echo("✅ Database initialized")


if __name__ == '__main__':
    main()
