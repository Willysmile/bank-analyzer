"""
GUI module - Graphical User Interface with Tkinter
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        self.root.geometry("1000x700")
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
        self.categorize_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.import_tab, text="📥 Import")
        self.notebook.add(self.transactions_tab, text="📋 Transactions")
        self.notebook.add(self.categorize_tab, text="🏷️ Catégorisation")
        self.notebook.add(self.report_tab, text="📊 Rapports")
        
        # Setup each tab
        self.setup_import_tab()
        self.setup_transactions_tab()
        self.setup_categorize_tab()
        self.setup_report_tab()
    
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
        columns = ("Date", "Description", "Montant", "Catégorie")
        self.transactions_tree = ttk.Treeview(table_frame, columns=columns, height=20)
        
        # Define column headings
        self.transactions_tree.column("#0", width=0, stretch=tk.NO)
        self.transactions_tree.column("Date", anchor=tk.W, width=80)
        self.transactions_tree.column("Description", anchor=tk.W, width=400)
        self.transactions_tree.column("Montant", anchor=tk.E, width=80)
        self.transactions_tree.column("Catégorie", anchor=tk.W, width=150)
        
        self.transactions_tree.heading("#0", text="", anchor=tk.W)
        self.transactions_tree.heading("Date", text="Date", anchor=tk.W)
        self.transactions_tree.heading("Description", text="Description", anchor=tk.W)
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
                values=(t.date, t.description[:60], amount_str, t.category or "-"),
                tags=(tag,)
            )
        
        # Configure tags for colors
        self.transactions_tree.tag_configure("positive", foreground="green")
        self.transactions_tree.tag_configure("negative", foreground="red")
    
    def setup_categorize_tab(self):
        """Setup the categorization tab"""
        frame = ttk.Frame(self.categorize_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Catégorisation Manuelle", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Info frame
        info_frame = ttk.LabelFrame(frame, text="Information", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        self.uncategorized_label = ttk.Label(info_frame, text="Chargement...", font=("Arial", 12))
        self.uncategorized_label.pack(pady=5)
        
        # Main content frame with two columns
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # Left column: Transaction details
        left_frame = ttk.LabelFrame(content_frame, text="Transaction", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(2, weight=1)
        
        # Date
        ttk.Label(left_frame, text="Date:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.cat_date_label = ttk.Label(left_frame, text="-", foreground="blue")
        self.cat_date_label.grid(row=0, column=0, sticky="e", padx=20)
        
        # Montant
        ttk.Label(left_frame, text="Montant:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.cat_amount_label = ttk.Label(left_frame, text="-", foreground="blue")
        self.cat_amount_label.grid(row=1, column=0, sticky="e", padx=20)
        
        # Libellé
        ttk.Label(left_frame, text="Libellé:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="nw", pady=5)
        
        # Text area for description (read-only)
        scrollbar = ttk.Scrollbar(left_frame)
        scrollbar.grid(row=2, column=1, sticky="ns")
        
        self.cat_description = tk.Text(left_frame, height=10, yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.cat_description.grid(row=2, column=0, sticky="nsew", pady=5)
        scrollbar.config(command=self.cat_description.yview)
        self.cat_description.config(state=tk.DISABLED)
        
        # Right column: Categorization
        right_frame = ttk.LabelFrame(content_frame, text="Catégorisation", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        right_frame.columnconfigure(0, weight=1)
        
        ttk.Label(right_frame, text="Sélectionne une catégorie:", font=("Arial", 10)).pack(anchor="w")
        
        self.category_var = tk.StringVar()
        categories = self.categorizer.get_categories()
        
        # Category buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.category_buttons = {}
        for i, category in enumerate(categories):
            btn = ttk.Button(
                button_frame,
                text=category,
                command=lambda cat=category: self.assign_category(cat)
            )
            btn.pack(fill=tk.X, pady=5)
            self.category_buttons[category] = btn
        
        # Navigation frame
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        prev_btn = ttk.Button(nav_frame, text="⬅️ Précédent", command=self.prev_transaction)
        prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.transaction_counter = ttk.Label(nav_frame, text="0/0", font=("Arial", 10))
        self.transaction_counter.pack(side=tk.LEFT, padx=20)
        
        next_btn = ttk.Button(nav_frame, text="Suivant ➡️", command=self.next_transaction)
        next_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(nav_frame, text="🔄 Actualiser", command=self.refresh_categorization)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Current transaction tracking
        self.uncategorized_transactions = []
        self.current_transaction_idx = 0
        
        self.refresh_categorization()
    
    def refresh_categorization(self):
        """Refresh uncategorized transactions list"""
        self.uncategorized_transactions = self.categorizer.get_uncategorized()
        self.current_transaction_idx = 0
        self.update_uncategorized_count()
        self.display_transaction()
    
    def display_transaction(self):
        """Display current transaction"""
        if not self.uncategorized_transactions:
            self.cat_date_label.config(text="Aucune transaction")
            self.cat_amount_label.config(text="-")
            self.cat_description.config(state=tk.NORMAL)
            self.cat_description.delete(1.0, tk.END)
            self.cat_description.insert(tk.END, "Aucune transaction non catégorisée!")
            self.cat_description.config(state=tk.DISABLED)
            self.transaction_counter.config(text="0/0")
            return
        
        t = self.uncategorized_transactions[self.current_transaction_idx]
        
        # Update display
        self.cat_date_label.config(text=t.date)
        amount_color = "green" if t.amount > 0 else "red"
        self.cat_amount_label.config(text=f"€{t.amount:.2f}", foreground=amount_color)
        
        self.cat_description.config(state=tk.NORMAL)
        self.cat_description.delete(1.0, tk.END)
        self.cat_description.insert(tk.END, t.description)
        self.cat_description.config(state=tk.DISABLED)
        
        # Update counter
        total = len(self.uncategorized_transactions)
        self.transaction_counter.config(text=f"{self.current_transaction_idx + 1}/{total}")
    
    def assign_category(self, category):
        """Assign category to current transaction and move to next"""
        if not self.uncategorized_transactions:
            return
        
        t = self.uncategorized_transactions[self.current_transaction_idx]
        
        if self.categorizer.categorize_transaction(t.id, category):
            self.next_transaction()
    
    def next_transaction(self):
        """Move to next transaction"""
        if self.current_transaction_idx < len(self.uncategorized_transactions) - 1:
            self.current_transaction_idx += 1
            self.display_transaction()
        else:
            messagebox.showinfo("Fin", "Toutes les transactions visibles ont été catégorisées!")
            self.refresh_categorization()
    
    def prev_transaction(self):
        """Move to previous transaction"""
        if self.current_transaction_idx > 0:
            self.current_transaction_idx -= 1
            self.display_transaction()
        else:
            messagebox.showinfo("Début", "Vous êtes déjà à la première transaction")
    
    def update_uncategorized_count(self):
        """Update uncategorized transactions count"""
        total = len(self.uncategorized_transactions)
        self.uncategorized_label.config(
            text=f"📊 {total} transaction(s) non catégorisée(s)"
        )
    
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


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = BankAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
