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
    
    def get_monthly_statistics(self) -> Dict[str, Dict]:
        """Get statistics grouped by month"""
        transactions = self.db.get_all_transactions()
        monthly_stats = defaultdict(lambda: {
            'income': 0.0,
            'expenses': 0.0,
            'count': 0,
            'transactions': []
        })
        
        for t in transactions:
            # Extract YYYY-MM from date
            month_key = t.date[:7] if len(t.date) >= 7 else t.date
            
            if t.amount > 0:
                monthly_stats[month_key]['income'] += t.amount
            else:
                monthly_stats[month_key]['expenses'] += abs(t.amount)
            
            monthly_stats[month_key]['count'] += 1
            monthly_stats[month_key]['transactions'].append(t)
        
        # Calculate net and ratio for each month
        for month_key in monthly_stats:
            stats = monthly_stats[month_key]
            stats['net'] = stats['income'] - stats['expenses']
            stats['income'] = round(stats['income'], 2)
            stats['expenses'] = round(stats['expenses'], 2)
            stats['net'] = round(stats['net'], 2)
            stats['ratio'] = round(stats['expenses'] / stats['income'], 2) if stats['income'] > 0 else 0
        
        return dict(sorted(monthly_stats.items(), reverse=True))
    
    def get_dashboard_summary(self) -> Dict:
        """Get dashboard summary with key metrics"""
        transactions = self.db.get_all_transactions()
        
        if not transactions:
            return {
                'balance': 0.0,
                'monthly_income': 0.0,
                'monthly_expenses': 0.0,
                'monthly_net': 0.0,
                'savings_ratio': 0.0,
                'transaction_count': 0,
                'status': 'aucune_donnee',
                'last_transaction': None,
                'recurring_monthly': 0.0,
                'external_vs_savings': {'external': 0.0, 'savings': 0.0}
            }
        
        # Get current month
        today = datetime.now()
        current_month = today.strftime("%Y-%m")
        
        # Filter current month transactions
        current_month_trans = [t for t in transactions if t.date.startswith(current_month)]
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        balance = total_income - total_expenses
        
        # Monthly stats
        month_income = sum(t.amount for t in current_month_trans if t.amount > 0)
        month_expenses = sum(abs(t.amount) for t in current_month_trans if t.amount < 0)
        month_net = month_income - month_expenses
        
        # Savings analysis
        external_income = sum(t.amount for t in transactions if t.amount > 0 and not t.savings)
        savings_income = sum(t.amount for t in transactions if t.amount > 0 and t.savings)
        external_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0 and not t.savings)
        savings_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0 and t.savings)
        
        # Recurring monthly charges
        recurring = [t for t in transactions if t.recurrence]
        recurring_monthly = sum(abs(t.amount) for t in recurring if t.amount < 0)
        
        # Determine status
        if month_net < 0:
            status = 'deficit'
        elif month_expenses > month_income * 0.8:
            status = 'warning'
        else:
            status = 'healthy'
        
        savings_ratio = (savings_income / external_income * 100) if external_income > 0 else 0
        
        return {
            'balance': round(balance, 2),
            'monthly_income': round(month_income, 2),
            'monthly_expenses': round(month_expenses, 2),
            'monthly_net': round(month_net, 2),
            'savings_ratio': round(savings_ratio, 2),
            'transaction_count': len(current_month_trans),
            'status': status,
            'last_transaction': transactions[0] if transactions else None,
            'recurring_monthly': round(recurring_monthly, 2),
            'external_vs_savings': {
                'external': round(external_income - external_expenses, 2),
                'savings': round(savings_income - savings_expenses, 2)
            }
        }
    
    def get_monthly_trend_chart(self) -> str:
        """Generate monthly trend chart (line chart of net balance)"""
        monthly = self.get_monthly_statistics()
        
        if not monthly:
            return None
        
        months = sorted(monthly.keys())[-12:]  # Last 12 months
        nets = [monthly[m]['net'] for m in months]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(months, nets, marker='o', linewidth=2, markersize=8, color='#3498DB')
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.fill_between(range(len(months)), nets, alpha=0.3, color='#3498DB')
        
        ax.set_title('Évolution du Bilan Net (Mensuel)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Bilan Net (€)')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()
        plt.close()
        
        return img_base64
    
    def get_savings_analysis(self) -> Dict:
        """Analyze impact of savings on finances"""
        transactions = self.db.get_all_transactions()
        
        external = [t for t in transactions if not t.savings]
        from_savings = [t for t in transactions if t.savings]
        
        external_income = sum(t.amount for t in external if t.amount > 0)
        external_expenses = sum(abs(t.amount) for t in external if t.amount < 0)
        
        savings_income = sum(t.amount for t in from_savings if t.amount > 0)
        savings_expenses = sum(abs(t.amount) for t in from_savings if t.amount < 0)
        
        return {
            'external_balance': round(external_income - external_expenses, 2),
            'savings_balance': round(savings_income - savings_expenses, 2),
            'external_transactions': len(external),
            'savings_transactions': len(from_savings),
            'savings_usage_ratio': round((savings_expenses / (external_expenses + savings_expenses) * 100), 2) if (external_expenses + savings_expenses) > 0 else 0,
            'external_income': round(external_income, 2),
            'external_expenses': round(external_expenses, 2),
            'savings_income': round(savings_income, 2),
            'savings_expenses': round(savings_expenses, 2),
        }
    
    def check_budget_status(self, month_key: str = None) -> Dict:
        """Check current budget status against objectives
        
        Args:
            month_key: Filter to specific month (format: YYYY-MM), defaults to current month
        
        Returns:
            Dictionary with budget status for each objective
        """
        if not month_key:
            today = datetime.now()
            month_key = today.strftime("%Y-%m")
        
        transactions = self.db.get_all_transactions()
        month_trans = [t for t in transactions if t.date.startswith(month_key)]
        
        # Get budget objectives
        objectives = self.db.get_budget_objectives()
        
        budget_status = {
            'month': month_key,
            'objectives': [],
            'total_budget': 0.0,
            'total_spent': 0.0,
            'total_remaining': 0.0,
            'alert_count': 0
        }
        
        for obj_id, category, limit in objectives:
            # Calculate spent for this category in current month
            spent = sum(abs(t.amount) for t in month_trans if t.amount < 0 and t.category == category)
            remaining = limit - spent
            percentage = (spent / limit * 100) if limit > 0 else 0
            
            # Determine status
            if percentage >= 100:
                status = 'dépassé'
                alert = True
            elif percentage >= 80:
                status = 'attention'
                alert = True
            else:
                status = 'ok'
                alert = False
            
            if alert:
                budget_status['alert_count'] += 1
            
            budget_status['objectives'].append({
                'id': obj_id,
                'category': category,
                'limit': limit,
                'spent': round(spent, 2),
                'remaining': round(remaining, 2),
                'percentage': round(percentage, 1),
                'status': status,
                'alert': alert
            })
            
            budget_status['total_budget'] += limit
            budget_status['total_spent'] += spent
        
        budget_status['total_remaining'] = round(budget_status['total_budget'] - budget_status['total_spent'], 2)
        budget_status['total_budget'] = round(budget_status['total_budget'], 2)
        budget_status['total_spent'] = round(budget_status['total_spent'], 2)
        
        return budget_status
    
    def get_weekday_analysis(self, start_date: str = None, end_date: str = None) -> Dict:
        """Analyze spending by day of week"""
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        days = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
        weekday_stats = {day: {'count': 0, 'income': 0.0, 'expenses': 0.0, 'net': 0.0} for day in days.values()}
        
        for trans in transactions:
            date_obj = datetime.strptime(trans.date, "%Y-%m-%d")
            weekday_name = days[date_obj.weekday()]
            
            if trans.amount > 0:
                weekday_stats[weekday_name]['income'] += trans.amount
            else:
                weekday_stats[weekday_name]['expenses'] += abs(trans.amount)
            
            weekday_stats[weekday_name]['net'] += trans.amount
            weekday_stats[weekday_name]['count'] += 1
        
        return weekday_stats
    
    def get_top_merchants(self, limit: int = 10, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get top merchants by transaction count and amount"""
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        merchant_stats = defaultdict(lambda: {'count': 0, 'total': 0.0, 'transactions': []})
        
        for trans in transactions:
            merchant = trans.description or "Non spécifié"
            merchant_stats[merchant]['count'] += 1
            merchant_stats[merchant]['total'] += abs(trans.amount)
            merchant_stats[merchant]['transactions'].append({
                'date': trans.date,
                'amount': abs(trans.amount),
                'category': trans.category
            })
        
        # Sort by total amount
        sorted_merchants = sorted(merchant_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:limit]
        
        result = []
        for merchant, stats in sorted_merchants:
            result.append({
                'merchant': merchant,
                'count': stats['count'],
                'total': round(stats['total'], 2),
                'average': round(stats['total'] / stats['count'], 2)
            })
        
        return result
    
    def get_transactions_by_amount_range(self, min_amount: float = 0, max_amount: float = None, 
                                       start_date: str = None, end_date: str = None) -> List[Transaction]:
        """Get transactions within a specific amount range"""
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        filtered = []
        for trans in transactions:
            amount = abs(trans.amount)
            if amount >= min_amount:
                if max_amount is None or amount <= max_amount:
                    filtered.append(trans)
        
        return sorted(filtered, key=lambda x: x.date, reverse=True)
    
    def detect_anomalies(self, start_date: str = None, end_date: str = None, threshold_std: float = 2.0) -> Dict:
        """Detect anomalous transactions based on statistical analysis"""
        if start_date and end_date:
            transactions = self.db.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.db.get_all_transactions()
        
        # Group by category
        category_groups = defaultdict(list)
        for trans in transactions:
            if trans.amount < 0:  # Only expenses
                category_groups[trans.category].append(abs(trans.amount))
        
        anomalies = {
            'by_category': {},
            'unusual_times': [],
            'total_anomalies': 0
        }
        
        # Calculate mean and std dev for each category
        for category, amounts in category_groups.items():
            if len(amounts) < 3:  # Need at least 3 transactions
                continue
            
            mean = sum(amounts) / len(amounts)
            variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
            std_dev = variance ** 0.5
            
            # Find anomalies (values > mean + threshold_std * std_dev)
            threshold = mean + (threshold_std * std_dev)
            anomalous = [a for a in amounts if a > threshold]
            
            if anomalous:
                anomalies['by_category'][category] = {
                    'count': len(anomalous),
                    'mean': round(mean, 2),
                    'std_dev': round(std_dev, 2),
                    'threshold': round(threshold, 2),
                    'anomalies': [round(a, 2) for a in anomalous]
                }
                anomalies['total_anomalies'] += len(anomalous)
        
        # Find unusual times (weekend spending, etc)
        weekend_spending = defaultdict(float)
        for trans in transactions:
            if trans.amount < 0:
                date_obj = datetime.strptime(trans.date, "%Y-%m-%d")
                if date_obj.weekday() >= 5:  # Saturday=5, Sunday=6
                    weekend_spending[trans.category] += abs(trans.amount)
        
        if weekend_spending:
            anomalies['weekend_spending'] = {k: round(v, 2) for k, v in weekend_spending.items()}
        
        return anomalies
    
    def get_category_trends(self, months: int = 6) -> Dict:
        """Get category spending trends over recent months"""
        trends = defaultdict(lambda: [0] * months)
        month_labels = []
        
        for i in range(months - 1, -1, -1):
            month_date = datetime.now() - timedelta(days=30 * i)
            start = month_date.replace(day=1)
            if i == months - 1:
                end = month_date
            else:
                end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_str = start.strftime("%m/%Y")
            month_labels.append(month_str)
            
            transactions = self.db.get_transactions_by_date_range(
                start.strftime("%Y-%m-%d"),
                end.strftime("%Y-%m-%d")
            )
            
            for trans in transactions:
                if trans.amount < 0:
                    trends[trans.category][months - 1 - i] += abs(trans.amount)
        
        result = {}
        for category, values in trends.items():
            result[category] = {
                'values': [round(v, 2) for v in values],
                'trend': 'up' if values[-1] > values[0] else 'down',
                'total': round(sum(values), 2),
                'average': round(sum(values) / len(values), 2)
            }
        
        return {
            'months': month_labels,
            'categories': result
        }
    
    def get_forecast_data(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get recurring transactions for forecasting
        
        Args:
            start_date: Optional start date (YYYY-MM-DD). If None, uses first day of last month
            end_date: Optional end date (YYYY-MM-DD). If None, uses last day of last month
        """
        # Get date range (last month by default)
        today = datetime.now()
        
        if start_date is None:
            last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        else:
            last_month_start = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date is None:
            last_month_end = today.replace(day=1) - timedelta(days=1)
        else:
            last_month_end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get recurring transactions in date range
        transactions = self.db.get_transactions_by_date_range(
            last_month_start.strftime("%Y-%m-%d"),
            last_month_end.strftime("%Y-%m-%d")
        )
        
        # Filter recurring
        recurring = [t for t in transactions if t.recurrence and t.recurrence != "non-récurrent"]
        
        # Group by description
        forecast_dict = defaultdict(lambda: {'amount': 0.0, 'category': '', 'type': '', 'vital': False})
        for trans in recurring:
            key = trans.description
            if key not in forecast_dict:
                forecast_dict[key]['amount'] = abs(trans.amount)
                forecast_dict[key]['category'] = trans.category
                forecast_dict[key]['type'] = trans.recurrence
                forecast_dict[key]['vital'] = trans.vital
        
        # Convert to list
        forecast = []
        for description, data in forecast_dict.items():
            forecast.append({
                'description': description or "Récurrence sans description",
                'amount': round(data['amount'], 2),
                'category': data['category'],
                'type': data['type'],
                'vital': data['vital'],
                'modified': round(data['amount'], 2)
            })
        
        return sorted(forecast, key=lambda x: x['amount'], reverse=True)
    
    def export_monthly_report(self, output_path: str, start_date: str = None, end_date: str = None) -> bool:
        """Export monthly report to PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.units import inch
            from datetime import datetime
            
            # Get data
            if start_date and end_date:
                transactions = self.db.get_transactions_by_date_range(start_date, end_date)
            else:
                transactions = self.db.get_all_transactions()
            
            stats = self.get_statistics(start_date, end_date)
            monthly_stats = self.get_monthly_statistics()
            
            # Create PDF
            doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            # Title
            title = Paragraph("📊 Rapport Financier Mensuel", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Summary section
            summary_data = [
                ["Métrique", "Valeur"],
                ["Revenus", f"€{stats['total_income']:.2f}"],
                ["Dépenses", f"€{stats['total_expenses']:.2f}"],
                ["Bilan Net", f"€{stats['net']:.2f}"],
                ["Transactions", str(stats['total_transactions'])],
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Monthly comparison
            subtitle = Paragraph("Comparaison Mensuelle", styles['Heading2'])
            elements.append(subtitle)
            elements.append(Spacer(1, 0.1*inch))
            
            monthly_data = [["Mois", "Revenus", "Dépenses", "Bilan", "Ratio"]]
            for month, data in list(monthly_stats.items())[-6:]:  # Last 6 months
                monthly_data.append([
                    month,
                    f"€{data['income']:.0f}",
                    f"€{data['expenses']:.0f}",
                    f"€{data['net']:.0f}",
                    f"{data['ratio']:.1f}%"
                ])
            
            monthly_table = Table(monthly_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
            monthly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
            ]))
            elements.append(monthly_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Category breakdown
            subtitle = Paragraph("Top 10 Catégories", styles['Heading2'])
            elements.append(subtitle)
            elements.append(Spacer(1, 0.1*inch))
            
            category_dict = defaultdict(float)
            for trans in transactions:
                if trans.amount < 0:
                    category_dict[trans.category] += abs(trans.amount)
            
            cat_data = [["Catégorie", "Total", "%"]]
            total_expenses = sum(category_dict.values())
            for cat, amount in sorted(category_dict.items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                cat_data.append([cat, f"€{amount:.2f}", f"{percentage:.1f}%"])
            
            cat_table = Table(cat_data, colWidths=[3*inch, 1.5*inch, 1*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
            ]))
            elements.append(cat_table)
            
            # Footer
            elements.append(Spacer(1, 0.2*inch))
            footer_text = f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
            elements.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(elements)
            return True
        
        except ImportError:
            print("❌ reportlab not installed. Run: pip install reportlab")
            return False
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return False

