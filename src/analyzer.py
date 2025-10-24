"""
Analyzer module - Generates statistics and reports
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
from src.database import Database, Transaction


class Analyzer:
    """Analyzes transactions and generates reports"""
    
    def __init__(self, db: Database):
        """Initialize analyzer"""
        self.db = db
    
    def get_statistics(self, start_date: str = None, end_date: str = None, category: str = None) -> Dict:
        """
        Get statistics for a date range and optional category
        
        Returns:
            Dictionary with statistics
        """
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        if category:
            transactions = [t for t in transactions if t.category == category]
        
        if not transactions:
            return {
                'total_transactions': 0,
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net': 0.0,
                'average_transaction': 0.0,
                'largest_income': 0.0,
                'largest_expense': 0.0,
            }
        
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        
        return {
            'total_transactions': len(transactions),
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'net': round(total_income - total_expenses, 2),
            'average_transaction': round(sum(t.amount for t in transactions) / len(transactions), 2),
            'largest_income': round(max((t.amount for t in transactions if t.amount > 0), default=0), 2),
            'largest_expense': round(min((t.amount for t in transactions if t.amount < 0), default=0), 2),
        }
    
    def get_by_category(self, start_date: str = None, end_date: str = None) -> Dict[str, float]:
        """Get total expenses by category"""
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        by_category = defaultdict(float)
        
        for t in transactions:
            category = t.category or "Sans catégorie"
            by_category[category] += abs(t.amount) if t.amount < 0 else 0
        
        return dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True))
    
    def get_monthly_breakdown(self, year: int = None, month: int = None) -> Dict[str, Dict]:
        """Get monthly breakdown of expenses"""
        transactions = self.db.get_all_transactions()
        
        monthly = defaultdict(lambda: defaultdict(float))
        
        for t in transactions:
            trans_date = datetime.strptime(t.date, '%Y-%m-%d')
            month_key = trans_date.strftime('%Y-%m')
            
            category = t.category or "Sans catégorie"
            monthly[month_key][category] += abs(t.amount) if t.amount < 0 else 0
        
        return dict(sorted(monthly.items()))
    
    def get_daily_trend(self) -> Dict[str, float]:
        """Get daily total of transactions"""
        transactions = self.db.get_all_transactions()
        
        daily = defaultdict(float)
        
        for t in transactions:
            daily[t.date] += t.amount
        
        return dict(sorted(daily.items()))
