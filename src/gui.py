"""
GUI module - Graphical User Interface with Tkinter
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from src.database import Database
from src.importer import CSVImporter
from src.categorizer import Categorizer
from src.analyzer import Analyzer


class BankAnalyzerGUI:
    """Main GUI application for Bank Analyzer"""
    
    # Color scheme
    COLORS = {
        'primary': '#2C3E50',      # Dark blue-grey
        'secondary': '#3498DB',    # Blue
        'success': '#27AE60',      # Green
        'warning': '#E74C3C',      # Red
        'light': '#ECF0F1',        # Light grey
        'text': '#2C3E50',         # Dark text
    }
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("Bank Analyzer 🏦")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Set background color
        self.root.configure(bg=self.COLORS['primary'])
        
        # Configure ttk style
        self.setup_styles()
        
        # Initialize database
        self.db = Database()
        self.categorizer = Categorizer(self.db)
        self.analyzer = Analyzer(self.db)
        self.importer = CSVImporter()
        
        # Initialize categories
        self.categorizer.init_categories()
        
        # Create header
        self.create_header()
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.import_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.categories_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.budget_tab = ttk.Frame(self.notebook)
        self.statistics_tab = ttk.Frame(self.notebook)
        self.forecast_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_tab, text="📊 Tableau de Bord")
        self.notebook.add(self.import_tab, text="📥 Import")
        self.notebook.add(self.transactions_tab, text="📋 Transactions")
        self.notebook.add(self.analysis_tab, text="📈 Analyses")
        self.notebook.add(self.categories_tab, text="📂 Catégories")
        self.notebook.add(self.report_tab, text="� Rapports")
        self.notebook.add(self.budget_tab, text="💰 Budget")
        self.notebook.add(self.statistics_tab, text="📊 Statistiques")
        self.notebook.add(self.forecast_tab, text="🔮 Prévisionnel")
        self.notebook.add(self.settings_tab, text="⚙️ Paramètres")
        
        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_import_tab()
        self.setup_analysis_tab()
        self.setup_transactions_tab()
        self.setup_categories_tab()
        self.setup_report_tab()
        self.setup_budget_tab()
        self.setup_statistics_tab()
        self.setup_forecast_tab()
        self.setup_settings_tab()
        
        # Create status bar
        self.create_status_bar()
        
        # Initial data load
        self.update_stats_display()
        self.refresh_transactions()
        self.refresh_categories_tree()
        self.refresh_rules_display()

    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for different elements
        style.configure('TFrame', background=self.COLORS['light'])
        style.configure('TLabel', background=self.COLORS['light'], foreground=self.COLORS['text'])
        style.configure('TButton', font=('Arial', 10))
        style.configure('TNotebook.Tab', font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground=self.COLORS['text'])
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), foreground=self.COLORS['secondary'])
        
        # Configure button styles
        style.map('TButton',
                  foreground=[('pressed', self.COLORS['light']),
                             ('active', self.COLORS['light'])],
                  background=[('pressed', self.COLORS['secondary']),
                             ('active', '#2980B9')])
    
    def create_header(self):
        """Create a header section"""
        header = tk.Frame(self.root, bg=self.COLORS['primary'], height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        # Logo and title
        logo_label = tk.Label(header, text="🏦", font=("Arial", 40), 
                             bg=self.COLORS['primary'], fg=self.COLORS['secondary'])
        logo_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        title_label = tk.Label(header, text="Bank Analyzer", 
                              font=("Arial", 24, "bold"),
                              bg=self.COLORS['primary'], fg=self.COLORS['light'])
        title_label.pack(side=tk.LEFT, padx=0, pady=10)
        
        subtitle_label = tk.Label(header, text="Analysez vos dépenses bancaires",
                                 font=("Arial", 11),
                                 bg=self.COLORS['primary'], fg='#BDC3C7')
        subtitle_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Quick stats on the right
        stats_frame = tk.Frame(header, bg=self.COLORS['primary'])
        stats_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        trans_count = len(self.db.get_all_transactions())
        stats_label = tk.Label(stats_frame, 
                              text=f"📊 {trans_count} transactions",
                              font=("Arial", 10),
                              bg=self.COLORS['primary'], fg=self.COLORS['light'])
        stats_label.pack()
        
        self.stats_label = stats_label  # Store reference for updates
    
    def setup_dashboard_tab(self):
        """Setup the dashboard tab with key metrics"""
        frame = ttk.Frame(self.dashboard_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="📊 Tableau de Bord Financier", style='Title.TLabel')
        title.pack(pady=15)
        
        # Main container with scrollbar
        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.dashboard_frame = ttk.Frame(canvas)
        
        self.dashboard_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.dashboard_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh button
        refresh_btn = tk.Button(frame, text="🔄 Actualiser le Tableau de Bord",
                               command=self.refresh_dashboard,
                               bg=self.COLORS['secondary'], fg=self.COLORS['light'],
                               font=("Arial", 11, "bold"),
                               padx=20, pady=8, cursor="hand2")
        refresh_btn.pack(pady=10, after=title)
        
        # Initial refresh
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Refresh dashboard with latest data"""
        # Clear previous content
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get dashboard data
            summary = self.analyzer.get_dashboard_summary()
            monthly = self.analyzer.get_monthly_statistics()
            savings = self.analyzer.get_savings_analysis()
            
            # 1. KPI Cards Section
            kpi_frame = ttk.LabelFrame(self.dashboard_frame, text="📈 Indicateurs Clés (Mois Actuel)", padding=15)
            kpi_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Grid of KPI cards
            cards_grid = ttk.Frame(kpi_frame)
            cards_grid.pack(fill=tk.X)
            
            # Card 1: Monthly Income
            self.create_kpi_card(cards_grid, "💰 Revenus", f"€{summary['monthly_income']:.2f}", 
                                "#27AE60", 0, 0)
            
            # Card 2: Monthly Expenses
            self.create_kpi_card(cards_grid, "💸 Dépenses", f"€{summary['monthly_expenses']:.2f}",
                                "#E74C3C", 0, 1)
            
            # Card 3: Monthly Net
            net_color = "#27AE60" if summary['monthly_net'] >= 0 else "#E74C3C"
            self.create_kpi_card(cards_grid, "📊 Bilan Net", f"€{summary['monthly_net']:.2f}",
                                net_color, 0, 2)
            
            # Card 4: Status
            status_emoji = "✅" if summary['status'] == 'healthy' else ("⚠️" if summary['status'] == 'warning' else "❌")
            status_text = "Bon" if summary['status'] == 'healthy' else ("Attention" if summary['status'] == 'warning' else "Déficit")
            status_color = "#27AE60" if summary['status'] == 'healthy' else ("#F39C12" if summary['status'] == 'warning' else "#E74C3C")
            self.create_kpi_card(cards_grid, "🎯 Statut", f"{status_emoji} {status_text}",
                                status_color, 1, 0)
            
            # Card 5: Recurring
            self.create_kpi_card(cards_grid, "🔄 Récurrent/mois", f"€{summary['recurring_monthly']:.2f}",
                                "#3498DB", 1, 1)
            
            # Card 6: Transactions
            self.create_kpi_card(cards_grid, "📝 Transactions", f"{summary['transaction_count']}",
                                "#9B59B6", 1, 2)
            
            # 2. Monthly Trend Chart
            trend_chart = self.analyzer.get_monthly_trend_chart()
            if trend_chart:
                chart_frame = ttk.LabelFrame(self.dashboard_frame, text="📈 Tendance Mensuelle", padding=10)
                chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                self.add_chart_to_frame(chart_frame, trend_chart, "")
            
            # 3. Savings Analysis
            savings_frame = ttk.LabelFrame(self.dashboard_frame, text="💾 Analyse Épargne", padding=15)
            savings_frame.pack(fill=tk.X, padx=10, pady=10)
            
            savings_text = f"""
📊 Bilan Externe: €{savings['external_balance']:.2f}
💾 Bilan Épargne: €{savings['savings_balance']:.2f}

💰 Revenus Externes: €{savings['external_income']:.2f}
💰 Revenus Épargne: €{savings['savings_income']:.2f}

💸 Dépenses Externes: €{savings['external_expenses']:.2f}
💸 Dépenses Épargne: €{savings['savings_expenses']:.2f}

📈 Utilisation de l'épargne: {savings['savings_usage_ratio']:.1f}%
"""
            ttk.Label(savings_frame, text=savings_text, font=("Courier", 10), justify=tk.LEFT).pack(anchor=tk.W)
            
            # 4. Top 5 Months
            if monthly:
                months_frame = ttk.LabelFrame(self.dashboard_frame, text="📅 Derniers Mois", padding=15)
                months_frame.pack(fill=tk.X, padx=10, pady=10)
                
                months_text = "Mois | Revenus | Dépenses | Bilan | Santé\n"
                months_text += "─" * 55 + "\n"
                
                for i, (month, stats) in enumerate(list(monthly.items())[:6]):
                    health = "✅" if stats['net'] >= 0 else "❌"
                    months_text += f"{month} | €{stats['income']:7.2f} | €{stats['expenses']:7.2f} | €{stats['net']:7.2f} | {health}\n"
                
                ttk.Label(months_frame, text=months_text, font=("Courier", 9), justify=tk.LEFT).pack(anchor=tk.W)
            
            self.update_status("Tableau de bord actualisé")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'actualisation du tableau de bord:\n{str(e)}")
            self.update_status("Erreur")
    
    def create_kpi_card(self, parent, title, value, color, row, col):
        """Create a KPI card widget"""
        card = tk.Frame(parent, bg=color, height=100, width=150)
        card.grid(row=row, column=col, padx=10, pady=10, sticky=tk.NSEW)
        card.pack_propagate(False)
        
        ttk.Label(card, text=title, font=("Arial", 9), background=color, foreground="white").pack(pady=(10, 0))
        ttk.Label(card, text=value, font=("Arial", 16, "bold"), background=color, foreground="white").pack(pady=10)
    
    def setup_analysis_tab(self):
        """Setup the analysis tab for detailed monthly and savings analysis"""
        frame = ttk.Frame(self.analysis_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="📈 Analyses Détaillées", style='Title.TLabel')
        title.pack(pady=15)
        
        # Main container with scrollbar
        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.analysis_frame = ttk.Frame(canvas)
        
        self.analysis_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.analysis_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh button
        refresh_btn = tk.Button(frame, text="🔄 Actualiser les Analyses",
                               command=self.refresh_analysis,
                               bg=self.COLORS['secondary'], fg=self.COLORS['light'],
                               font=("Arial", 11, "bold"),
                               padx=20, pady=8, cursor="hand2")
        refresh_btn.pack(pady=10, after=title)
        
        # Initial refresh
        self.refresh_analysis()
    
    def refresh_analysis(self):
        """Refresh analysis tab with detailed reports"""
        # Clear previous content
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        
        try:
            monthly = self.analyzer.get_monthly_statistics()
            savings = self.analyzer.get_savings_analysis()
            
            # 1. Monthly Comparison Table
            monthly_frame = ttk.LabelFrame(self.analysis_frame, text="📅 Historique Mensuel (12 derniers mois)", padding=15)
            monthly_frame.pack(fill=tk.X, padx=10, pady=10)
            
            months_sorted = sorted(monthly.items(), reverse=True)[:12]
            
            table_text = "Mois      | Revenus   | Dépenses  | Bilan    | Ratio | Statut\n"
            table_text += "─" * 70 + "\n"
            
            for month_key, stats in months_sorted:
                health = "✅" if stats['net'] >= 0 else "❌"
                expense_ratio = f"{stats['ratio']:.2f}" if stats['ratio'] >= 0 else "N/A"
                table_text += f"{month_key} │ €{stats['income']:7.2f} │ €{stats['expenses']:7.2f} │ €{stats['net']:7.2f} │ {expense_ratio} │ {health}\n"
            
            ttk.Label(monthly_frame, text=table_text, font=("Courier", 9), justify=tk.LEFT).pack(anchor=tk.W)
            
            # 2. Monthly Statistics
            if months_sorted:
                first_6 = [s for _, s in months_sorted[:6]]
                avg_income = sum(s['income'] for s in first_6) / len(first_6) if first_6 else 0
                avg_expenses = sum(s['expenses'] for s in first_6) / len(first_6) if first_6 else 0
                avg_net = avg_income - avg_expenses
                
                stats_frame = ttk.LabelFrame(self.analysis_frame, text="📊 Moyenne des 6 derniers mois", padding=15)
                stats_frame.pack(fill=tk.X, padx=10, pady=10)
                
                stats_text = f"""
💰 Revenus moyens: €{avg_income:.2f}
💸 Dépenses moyennes: €{avg_expenses:.2f}
📈 Bilan moyen: €{avg_net:.2f}
📊 Ratio dépenses/revenus: {(avg_expenses/avg_income*100):.1f}%
"""
                ttk.Label(stats_frame, text=stats_text, font=("Courier", 10), justify=tk.LEFT).pack(anchor=tk.W)
            
            # 3. Savings Detailed Analysis
            savings_frame = ttk.LabelFrame(self.analysis_frame, text="💾 Analyse Détaillée Épargne/Externe", padding=15)
            savings_frame.pack(fill=tk.X, padx=10, pady=10)
            
            savings_text = f"""
╔ BILAN GLOBAL
│
├─ Bilan Externe: €{savings['external_balance']:.2f}
│  ├─ Revenus: €{savings['external_income']:.2f}
│  ├─ Dépenses: €{savings['external_expenses']:.2f}
│
├─ Bilan Épargne: €{savings['savings_balance']:.2f}
│  ├─ Revenus: €{savings['savings_income']:.2f}
│  ├─ Dépenses: €{savings['savings_expenses']:.2f}
│
├─ Utilisation Épargne: {savings['savings_usage_ratio']:.1f}%
│
└─ Transactions:
   ├─ Externes: {savings['external_transactions']}
   └─ De l'épargne: {savings['savings_transactions']}
"""
            ttk.Label(savings_frame, text=savings_text, font=("Courier", 9), justify=tk.LEFT).pack(anchor=tk.W)
            
            # 4. Trend Analysis
            trend_chart = self.analyzer.get_monthly_trend_chart()
            if trend_chart:
                chart_frame = ttk.LabelFrame(self.analysis_frame, text="📈 Tendance du Bilan Net", padding=10)
                chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                self.add_chart_to_frame(chart_frame, trend_chart, "")
            
            self.update_status("Analyses actualisées")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du calcul des analyses:\n{str(e)}")
            self.update_status("Erreur")
    
    def setup_budget_tab(self):
        """Setup budget objectives tracking tab"""
        frame = ttk.Frame(self.budget_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="💰 Gestion des Objectifs Budgétaires", style='Title.TLabel')
        title.pack(pady=15)
        
        # Button frame for actions
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        add_btn = tk.Button(button_frame, text="➕ Ajouter un Objectif",
                           command=self.add_budget_objective,
                           bg=self.COLORS['success'], fg=self.COLORS['light'],
                           font=("Arial", 10, "bold"),
                           padx=15, pady=8, cursor="hand2")
        add_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(button_frame, text="🔄 Actualiser",
                               command=self.refresh_budget_tab,
                               bg=self.COLORS['secondary'], fg=self.COLORS['light'],
                               font=("Arial", 10, "bold"),
                               padx=15, pady=8, cursor="hand2")
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Budget status frame
        status_frame = ttk.LabelFrame(frame, text="📊 Statut Budgétaire du Mois", padding=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.budget_status_label = ttk.Label(status_frame, text="", font=("Courier", 10), justify=tk.LEFT)
        self.budget_status_label.pack(anchor=tk.W)
        
        # Budget objectives table
        table_frame = ttk.LabelFrame(frame, text="📋 Objectifs Budgétaires", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview
        columns = ("Catégorie", "Limite", "Dépensé", "Restant", "Progression", "Statut")
        self.budget_tree = ttk.Treeview(table_frame, columns=columns, height=15, show="headings")
        
        self.budget_tree.column("Catégorie", anchor=tk.W, width=120)
        self.budget_tree.column("Limite", anchor=tk.E, width=80)
        self.budget_tree.column("Dépensé", anchor=tk.E, width=80)
        self.budget_tree.column("Restant", anchor=tk.E, width=80)
        self.budget_tree.column("Progression", anchor=tk.CENTER, width=100)
        self.budget_tree.column("Statut", anchor=tk.CENTER, width=80)
        
        self.budget_tree.heading("Catégorie", text="📂 Catégorie")
        self.budget_tree.heading("Limite", text="💰 Limite")
        self.budget_tree.heading("Dépensé", text="💸 Dépensé")
        self.budget_tree.heading("Restant", text="📈 Restant")
        self.budget_tree.heading("Progression", text="📊 Progression")
        self.budget_tree.heading("Statut", text="🎯 Statut")
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.budget_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.budget_tree.xview)
        self.budget_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.budget_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Right-click menu
        self.budget_tree.bind("<Button-3>", self.show_budget_context_menu)
        
        # Initial refresh
        self.refresh_budget_tab()
    
    def refresh_budget_tab(self):
        """Refresh budget tab"""
        # Clear tree
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        try:
            # Get budget status
            budget_status = self.analyzer.check_budget_status()
            
            # Update status label
            status_text = f"""Mois: {budget_status['month']}
Budget Total: €{budget_status['total_budget']:.2f} | Dépensé: €{budget_status['total_spent']:.2f} | Restant: €{budget_status['total_remaining']:.2f}
Alertes: {budget_status['alert_count']} objectif(s) dépassé(s) ou en attention
"""
            self.budget_status_label.config(text=status_text)
            
            # Add objectives to tree
            for obj in budget_status['objectives']:
                progress_bar = "█" * int(obj['percentage'] // 10) + "░" * (10 - int(obj['percentage'] // 10))
                progress_text = f"{progress_bar} {obj['percentage']:.0f}%"
                
                tag = ""
                if obj['status'] == 'dépassé':
                    tag = "alert_red"
                elif obj['status'] == 'attention':
                    tag = "alert_yellow"
                else:
                    tag = "ok"
                
                self.budget_tree.insert(
                    "",
                    "end",
                    values=(obj['category'], f"€{obj['limit']:.2f}", f"€{obj['spent']:.2f}",
                           f"€{obj['remaining']:.2f}", progress_text, obj['status']),
                    tags=(tag,)
                )
            
            # Configure tags
            self.budget_tree.tag_configure("ok", foreground="#27AE60")
            self.budget_tree.tag_configure("alert_yellow", foreground="#F39C12")
            self.budget_tree.tag_configure("alert_red", foreground="#E74C3C")
            
            self.update_status("Budget actualisé")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du calcul du budget:\n{str(e)}")
            self.update_status("Erreur")
    
    def add_budget_objective(self):
        """Add a new budget objective"""
        # Get all categories
        all_categories = self.categorizer.get_all_categories_with_parent()
        categories = [c['name'] for c in all_categories if c['parent_id'] is not None]  # Only subcategories
        
        if not categories:
            messagebox.showwarning("Attention", "Aucune catégorie disponible")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un Objectif Budgétaire")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Category selection
        ttk.Label(dialog, text="Catégorie:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        category_var = tk.StringVar(value=categories[0] if categories else "")
        category_combo = ttk.Combobox(dialog, textvariable=category_var, values=categories, state="readonly", width=30)
        category_combo.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=10)
        
        # Limit amount
        ttk.Label(dialog, text="Limite (€):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        limit_var = tk.StringVar(value="100")
        limit_entry = ttk.Entry(dialog, textvariable=limit_var, width=30)
        limit_entry.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=10)
        
        # Buttons
        def save():
            try:
                category = category_var.get()
                limit = float(limit_var.get())
                if limit <= 0:
                    messagebox.showerror("Erreur", "La limite doit être positive")
                    return
                
                self.db.add_budget_objective(category, limit)
                messagebox.showinfo("Succès", f"Objectif ajouté pour {category}: €{limit:.2f}")
                self.refresh_budget_tab()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique valide")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="✅ Ajouter", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.columnconfigure(1, weight=1)
    
    def show_budget_context_menu(self, event):
        """Show context menu on right-click in budget tree"""
        row_id = self.budget_tree.identify_row(event.y)
        if row_id:
            self.budget_tree.selection_set(row_id)
            
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="✏️ Modifier la limite", command=lambda: self.edit_budget_objective(row_id))
            menu.add_command(label="🗑️ Supprimer", command=lambda: self.delete_budget_objective(row_id))
            
            menu.post(event.x_root, event.y_root)
    
    def edit_budget_objective(self, row_id):
        """Edit a budget objective"""
        # Get item values
        values = self.budget_tree.item(row_id, 'values')
        category = values[0]
        current_limit = float(values[1].replace('€', '').strip())
        
        # Get objectives to find ID
        objectives = self.db.get_budget_objectives()
        obj_id = None
        for oid, cat, _ in objectives:
            if cat == category:
                obj_id = oid
                break
        
        if not obj_id:
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Modifier - {category}")
        dialog.geometry("350x120")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Nouvelle limite (€):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        limit_var = tk.StringVar(value=str(current_limit))
        limit_entry = ttk.Entry(dialog, textvariable=limit_var, width=25)
        limit_entry.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=10)
        
        def save():
            try:
                new_limit = float(limit_var.get())
                if new_limit <= 0:
                    messagebox.showerror("Erreur", "La limite doit être positive")
                    return
                
                self.db.update_budget_objective(obj_id, new_limit)
                messagebox.showinfo("Succès", f"Limite mise à jour: €{new_limit:.2f}")
                self.refresh_budget_tab()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique valide")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="✅ Sauvegarder", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.columnconfigure(1, weight=1)
    
    def delete_budget_objective(self, row_id):
        """Delete a budget objective"""
        values = self.budget_tree.item(row_id, 'values')
        category = values[0]
        
        if messagebox.askyesno("Confirmation", f"Supprimer l'objectif pour '{category}' ?"):
            objectives = self.db.get_budget_objectives()
            for oid, cat, _ in objectives:
                if cat == category:
                    self.db.delete_budget_objective(oid)
                    self.refresh_budget_tab()
                    messagebox.showinfo("Succès", "Objectif supprimé")
                    break
    
    def setup_forecast_tab(self):
        """Setup forecast/prévisionnel tab"""
        frame = ttk.Frame(self.forecast_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="🔮 Analyse des Récurrences", style='Title.TLabel')
        title.pack(pady=15)
        
        # Info label
        info_text = "Analyser les transactions récurrentes sur une période donnée - Modifiez les montants pour des prévisions"
        ttk.Label(frame, text=info_text, font=("Arial", 9, "italic")).pack()
        
        # Date filter frame
        date_filter_frame = ttk.LabelFrame(frame, text="📅 Filtrer par date", padding=10)
        date_filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(date_filter_frame, text="Du:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.forecast_start_date = DateEntry(date_filter_frame, width=15, background='darkblue', 
                                             foreground='white', borderwidth=2,
                                             year=(datetime.now().replace(day=1) - timedelta(days=1)).year,
                                             month=(datetime.now().replace(day=1) - timedelta(days=1)).month,
                                             day=1)
        self.forecast_start_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(date_filter_frame, text="Au:").grid(row=0, column=2, sticky=tk.W, padx=15, pady=5)
        last_day = (datetime.now().replace(day=1) - timedelta(days=1))
        self.forecast_end_date = DateEntry(date_filter_frame, width=15, background='darkblue',
                                           foreground='white', borderwidth=2,
                                           year=last_day.year,
                                           month=last_day.month,
                                           day=last_day.day)
        self.forecast_end_date.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        refresh_btn = tk.Button(button_frame, text="🔄 Actualiser",
                               command=self.refresh_forecast,
                               bg=self.COLORS['secondary'], fg=self.COLORS['light'],
                               font=("Arial", 10, "bold"), padx=15, pady=8, cursor="hand2")
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(button_frame, text="🔁 Réinitialiser Prévisions",
                             command=self.reset_forecast,
                             bg=self.COLORS['warning'], fg=self.COLORS['light'],
                             font=("Arial", 10, "bold"), padx=15, pady=8, cursor="hand2")
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Report button
        report_btn = tk.Button(button_frame, text="📄 Générer Rapport",
                              command=self.generate_forecast_report,
                              bg=self.COLORS['success'], fg=self.COLORS['light'],
                              font=("Arial", 10, "bold"), padx=15, pady=8, cursor="hand2")
        report_btn.pack(side=tk.LEFT, padx=5)
        
        # Report frame (for text display)
        report_frame = ttk.LabelFrame(frame, text="📋 Rapport Détaillé", padding=10)
        report_frame.pack(fill=tk.BOTH, expand=False, pady=10, padx=0)
        
        self.forecast_report_text = tk.Text(report_frame, height=8, width=100, wrap=tk.WORD, font=("Courier", 9))
        self.forecast_report_text.pack(fill=tk.BOTH, expand=True)
        
        # Summary frame
        summary_frame = ttk.LabelFrame(frame, text="📊 Résumé", padding=10)
        summary_frame.pack(fill=tk.X, pady=10)
        
        self.forecast_summary_label = ttk.Label(summary_frame, text="", font=("Courier", 10), justify=tk.LEFT)
        self.forecast_summary_label.pack(anchor=tk.W)
        
        # Table frame
        table_frame = ttk.LabelFrame(frame, text="📋 Récurrences Prévues", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview with editable cells
        columns = ("Description", "Catégorie", "Récurrence", "Vital", "Montant Original", "Prévision")
        self.forecast_tree = ttk.Treeview(table_frame, columns=columns, height=15, show="headings")
        
        self.forecast_tree.column("Description", anchor=tk.W, width=180)
        self.forecast_tree.column("Catégorie", anchor=tk.CENTER, width=100)
        self.forecast_tree.column("Récurrence", anchor=tk.CENTER, width=90)
        self.forecast_tree.column("Vital", anchor=tk.CENTER, width=50)
        self.forecast_tree.column("Montant Original", anchor=tk.E, width=110)
        self.forecast_tree.column("Prévision", anchor=tk.E, width=110)
        
        for col in columns:
            self.forecast_tree.heading(col, text=col)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.forecast_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.forecast_tree.xview)
        self.forecast_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.forecast_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to edit
        self.forecast_tree.bind("<Double-1>", self.edit_forecast_cell)
        
        # Store forecast data
        self.forecast_data = {}
        
        # Initial refresh
        self.refresh_forecast()
    
    def refresh_forecast(self):
        """Refresh forecast display"""
        # Clear tree
        for item in self.forecast_tree.get_children():
            self.forecast_tree.delete(item)
        
        try:
            # Get date range from widgets
            start_date = self.forecast_start_date.get_date().strftime("%Y-%m-%d")
            end_date = self.forecast_end_date.get_date().strftime("%Y-%m-%d")
            
            forecast_data = self.analyzer.get_forecast_data(start_date, end_date)
            self.forecast_data = {i: item for i, item in enumerate(forecast_data)}
            
            total_original = 0.0
            total_modified = 0.0
            vital_count = 0
            vital_amount = 0.0
            
            for i, item in enumerate(forecast_data):
                total_original += item['amount']
                total_modified += item['modified']
                
                # Count vital transactions
                if item.get('vital'):
                    vital_count += 1
                    vital_amount += item['amount']
                
                vital_indicator = "⭐" if item.get('vital') else ""
                
                self.forecast_tree.insert(
                    "",
                    "end",
                    iid=str(i),
                    values=(
                        item['description'][:50],
                        item['category'],
                        item['type'],
                        vital_indicator,
                        f"€{item['amount']:.2f}",
                        f"€{item['modified']:.2f}"
                    )
                )
            
            # Update summary
            difference = total_modified - total_original
            diff_text = f"+€{difference:.2f}" if difference > 0 else f"€{difference:.2f}"
            summary = f"Total Original: €{total_original:.2f} | Total Prévisionnel: €{total_modified:.2f} | Différence: {diff_text}\n"
            summary += f"Transactions Vitales: {vital_count} | Montant Vital: €{vital_amount:.2f}"
            self.forecast_summary_label.config(text=summary)
            
            # Generate report
            self.generate_forecast_report()
            
            self.update_status("Prévisions actualisées")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des prévisions:\n{str(e)}")
    
    def generate_forecast_report(self):
        """Generate detailed forecast report"""
        try:
            # Clear report
            self.forecast_report_text.config(state=tk.NORMAL)
            self.forecast_report_text.delete("1.0", tk.END)
            
            if not self.forecast_data:
                return
            
            # Header
            start_date = self.forecast_start_date.get_date().strftime("%d/%m/%Y")
            end_date = self.forecast_end_date.get_date().strftime("%d/%m/%Y")
            report = f"{'='*120}\n"
            report += f"📋 RAPPORT DÉTAILLÉ DES RÉCURRENCES\n"
            report += f"Période: {start_date} → {end_date}\n"
            report += f"{'='*120}\n\n"
            
            # Aggregate data
            by_category = {}
            vital_total = 0.0
            non_vital_total = 0.0
            vital_count = 0
            non_vital_count = 0
            
            for item in self.forecast_data.values():
                cat = item['category']
                if cat not in by_category:
                    by_category[cat] = {'vital': 0.0, 'non_vital': 0.0, 'items': []}
                
                if item.get('vital'):
                    by_category[cat]['vital'] += item['amount']
                    vital_total += item['amount']
                    vital_count += 1
                else:
                    by_category[cat]['non_vital'] += item['amount']
                    non_vital_total += item['amount']
                    non_vital_count += 1
                
                by_category[cat]['items'].append(item)
            
            # Summary section
            report += f"📊 RÉSUMÉ GLOBAL\n"
            report += f"{'-'*120}\n"
            report += f"  Total Transactions Vitales:      {vital_count:3d}  |  €{vital_total:10.2f}\n"
            report += f"  Total Transactions Normales:     {non_vital_count:3d}  |  €{non_vital_total:10.2f}\n"
            report += f"  TOTAL GÉNÉRAL:                  {vital_count + non_vital_count:3d}  |  €{vital_total + non_vital_total:10.2f}\n"
            report += f"\n"
            
            # By category section
            report += f"📂 DÉTAIL PAR CATÉGORIE\n"
            report += f"{'-'*120}\n"
            
            for category in sorted(by_category.keys()):
                data = by_category[category]
                total_cat = data['vital'] + data['non_vital']
                vital_pct = (data['vital'] / total_cat * 100) if total_cat > 0 else 0
                
                report += f"\n  {category.upper()}\n"
                report += f"  {'─'*50}\n"
                report += f"    ⭐ Vitales:     €{data['vital']:10.2f}  ({vital_pct:5.1f}%)\n"
                report += f"    ◌ Normales:    €{data['non_vital']:10.2f}  ({100-vital_pct:5.1f}%)\n"
                report += f"    Total:         €{total_cat:10.2f}\n"
            
            report += f"\n{'='*120}\n"
            
            # Display report
            self.forecast_report_text.insert("1.0", report)
            self.forecast_report_text.config(state=tk.DISABLED)
        
        except Exception as e:
            pass  # Silently fail if report generation fails
    
    def edit_forecast_cell(self, event):
        """Edit forecast cell on double-click"""
        item = self.forecast_tree.selection()[0]
        col = self.forecast_tree.identify_column(event.x)
        
        # Only allow editing of last column (index 4)
        if col != "#5":
            return
        
        try:
            idx = int(item)
            old_value = self.forecast_tree.item(item, 'values')[4].replace('€', '').strip()
            
            # Create edit dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Modifier Prévision")
            dialog.geometry("300x120")
            dialog.resizable(False, False)
            
            ttk.Label(dialog, text=f"Description: {self.forecast_data[idx]['description'][:40]}").pack(padx=10, pady=10)
            ttk.Label(dialog, text="Nouveau montant (€):").pack(padx=10, pady=5)
            
            entry = ttk.Entry(dialog, width=20)
            entry.insert(0, old_value)
            entry.pack(padx=10, pady=5)
            entry.focus()
            
            def save():
                try:
                    new_value = float(entry.get())
                    if new_value < 0:
                        messagebox.showerror("Erreur", "Le montant doit être positif")
                        return
                    
                    self.forecast_data[idx]['modified'] = new_value
                    self.refresh_forecast()
                    dialog.destroy()
                except ValueError:
                    messagebox.showerror("Erreur", "Veuillez entrer un nombre valide")
            
            ttk.Button(dialog, text="✅ Sauvegarder", command=save).pack(pady=10)
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'édition: {str(e)}")
    
    def reset_forecast(self):
        """Reset forecast to original values"""
        if messagebox.askyesno("Confirmation", "Réinitialiser toutes les prévisions aux montants originaux ?"):
            for item in self.forecast_data.values():
                item['modified'] = item['amount']
            self.refresh_forecast()
    
    def create_status_bar(self):
        """Create a status bar at the bottom"""
        status_bar = tk.Frame(self.root, bg=self.COLORS['primary'], height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        self.status_text = tk.Label(status_bar, text="Prêt", 
                                   font=("Arial", 9),
                                   bg=self.COLORS['primary'], fg=self.COLORS['light'])
        self.status_text.pack(side=tk.LEFT, padx=10, pady=5)
    
    def update_status(self, message):
        """Update status bar message"""
        if hasattr(self, 'status_text'):
            self.status_text.config(text=message)
            self.root.update()
    
    def update_stats_display(self):
        """Update header stats"""
        trans_count = len(self.db.get_all_transactions())
        self.stats_label.config(text=f"📊 {trans_count} transactions")

    
    def setup_import_tab(self):
        """Setup the import tab"""
        frame = ttk.Frame(self.import_tab, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="📥 Importer un fichier CSV", style='Title.TLabel')
        title.pack(pady=20)
        
        # Instructions
        instructions = ttk.Label(frame, 
                                text="Sélectionnez un fichier CSV depuis votre banque pour importer les transactions",
                                font=("Arial", 10),
                                foreground="gray")
        instructions.pack(pady=10)
        
        # File selection
        file_frame = ttk.LabelFrame(frame, text="📂 Sélectionner un fichier", padding=15)
        file_frame.pack(fill=tk.X, pady=15)
        
        self.file_label = ttk.Label(file_frame, text="Aucun fichier sélectionné", foreground="gray", font=("Arial", 11))
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="🔍 Parcourir...", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # Import section
        import_frame = tk.Frame(frame, bg=self.COLORS['light'])
        import_frame.pack(fill=tk.X, pady=20)
        
        import_btn = tk.Button(import_frame, text="📥 Importer les données", 
                              command=self.import_file,
                              bg=self.COLORS['success'], fg=self.COLORS['light'],
                              font=("Arial", 12, "bold"),
                              height=2,
                              cursor="hand2")
        import_btn.pack(fill=tk.X)
        
        # Results area
        results_frame = ttk.LabelFrame(frame, text="📊 Résultats de l'importation", padding=15)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.import_text = tk.Text(results_frame, height=15, 
                                   yscrollcommand=scrollbar.set,
                                   font=("Courier", 10),
                                   bg='#f8f9fa', fg=self.COLORS['text'])
        self.import_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.import_text.yview)
        
        self.file_path = None
    
    def browse_file(self):
        """Browse for a CSV file"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            filename = Path(file_path).name
            size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            self.file_label.config(text=f"✓ {filename} ({size_mb:.2f} MB)", foreground=self.COLORS['success'])
            self.update_status(f"Fichier sélectionné: {filename}")
    
    def import_file(self):
        """Import the selected CSV file"""
        if not self.file_path:
            messagebox.showwarning("Attention", "Sélectionne un fichier d'abord")
            return
        
        self.import_text.delete(1.0, tk.END)
        self.import_text.insert(tk.END, "⏳ Importation en cours...\n")
        self.root.update()
        
        try:
            transactions, warnings, skipped_count = self.importer.import_file(self.file_path, self.db)
            
            imported_count = len(transactions)
            
            self.import_text.insert(tk.END, f"✅ Succès!\n\n")
            self.import_text.insert(tk.END, f"📊 {imported_count} transactions importées\n")
            self.import_text.insert(tk.END, f"⏭️ {skipped_count} doublons ignorés\n")
            
            if warnings:
                self.import_text.insert(tk.END, f"\n⚠️ Avertissements ({len(warnings)}):\n")
                for warning in warnings:
                    self.import_text.insert(tk.END, f"  • {warning}\n")

            messagebox.showinfo("Succès", f"{imported_count} transactions importées ({skipped_count} doublons ignorés)!")
            
            # Refresh views
            self.update_stats_display()
            self.refresh_transactions()
            self.update_info_text()
            
        except Exception as e:
            self.import_text.insert(tk.END, f"❌ Erreur: {str(e)}\n")
            messagebox.showerror("Erreur", str(e))
    
    def export_report_pdf(self):
        """Export monthly report to PDF"""
        try:
            # Get date filters
            start_date = None
            end_date = None
            
            if self.report_from_date_enabled.get():
                start_date = self.report_from_date.get_date().strftime("%Y-%m-%d")
                
            if self.report_to_date_enabled.get():
                end_date = self.report_to_date.get_date().strftime("%Y-%m-%d")
            
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
                initialfile=f"Rapport_Financier_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
            
            if not file_path:
                return
            
            self.update_status("Export PDF en cours...")
            success = self.analyzer.export_monthly_report(file_path, start_date, end_date)
            
            if success:
                messagebox.showinfo("Succès", f"📄 Rapport exporté:\n{file_path}")
                self.update_status("PDF exporté avec succès")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'export PDF")
                self.update_status("Erreur lors de l'export")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def setup_transactions_tab(self):
        """Setup the transactions tab"""
        frame = ttk.Frame(self.transactions_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="📋 Transactions", style='Title.TLabel')
        title.pack(pady=15)
        
        # Filters frame
        filter_frame = ttk.LabelFrame(frame, text="🔍 Filtres et Options", padding=12)
        filter_frame.pack(fill=tk.X, pady=10)
        
        # Left side - Limit selector
        limit_frame = ttk.Frame(filter_frame)
        limit_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(limit_frame, text="Afficher:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.limit_var = tk.IntVar(value=50)
        limit_spin = ttk.Spinbox(limit_frame, from_=10, to=500, textvariable=self.limit_var, width=5)
        limit_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(limit_frame, text="dernières transactions", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Right side - Refresh button
        refresh_btn = ttk.Button(filter_frame, text="🔄 Actualiser", command=self.refresh_transactions)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Transactions table
        table_frame = ttk.LabelFrame(frame, text="💳 Liste des Transactions", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for transactions
        columns = ("Date", "Type", "Nom", "Montant", "Catégorie", "Sous-catégorie", "Récurrence", "Vital", "Épargne")
        self.transactions_tree = ttk.Treeview(table_frame, columns=columns, height=20, show="headings")
        
        # Define column headings
        self.transactions_tree.column("Date", anchor=tk.W, width=70)
        self.transactions_tree.column("Type", anchor=tk.W, width=80)
        self.transactions_tree.column("Nom", anchor=tk.W, width=150)
        self.transactions_tree.column("Montant", anchor=tk.E, width=80)
        self.transactions_tree.column("Catégorie", anchor=tk.W, width=90)
        self.transactions_tree.column("Sous-catégorie", anchor=tk.W, width=90)
        self.transactions_tree.column("Récurrence", anchor=tk.CENTER, width=80)
        self.transactions_tree.column("Vital", anchor=tk.CENTER, width=60)
        self.transactions_tree.column("Épargne", anchor=tk.CENTER, width=70)
        
        self.transactions_tree.heading("Date", text="📅 Date", anchor=tk.W)
        self.transactions_tree.heading("Type", text="🔹 Type", anchor=tk.W)
        self.transactions_tree.heading("Nom", text="📝 Nom", anchor=tk.W)
        self.transactions_tree.heading("Montant", text="💰 Montant", anchor=tk.E)
        self.transactions_tree.heading("Catégorie", text="📂 Catégorie", anchor=tk.W)
        self.transactions_tree.heading("Sous-catégorie", text="🏷️ Sous-cat.", anchor=tk.W)
        self.transactions_tree.heading("Récurrence", text="🔄 Récurrence", anchor=tk.CENTER)
        self.transactions_tree.heading("Vital", text="⭐ Vital", anchor=tk.CENTER)
        self.transactions_tree.heading("Épargne", text="💾 Épargne", anchor=tk.CENTER)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.transactions_tree.xview)
        
        self.transactions_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        # Pack treeview and scrollbars
        self.transactions_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind right-click to show context menu
        self.transactions_tree.bind("<Button-3>", self.show_transaction_context_menu)
        
        # Initial load
        self.refresh_transactions()

    
    def refresh_transactions(self):
        """Refresh transactions list"""
        # Clear treeview
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Get transactions
        limit = self.limit_var.get()
        transactions = self.db.get_all_transactions(limit=limit)
        
        # Get all categories to find subcategories
        all_categories = self.categorizer.get_all_categories_with_parent()
        
        # Build a map of category name -> parent name
        cat_parent_map = {}
        for cat in all_categories:
            if cat['parent_id'] is not None:
                # This is a subcategory
                parent = next((c for c in all_categories if c['id'] == cat['parent_id']), None)
                if parent:
                    cat_parent_map[cat['name']] = parent['name']
        
        # Add to treeview
        for i, t in enumerate(transactions):
            amount_str = f"€{t.amount:.2f}"
            tag = "positive" if t.amount > 0 else "negative"
            
            # Get parent category if this is a subcategory
            subcategory = ""
            if t.category and t.category in cat_parent_map:
                subcategory = t.category
                main_category = cat_parent_map[t.category]
            else:
                main_category = t.category or "-"
            
            # Format recurrence, vital and savings
            recurrence_text = "✓" if t.recurrence else ""
            vital_text = "✓" if t.vital else ""
            savings_text = "💾" if t.savings else ""
            
            self.transactions_tree.insert(
                "",
                "end",
                values=(t.date, t.type or "-", t.name or "-", amount_str, main_category, 
                       subcategory or "-", recurrence_text, vital_text, savings_text),
                tags=(tag,)
            )
        
        # Configure tags for colors
        self.transactions_tree.tag_configure("positive", foreground="green")
        self.transactions_tree.tag_configure("negative", foreground="red")
    
    def show_transaction_context_menu(self, event):
        """Show context menu on right-click"""
        # Select the row under the cursor
        row_id = self.transactions_tree.identify_row(event.y)
        if row_id:
            self.transactions_tree.selection_set(row_id)
            
            # Create context menu
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="🏷️ Catégoriser", command=self.categorize_selected_transaction)
            menu.add_separator()
            menu.add_command(label="🔄 Marquer comme récurrente", command=lambda: self.toggle_recurrence(row_id))
            menu.add_command(label="⭐ Marquer comme vitale", command=lambda: self.toggle_vital(row_id))
            menu.add_command(label="💾 Marquer comme épargne", command=lambda: self.toggle_savings(row_id))
            menu.add_separator()
            menu.add_command(label="📝 Ajouter une note", command=lambda: self.edit_transaction_notes(row_id))
            menu.add_command(label="🏷️ Gérer les tags", command=lambda: self.manage_transaction_tags(row_id))
            
            # Display the menu
            menu.post(event.x_root, event.y_root)
    
    def categorize_selected_transaction(self):
        """Open category selection dialog for selected transaction"""
        selection = self.transactions_tree.selection()
        if not selection:
            return
        
        # Get transaction index from treeview
        transaction_index = self.transactions_tree.index(selection[0])
        
        # Get all transactions to find the ID
        limit = self.limit_var.get()
        transactions = self.db.get_all_transactions(limit=limit)
        
        if transaction_index >= len(transactions):
            return
        
        transaction = transactions[transaction_index]
        transaction_id = transaction.id
        
        # Get all categories with hierarchy
        all_categories = self.categorizer.get_all_categories_with_parent()
        
        # Create category selection window
        window = tk.Toplevel(self.root)
        window.title("Sélectionner une catégorie")
        window.geometry("400x500")
        
        ttk.Label(window, text="Catégorie:", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Create a frame with scrollbar for categories using Treeview
        cat_frame = ttk.Frame(window)
        cat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(cat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Use Treeview for hierarchical display
        cat_tree = ttk.Treeview(cat_frame, yscrollcommand=scrollbar.set, height=15)
        cat_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=cat_tree.yview)
        
        # Build hierarchical tree
        parent_map = {}
        for cat in all_categories:
            if cat['parent_id'] is None:
                # Parent category
                parent_map[cat['id']] = cat_tree.insert('', 'end', text=f"📁 {cat['name']}", open=True)
        
        # Add subcategories
        for cat in all_categories:
            if cat['parent_id'] is not None:
                parent_id = cat['parent_id']
                parent_node = parent_map.get(parent_id)
                if parent_node:
                    cat_tree.insert(parent_node, 'end', text=f"  ↳ {cat['name']}")
        
        def assign_and_close():
            selection_item = cat_tree.selection()
            if selection_item:
                item_text = cat_tree.item(selection_item[0])['text']
                # Extract category name from display text
                selected_cat = item_text.replace("📁 ", "").replace("  ↳ ", "").strip()
                if selected_cat:
                    self.categorizer.categorize_transaction(transaction_id, selected_cat)
                    self.refresh_transactions()
                    self.update_stats_display()
                    window.destroy()
        
        ttk.Button(window, text="✅ Valider", command=assign_and_close).pack(pady=10)
    
    def toggle_recurrence(self, row_id):
        """Toggle recurrence flag for transaction"""
        # Get transaction index from treeview
        transaction_index = self.transactions_tree.index(row_id)
        
        # Get all transactions to find the transaction
        limit = self.limit_var.get()
        transactions = self.db.get_all_transactions(limit=limit)
        
        if transaction_index >= len(transactions):
            return
        
        transaction = transactions[transaction_index]
        new_value = not transaction.recurrence
        
        # Update database
        self.db.update_transaction_flags(transaction.id, recurrence=new_value)
        
        # Refresh display
        self.refresh_transactions()
    
    def toggle_vital(self, row_id):
        """Toggle vital flag for transaction"""
        # Get transaction index from treeview
        transaction_index = self.transactions_tree.index(row_id)
        
        # Get all transactions to find the transaction
        limit = self.limit_var.get()
        transactions = self.db.get_all_transactions(limit=limit)
        
        if transaction_index >= len(transactions):
            return
        
        transaction = transactions[transaction_index]
        new_value = not transaction.vital
        
        # Update database
        self.db.update_transaction_flags(transaction.id, vital=new_value)
        
        # Refresh display
        self.refresh_transactions()
    
    def toggle_savings(self, row_id):
        """Toggle savings flag for transaction"""
        # Get transaction index from treeview
        transaction_index = self.transactions_tree.index(row_id)
        
        # Get all transactions to find the transaction
        limit = self.limit_var.get()
        transactions = self.db.get_all_transactions(limit=limit)
        
        if transaction_index >= len(transactions):
            return
        
        transaction = transactions[transaction_index]
        new_value = not transaction.savings
        
        # Update database
        self.db.update_transaction_flags(transaction.id, savings=new_value)
        
        # Refresh display
        self.refresh_transactions()
    
    def edit_transaction_notes(self, row_id):
        """Edit notes for a transaction"""
        # Get transaction index
        transaction_index = self.transactions_tree.index(row_id)
        limit = self.limit_var.get()
        transactions = self.db.get_all_transactions(limit=limit)
        
        if transaction_index >= len(transactions):
            return
        
        transaction = transactions[transaction_index]
        current_notes = self.db.get_transaction_notes(transaction.id)
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Notes - {transaction.description[:50]}")
        dialog.geometry("500x300")
        
        ttk.Label(dialog, text="Notes de transaction:").pack(padx=10, pady=10)
        
        text_widget = tk.Text(dialog, height=10, width=60, wrap=tk.WORD)
        text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", current_notes)
        
        def save():
            notes = text_widget.get("1.0", tk.END).strip()
            self.db.update_transaction_notes(transaction.id, notes)
            messagebox.showinfo("Succès", "Notes mises à jour")
            dialog.destroy()
            self.refresh_transactions()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="✅ Sauvegarder", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def manage_transaction_tags(self, row_id):
        """Manage tags for a transaction"""
        # Get transaction index
        transaction_index = self.transactions_tree.index(row_id)
        limit = self.limit_var.get()
        transactions = self.db.get_all_transactions(limit=limit)
        
        if transaction_index >= len(transactions):
            return
        
        transaction = transactions[transaction_index]
        current_tags = self.db.get_transaction_tags(transaction.id)
        current_tag_ids = {tag[0] for tag in current_tags}
        all_tags = self.db.get_all_tags()
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Tags - {transaction.description[:50]}")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Sélectionnez les tags:").pack(padx=10, pady=10)
        
        # Create frame for checkboxes
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        tag_vars = {}
        for tag_id, tag_name, tag_color in all_tags:
            var = tk.BooleanVar(value=tag_id in current_tag_ids)
            tag_vars[tag_id] = var
            ttk.Checkbutton(scrollable, text=tag_name, variable=var).pack(anchor=tk.W, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def save_tags():
            # Remove all existing tags
            for tag_id, _ in [(t[0], t[1]) for t in current_tags]:
                self.db.remove_tag_from_transaction(transaction.id, tag_id)
            
            # Add selected tags
            for tag_id, var in tag_vars.items():
                if var.get():
                    self.db.tag_transaction(transaction.id, tag_id)
            
            messagebox.showinfo("Succès", "Tags mis à jour")
            dialog.destroy()
            self.refresh_transactions()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="✅ Sauvegarder", command=save_tags).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="➕ Nouveau Tag", command=lambda: self.create_new_tag(tag_vars)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_new_tag(self, tag_vars):
        """Create a new tag"""
        new_tag = simpledialog.askstring("Nouveau Tag", "Nom du tag:")
        if new_tag:
            tag_id = self.db.add_tag(new_tag)
            tag_vars[tag_id] = tk.BooleanVar(value=True)
            messagebox.showinfo("Succès", f"Tag '{new_tag}' créé")
    
    
    def setup_report_tab(self):
        """Setup the report tab with comprehensive statistics and charts"""
        frame = ttk.Frame(self.report_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="📊 Rapport Financier Détaillé", style='Title.TLabel')
        title.pack(pady=15)
        
        # Date selection frame
        date_frame = ttk.LabelFrame(frame, text="📅 Sélection des dates", padding=10)
        date_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # From date with calendar
        ttk.Label(date_frame, text="Du (inclus):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_from_date = DateEntry(
            date_frame, 
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            year=datetime.now().year,
            month=datetime.now().month,
            day=1,
            locale='fr_FR'
        )
        self.report_from_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.report_from_date_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(date_frame, text="Activer", variable=self.report_from_date_enabled).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(date_frame, text="(Cocher pour activer)", font=("Arial", 9)).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # To date with calendar
        ttk.Label(date_frame, text="Au (inclus):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_to_date = DateEntry(
            date_frame,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            locale='fr_FR'
        )
        self.report_to_date.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.report_to_date_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(date_frame, text="Activer", variable=self.report_to_date_enabled).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(date_frame, text="(Cocher pour activer)", font=("Arial", 9)).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Generate button
        gen_btn = tk.Button(frame, text="🔄 Générer le Rapport", 
                           command=self.generate_comprehensive_report,
                           bg=self.COLORS['secondary'], fg=self.COLORS['light'],
                           font=("Arial", 12, "bold"),
                           padx=30, pady=10, cursor="hand2")
        gen_btn.pack(pady=10)
        
        # Export PDF button
        export_btn = tk.Button(frame, text="📄 Exporter en PDF", 
                              command=self.export_report_pdf,
                              bg=self.COLORS['success'], fg=self.COLORS['light'],
                              font=("Arial", 12, "bold"),
                              padx=30, pady=10, cursor="hand2")
        export_btn.pack(pady=5)
        
        # Create main container with scrollbar
        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbar for report content
        canvas = tk.Canvas(container, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.report_frame = ttk.Frame(canvas)
        
        self.report_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.report_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store canvas for later use
        self.report_canvas = canvas
    
    def generate_comprehensive_report(self):
        """Generate comprehensive report with charts"""
        # Clear previous report
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        self.update_status("Génération du rapport en cours...")
        
        try:
            # Get date filters (only if enabled)
            start_date = None
            end_date = None
            
            if self.report_from_date_enabled.get():
                start_date = self.report_from_date.get_date().strftime("%Y-%m-%d")
                
            if self.report_to_date_enabled.get():
                end_date = self.report_to_date.get_date().strftime("%Y-%m-%d")
            
            # Get comprehensive report data
            report_data = self.analyzer.generate_comprehensive_report(start_date, end_date)
            
            stats = report_data['stats']
            recurrence_stats = report_data['recurrence_stats']
            vital_stats = report_data['vital_stats']
            by_category = report_data['by_category']
            charts = report_data['charts']
            
            # Display date range in title
            date_info = ""
            if start_date or end_date:
                date_info = f" ({start_date or 'début'} à {end_date or 'fin'})"
            
            # 1. General Statistics Section
            stats_frame = ttk.LabelFrame(self.report_frame, text="📊 Statistiques Générales" + date_info, padding=15)
            stats_frame.pack(fill=tk.X, padx=10, pady=10)
            
            stats_text = f"""
