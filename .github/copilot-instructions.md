# GitHub Copilot Instructions

This project is a bank statement analyzer tool.

## Project Overview

- Language: Python 3.9+
- Type: CLI Application
- Purpose: Analyze bank CSV exports with categorization and reporting

## Key Files

- `main.py` - Application entry point
- `src/cli.py` - Command-line interface
- `src/database.py` - SQLite database management
- `src/importer.py` - CSV import logic
- `src/categorizer.py` - Transaction categorization
- `src/analyzer.py` - Statistics and analysis
- `requirements.txt` - Python dependencies

## Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Document code with docstrings
- Keep database schema changes backward compatible

## Common Tasks

### Add a new feature
1. Create a new method in the appropriate module
2. Add tests in `tests/`
3. Update CLI if needed in `src/cli.py`
4. Update documentation

### Add a new category
1. Add to `DEFAULT_CATEGORIES` in `src/categorizer.py`
2. Add keywords for auto-categorization in `AUTO_RULES`
3. Test the auto-categorization
