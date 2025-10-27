"""
Unit tests for CSV Importer module
"""
import pytest
import tempfile
import os
from pathlib import Path
from src.importer import CSVImporter
from src.database import Transaction


class TestCSVImporter:
    """Test cases for CSVImporter class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.importer = CSVImporter()

    def test_detect_encoding_utf8(self):
        """Test encoding detection for UTF-8 files"""
        # Create a temporary UTF-8 file
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write("Date,Libellé,Débit euros,Crédit euros\n")
            f.write("01/01/2025,Test transaction,0,100.50\n")
            temp_file = f.name

        try:
            encoding = self.importer._detect_encoding(temp_file)
            assert encoding in ['utf-8', 'UTF-8']
        finally:
            os.unlink(temp_file)

    def test_parse_description_paiement_carte(self):
        """Test parsing description for card payments"""
        desc = "PAIEMENT PAR CARTE X3573 LIDL 0780"
        trans_type, name = self.importer._parse_description(desc)
        assert trans_type == "PAIEMENT PAR CARTE"
        assert name == "LIDL 0780"

    def test_parse_description_prelevement(self):
        """Test parsing description for direct debits"""
        desc = "PRELEVEMENT Orange SA"
        trans_type, name = self.importer._parse_description(desc)
        assert trans_type == "PRELEVEMENT"
        assert name == "Orange SA"

    def test_parse_description_virement(self):
        """Test parsing description for transfers"""
        desc = "VIREMENT EN VOTRE FAVEUR LBC France"
        trans_type, name = self.importer._parse_description(desc)
        assert trans_type == "VIREMENT EN VOTRE FAVEUR"
        assert name == "LBC France"

    def test_clean_amount_comma_separator(self):
        """Test cleaning amounts with comma decimal separator"""
        assert self.importer._clean_amount("1 330,55") == 1330.55
        assert self.importer._clean_amount("1,330.55") == 1330.55
        assert self.importer._clean_amount("100,00") == 100.00

    def test_clean_amount_dot_separator(self):
        """Test cleaning amounts with dot decimal separator"""
        assert self.importer._clean_amount("1330.55") == 1330.55
        assert self.importer._clean_amount("100.00") == 100.00

    def test_clean_amount_empty(self):
        """Test cleaning empty amounts"""
        assert self.importer._clean_amount("") == 0.0
        assert self.importer._clean_amount("   ") == 0.0

    def test_parse_date_valid(self):
        """Test parsing valid dates"""
        assert self.importer._parse_date("01/01/2025") == "2025-01-01"
        assert self.importer._parse_date("31/12/2024") == "2024-12-31"

    def test_parse_date_invalid(self):
        """Test parsing invalid dates"""
        with pytest.raises(ValueError):
            self.importer._parse_date("32/01/2025")

        with pytest.raises(ValueError):
            self.importer._parse_date("invalid date")

    def test_parse_csv_valid_file(self):
        """Test parsing a valid CSV file"""
        csv_content = """Date,Libellé,Débit euros,Crédit euros
01/01/2025,Test transaction 1,0,100.50
02/01/2025,Test transaction 2,50.25,0
"""

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            rows = self.importer._parse_csv(temp_file)
            assert len(rows) == 2
            assert rows[0]['Date'] == '01/01/2025'
            assert rows[0]['Libellé'] == 'Test transaction 1'
            assert rows[0]['Débit euros'] == '0'
            assert rows[0]['Crédit euros'] == '100.50'
        finally:
            os.unlink(temp_file)

    def test_parse_csv_missing_header(self):
        """Test parsing CSV with missing header"""
        csv_content = """Some other data
Not header data
01/01/2025,Test transaction,0,100.50
"""

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            with pytest.raises(Exception, match="Could not find header row"):
                self.importer._parse_csv(temp_file)
        finally:
            os.unlink(temp_file)

    def test_import_file_nonexistent(self):
        """Test importing non-existent file"""
        with pytest.raises(FileNotFoundError):
            self.importer.import_file("nonexistent_file.csv")

    def test_import_file_valid_data(self):
        """Test importing valid CSV data"""
        csv_content = """Date,Libellé,Débit euros,Crédit euros
01/01/2025,PAIEMENT PAR CARTE LIDL,0,50.00
02/01/2025,PRELEVEMENT EDF,25.50,0
"""

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            transactions, warnings, duplicates = self.importer.import_file(temp_file)

            assert len(transactions) == 2
            assert len(warnings) == 0
            assert duplicates == 0

            # Check first transaction
            assert transactions[0].date == "2025-01-01"
            assert transactions[0].description == "PAIEMENT PAR CARTE LIDL"
            assert transactions[0].amount == 50.00
            assert transactions[0].type == "PAIEMENT PAR CARTE"
            assert transactions[0].name == "LIDL"

            # Check second transaction
            assert transactions[1].date == "2025-01-02"
            assert transactions[1].description == "PRELEVEMENT EDF"
            assert transactions[1].amount == -25.50
            assert transactions[1].type == "PRELEVEMENT"
            assert transactions[1].name == "EDF"

        finally:
            os.unlink(temp_file)

    def test_import_file_with_warnings(self):
        """Test importing CSV with some invalid rows"""
        csv_content = """Date,Libellé,Débit euros,Crédit euros
01/01/2025,,0,50.00
invalid_date,Valid description,25.50,0
02/01/2025,Valid transaction,10.00,0
"""

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            transactions, warnings, duplicates = self.importer.import_file(temp_file)

            assert len(transactions) == 1  # Only valid transaction
            assert len(warnings) >= 2  # Should have warnings for invalid rows
            assert "Empty description" in str(warnings)
            assert duplicates == 0

        finally:
            os.unlink(temp_file)