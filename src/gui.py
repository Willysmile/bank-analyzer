"""
GUI module - Graphical User Interface with Tkinter
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from datetime import datetime
from src.database import Database
from src.importer import CSVImporter
from src.categorizer import Categorizer
from src.analyzer import Analyzer


class BankAnalyzerGUI:
    """Main GUI application for Bank Analyzer"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("Bank Analyzer 🏦")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Initialize database
        self.db = Database()
        self.categorizer = Categorizer(self.db)
        self.analyzer = Analyzer(self.db)
        self.importer = CSVImporter()
        
        # Initialize categories
        self.categorizer.init_categories()
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.import_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.categorize_tab = ttk.Frame(self.notebook)
        self.categories_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.import_tab, text="📥 Import")
        self.notebook.add(self.transactions_tab, text="📋 Transactions")
        self.notebook.add(self.categorize_tab, text="🏷️ Catégoriser")
        self.notebook.add(self.categories_tab, text="⚙️ Catégories")
        self.notebook.add(self.report_tab, text="📊 Rapports")
        self.notebook.add(self.settings_tab, text="⚙️ Paramètres")
        
        # Setup each tab
        self.setup_import_tab()
        self.setup_transactions_tab()
        self.setup_categorize_tab()
        self.setup_categories_tab()
        self.setup_report_tab()
        self.setup_settings_tab()
    
    def setup_import_tab(self):
        """Setup the import tab"""
        frame = ttk.Frame(self.import_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Importer un fichier CSV", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # File selection
        file_frame = ttk.LabelFrame(frame, text="Sélectionner un fichier", padding=10)
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_label = ttk.Label(file_frame, text="Aucun fichier sélectionné", foreground="gray")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="Parcourir...", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # Import button
        import_btn = ttk.Button(frame, text="📥 Importer", command=self.import_file)
        import_btn.pack(pady=20)
        
        # Results area
        results_frame = ttk.LabelFrame(frame, text="Résultats", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.import_text = tk.Text(results_frame, height=15, yscrollcommand=scrollbar.set)
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
            self.file_label.config(text=filename, foreground="black")
    
    def import_file(self):
        """Import the selected CSV file"""
        if not self.file_path:
            messagebox.showwarning("Attention", "Sélectionne un fichier d'abord")
            return
        
        self.import_text.delete(1.0, tk.END)
        self.import_text.insert(tk.END, "⏳ Importation en cours...\n")
        self.root.update()
        
        try:
            transactions, warnings = self.importer.import_file(self.file_path, self.db)
            
            # Display warnings
            if warnings:
                self.import_text.insert(tk.END, "⚠️ Avertissements:\n")
                for warning in warnings:
                    self.import_text.insert(tk.END, f"  • {warning}\n")
                self.import_text.insert(tk.END, "\n")
            
            # Insert transactions
            imported_count = 0
            for transaction in transactions:
                self.db.insert_transaction(transaction)
                imported_count += 1
            
            self.import_text.insert(tk.END, f"✅ Succès!\n\n")
            self.import_text.insert(tk.END, f"📊 {imported_count} transactions importées\n")
            self.import_text.insert(tk.END, f"⚠️ {len(warnings)} avertissements\n")
            
            messagebox.showinfo("Succès", f"{imported_count} transactions importées!")
            
        except Exception as e:
            self.import_text.insert(tk.END, f"❌ Erreur: {str(e)}\n")
            messagebox.showerror("Erreur", str(e))
    
    def setup_transactions_tab(self):
        """Setup the transactions tab"""
        frame = ttk.Frame(self.transactions_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Transactions", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Filters frame
        filter_frame = ttk.LabelFrame(frame, text="Filtres", padding=10)
        filter_frame.pack(fill=tk.X, pady=10)
        
        # Limit selector
        limit_frame = ttk.Frame(filter_frame)
        limit_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(limit_frame, text="Afficher:").pack(side=tk.LEFT)
        self.limit_var = tk.IntVar(value=50)
        limit_spin = ttk.Spinbox(limit_frame, from_=10, to=500, textvariable=self.limit_var, width=5)
        limit_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(limit_frame, text="dernières transactions").pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = ttk.Button(filter_frame, text="🔄 Actualiser", command=self.refresh_transactions)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Transactions table
        table_frame = ttk.LabelFrame(frame, text="Liste", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for transactions
        columns = ("Date", "Type", "Nom", "Montant", "Catégorie")
        self.transactions_tree = ttk.Treeview(table_frame, columns=columns, height=20)
        
        # Define column headings
        self.transactions_tree.column("#0", width=0, stretch=tk.NO)
        self.transactions_tree.column("Date", anchor=tk.W, width=80)
        self.transactions_tree.column("Type", anchor=tk.W, width=120)
        self.transactions_tree.column("Nom", anchor=tk.W, width=250)
        self.transactions_tree.column("Montant", anchor=tk.E, width=80)
        self.transactions_tree.column("Catégorie", anchor=tk.W, width=120)
        
        self.transactions_tree.heading("#0", text="", anchor=tk.W)
        self.transactions_tree.heading("Date", text="Date", anchor=tk.W)
        self.transactions_tree.heading("Type", text="Type", anchor=tk.W)
        self.transactions_tree.heading("Nom", text="Nom/Description", anchor=tk.W)
        self.transactions_tree.heading("Montant", text="Montant", anchor=tk.E)
        self.transactions_tree.heading("Catégorie", text="Catégorie", anchor=tk.W)
        
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
        
        # Initial load
        self.refresh_transactions()
    
    def refresh_transactions(self):
        """Refresh transactions list"""
        # Clear treeview
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Get transactions
        transactions = self.db.get_all_transactions()[:self.limit_var.get()]
        
        # Add to treeview
        for i, t in enumerate(transactions):
            amount_str = f"€{t.amount:.2f}"
            tag = "positive" if t.amount > 0 else "negative"
            
            self.transactions_tree.insert(
                "",
                "end",
                values=(t.date, t.type or "-", t.name or "-", amount_str, t.category or "-"),
                tags=(tag,)
            )
        
        # Configure tags for colors
        self.transactions_tree.tag_configure("positive", foreground="green")
        self.transactions_tree.tag_configure("negative", foreground="red")
    
    def setup_categorize_tab(self):
        """Setup the categorization tab with table view"""
        frame = ttk.Frame(self.categorize_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Catégoriser les Transactions", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Info
        self.cat_info_label = ttk.Label(frame, text="Chargement...", font=("Arial", 10))
        self.cat_info_label.pack(pady=5)
        
        # Table frame
        table_frame = ttk.LabelFrame(frame, text="Transactions non catégorisées", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for transactions
        columns = ("Date", "Type", "Nom", "Montant", "Catégorie")
        self.cat_tree = ttk.Treeview(table_frame, columns=columns, height=20)
        
        # Define columns
        self.cat_tree.column("#0", width=0, stretch=tk.NO)
        self.cat_tree.column("Date", anchor=tk.W, width=80)
        self.cat_tree.column("Type", anchor=tk.W, width=120)
        self.cat_tree.column("Nom", anchor=tk.W, width=250)
        self.cat_tree.column("Montant", anchor=tk.E, width=80)
        self.cat_tree.column("Catégorie", anchor=tk.W, width=120)
        
        self.cat_tree.heading("#0", text="", anchor=tk.W)
        self.cat_tree.heading("Date", text="Date", anchor=tk.W)
        self.cat_tree.heading("Type", text="Type", anchor=tk.W)
        self.cat_tree.heading("Nom", text="Nom/Description", anchor=tk.W)
        self.cat_tree.heading("Montant", text="Montant", anchor=tk.E)
        self.cat_tree.heading("Catégorie", text="Catégorie", anchor=tk.W)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.cat_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.cat_tree.xview)
        
        self.cat_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.cat_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to categorize
        self.cat_tree.bind("<Double-1>", self.on_transaction_double_click)
        
        # Bottom actions
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        refresh_btn = ttk.Button(action_frame, text="🔄 Actualiser", command=self.refresh_categorize_tab)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        auto_btn = ttk.Button(action_frame, text="🤖 Auto-catégoriser", command=self.auto_categorize_all)
        auto_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_categorize_tab()
    
    def refresh_categorize_tab(self):
        """Refresh categorization table"""
        # Clear table
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        
        # Get uncategorized transactions
        uncategorized = self.categorizer.get_uncategorized()
        
        # Add to table
        for t in uncategorized:
            amount_str = f"€{t.amount:.2f}"
            tag = "positive" if t.amount > 0 else "negative"
            
            self.cat_tree.insert(
                "",
                "end",
                iid=t.id,
                values=(t.date, t.description[:60], amount_str, "-"),
                tags=(tag,)
            )
        
        # Configure tags
        self.cat_tree.tag_configure("positive", foreground="green")
        self.cat_tree.tag_configure("negative", foreground="red")
        
        # Update info
        self.cat_info_label.config(text=f"📊 {len(uncategorized)} transaction(s) à catégoriser")
    
    def on_transaction_double_click(self, event):
        """Handle double-click on transaction"""
        selection = self.cat_tree.selection()
        if not selection:
            return
        
        transaction_id = int(selection[0])
        
        # Get categories
        categories = self.categorizer.get_categories()
        
        # Create category selection window
        window = tk.Toplevel(self.root)
        window.title("Sélectionner une catégorie")
        window.geometry("300x400")
        
        ttk.Label(window, text="Catégorie:", font=("Arial", 12, "bold")).pack(pady=10)
        
        selected_category = tk.StringVar()
        
        def assign_and_close():
            cat = selected_category.get()
            if cat:
                self.categorizer.categorize_transaction(transaction_id, cat)
                self.refresh_categorize_tab()
                window.destroy()
        
        for cat in categories:
            ttk.Radiobutton(
                window,
                text=cat,
                variable=selected_category,
                value=cat
            ).pack(anchor=tk.W, padx=20, pady=5)
        
        ttk.Button(window, text="✅ Valider", command=assign_and_close).pack(pady=20)
    
    def auto_categorize_all(self):
        """Auto-categorize all uncategorized transactions"""
        uncategorized = self.categorizer.get_uncategorized()
        count = 0
        
        for t in uncategorized:
            category = self.categorizer.auto_categorize(t)
            if self.categorizer.categorize_transaction(t.id, category):
                count += 1
        
        messagebox.showinfo("Succès", f"{count} transactions auto-catégorisées!")
        self.refresh_categorize_tab()
    
    def setup_report_tab(self):
        """Setup the report tab"""
        frame = ttk.Frame(self.report_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Rapports et Statistiques", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Filters frame
        filter_frame = ttk.LabelFrame(frame, text="Filtres", padding=10)
        filter_frame.pack(fill=tk.X, pady=10)
        
        # Date range
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(date_frame, text="Du:").pack(side=tk.LEFT)
        self.start_date_entry = ttk.Entry(date_frame, width=12)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        self.start_date_entry.insert(0, "2025-01-01")
        
        ttk.Label(date_frame, text="Au:").pack(side=tk.LEFT)
        self.end_date_entry = ttk.Entry(date_frame, width=12)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Category filter
        cat_frame = ttk.Frame(filter_frame)
        cat_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(cat_frame, text="Catégorie:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        categories = ["Toutes"] + self.categorizer.get_categories()
        cat_combo = ttk.Combobox(cat_frame, textvariable=self.category_var, values=categories, width=15, state="readonly")
        cat_combo.pack(side=tk.LEFT, padx=5)
        cat_combo.set("Toutes")
        
        # Generate button
        gen_btn = ttk.Button(filter_frame, text="📊 Générer", command=self.generate_report)
        gen_btn.pack(side=tk.RIGHT, padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(frame, text="Résultats", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.report_text = tk.Text(results_frame, height=20, yscrollcommand=scrollbar.set)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.report_text.yview)
    
    def generate_report(self):
        """Generate a report"""
        start_date = self.start_date_entry.get() or None
        end_date = self.end_date_entry.get() or None
        category = self.category_var.get()
        
        if category == "Toutes":
            category = None
        
        self.report_text.delete(1.0, tk.END)
        
        try:
            stats = self.analyzer.get_statistics(start_date, end_date, category)
            
            report = "📊 RAPPORT FINANCIER\n"
            report += "=" * 50 + "\n\n"
            
            if start_date or end_date:
                report += f"Période: {start_date or 'Début'} à {end_date or 'Fin'}\n"
            if category:
                report += f"Catégorie: {category}\n"
            
            report += "\n" + "-" * 50 + "\n"
            report += f"📊 Statistiques Générales\n"
            report += "-" * 50 + "\n"
            report += f"Nombre de transactions: {stats['total_transactions']}\n"
            report += f"Revenu total: €{stats['total_income']:.2f}\n"
            report += f"Dépenses totales: €{stats['total_expenses']:.2f}\n"
            report += f"Bilan net: €{stats['net']:.2f}\n"
            report += f"Moyenne par transaction: €{stats['average_transaction']:.2f}\n"
            report += f"Plus grand revenu: €{stats['largest_income']:.2f}\n"
            report += f"Plus grande dépense: €{stats['largest_expense']:.2f}\n"
            
            # Category breakdown
            if not category:
                by_cat = self.analyzer.get_by_category(start_date, end_date)
                if by_cat:
                    report += "\n" + "-" * 50 + "\n"
                    report += "📈 Par Catégorie\n"
                    report += "-" * 50 + "\n"
                    for cat, amount in by_cat.items():
                        report += f"{cat}: €{amount:.2f}\n"
            
            self.report_text.insert(tk.END, report)
        
        except Exception as e:
            self.report_text.insert(tk.END, f"❌ Erreur: {str(e)}\n")
            messagebox.showerror("Erreur", str(e))
    
    def setup_categories_tab(self):
        """Setup categories management tab"""
        frame = ttk.Frame(self.categories_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Gestion des Catégories et Règles", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Left: Categories
        left_frame = ttk.LabelFrame(frame, text="Catégories", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(left_frame, text="Catégories disponibles:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        cat_list_frame = ttk.Frame(left_frame)
        cat_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(cat_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cat_listbox = tk.Listbox(cat_list_frame, yscrollcommand=scrollbar.set)
        self.cat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.cat_listbox.yview)
        
        # Refresh categories list
        for cat in self.categorizer.get_categories():
            self.cat_listbox.insert(tk.END, cat)
        
        cat_btn_frame = ttk.Frame(left_frame)
        cat_btn_frame.pack(fill=tk.X)
        
        ttk.Button(cat_btn_frame, text="➕ Ajouter", command=self.add_category).pack(side=tk.LEFT, padx=5, pady=5)
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
            self.cat_listbox.insert(tk.END, dialog)
            messagebox.showinfo("Succès", f"Catégorie '{dialog}' ajoutée!")
    
    def delete_category(self):
        """Delete a category"""
        sel = self.cat_listbox.curselection()
        if sel:
            cat = self.cat_listbox.get(sel[0])
            if messagebox.askyesno("Confirmer", f"Supprimer '{cat}'?"):
                self.categorizer.delete_category(cat)
                self.cat_listbox.delete(sel[0])
    
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
        ttk.Button(btn_frame, text="🗑️ Vider", command=self.clear_db).pack(side=tk.LEFT, padx=5)
        
        # Info section
        info_frame = ttk.LabelFrame(frame, text="Informations", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        info_text = tk.Text(info_frame, height=10)
        info_text.pack(fill=tk.BOTH, expand=True)
        
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
        
        info_text.insert(tk.END, info)
        info_text.config(state=tk.DISABLED)
    
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
        if messagebox.askyesno("Attention!", "Vider complètement la base de données?\n\nCette action est irréversible!"):
            self.db.close()
            Path(self.db.db_path).unlink(missing_ok=True)
            self.db = Database()
            self.categorizer = Categorizer(self.db)
            self.categorizer.init_categories()
            self.analyzer = Analyzer(self.db)
            messagebox.showinfo("Succès", "Base de données vidée!")


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = BankAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