💰 Revenus totaux: €{stats['total_income']:.2f}
💸 Dépenses totales: €{stats['total_expenses']:.2f}
📈 Bilan net: €{stats['net']:.2f}
📋 Nombre de transactions: {stats['total_transactions']}
📊 Moyenne par transaction: €{stats['average_transaction']:.2f}
⬆️ Plus grand revenu: €{stats['largest_income']:.2f}
⬇️ Plus grande dépense: €{stats['largest_expense']:.2f}
"""
            ttk.Label(stats_frame, text=stats_text, font=("Courier", 11), justify=tk.LEFT).pack(anchor=tk.W)
            
            # 2. Charts Grid
            charts_container = ttk.Frame(self.report_frame)
            charts_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Row 1: Income/Expense and Recurrence charts
            row1 = ttk.Frame(charts_container)
            row1.pack(fill=tk.X, pady=5)
            
            if charts.get('income_expense'):
                self.add_chart_to_frame(row1, charts['income_expense'], "Revenus vs Dépenses", side=tk.LEFT)
            
            if charts.get('recurrence'):
                self.add_chart_to_frame(row1, charts['recurrence'], "Dépenses: Récurrentes vs Ponctuelles", side=tk.LEFT)
            
            # Row 2: Vital and Top Categories charts
            row2 = ttk.Frame(charts_container)
            row2.pack(fill=tk.X, pady=5)
            
            if charts.get('vital'):
                self.add_chart_to_frame(row2, charts['vital'], "Dépenses: Vitales vs Non-vitales", side=tk.LEFT)
            
            if charts.get('top_categories'):
                self.add_chart_to_frame(row2, charts['top_categories'], "Top 10 Catégories", side=tk.LEFT)
            
            # 3. Recurrence Statistics Section
            rec_frame = ttk.LabelFrame(self.report_frame, text="� Analyse des Transactions Récurrentes", padding=15)
            rec_frame.pack(fill=tk.X, padx=10, pady=10)
            
            rec_text = f"""
