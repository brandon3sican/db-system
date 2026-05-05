import tkinter as tk
from tkinter import ttk, messagebox

class AdminConfigWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.field_configs = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Database Configuration")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.load_current_config()
        self.create_widgets()
        
    def load_current_config(self):
        """Load current field configuration from database"""
        config = self.db.get_table_config()
        self.field_configs = []
        for field_name, field_type, is_required, field_order in config:
            self.field_configs.append({
                'name': field_name,
                'type': field_type,
                'required': bool(is_required)
            })
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Configure Database Fields", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        info_label = ttk.Label(main_frame, text="Configure the fields for your database table. You can add, remove, or modify fields.", 
                               font=('Arial', 10), wraplength=500)
        info_label.pack(pady=(0, 20))
        
        # Field configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Field Configuration", padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create treeview for field configuration
        tree_frame = ttk.Frame(config_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.config_tree = ttk.Treeview(tree_frame, yscrollcommand=y_scrollbar.set, height=10)
        self.config_tree.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.config_tree.yview)
        
        # Configure columns
        self.config_tree['columns'] = ('name', 'type', 'required')
        self.config_tree.column('#0', width=0, stretch=tk.NO)
        self.config_tree.heading('#0', text='')
        
        self.config_tree.column('name', width=200, anchor=tk.W)
        self.config_tree.heading('name', text='Field Name')
        
        self.config_tree.column('type', width=150, anchor=tk.CENTER)
        self.config_tree.heading('type', text='Data Type')
        
        self.config_tree.column('required', width=100, anchor=tk.CENTER)
        self.config_tree.heading('required', text='Required')
        
        # Button frame
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add field button
        add_button = ttk.Button(button_frame, text="Add Field", command=self.add_field)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Edit field button
        edit_button = ttk.Button(button_frame, text="Edit Field", command=self.edit_field)
        edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Remove field button
        remove_button = ttk.Button(button_frame, text="Remove Field", command=self.remove_field)
        remove_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Move up button
        up_button = ttk.Button(button_frame, text="Move Up", command=self.move_field_up)
        up_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Move down button
        down_button = ttk.Button(button_frame, text="Move Down", command=self.move_field_down)
        down_button.pack(side=tk.LEFT)
        
        # Populate treeview
        self.populate_treeview()
        
        # Bottom button frame
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)
        
        # Save button
        save_button = ttk.Button(bottom_frame, text="Save Configuration", command=self.save_configuration)
        save_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Cancel button
        cancel_button = ttk.Button(bottom_frame, text="Cancel", command=self.dialog.destroy)
        cancel_button.pack(side=tk.RIGHT)
    
    def populate_treeview(self):
        """Populate the treeview with current field configuration"""
        # Clear existing items
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)
        
        # Add field configurations
        for config in self.field_configs:
            required_text = "Yes" if config['required'] else "No"
            self.config_tree.insert('', tk.END, values=(
                config['name'],
                config['type'],
                required_text
            ))
    
    def add_field(self):
        """Add a new field"""
        dialog = FieldEditDialog(self.dialog, "Add Field")
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.field_configs.append(dialog.result)
            self.populate_treeview()
    
    def edit_field(self):
        """Edit selected field"""
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a field to edit.")
            return
        
        item = self.config_tree.item(selection[0])
        field_index = self.config_tree.get_children().index(selection[0])
        
        current_config = self.field_configs[field_index]
        dialog = FieldEditDialog(self.dialog, "Edit Field", current_config)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.field_configs[field_index] = dialog.result
            self.populate_treeview()
    
    def remove_field(self):
        """Remove selected field"""
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a field to remove.")
            return
        
        field_index = self.config_tree.get_children().index(selection[0])
        
        if messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove the field '{self.field_configs[field_index]['name']}'?"):
            del self.field_configs[field_index]
            self.populate_treeview()
    
    def move_field_up(self):
        """Move field up in order"""
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a field to move.")
            return
        
        field_index = self.config_tree.get_children().index(selection[0])
        
        if field_index > 0:
            # Swap with previous field
            self.field_configs[field_index], self.field_configs[field_index - 1] = \
                self.field_configs[field_index - 1], self.field_configs[field_index]
            self.populate_treeview()
            # Select the moved item
            new_selection = self.config_tree.get_children()[field_index - 1]
            self.config_tree.selection_set(new_selection)
    
    def move_field_down(self):
        """Move field down in order"""
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a field to move.")
            return
        
        field_index = self.config_tree.get_children().index(selection[0])
        
        if field_index < len(self.field_configs) - 1:
            # Swap with next field
            self.field_configs[field_index], self.field_configs[field_index + 1] = \
                self.field_configs[field_index + 1], self.field_configs[field_index]
            self.populate_treeview()
            # Select the moved item
            new_selection = self.config_tree.get_children()[field_index + 1]
            self.config_tree.selection_set(new_selection)
    
    def save_configuration(self):
        """Save the field configuration to database"""
        if len(self.field_configs) == 0:
            messagebox.showerror("Error", "You must have at least one field.")
            return
        
        # Validate field names
        field_names = [config['name'] for config in self.field_configs]
        if len(field_names) != len(set(field_names)):
            messagebox.showerror("Error", "Field names must be unique.")
            return
        
        # Check for empty field names
        for config in self.field_configs:
            if not config['name'].strip():
                messagebox.showerror("Error", "Field names cannot be empty.")
                return
        
        try:
            self.db.update_table_config(self.field_configs)
            messagebox.showinfo("Success", "Database configuration saved successfully!")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

class FieldEditDialog:
    def __init__(self, parent, title, current_config=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"400x250+{x}+{y}")
        
        self.current_config = current_config
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Field name
        ttk.Label(main_frame, text="Field Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Data type
        ttk.Label(main_frame, text="Data Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value="TEXT")
        self.type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, width=27, state="readonly")
        self.type_combo['values'] = ('TEXT', 'INTEGER', 'REAL', 'BOOLEAN')
        self.type_combo.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Required checkbox
        self.required_var = tk.BooleanVar()
        self.required_check = ttk.Checkbutton(main_frame, text="Required Field", variable=self.required_var)
        self.required_check.grid(row=2, column=0, columnspan=2, pady=20, sticky=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # OK button
        ok_button = ttk.Button(button_frame, text="OK", command=self.ok_clicked)
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy)
        cancel_button.pack(side=tk.RIGHT)
        
        # Load current config if editing
        if self.current_config:
            self.name_entry.insert(0, self.current_config['name'])
            self.type_var.set(self.current_config['type'])
            self.required_var.set(self.current_config['required'])
        
        # Set focus to name entry
        self.name_entry.focus()
    
    def ok_clicked(self):
        name = self.name_entry.get().strip()
        field_type = self.type_var.get()
        required = self.required_var.get()
        
        if not name:
            messagebox.showerror("Error", "Field name cannot be empty.")
            return
        
        # Validate field name (no special characters, no spaces)
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            messagebox.showerror("Error", "Field name must start with a letter or underscore and contain only letters, numbers, and underscores.")
            return
        
        self.result = {
            'name': name,
            'type': field_type,
            'required': required
        }
        
        self.dialog.destroy()
