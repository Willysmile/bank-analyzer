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
        'encoding': 'iso-8859-1',
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
        skip_rows = self.config.get('skip_rows', 0)
        
        rows = []
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Skip rows if needed
                for _ in range(skip_rows):
                    next(reader, None)
                
                for row in reader:
                    # Skip empty rows
                    if any(row.values()):
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
            
            # Check required columns
            if rows:
                required_cols = [date_col, desc_col, debit_col, credit_col]
                available_cols = set(rows[0].keys())
                missing_cols = [col for col in required_cols if col not in available_cols]
                
                if missing_cols:
                    raise ValueError(f"Missing columns in CSV: {', '.join(missing_cols)}")
            
            # Process each row
            for idx, row in enumerate(rows, start=1):
                try:
                    date = self._parse_date(row.get(date_col, '').strip())
                    description = row.get(desc_col, '').strip()
                    
                    debit = self._clean_amount(row.get(debit_col, ''))
                    credit = self._clean_amount(row.get(credit_col, ''))
                    
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