📊 Transactions récurrentes: {recurrence_stats['recurring_count']}
📊 Transactions ponctuelles: {recurrence_stats['non_recurring_count']}

💸 Dépenses récurrentes: €{recurrence_stats['recurring_expenses']:.2f}
💸 Dépenses ponctuelles: €{recurrence_stats['non_recurring_expenses']:.2f}

💰 Revenus récurrents: €{recurrence_stats['recurring_income']:.2f}
💰 Revenus ponctuels: €{recurrence_stats['non_recurring_income']:.2f}

📈 Bilan net récurrent: €{recurrence_stats['recurring_net']:.2f}
📈 Bilan net ponctuel: €{recurrence_stats['non_recurring_net']:.2f}
"""
            ttk.Label(rec_frame, text=rec_text, font=("Courier", 10), justify=tk.LEFT).pack(anchor=tk.W)
            
            # 4. Vital Statistics Section
            vital_frame = ttk.LabelFrame(self.report_frame, text="⭐ Analyse des Transactions Vitales", padding=15)
            vital_frame.pack(fill=tk.X, padx=10, pady=10)
            
            vital_text = f"""
📊 Transactions vitales: {vital_stats['vital_count']}
📊 Transactions non-vitales: {vital_stats['non_vital_count']}

💸 Dépenses vitales: €{vital_stats['vital_expenses']:.2f}
💸 Dépenses non-vitales: €{vital_stats['non_vital_expenses']:.2f}

