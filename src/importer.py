"""
CSV Importer module - Handles CSV file parsing and import
"""
import csv
import chardet
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
from src.database import Database, Transaction


class CSVImporter:
    """Imports CSV files from bank exports"""
    
    # Default configuration for supported banks
    DEFAULT_CONFIG = {
        'date_column': 'Date',
        'description_column': 'Libellé',
        'debit_column': 'Débit euros',
        'credit_column': 'Crédit euros',
        'encoding': 'utf-8',
        'delimiter': ',',
        'skip_rows': 0,
        'date_format': '%d/%m/%Y'
    }
    
    def __init__(self, config: dict = None):
        """Initialize importer with optional custom config"""
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
    
    def _detect_encoding(self, filepath: str) -> str:
        """Detect file encoding"""
        with open(filepath, 'rb') as f:
            result = chardet.detect(f.read(10000))
            return result.get('encoding', 'utf-8')
    
    def _parse_csv(self, filepath: str) -> List[dict]:
        """Parse CSV file and return list of rows"""
        encoding = self.config.get('encoding')
        delimiter = self.config.get('delimiter', ',')
        
        rows = []
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            # Find the header row by looking for the line with our expected columns
            header_row_idx = None
            expected_keywords = {'Date', 'Libellé', 'Débit', 'Crédit'}
            
            for idx, line in enumerate(lines):
                # Check if this line looks like a header
                line_upper = line.upper()
                if all(keyword.upper() in line_upper for keyword in expected_keywords):
                    header_row_idx = idx
                    break
            
            if header_row_idx is None:
                # Fallback: try to find line with Date and Libellé
                for idx, line in enumerate(lines):
                    if 'Date' in line and 'Libellé' in line:
                        header_row_idx = idx
                        break
            
            if header_row_idx is None:
                raise ValueError("Could not find header row in CSV file")
            
            # Now parse from the header row onward
            with open(filepath, 'r', encoding=encoding) as f:
                # Skip to header row
                for _ in range(header_row_idx):
                    f.readline()
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row in reader:
                    # Skip empty rows and rows with all empty values
                    if row and any(str(v).strip() for v in row.values()):
                        rows.append(row)
            
            return rows
        except Exception as e:
            raise Exception(f"Error parsing CSV: {str(e)}")
    
    def _clean_amount(self, amount_str: str) -> float:
        """Clean and convert amount string to float"""
        if not amount_str or not amount_str.strip():
            return 0.0
        
        # Remove spaces and normalize decimal separator
        amount_str = amount_str.strip().replace(' ', '')
        amount_str = amount_str.replace(',', '.')
        
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date and convert to ISO format (YYYY-MM-DD)"""
        try:
            date_obj = datetime.strptime(date_str.strip(), self.config['date_format'])
            return date_obj.strftime('%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Cannot parse date '{date_str}': {str(e)}")
    
    def import_file(self, filepath: str, db: Database = None) -> Tuple[List[Transaction], List[str]]:
        """
        Import CSV file and return transactions and warnings
        
        Returns:
            Tuple of (transactions list, warnings list)
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        warnings = []
        transactions = []
        
        try:
            rows = self._parse_csv(filepath)
            
            if not rows:
                warnings.append("No transactions found in file")
                return transactions, warnings
            
            date_col = self.config['date_column']
            desc_col = self.config['description_column']
            debit_col = self.config['debit_column']
            credit_col = self.config['credit_column']
            
            # Check required columns - be flexible with whitespace
            if rows:
                first_row = rows[0]
                # Clean column names from whitespace
                available_cols = {k.strip(): v for k, v in first_row.items()}
                required_cols = [date_col, desc_col, debit_col, credit_col]
                
                missing_cols = [col for col in required_cols if col not in available_cols]
                
                if missing_cols:
                    # Try to find columns with similar names
                    available_names = list(available_cols.keys())
                    raise ValueError(f"Missing columns in CSV. Expected: {', '.join(required_cols)}\nFound: {', '.join(available_names)}")
            
            # Process each row
            for idx, row in enumerate(rows, start=1):
                try:
                    # Clean row keys (strip whitespace)
                    clean_row = {k.strip(): v for k, v in row.items()}
                    
                    date = self._parse_date(clean_row.get(date_col, '').strip())
                    description = clean_row.get(desc_col, '').strip()
                    
                    debit = self._clean_amount(clean_row.get(debit_col, ''))
                    credit = self._clean_amount(clean_row.get(credit_col, ''))
                    
                    # Combine debit/credit: debit is negative, credit is positive
                    amount = credit - debit if credit > 0 else -debit
                    
                    if not description:
                        warnings.append(f"Row {idx}: Empty description, skipping")
                        continue
                    
                    transaction = Transaction(
                        date=date,
                        description=description,
                        amount=amount
                    )
                    
                    # Check for duplicates if db provided
                    if db:
                        if db.get_duplicate_check(date, description, amount):
                            warnings.append(f"Row {idx}: Duplicate transaction, skipping")
                            continue
                    
                    transactions.append(transaction)
                
                except ValueError as e:
                    warnings.append(f"Row {idx}: {str(e)}")
                    continue
        
        except Exception as e:
            raise Exception(f"Import failed: {str(e)}")
        
        return transactions, warnings
