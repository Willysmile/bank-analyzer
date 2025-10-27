"""
Unit tests for Categorizer module
"""
import pytest
import tempfile
import os
from src.categorizer import Categorizer
from src.database import Database, Transaction


class TestCategorizer:
    """Test cases for Categorizer class"""

    def setup_method(self):
        """Setup test fixtures"""
        # Create temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)
        self.categorizer = Categorizer(self.db)

    def teardown_method(self):
        """Cleanup test fixtures"""
        if self.db:
            self.db.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_auto_categorize_alimentation(self):
        """Test auto-categorization for food transactions"""
        transaction = Transaction(
            date="2025-01-01",
            description="PAIEMENT CARTE LIDL 0780",
            amount=-25.50
        )

        category = self.categorizer.auto_categorize(transaction)
        assert category == "Alimentation"

    def test_auto_categorize_transport(self):
        """Test auto-categorization for transport transactions"""
        transaction = Transaction(
            date="2025-01-01",
            description="PRELEVEMENT STATION ESSENCE TOTAL",
            amount=-45.00
        )

        category = self.categorizer.auto_categorize(transaction)
        assert category == "Transport"

    def test_auto_categorize_logement(self):
        """Test auto-categorization for housing transactions"""
        transaction = Transaction(
            date="2025-01-01",
            description="VIREMENT LOYER M. DUPONT",
            amount=-650.00
        )

        category = self.categorizer.auto_categorize(transaction)
        assert category == "Logement"

    def test_auto_categorize_internet(self):
        """Test auto-categorization for internet/phone transactions"""
        transaction = Transaction(
            date="2025-01-01",
            description="PRELEVEMENT ORANGE TELECOM",
            amount=-29.99
        )

        category = self.categorizer.auto_categorize(transaction)
        assert category == "Internet/Téléphone"

    def test_auto_categorize_loisirs(self):
        """Test auto-categorization for leisure transactions"""
        transaction = Transaction(
            date="2025-01-01",
            description="PAIEMENT CARTE NETFLIX",
            amount=-15.99
        )

        category = self.categorizer.auto_categorize(transaction)
        assert category == "Loisirs"

    def test_auto_categorize_sante(self):
        """Test auto-categorization for health transactions"""
        transaction = Transaction(
            date="2025-01-01",
            description="PAIEMENT PHARMACIE",
            amount=-12.50
        )

        category = self.categorizer.auto_categorize(transaction)
        assert category == "Santé"

    def test_auto_categorize_unknown(self):
        """Test auto-categorization for unknown transactions"""
        transaction = Transaction(
            date="2025-01-01",
            description="TRANSACTION INCONNUE XYZ123",
            amount=-100.00
        )

        category = self.categorizer.auto_categorize(transaction)
        assert category == "Autres"

    def test_auto_categorize_case_insensitive(self):
        """Test that auto-categorization is case insensitive"""
        transaction = Transaction(
            date="2025-01-01",
            description="paiement carte LIDL magasin",
            amount=-25.50
        )

        category = self.categorizer.auto_categorize(transaction)
        assert category == "Alimentation"

    def test_categorize_transaction_success(self):
        """Test manual categorization of a transaction"""
        # Insert a test transaction
        transaction = Transaction(
            date="2025-01-01",
            description="Test transaction",
            amount=-50.00
        )
        transaction_id = self.db.insert_transaction(transaction)

        # Categorize it
        success = self.categorizer.categorize_transaction(transaction_id, "Alimentation")
        assert success == True

        # Verify categorization
        updated_transaction = self.db.get_transaction_by_id(transaction_id)
        assert updated_transaction.category == "Alimentation"

    def test_categorize_transaction_invalid_id(self):
        """Test manual categorization with invalid transaction ID"""
        success = self.categorizer.categorize_transaction(99999, "Alimentation")
        assert success == False

    def test_get_uncategorized_empty(self):
        """Test getting uncategorized transactions when none exist"""
        uncategorized = self.categorizer.get_uncategorized()
        assert len(uncategorized) == 0

    def test_get_uncategorized_with_data(self):
        """Test getting uncategorized transactions"""
        # Insert uncategorized transaction
        transaction1 = Transaction(
            date="2025-01-01",
            description="Uncategorized transaction 1",
            amount=-25.00
        )
        self.db.insert_transaction(transaction1)

        # Insert categorized transaction
        transaction2 = Transaction(
            date="2025-01-02",
            description="Categorized transaction",
            amount=-50.00,
            category="Alimentation"
        )
        self.db.insert_transaction(transaction2)

        # Insert another uncategorized transaction
        transaction3 = Transaction(
            date="2025-01-03",
            description="Uncategorized transaction 2",
            amount=-75.00
        )
        self.db.insert_transaction(transaction3)

        uncategorized = self.categorizer.get_uncategorized()
        assert len(uncategorized) == 2
        assert uncategorized[0].description == "Uncategorized transaction 2"  # Most recent first
        assert uncategorized[1].description == "Uncategorized transaction 1"

    def test_categorize_all_auto(self):
        """Test auto-categorizing all uncategorized transactions"""
        # Insert several uncategorized transactions
        transactions = [
            Transaction(date="2025-01-01", description="PAIEMENT CARTE LIDL", amount=-25.00),
            Transaction(date="2025-01-02", description="PRELEVEMENT EDF", amount=-45.00),
            Transaction(date="2025-01-03", description="Unknown transaction", amount=-100.00),
        ]

        for transaction in transactions:
            self.db.insert_transaction(transaction)

        # Auto-categorize all
        count = self.categorizer.categorize_all_auto()
        assert count == 3

        # Verify categorizations
        all_transactions = self.db.get_all_transactions()
        categories = [t.category for t in all_transactions]
        assert "Alimentation" in categories
        assert "Internet/Téléphone" in categories
        assert "Autres" in categories

    def test_get_categories(self):
        """Test getting all available categories"""
        # Initialize default categories
        self.categorizer.init_categories()

        categories = self.categorizer.get_categories()
        assert len(categories) > 0
        assert "Alimentation" in categories
        assert "Transport" in categories

    def test_add_category(self):
        """Test adding a new category"""
        success = self.categorizer.add_category("Test Category", "Test description")
        assert success == True

        categories = self.categorizer.get_categories()
        assert "Test Category" in categories

    def test_add_duplicate_category(self):
        """Test adding a duplicate category"""
        # Add category first time
        self.categorizer.add_category("Unique Category")

        # Try to add same category again
        success = self.categorizer.add_category("Unique Category")
        assert success == False

    def test_delete_category(self):
        """Test deleting a category"""
        # Add a category
        self.categorizer.add_category("Category to Delete")

        # Delete it
        success = self.categorizer.delete_category("Category to Delete")
        assert success == True

        # Verify it's gone
        categories = self.categorizer.get_categories()
        assert "Category to Delete" not in categories

    def test_delete_nonexistent_category(self):
        """Test deleting a non-existent category"""
        success = self.categorizer.delete_category("Nonexistent Category")
        assert success == False

    def test_add_rule(self):
        """Test adding a categorization rule"""
        success = self.categorizer.add_rule("testkeyword", "Test Category")
        assert success == True

        rules = self.categorizer.get_rules()
        assert len(rules) > 0
        assert any(rule['keyword'] == 'testkeyword' and rule['category'] == 'Test Category' for rule in rules)

    def test_get_rules(self):
        """Test getting all categorization rules"""
        # Add some rules
        self.categorizer.add_rule("keyword1", "Category1")
        self.categorizer.add_rule("keyword2", "Category2")

        rules = self.categorizer.get_rules()
        assert len(rules) >= 2

    def test_delete_rule(self):
        """Test deleting a categorization rule"""
        # Add a rule
        self.categorizer.add_rule("keyword_to_delete", "Category")

        # Get its ID
        rules = self.categorizer.get_rules()
        rule_to_delete = next((rule for rule in rules if rule['keyword'] == 'keyword_to_delete'), None)
        assert rule_to_delete is not None

        # Delete it
        success = self.categorizer.delete_rule(rule_to_delete['id'])
        assert success == True

        # Verify it's gone
        rules_after = self.categorizer.get_rules()
        assert not any(rule['keyword'] == 'keyword_to_delete' for rule in rules_after)

    def test_get_all_categories_with_parent(self):
        """Test getting categories with parent hierarchy"""
        # Initialize default categories
        self.categorizer.init_categories()

        categories = self.categorizer.get_all_categories_with_parent()
        assert len(categories) > 0

        # Check structure
        for category in categories:
            assert 'name' in category
            assert 'parent' in category

    def test_add_subcategory(self):
        """Test adding a subcategory"""
        # First add a parent category
        self.categorizer.add_category("Parent Category")

        # Add subcategory
        success = self.categorizer.add_subcategory("Sub Category", "Parent Category")
        assert success == True

    def test_get_subcategories(self):
        """Test getting subcategories for a parent category"""
        # Add parent and subcategory
        self.categorizer.add_category("Parent")
        self.categorizer.add_subcategory("Child1", "Parent")
        self.categorizer.add_subcategory("Child2", "Parent")

        subcategories = self.categorizer.get_subcategories("Parent")
        assert len(subcategories) == 2
        subcategory_names = [sub['name'] for sub in subcategories]
        assert "Child1" in subcategory_names
        assert "Child2" in subcategory_names

    def test_get_parent_category(self):
        """Test getting parent category for a subcategory"""
        # Add parent and subcategory
        self.categorizer.add_category("Parent")
        self.categorizer.add_subcategory("Child", "Parent")

        parent = self.categorizer.get_parent_category("Child")
        assert parent == "Parent"

    def test_get_parent_category_no_parent(self):
        """Test getting parent for a category that has no parent"""
        self.categorizer.add_category("Standalone Category")

        parent = self.categorizer.get_parent_category("Standalone Category")
        assert parent == ""