💰 Revenus vitaux: €{vital_stats['vital_income']:.2f}
💰 Revenus non-vitaux: €{vital_stats['non_vital_income']:.2f}

📈 Bilan net vital: €{vital_stats['vital_net']:.2f}
📈 Bilan net non-vital: €{vital_stats['non_vital_net']:.2f}
"""
            ttk.Label(vital_frame, text=vital_text, font=("Courier", 10), justify=tk.LEFT).pack(anchor=tk.W)
            
            # 5. Category Breakdown
            if by_category:
                cat_frame = ttk.LabelFrame(self.report_frame, text="📂 Dépenses par Catégorie", padding=15)
                cat_frame.pack(fill=tk.X, padx=10, pady=10)
                
                cat_text = "\n".join([f"{cat}: €{amount:.2f}" for cat, amount in list(by_category.items())[:15]])
                ttk.Label(cat_frame, text=cat_text, font=("Courier", 10), justify=tk.LEFT).pack(anchor=tk.W)
            
            self.update_status("Rapport généré avec succès!")
            
        except Exception as e:
            error_label = ttk.Label(self.report_frame, 
                                   text=f"❌ Erreur lors de la génération du rapport:\n{str(e)}",
                                   font=("Arial", 12),
                                   foreground='red')
            error_label.pack(pady=20)
            self.update_status(f"Erreur: {str(e)}")
    
    def add_chart_to_frame(self, parent_frame, image_base64, title, side=tk.LEFT):
        """Add a chart image to a frame"""
        try:
            from PIL import Image, ImageTk
            import base64
            from io import BytesIO
            
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            # Resize for display
            image = image.resize((400, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Create frame for chart
            chart_frame = ttk.LabelFrame(parent_frame, text=title, padding=10)
            chart_frame.pack(side=side, padx=10, pady=10, expand=True)
            
            # Add image
            label = ttk.Label(chart_frame, image=photo)
            label.image = photo  # Keep reference
            label.pack()
            
        except ImportError:
            # PIL not available, show error
            error_label = ttk.Label(parent_frame, 
                                   text=f"⚠️ {title}\n(PIL requis pour afficher les graphiques)",
                                   font=("Arial", 10))
            error_label.pack(side=side, padx=10, pady=10)
        except Exception as e:
            error_label = ttk.Label(parent_frame, 
                                   text=f"❌ Erreur: {str(e)}",
                                   font=("Arial", 10),
                                   foreground='red')
            error_label.pack(side=side, padx=10, pady=10)
    
    def setup_categories_tab(self):
        """Setup categories management tab"""
        frame = ttk.Frame(self.categories_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Gestion des Catégories et Sous-Catégories", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Left: Categories with tree view
        left_frame = ttk.LabelFrame(frame, text="Catégories et Sous-Catégories", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(left_frame, text="Structure hiérarchique:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        cat_tree_frame = ttk.Frame(left_frame)
        cat_tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(cat_tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Use Treeview for hierarchical display
        self.categories_tree = ttk.Treeview(cat_tree_frame, yscrollcommand=scrollbar.set, height=15)
        self.categories_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.categories_tree.yview)
        
        self.refresh_categories_tree()
        
        cat_btn_frame = ttk.Frame(left_frame)
        cat_btn_frame.pack(fill=tk.X)
        
        ttk.Button(cat_btn_frame, text="➕ Ajouter catégorie", command=self.add_category).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(cat_btn_frame, text="➕ Ajouter sous-catégorie", command=self.add_subcategory).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(cat_btn_frame, text="❌ Supprimer", command=self.delete_category).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Right: Rules
        right_frame = ttk.LabelFrame(frame, text="Règles de Catégorisation", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(right_frame, text="Mots-clés associés:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        rules_list_frame = ttk.Frame(right_frame)
        rules_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar2 = ttk.Scrollbar(rules_list_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.rules_text = tk.Text(rules_list_frame, height=15, yscrollcommand=scrollbar2.set)
        self.rules_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.rules_text.yview)
        
        self.refresh_rules_display()
        
        rules_btn_frame = ttk.Frame(right_frame)
        rules_btn_frame.pack(fill=tk.X)
        
        ttk.Button(rules_btn_frame, text="➕ Ajouter règle", command=self.add_rule).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(rules_btn_frame, text="🔄 Actualiser", command=self.refresh_rules_display).pack(side=tk.LEFT, padx=5, pady=5)
    
    def refresh_categories_tree(self):
        """Refresh categories tree view with hierarchy"""
        # Clear existing items
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        
        # Get all categories
        all_cats = self.categorizer.get_all_categories_with_parent()
        
        # Create mapping of parent categories
        parent_map = {}
        for cat in all_cats:
            if cat['parent_id'] is None:
                # Add parent category
                parent_map[cat['id']] = self.categories_tree.insert('', 'end', text=cat['name'], open=True)
        
        # Add subcategories
        for cat in all_cats:
            if cat['parent_id'] is not None:
                parent_id = cat['parent_id']
                parent_node = parent_map.get(parent_id)
                if parent_node:
                    self.categories_tree.insert(parent_node, 'end', text=f"  {cat['name']}")

    
    def refresh_rules_display(self):
        """Refresh rules display"""
        self.rules_text.config(state=tk.NORMAL)
        self.rules_text.delete(1.0, tk.END)
        
        rules = self.categorizer.get_rules()
        current_cat = None
        
        for rule in rules:
            if rule['category'] != current_cat:
                current_cat = rule['category']
                self.rules_text.insert(tk.END, f"\n🏷️ {current_cat}:\n", "header")
            
            self.rules_text.insert(tk.END, f"   • {rule['keyword']}\n")
        
        self.rules_text.tag_config("header", font=("Arial", 10, "bold"), foreground="blue")
        self.rules_text.config(state=tk.DISABLED)
    
    def add_category(self):
        """Add a new category"""
        dialog = simpledialog.askstring("Ajouter une catégorie", "Nom de la catégorie:")
        if dialog:
            self.categorizer.add_category(dialog)
            self.refresh_categories_tree()
            messagebox.showinfo("Succès", f"Catégorie '{dialog}' ajoutée!")
    
    def add_subcategory(self):
        """Add a new subcategory under a parent"""
        # First, ask for parent category
        categories = [cat['name'] for cat in self.categorizer.get_all_categories_with_parent() if cat['parent_id'] is None]
        
        if not categories:
            messagebox.showwarning("Attention", "Aucune catégorie parent disponible")
            return
        
        parent_window = tk.Toplevel(self.root)
        parent_window.title("Sélectionner la catégorie parent")
        parent_window.geometry("300x200")
        
        selected_parent = tk.StringVar()
        
        ttk.Label(parent_window, text="Catégorie parent:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=10)
        
        for cat in categories:
            ttk.Radiobutton(parent_window, text=cat, variable=selected_parent, value=cat).pack(anchor=tk.W, padx=30)
        
        def select_parent():
            if selected_parent.get():
                parent_window.destroy()
                
                # Now ask for subcategory name
                subcat_name = simpledialog.askstring("Ajouter une sous-catégorie", 
                                                      f"Nom de la sous-catégorie pour '{selected_parent.get()}':")
                if subcat_name:
                    self.categorizer.add_subcategory(subcat_name, selected_parent.get())
                    self.refresh_categories_tree()
                    messagebox.showinfo("Succès", f"Sous-catégorie '{subcat_name}' ajoutée!")
        
        ttk.Button(parent_window, text="Continuer", command=select_parent).pack(pady=10)
    
    def delete_category(self):
        """Delete a category"""
        selection = self.categories_tree.selection()
        if selection:
            item_id = selection[0]
            item_text = self.categories_tree.item(item_id)['text'].strip()
            if messagebox.askyesno("Confirmer", f"Supprimer '{item_text}'?"):
                self.categorizer.delete_category(item_text)
                self.refresh_categories_tree()

    
    def add_rule(self):
        """Add a new categorization rule"""
        keyword = simpledialog.askstring("Ajouter une règle", "Mot-clé:")
        if keyword:
            categories = self.categorizer.get_categories()
            # Simple selection
            cat = tk.Toplevel(self.root)
            cat.title("Sélectionner une catégorie")
            
            selected = tk.StringVar()
            
            for c in categories:
                ttk.Radiobutton(cat, text=c, variable=selected, value=c).pack(anchor=tk.W, padx=20)
            
            def confirm():
                if selected.get():
                    self.categorizer.add_rule(keyword, selected.get())
                    self.refresh_rules_display()
                    messagebox.showinfo("Succès", f"Règle '{keyword}' ajoutée!")
                    cat.destroy()
            
            ttk.Button(cat, text="Valider", command=confirm).pack(pady=10)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        frame = ttk.Frame(self.settings_tab, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Paramètres et Maintenance", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Database section
        db_frame = ttk.LabelFrame(frame, text="Base de Données", padding=15)
        db_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(db_frame, text="Gestion de la base de données:", font=("Arial", 10)).pack(anchor="w")
        
        btn_frame = ttk.Frame(db_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📊 Statistiques BD", command=self.show_db_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Exporter", command=self.export_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="� Supprimer doublons", command=self.remove_duplicates).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="�🗑️ Vider", command=self.clear_db).pack(side=tk.LEFT, padx=5)
        
        # Info section
        info_frame = ttk.LabelFrame(frame, text="Informations", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.info_text = tk.Text(info_frame, height=10)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        self.update_info_text()
    
    def update_info_text(self):
        """Update the info text in settings tab"""
        info = f"""
