"""
Integration tests for the complete Bank Analyzer workflow
"""
import pytest
import tempfile
import os
from pathlib import Path
from src.database import Database
from src.importer import CSVImporter
from src.categorizer import Categorizer
from src.analyzer import Analyzer


class TestIntegrationWorkflow:
    """Integration tests for complete workflow"""

    def setup_method(self):
        """Setup test fixtures"""
        # Create temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)
        self.importer = CSVImporter()
        self.categorizer = Categorizer(self.db)
        self.analyzer = Analyzer(self.db)

        # Initialize categories
        self.categorizer.init_categories()

    def teardown_method(self):
        """Cleanup test fixtures"""
        if self.db:
            self.db.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_complete_workflow_import_categorize_analyze(self):
        """Test complete workflow: import -> categorize -> analyze"""
        # Create test CSV data
        csv_content = """Date,Libellé,Débit euros,Crédit euros
01/01/2025,PAIEMENT CARTE LIDL 0780,85.50,0
02/01/2025,PRELEVEMENT EDF,45.25,0
03/01/2025,VIREMENT SALAIRE,0,2500.00
04/01/2025,PAIEMENT CARTE SNCF,75.00,0
05/01/2025,PRELEVEMENT ORANGE,29.99,0
06/01/2025,PAIEMENT CARTE PHARMACIE,25.75,0
"""

        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_file = f.name

        try:
            # Step 1: Import CSV
            transactions, warnings, duplicates = self.importer.import_file(csv_file, self.db)

            assert len(transactions) == 6
            assert len(warnings) == 0
            assert duplicates == 0

            # Verify transactions in database
            all_transactions = self.db.get_all_transactions()
            assert len(all_transactions) == 6

            # Step 2: Auto-categorize
            categorized_count = self.categorizer.categorize_all_auto()
            assert categorized_count == 6

            # Verify categorizations
            categorized_transactions = self.db.get_all_transactions()
            categories = [t.category for t in categorized_transactions if t.category]

            assert "Alimentation" in categories  # LIDL
            assert "Internet/Téléphone" in categories  # EDF, ORANGE
            assert "Transport" in categories  # SNCF
            assert "Santé" in categories  # PHARMACIE
            assert "Salaire" in categories  # SALAIRE

            # Step 3: Analyze data
            stats = self.analyzer.get_statistics()

            assert stats['total_transactions'] == 6
            assert stats['total_income'] == 2500.00
            assert abs(stats['total_expenses'] - 261.49) < 0.01  # 85.50 + 45.25 + 75.00 + 29.99 + 25.75
            # So expenses should be 261.49, income 2500, net = 2500 - 261.49 = 2238.51

            assert abs(stats['total_expenses'] - 261.49) < 0.01
            assert stats['total_income'] == 2500.00
            assert abs(stats['net'] - 2238.51) < 0.01

            # Step 4: Test category breakdown
            by_category = self.analyzer.get_by_category()

            # Should have multiple categories
            assert len(by_category) > 1
            assert "Alimentation" in by_category
            assert "Internet/Téléphone" in by_category

            # Step 5: Test monthly breakdown
            monthly = self.analyzer.get_monthly_breakdown()

            # Should have data for January 2025
            assert "2025-01" in monthly
            january_data = monthly["2025-01"]

            # Should have categorized expenses
            assert len(january_data) > 0

        finally:
            os.unlink(csv_file)

    def test_workflow_with_duplicates(self):
        """Test workflow handling of duplicate transactions"""
        # Create CSV with duplicate transactions
        csv_content = """Date,Libellé,Débit euros,Crédit euros
01/01/2025,PAIEMENT CARTE LIDL,0,50.00
01/01/2025,PAIEMENT CARTE LIDL,0,50.00
02/01/2025,PRELEVEMENT EDF,25.00,0
"""

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_file = f.name

        try:
            # Import first time
            transactions1, warnings1, duplicates1 = self.importer.import_file(csv_file, self.db)
            assert len(transactions1) == 3
            assert duplicates1 == 0

            # Import same file again - should detect duplicates
            transactions2, warnings2, duplicates2 = self.importer.import_file(csv_file, self.db)
            assert len(transactions2) == 0  # All transactions are duplicates
            assert duplicates2 == 3  # All 3 transactions detected as duplicates

            # Total transactions in DB should still be 3 (no duplicates added)
            all_transactions = self.db.get_all_transactions()
            assert len(all_transactions) == 3

        finally:
            os.unlink(csv_file)

    def test_workflow_with_invalid_data(self):
        """Test workflow handling of invalid CSV data"""
        # Create CSV with invalid data
        csv_content = """Date,Libellé,Débit euros,Crédit euros
01/01/2025,,0,50.00
invalid_date,Valid description,25.00,0
02/01/2025,Valid transaction,10.00,0
32/01/2025,Invalid date transaction,5.00,0
"""

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_file = f.name

        try:
            transactions, warnings, duplicates = self.importer.import_file(csv_file, self.db)

            # Should only import valid transactions
            assert len(transactions) == 1
            assert transactions[0].description == "Valid transaction"

            # Should have warnings for invalid rows
            assert len(warnings) >= 3  # Empty description, invalid date, invalid date

            # Verify warnings content
            warning_text = ' '.join(str(w) for w in warnings)
            assert "Empty description" in warning_text
            assert "Cannot parse date" in warning_text

        finally:
            os.unlink(csv_file)

    def test_categorization_workflow_with_manual_override(self):
        """Test categorization workflow with manual overrides"""
        # Import transactions
        csv_content = """Date,Libellé,Débit euros,Crédit euros
01/01/2025,PAIEMENT CARTE LIDL,0,50.00
02/01/2025,PRELEVEMENT UNKNOWN,25.00,0
"""

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_file = f.name

        try:
            # Import
            self.importer.import_file(csv_file, self.db)

            # Auto-categorize
            self.categorizer.categorize_all_auto()

            # Check initial categorizations
            transactions = self.db.get_all_transactions()
            categories = {t.description: t.category for t in transactions}

            assert categories["PAIEMENT CARTE LIDL"] == "Alimentation"
            assert categories["PRELEVEMENT UNKNOWN"] == "Autres"

            # Manually override categorization
            unknown_transaction = next(t for t in transactions if t.description == "PRELEVEMENT UNKNOWN")
            success = self.categorizer.categorize_transaction(unknown_transaction.id, "Transport")
            assert success == True

            # Verify manual categorization
            updated_transaction = self.db.get_transaction_by_id(unknown_transaction.id)
            assert updated_transaction.category == "Transport"

        finally:
            os.unlink(csv_file)

    def test_analysis_workflow_with_date_filters(self):
        """Test analysis workflow with date filtering"""
        # Import transactions spanning multiple months
        csv_content = """Date,Libellé,Débit euros,Crédit euros
01/01/2025,PAIEMENT CARTE LIDL,50.00,0
15/01/2025,PRELEVEMENT EDF,25.00,0
01/02/2025,VIREMENT SALAIRE,0,2000.00
15/02/2025,PAIEMENT CARTE SNCF,75.00,0
"""

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            csv_file = f.name

        try:
            # Import and categorize
            self.importer.import_file(csv_file, self.db)
            self.categorizer.categorize_all_auto()

            # Test analysis for January only
            jan_stats = self.analyzer.get_statistics("2025-01-01", "2025-01-31")
            assert jan_stats['total_transactions'] == 2
            assert abs(jan_stats['total_expenses'] - 75.00) < 0.01  # 50 + 25

            # Test analysis for February only
            feb_stats = self.analyzer.get_statistics("2025-02-01", "2025-02-28")
            assert feb_stats['total_transactions'] == 2
            assert feb_stats['total_income'] == 2000.00
            assert feb_stats['total_expenses'] == 75.00

            # Test analysis for all data
            all_stats = self.analyzer.get_statistics()
            assert all_stats['total_transactions'] == 4
            assert all_stats['total_income'] == 2000.00
            assert abs(all_stats['total_expenses'] - 150.00) < 0.01  # 50 + 25 + 75

        finally:
            os.unlink(csv_file)