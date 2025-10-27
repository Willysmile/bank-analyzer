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
    
    # Predefined configurations for different banks
    BANK_CONFIGS = {
        'french_bank': {
            'name': 'Banque Française (Standard)',
            'date_column': 'Date',
            'description_column': 'Libellé',
            'debit_column': 'Débit euros',
            'credit_column': 'Crédit euros',
            'encoding': 'utf-8',
            'delimiter': ';',
            'skip_rows': 0,
            'date_format': '%d/%m/%Y'
        },
        'french_bank_windows': {
            'name': 'Banque Française (Windows-1252)',
            'date_column': 'Date',
            'description_column': 'Libellé',
            'debit_column': 'Débit euros',
            'credit_column': 'Crédit euros',
            'encoding': 'windows-1252',
            'delimiter': ';',
            'skip_rows': 0,
            'date_format': '%d/%m/%Y'
        },
        'french_bank_windows_comma': {
            'name': 'Banque Française (Windows-1252, Virgule)',
            'date_column': 'Date',
            'description_column': 'Libellé',
            'debit_column': 'Débit euros',
            'credit_column': 'Crédit euros',
            'encoding': 'windows-1252',
            'delimiter': ',',
            'skip_rows': 0,
            'date_format': '%d/%m/%Y'
        },
        'french_bank_comma': {
            'name': 'Banque Française (Virgule)',
            'date_column': 'Date',
            'description_column': 'Libellé',
            'debit_column': 'Débit euros',
            'credit_column': 'Crédit euros',
            'encoding': 'utf-8',
            'delimiter': ',',
            'skip_rows': 0,
            'date_format': '%d/%m/%Y'
        },
        'paypal': {
            'name': 'PayPal',
            'date_column': 'Date',
            'description_column': 'Nom',
            'debit_column': 'Débit',
            'credit_column': 'Crédit',
            'encoding': 'utf-8',
            'delimiter': ',',
            'skip_rows': 0,
            'date_format': '%d/%m/%Y'
        },
        'american_bank': {
            'name': 'Banque Américaine',
            'date_column': 'Date',
            'description_column': 'Description',
            'debit_column': 'Debit',
            'credit_column': 'Credit',
            'encoding': 'utf-8',
            'delimiter': ',',
            'skip_rows': 0,
            'date_format': '%m/%d/%Y'
        },
        'generic_debit_credit': {
            'name': 'Générique (Débit/Crédit)',
            'date_column': 'Date',
            'description_column': 'Description',
            'debit_column': 'Débit',
            'credit_column': 'Crédit',
            'encoding': 'utf-8',
            'delimiter': ',',
            'skip_rows': 0,
            'date_format': '%Y-%m-%d'
        },
        'generic_amount': {
            'name': 'Générique (Montant)',
            'date_column': 'Date',
            'description_column': 'Description',
            'amount_column': 'Montant',
            'encoding': 'utf-8',
            'delimiter': ',',
            'skip_rows': 0,
            'date_format': '%Y-%m-%d',
            'amount_sign': 'mixed'  # positive/negative amounts
        }
    }
    
    # Default configuration (fallback)
    DEFAULT_CONFIG = BANK_CONFIGS['french_bank']
    
    def __init__(self, config: dict = None):
        """Initialize importer with optional custom config"""
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
    
    @classmethod
    def get_available_configs(cls):
        """Get list of available bank configurations"""
        return {key: config['name'] for key, config in cls.BANK_CONFIGS.items()}
    
    @classmethod
    def get_config(cls, config_key: str):
        """Get configuration by key"""
        return cls.BANK_CONFIGS.get(config_key, cls.DEFAULT_CONFIG)
    
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
            # Be more flexible with encoding issues - look for key parts
            expected_patterns = [
                ('Date', 'Libell'),  # Libellé becomes LibellÃ© in wrong encoding
                ('Date', 'D'),       # Débit becomes DÃ©bit
                ('Date', 'Crédit')   # Crédit might be preserved
            ]
            
            for idx, line in enumerate(lines):
                line_upper = line.upper()
                # Check multiple pattern combinations
                for pattern in expected_patterns:
                    if all(part.upper() in line_upper for part in pattern):
                        header_row_idx = idx
                        break
                if header_row_idx is not None:
                    break
            
            if header_row_idx is None:
                # Fallback: try to find line with Date and some form of description column
                for idx, line in enumerate(lines):
                    if 'Date' in line and ('Libell' in line or 'Description' in line):
                        header_row_idx = idx
                        break
            
            if header_row_idx is None:
                raise ValueError("Could not find header row in CSV file")
            
            # Now parse from the header row onward
            with open(filepath, 'r', encoding=encoding) as f:
                # Skip to header row
                for _ in range(header_row_idx):
                    f.readline()
                
                # Use csv module with proper quote handling for multi-line fields
                reader = csv.DictReader(f, delimiter=delimiter, quoting=csv.QUOTE_ALL)
                
                for row in reader:
                    # Skip empty rows and rows with all empty values
                    if row and any(str(v).strip() for v in row.values()):
                        rows.append(row)
            
            return rows
        except Exception as e:
            raise Exception(f"Error parsing CSV: {str(e)}")
    
    def _parse_description(self, description: str) -> tuple:
        """
        Parse description to extract type and name
        Examples:
        - "PAIEMENT PAR CARTE X3573 LIDL 0780" -> ("PAIEMENT", "LIDL 0780")
        - "PRELEVEMENT Orange SA" -> ("PRELEVEMENT", "Orange SA")
        - "VIREMENT EN VOTRE FAVEUR LBC France" -> ("VIREMENT", "LBC France")
        """
        # Clean up multi-line descriptions (replace newlines with spaces)
        description = description.replace('\n', ' ').replace('\r', ' ')
        # Remove extra spaces
        description = ' '.join(description.split())
        description = description.strip()
        
        # Common transaction types
        transaction_types = [
            "PAIEMENT PAR CARTE",
            "VIREMENT EN VOTRE FAVEUR",
            "VIREMENT EMIS",
            "VIREMENT",
            "PRELEVEMENT",
            "RETRAIT AU DISTRIBUTEUR",
            "REMBOURSEMENT DE PRET",
            "COTISATION",
            "REGLEMENT",
            "AVOIR",
            "INTERETS",
            "FRAIS"
        ]
        
        transaction_type = "AUTRE"
        name = description
        
        # Find the transaction type
        for t_type in transaction_types:
            if description.upper().startswith(t_type):
                transaction_type = t_type
                # Extract name after type
                name = description[len(t_type):].strip()
                # Clean up extra spaces and take first meaningful part
                name_parts = name.split()
                if name_parts:
                    # For "PAIEMENT PAR CARTE", skip the card reference if it starts with X
                    if t_type == "PAIEMENT PAR CARTE" and name_parts and name_parts[0].startswith("X"):
                        name = " ".join(name_parts[1:]) if len(name_parts) > 1 else name
                break
        
        # Clean up name
        name = name[:50] if name else "-"  # Limit to 50 chars
        
        return (transaction_type, name)
    
    def _clean_amount(self, amount_str: str) -> float:
        """Clean and convert amount string to float
        Handles various formats:
        - Spaces: 1 330,55 or 1 330.55
        - Non-breaking spaces: 1\xa0330,55
        - Commas: 1,330.55 or 1,330,55
        """
        if not amount_str or not amount_str.strip():
            return 0.0
        
        # Remove all spaces and non-breaking spaces
        amount_str = amount_str.replace(' ', '').replace('\xa0', '')
        amount_str = amount_str.strip()
        
        # Normalize decimal separator: comma to dot
        amount_str = amount_str.replace(',', '.')
        
        # Remove thousands separator (if present)
        # e.g., "1.330,55" (European format) should become "1330.55"
        if amount_str.count('.') > 1:
            # Multiple dots: it's a thousands separator issue
            # Keep only the last dot as decimal
            parts = amount_str.split('.')
            amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
        
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
            Transactions are saved to database if db is provided
            Duplicates are automatically skipped
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        warnings = []
        transactions = []
        duplicates_skipped = 0
        
        try:
            rows = self._parse_csv(filepath)
            
            if not rows:
                warnings.append("No transactions found in file")
                return transactions, warnings
            
            date_col = self.config['date_column']
            desc_col = self.config['description_column']
            
            # Check if using amount column or debit/credit columns
            if 'amount_column' in self.config:
                amount_col = self.config['amount_column']
                required_cols = [date_col, desc_col, amount_col]
            else:
                debit_col = self.config['debit_column']
                credit_col = self.config['credit_column']
                required_cols = [date_col, desc_col, debit_col, credit_col]
            
            # Check required columns - be flexible with whitespace and encoding
            if rows:
                first_row = rows[0]
                # Clean column names from whitespace
                available_cols = {k.strip(): v for k, v in first_row.items()}
                
                # Create mapping for flexible column matching
                col_mapping = {}
                for required_col in required_cols:
                    # Try exact match first
                    if required_col in available_cols:
                        col_mapping[required_col] = required_col
                    else:
                        # Try flexible matching for encoding issues
                        req_lower = required_col.lower()
                        for avail_col in available_cols:
                            avail_lower = avail_col.lower()
                            # Match key parts (ignore accents/encoding issues)
                            if ('date' in req_lower and 'date' in avail_lower) or \
                               ('libell' in req_lower and 'libell' in avail_lower) or \
                               ('d' in req_lower and 'd' in avail_lower and 'euros' in avail_lower) or \
                               ('cr' in req_lower and 'cr' in avail_lower and 'euros' in avail_lower) or \
                               ('montant' in req_lower and 'montant' in avail_lower):
                                col_mapping[required_col] = avail_col
                                break
                
                missing_cols = [col for col in required_cols if col not in col_mapping]
                
                if missing_cols:
                    available_names = list(available_cols.keys())
                    raise ValueError(f"Colonnes manquantes dans le CSV. Attendu: {', '.join(required_cols)}\nTrouvé: {', '.join(available_names)}")
            
            # Process each row
            for idx, row in enumerate(rows, start=1):
                try:
                    # Clean row keys (strip whitespace)
                    clean_row = {k.strip(): v for k, v in row.items()}
                    
                    # Use mapped column names
                    date_col_mapped = col_mapping.get(date_col, date_col)
                    desc_col_mapped = col_mapping.get(desc_col, desc_col)
                    
                    date = self._parse_date(clean_row.get(date_col_mapped, '').strip())
                    description = clean_row.get(desc_col_mapped, '').strip()
                    
                    # Handle amount calculation based on config
                    if 'amount_column' in self.config:
                        # Single amount column (positive/negative)
                        amount_col_mapped = col_mapping.get(amount_col, amount_col)
                        amount_str = clean_row.get(amount_col_mapped, '')
                        amount = self._clean_amount(amount_str)
                    else:
                        # Separate debit/credit columns
                        debit_col_mapped = col_mapping.get(debit_col, debit_col)
                        credit_col_mapped = col_mapping.get(credit_col, credit_col)
                        debit = self._clean_amount(clean_row.get(debit_col_mapped, ''))
                        credit = self._clean_amount(clean_row.get(credit_col_mapped, ''))
                        # Combine debit/credit: debit is negative, credit is positive
                        amount = credit - debit if credit > 0 else -debit
                    
                    if not description:
                        warnings.append(f"Row {idx}: Empty description, skipping")
                        continue
                    
                    # Parse description to extract type and name
                    trans_type, trans_name = self._parse_description(description)
                    
                    transaction = Transaction(
                        date=date,
                        description=description,
                        amount=amount,
                        type=trans_type,
                        name=trans_name
                    )
                    
                    # Check for duplicates if db provided
                    if db:
                        if db.get_duplicate_check(date, description, amount):
                            duplicates_skipped += 1
                            continue
                    
                    transactions.append(transaction)
                
                except ValueError as e:
                    warnings.append(f"Row {idx}: {str(e)}")
                    continue
        
        except Exception as e:
            raise Exception(f"Import failed: {str(e)}")
        
        # Add summary of duplicates skipped
        if duplicates_skipped > 0:
            warnings.append(f"⚠️ {duplicates_skipped} transaction(s) dupliquée(s) ignorée(s)")
        
        # Save transactions to database if db provided
        if db and transactions:
            for transaction in transactions:
                db.insert_transaction(transaction)
        
        return transactions, warnings, duplicates_skipped
