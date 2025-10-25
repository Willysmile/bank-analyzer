"""
GUI module - Graphical User Interface with Tkinter
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from datetime import datetime
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
        self.import_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.categories_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.import_tab, text="📥 Import")
        self.notebook.add(self.transactions_tab, text="📋 Transactions")
        self.notebook.add(self.categories_tab, text="📂 Catégories")
        self.notebook.add(self.report_tab, text="📊 Rapports")
        self.notebook.add(self.settings_tab, text="⚙️ Paramètres")
        
        # Setup each tab
        self.setup_import_tab()
        self.setup_transactions_tab()
        self.setup_categories_tab()
        self.setup_report_tab()
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


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = BankAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
