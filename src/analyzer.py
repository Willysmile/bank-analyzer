"""
Analyzer module - Generates statistics and reports
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
from src.database import Database, Transaction
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64


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
    
    def get_recurrence_statistics(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get statistics about recurring transactions
        
        Args:
            start_date: Filter from this date (format: YYYY-MM-DD)
            end_date: Filter to this date (format: YYYY-MM-DD)
        """
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        recurring = [t for t in transactions if t.recurrence]
        non_recurring = [t for t in transactions if not t.recurrence]
        
        recurring_expenses = sum(abs(t.amount) for t in recurring if t.amount < 0)
        recurring_income = sum(t.amount for t in recurring if t.amount > 0)
        
        non_recurring_expenses = sum(abs(t.amount) for t in non_recurring if t.amount < 0)
        non_recurring_income = sum(t.amount for t in non_recurring if t.amount > 0)
        
        return {
            'recurring_count': len(recurring),
            'non_recurring_count': len(non_recurring),
            'recurring_expenses': round(recurring_expenses, 2),
            'recurring_income': round(recurring_income, 2),
            'non_recurring_expenses': round(non_recurring_expenses, 2),
            'non_recurring_income': round(non_recurring_income, 2),
            'recurring_net': round(recurring_income - recurring_expenses, 2),
            'non_recurring_net': round(non_recurring_income - non_recurring_expenses, 2),
        }
    
    def get_vital_statistics(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get statistics about vital transactions
        
        Args:
            start_date: Filter from this date (format: YYYY-MM-DD)
            end_date: Filter to this date (format: YYYY-MM-DD)
        """
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        vital = [t for t in transactions if t.vital]
        non_vital = [t for t in transactions if not t.vital]
        
        vital_expenses = sum(abs(t.amount) for t in vital if t.amount < 0)
        vital_income = sum(t.amount for t in vital if t.amount > 0)
        
        non_vital_expenses = sum(abs(t.amount) for t in non_vital if t.amount < 0)
        non_vital_income = sum(t.amount for t in non_vital if t.amount > 0)
        
        return {
            'vital_count': len(vital),
            'non_vital_count': len(non_vital),
            'vital_expenses': round(vital_expenses, 2),
            'vital_income': round(vital_income, 2),
            'non_vital_expenses': round(non_vital_expenses, 2),
            'non_vital_income': round(non_vital_income, 2),
            'vital_net': round(vital_income - vital_expenses, 2),
            'non_vital_net': round(non_vital_income - non_vital_expenses, 2),
        }
    
    def generate_pie_chart(self, data: Dict[str, float], title: str, colors: List[str] = None) -> str:
        """Generate a pie chart and return as base64 encoded image"""
        if not data or sum(data.values()) == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = list(data.keys())
        values = list(data.values())
        
        # Filter out zero values
        filtered_data = [(l, v) for l, v in zip(labels, values) if v > 0]
        if not filtered_data:
            plt.close()
            return None
        
        labels, values = zip(*filtered_data)
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        # Improve text
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    def generate_comprehensive_report(self, start_date: str = None, end_date: str = None) -> Dict:
        """Generate comprehensive report with all statistics and charts
        
        Args:
            start_date: Filter from this date (format: YYYY-MM-DD or DD/MM/YYYY)
            end_date: Filter to this date (format: YYYY-MM-DD or DD/MM/YYYY)
        """
        stats = self.get_statistics(start_date, end_date)
        by_category = self.get_by_category(start_date, end_date)
        recurrence_stats = self.get_recurrence_statistics(start_date, end_date)
        vital_stats = self.get_vital_statistics(start_date, end_date)
        
        # Separate expenses and income categories
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        expenses_by_cat = defaultdict(float)
        income_by_cat = defaultdict(float)
        
        for t in transactions:
            category = t.category or "Sans catégorie"
            if t.amount < 0:
                expenses_by_cat[category] += abs(t.amount)
            else:
                income_by_cat[category] += t.amount
        
        # Top 10 categories for expenses
        top_expenses = dict(sorted(expenses_by_cat.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Generate charts
        charts = {}
        
        # 1. Income vs Expenses
        income_expense_data = {
            'Revenus': stats['total_income'],
            'Dépenses': stats['total_expenses']
        }
        charts['income_expense'] = self.generate_pie_chart(
            income_expense_data, 
            'Revenus vs Dépenses',
            ['#27AE60', '#E74C3C']
        )
        
        # 2. Recurring vs Non-recurring expenses
        recurrence_expense_data = {
            'Récurrentes': recurrence_stats['recurring_expenses'],
            'Ponctuelles': recurrence_stats['non_recurring_expenses']
        }
        charts['recurrence'] = self.generate_pie_chart(
            recurrence_expense_data,
            'Dépenses: Récurrentes vs Ponctuelles',
            ['#3498DB', '#95A5A6']
        )
        
        # 3. Vital vs Non-vital expenses
        vital_expense_data = {
            'Vitales': vital_stats['vital_expenses'],
            'Non-vitales': vital_stats['non_vital_expenses']
        }
        charts['vital'] = self.generate_pie_chart(
            vital_expense_data,
            'Dépenses: Vitales vs Non-vitales',
            ['#E67E22', '#BDC3C7']
        )
        
        # 4. Top expenses by category
        if top_expenses:
            charts['top_categories'] = self.generate_pie_chart(
                top_expenses,
                'Top 10 Catégories de Dépenses'
            )
        
        return {
            'stats': stats,
            'recurrence_stats': recurrence_stats,
            'vital_stats': vital_stats,
            'by_category': by_category,
            'charts': charts
        }