📱 Bank Analyzer v0.1.0

📁 Base de données: data/database.db
💾 Localisation: {self.db.db_path}

📊 Contenu actuel:
   • {len(self.db.get_all_transactions())} transactions importées
   • {len(self.categorizer.get_uncategorized())} non catégorisées

⚙️ Catégories:
   • {len(self.categorizer.get_categories())} catégories
   • {len(self.categorizer.get_rules())} règles de catégorisation

✅ Toutes les données sont stockées localement.
🔒 Aucune synchronisation cloud.
        """
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)
    
    def show_db_stats(self):
        """Show database statistics"""
        total = len(self.db.get_all_transactions())
        uncategorized = len(self.categorizer.get_uncategorized())
        
        stats = f"""
Statistiques de la Base de Données
==================================

Total transactions: {total}
Catégorisées: {total - uncategorized}
Non catégorisées: {uncategorized}

Catégories: {len(self.categorizer.get_categories())}
Règles: {len(self.categorizer.get_rules())}
        """
        
        messagebox.showinfo("Statistiques", stats)
    
    def export_db(self):
        """Export database"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database", "*.db"), ("All files", "*.*")]
        )
        
        if file_path:
            import shutil
            shutil.copy(str(self.db.db_path), file_path)
            messagebox.showinfo("Succès", f"Base de données exportée vers:\n{file_path}")
    
    def clear_db(self):
        """Clear database"""
        if messagebox.askyesno("Attention!", "Vider complètement la base de données?\n\nCette action est irréversible!\n(Les catégories personnalisées seront conservées)"):
            try:
                # Delete all transactions
                self.db.cursor.execute("DELETE FROM transactions")
                self.db.connection.commit()
                
                # Delete all categorization rules
                self.db.cursor.execute("DELETE FROM categorization_rules")
                self.db.connection.commit()
                
                # Ensure default categories exist (without deleting custom ones)
                self.categorizer.ensure_default_categories()
                
                # Refresh all views
                self.refresh_transactions()
                self.refresh_categories_tree()
                self.refresh_rules_display()
                # Clear report area if exists
                try:
                    for widget in self.report_frame.winfo_children():
                        widget.destroy()
                except Exception:
                    pass

                # Update header stats
                try:
                    self.update_stats_display()
                except Exception:
                    pass
                
                # Update info text in settings tab
                try:
                    self.update_info_text()
                except Exception:
                    pass
                
                messagebox.showinfo("Succès", "Base de données vidée!\n(Les catégories ont été conservées)")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du vidage: {str(e)}")
    
    def remove_duplicates(self):
        """Remove duplicate transactions"""
        if messagebox.askyesno("Attention!", "Supprimer les transactions dupliquées?\n\nCela gardera la première occurrence et supprimera les doublons."):
            try:
                deleted = self.categorizer.remove_duplicate_transactions()
                
                # Refresh all views
                self.refresh_transactions()
                # Update header stats
                try:
                    self.update_stats_display()
                except Exception:
                    pass
                
                # Update info text in settings tab
                try:
                    self.update_info_text()
                except Exception:
                    pass
                
                messagebox.showinfo("Succès", f"✅ {deleted} transaction(s) dupliquée(s) supprimée(s)!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression des doublons: {str(e)}")
    
    def setup_statistics_tab(self):
        """Setup advanced statistics tab"""
        frame = ttk.Frame(self.statistics_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="📊 Statistiques Avancées", style='Title.TLabel')
        title.pack(pady=15)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(frame, text="🔍 Filtres", padding=10)
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Plage de dates:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(filter_frame, text="De:").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.stat_start_date = DateEntry(filter_frame, width=15, background='darkblue', foreground='white', borderwidth=2)
        self.stat_start_date.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="À:").grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.stat_end_date = DateEntry(filter_frame, width=15, background='darkblue', foreground='white', borderwidth=2)
        self.stat_end_date.grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Montant min (€):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.stat_min_amount = ttk.Entry(filter_frame, width=10)
        self.stat_min_amount.insert(0, "0")
        self.stat_min_amount.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Montant max (€):").grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.stat_max_amount = ttk.Entry(filter_frame, width=10)
        self.stat_max_amount.grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        
        # Analysis options
        ttk.Label(filter_frame, text="Analyse:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        analysis_var = tk.StringVar(value="weekday")
        analysis_combo = ttk.Combobox(filter_frame, textvariable=analysis_var, width=20,
                                      values=["weekday", "merchants", "anomalies", "trends"], state="readonly")
        analysis_combo.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.stat_analysis_var = analysis_var
        
        # Buttons
        refresh_btn = tk.Button(filter_frame, text="🔄 Actualiser",
                               command=self.refresh_statistics,
                               bg=self.COLORS['secondary'], fg=self.COLORS['light'],
                               font=("Arial", 10, "bold"), padx=15, pady=8, cursor="hand2")
        refresh_btn.grid(row=2, column=3, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas for scrollable content
        canvas = tk.Canvas(results_frame, bg=self.COLORS['light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.config(yscrollcommand=scrollbar.set)
        
        self.stat_results_frame = scrollable_frame
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def refresh_statistics(self):
        """Refresh statistics display"""
        # Clear previous results
        for widget in self.stat_results_frame.winfo_children():
            widget.destroy()
        
        try:
            analysis_type = self.stat_analysis_var.get()
            start_date = self.stat_start_date.get_date().strftime("%Y-%m-%d")
            end_date = self.stat_end_date.get_date().strftime("%Y-%m-%d")
            
            if analysis_type == "weekday":
                self.show_weekday_analysis(start_date, end_date)
            elif analysis_type == "merchants":
                self.show_merchants_analysis(start_date, end_date)
            elif analysis_type == "anomalies":
                self.show_anomalies_analysis(start_date, end_date)
            elif analysis_type == "trends":
                self.show_trends_analysis()
            
            self.update_status("Statistiques actualisées")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse: {str(e)}")
    
    def show_weekday_analysis(self, start_date, end_date):
        """Display weekday analysis"""
        title = ttk.Label(self.stat_results_frame, text="📅 Dépenses par Jour de la Semaine", 
                         font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        stats = self.analyzer.get_weekday_analysis(start_date, end_date)
        
        # Create table
        table_frame = ttk.Frame(self.stat_results_frame)
        table_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        columns = ("Jour", "Transactions", "Revenus", "Dépenses", "Bilan", "Avg/Trans")
        tree = ttk.Treeview(table_frame, columns=columns, height=10, show="headings")
        
        tree.column("Jour", anchor=tk.W, width=100)
        tree.column("Transactions", anchor=tk.CENTER, width=80)
        tree.column("Revenus", anchor=tk.E, width=80)
        tree.column("Dépenses", anchor=tk.E, width=80)
        tree.column("Bilan", anchor=tk.E, width=80)
        tree.column("Avg/Trans", anchor=tk.E, width=90)
        
        for col in columns:
            tree.heading(col, text=col)
        
        for day, data in stats.items():
            avg = data['net'] / data['count'] if data['count'] > 0 else 0
            tree.insert("", "end", values=(
                day,
                data['count'],
                f"€{data['income']:.2f}",
                f"€{data['expenses']:.2f}",
                f"€{data['net']:.2f}",
                f"€{avg:.2f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
    
    def show_merchants_analysis(self, start_date, end_date):
        """Display top merchants analysis"""
        title = ttk.Label(self.stat_results_frame, text="🏪 Top Marchands", 
                         font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        merchants = self.analyzer.get_top_merchants(limit=15, start_date=start_date, end_date=end_date)
        
        if not merchants:
            ttk.Label(self.stat_results_frame, text="Aucune données disponibles").pack()
            return
        
        # Create table
        table_frame = ttk.Frame(self.stat_results_frame)
        table_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        columns = ("Marchand", "Transactions", "Total", "Moyenne")
        tree = ttk.Treeview(table_frame, columns=columns, height=15, show="headings")
        
        tree.column("Marchand", anchor=tk.W, width=250)
        tree.column("Transactions", anchor=tk.CENTER, width=80)
        tree.column("Total", anchor=tk.E, width=100)
        tree.column("Moyenne", anchor=tk.E, width=100)
        
        for col in columns:
            tree.heading(col, text=col)
        
        for i, m in enumerate(merchants, 1):
            tree.insert("", "end", values=(
                f"{i}. {m['merchant'][:50]}",
                m['count'],
                f"€{m['total']:.2f}",
                f"€{m['average']:.2f}"
            ), tags=("oddrow" if i % 2 == 0 else "evenrow",))
        
        tree.tag_configure("oddrow", background="#ECF0F1")
        tree.tag_configure("evenrow", background="#FFFFFF")
        tree.pack(fill=tk.BOTH, expand=True)
    
    def show_anomalies_analysis(self, start_date, end_date):
        """Display anomalies detection"""
        title = ttk.Label(self.stat_results_frame, text="⚠️ Transactions Anormales", 
                         font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        anomalies = self.analyzer.detect_anomalies(start_date, end_date, threshold_std=2.0)
        
        if not anomalies['by_category']:
            ttk.Label(self.stat_results_frame, text="✅ Aucune anomalie détectée").pack()
            return
        
        # Summary
        summary_text = f"🔍 Total anomalies détectées: {anomalies['total_anomalies']}"
        ttk.Label(self.stat_results_frame, text=summary_text, font=("Arial", 10, "bold")).pack(pady=5)
        
        # By category
        for category, data in anomalies['by_category'].items():
            cat_frame = ttk.LabelFrame(self.stat_results_frame, text=f"📂 {category}", padding=10)
            cat_frame.pack(fill=tk.X, padx=10, pady=5)
            
            stats_text = (f"Moyenne: €{data['mean']:.2f} | "
                         f"Écart-type: €{data['std_dev']:.2f} | "
                         f"Seuil: €{data['threshold']:.2f} | "
                         f"Anomalies: {data['count']}")
            ttk.Label(cat_frame, text=stats_text, font=("Courier", 9)).pack(anchor=tk.W)
            
            anom_text = f"Montants anormaux: {', '.join(f'€{a:.2f}' for a in data['anomalies'][:10])}"
            ttk.Label(cat_frame, text=anom_text, font=("Courier", 9, "bold"), foreground="#E74C3C").pack(anchor=tk.W)
    
    def show_trends_analysis(self):
        """Display category trends"""
        title = ttk.Label(self.stat_results_frame, text="📈 Tendances des Catégories (6 mois)", 
                         font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        trends = self.analyzer.get_category_trends(months=6)
        
        # Create table
        table_frame = ttk.Frame(self.stat_results_frame)
        table_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        columns = ["Catégorie"] + trends['months'] + ["Tendance", "Total", "Moyenne"]
        tree = ttk.Treeview(table_frame, columns=columns, height=12, show="headings")
        
        tree.column("Catégorie", anchor=tk.W, width=120)
        for month in trends['months']:
            tree.column(month, anchor=tk.E, width=70)
        tree.column("Tendance", anchor=tk.CENTER, width=70)
        tree.column("Total", anchor=tk.E, width=80)
        tree.column("Moyenne", anchor=tk.E, width=80)
        
        for col in columns:
            tree.heading(col, text=col)
        
        for category, data in sorted(trends['categories'].items(), key=lambda x: x[1]['total'], reverse=True):
            trend_icon = "📈" if data['trend'] == 'up' else "📉"
            values = [category]
            for v in data['values']:
                values.append(f"€{v:.2f}")
            values.extend([
                f"{trend_icon} {data['trend']}",
                f"€{data['total']:.2f}",
                f"€{data['average']:.2f}"
            ])
            tree.insert("", "end", values=values)
        
        tree.pack(fill=tk.BOTH, expand=True)


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = BankAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
