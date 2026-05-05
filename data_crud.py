import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class DataCRUDWindow:
    def __init__(self, parent, db, current_user, record_id=None):
        self.parent = parent
        self.db = db
        self.current_user = current_user
        self.record_id = record_id
        self.is_editing = record_id is not None
        
        self.dialog = tk.Toplevel(parent)
        title = "Edit Record" if self.is_editing else "Add Record"
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.field_entries = {}
        self.create_widgets()
        
        if self.is_editing:
            self.load_record_data()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = "Edit Record" if self.is_editing else "Add New Record"
        title_label = ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Get field configuration
        self.field_config = self.db.get_table_config()
        
        # Create scrollable frame for fields
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create field entries
        for i, (field_name, field_type, is_required, field_order) in enumerate(self.field_config):
            field_frame = ttk.Frame(scrollable_frame)
            field_frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Field label with required indicator
            display_name = field_name.replace('_', ' ').title()
            label_text = f"{display_name}:"
            if is_required:
                label_text += " *"
            label = ttk.Label(field_frame, text=label_text, width=15)
            label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Create appropriate entry widget based on field type
            if field_type == 'BOOLEAN':
                var = tk.BooleanVar()
                entry = ttk.Checkbutton(field_frame, variable=var)
                self.field_entries[field_name] = var
            elif field_type == 'INTEGER':
                var = tk.StringVar()
                entry = ttk.Entry(field_frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.field_entries[field_name] = var
            elif field_type == 'REAL':
                var = tk.StringVar()
                entry = ttk.Entry(field_frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.field_entries[field_name] = var
            else:  # TEXT
                var = tk.StringVar()
                entry = ttk.Entry(field_frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.field_entries[field_name] = var
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Save button
        save_button = ttk.Button(button_frame, text="Save", command=self.save_record)
        save_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy)
        cancel_button.pack(side=tk.RIGHT)
        
        # Required fields notice
        if any(is_required for _, _, is_required, _ in self.field_config):
            notice_label = ttk.Label(main_frame, text="* Required fields", font=('Arial', 9, 'italic'))
            notice_label.pack(pady=(5, 0))
    
    def load_record_data(self):
        """Load existing record data for editing"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM dynamic_data WHERE id = ?", (self.record_id,))
        record = cursor.fetchone()
        
        conn.close()
        
        if record:
            # Map field data to entries
            for i, (field_name, field_type, is_required, field_order) in enumerate(self.field_config):
                field_value = record[i + 1]  # Skip id column
                if field_name in self.field_entries:
                    if field_type == 'BOOLEAN':
                        self.field_entries[field_name].set(bool(field_value) if field_value else False)
                    else:
                        self.field_entries[field_name].set(field_value if field_value else '')
    
    def validate_fields(self):
        """Validate required fields"""
        errors = []
        
        for field_name, field_type, is_required, field_order in self.field_config:
            if is_required:
                value = self.field_entries[field_name].get()
                if field_type == 'BOOLEAN':
                    # For boolean fields, we don't require them to be True, just that they have a value
                    pass
                else:
                    if not value or not str(value).strip():
                        errors.append(f"{field_name} is required")
            
            # Type validation
            if field_name in self.field_entries:
                value = self.field_entries[field_name].get()
                if value and str(value).strip():
                    try:
                        if field_type == 'INTEGER':
                            int(value)
                        elif field_type == 'REAL':
                            float(value)
                    except ValueError:
                        errors.append(f"{field_name} must be a valid {field_type.lower()}")
        
        return errors
    
    def save_record(self):
        """Save the record"""
        # Validate fields
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Validation Error", "\\n".join(errors))
            return
        
        # Collect field data
        field_data = {}
        for field_name, field_type, is_required, field_order in self.field_config:
            value = self.field_entries[field_name].get()
            if field_type == 'BOOLEAN':
                field_data[field_name] = 1 if value else 0
            elif field_type == 'INTEGER':
                field_data[field_name] = int(value) if value else None
            elif field_type == 'REAL':
                field_data[field_name] = float(value) if value else None
            else:
                field_data[field_name] = str(value).strip() if value else ''
        
        try:
            if self.is_editing:
                self.db.update_record(self.record_id, field_data)
                messagebox.showinfo("Success", "Record updated successfully!")
            else:
                self.db.create_record(self.current_user['id'], field_data)
                messagebox.showinfo("Success", "Record created successfully!")
            
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save record: {str(e)}")
