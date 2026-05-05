import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class SearchManager:
    def __init__(self, db, current_user):
        self.db = db
        self.current_user = current_user
        
    def search_records(self, search_criteria):
        """Search records based on criteria"""
        try:
            # Get all records
            records = self.db.get_records(include_archived=False)
            
            if not records:
                return []
            
            # Get field configuration
            config = self.db.get_table_config()
            
            # Prepare search term
            search_term = search_criteria['search_term']
            if not search_criteria['case_sensitive']:
                search_term = search_term.lower()
            
            # Filter records based on search criteria
            filtered_records = []
            
            for record in records:
                match = False
                
                # Check each field for match
                for i, (field_name, field_type, is_required, field_order) in enumerate(config):
                    if i + 1 < len(record) - 3:  # Exclude metadata columns
                        field_value = str(record[i + 1]) if record[i + 1] else ''
                        
                        # Apply case sensitivity
                        compare_value = field_value if search_criteria['case_sensitive'] else field_value.lower()
                        
                        # Check if field value matches search criteria
                        if search_criteria['field_name'] == 'all':
                            # Search in all fields
                            if search_criteria['exact_match']:
                                if compare_value == search_term:
                                    match = True
                                    break
                            else:
                                if search_term in compare_value:
                                    match = True
                                    break
                        else:
                            # Search in specific field
                            if field_name == search_criteria['field_name']:
                                if search_criteria['exact_match']:
                                    if compare_value == search_term:
                                        match = True
                                else:
                                    if search_term in compare_value:
                                        match = True
                                break
                
                # Also check metadata fields if searching in all fields
                if not match and search_criteria['field_name'] == 'all':
                    # Check created_by
                    created_by = str(record[-4]) if record[-4] else ''
                    compare_created_by = created_by if search_criteria['case_sensitive'] else created_by.lower()
                    
                    if search_criteria['exact_match']:
                        if compare_created_by == search_term:
                            match = True
                    else:
                        if search_term in compare_created_by:
                            match = True
                    
                    # Check dates
                    if not match:
                        created_at = str(record[-3])[:19] if record[-3] else ''
                        compare_created_at = created_at if search_criteria['case_sensitive'] else created_at.lower()
                        
                        if search_criteria['exact_match']:
                            if compare_created_at == search_term:
                                match = True
                        else:
                            if search_term in compare_created_at:
                                match = True
                
                if match:
                    filtered_records.append(record)
            
            return filtered_records
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Error during search: {str(e)}")
            return []

class SearchWindow:
    def __init__(self, parent, db, current_user, on_search_callback):
        self.parent = parent
        self.db = db
        self.current_user = current_user
        self.on_search_callback = on_search_callback
        self.search_manager = SearchManager(db, current_user)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Search Records")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"400x250+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Search Records", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Search criteria frame
        criteria_frame = ttk.LabelFrame(main_frame, text="Search Criteria", padding="15")
        criteria_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Field selection
        ttk.Label(criteria_frame, text="Search in:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Get field configuration for dropdown
        config = self.db.get_table_config()
        field_options = [('All Fields', 'all')]
        for field_name, field_type, is_required, field_order in config:
            display_name = field_name.replace('_', ' ').title()
            field_options.append((display_name, field_name))
        
        self.field_var = tk.StringVar(value='all')
        self.field_combo = ttk.Combobox(criteria_frame, textvariable=self.field_var, width=30, state="readonly")
        self.field_combo['values'] = [option[0] for option in field_options]
        self.field_combo.grid(row=0, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        
        # Store field mapping
        self.field_mapping = {option[0]: option[1] for option in field_options}
        
        # Search term
        ttk.Label(criteria_frame, text="Search term:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.search_entry = ttk.Entry(criteria_frame, width=32)
        self.search_entry.grid(row=1, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        
                
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Search button
        search_button = ttk.Button(button_frame, text="Search", command=self.perform_search)
        search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_search)
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", command=self.dialog.destroy)
        close_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda event: self.perform_search())
        
        # Set focus to search entry
        self.search_entry.focus()
    
    def perform_search(self):
        """Perform the search"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showwarning("Empty Search", "Please enter a search term.")
            return
        
        # Get selected field
        selected_display = self.field_var.get()
        field_name = self.field_mapping.get(selected_display, 'all')
        
        # Prepare search criteria
        search_criteria = {
            'field_name': field_name,
            'search_term': search_term,
            'case_sensitive': False,  # Default to case-insensitive
            'exact_match': False      # Default to partial match
        }
        
        # Perform search
        results = self.search_manager.search_records(search_criteria)
        
        # Show results
        if results:
            messagebox.showinfo("Search Results", f"Found {len(results)} matching records.")
            
            # Call callback to update main table
            if self.on_search_callback:
                self.on_search_callback(results, search_criteria)
            
            self.dialog.destroy()
        else:
            messagebox.showinfo("Search Results", "No matching records found.")
    
    def clear_search(self):
        """Clear search fields"""
        self.search_entry.delete(0, tk.END)
        self.field_var.set('all')
        self.search_entry.focus()
