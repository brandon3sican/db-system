import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from database import DatabaseManager
import os

class ExcelManager:
    def __init__(self, db):
        self.db = db
    
    def export_to_excel(self, include_archived=False):
        """Export database records to Excel file"""
        try:
            # Get records from database
            records = self.db.get_records(include_archived=include_archived)
            
            if not records:
                messagebox.showwarning("No Data", "No records to export.")
                return False
            
            # Get field configuration
            config = self.db.get_table_config()
            
            # Prepare data for DataFrame
            data = []
            for record in records:
                row = {}
                # Add ID
                row['ID'] = record[0]
                
                # Add field data
                for i, (field_name, field_type, is_required, field_order) in enumerate(config):
                    if i + 1 < len(record) - 3:  # Exclude metadata columns
                        display_name = field_name.replace('_', ' ').title()
                        row[display_name] = record[i + 1] if record[i + 1] else ''
                
                # Add metadata
                row['Created At'] = str(record[-3])[:19] if record[-3] else ''
                row['Updated At'] = str(record[-2])[:19] if record[-2] else ''
                row['Created By'] = record[-4] if record[-4] else 'Unknown'
                
                data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Ask user for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Excel File"
            )
            
            if file_path:
                # Export to Excel
                df.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("Success", f"Data exported successfully to {os.path.basename(file_path)}")
                return True
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
            return False
        
        return False
    
    def import_from_excel(self, current_user_id):
        """Import data from Excel file"""
        try:
            # Ask user for file location
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx"), ("Excel files", "*.xls"), ("All files", "*.*")],
                title="Select Excel File to Import"
            )
            
            if not file_path:
                return False
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            if df.empty:
                messagebox.showwarning("Empty File", "The Excel file is empty.")
                return False
            
            # Get field configuration
            config = self.db.get_table_config()
            
            # Validate columns
            required_columns = []
            for field_name, field_type, is_required, field_order in config:
                display_name = field_name.replace('_', ' ').title()
                required_columns.append(display_name)
            
            # Check if required columns exist
            missing_columns = []
            for col in required_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                messagebox.showerror(
                    "Column Mismatch", 
                    f"The following required columns are missing in the Excel file:\n{', '.join(missing_columns)}\n\n"
                    f"Expected columns: {', '.join(required_columns)}"
                )
                return False
            
            # Import data
            imported_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Prepare data for database
                    field_data = {}
                    for field_name, field_type, is_required, field_order in config:
                        display_name = field_name.replace('_', ' ').title()
                        
                        if display_name in df.columns:
                            value = row[display_name]
                            
                            # Handle NaN values
                            if pd.isna(value):
                                value = None
                            
                            # Type conversion
                            if field_type == 'INTEGER' and value is not None:
                                try:
                                    value = int(value)
                                except (ValueError, TypeError):
                                    value = None
                            elif field_type == 'REAL' and value is not None:
                                try:
                                    value = float(value)
                                except (ValueError, TypeError):
                                    value = None
                            elif field_type == 'BOOLEAN' and value is not None:
                                if isinstance(value, str):
                                    value = value.lower() in ['true', 'yes', '1', 'on']
                                else:
                                    value = bool(value)
                            
                            field_data[field_name] = value
                    
                    # Validate required fields
                    missing_required = []
                    for field_name, field_type, is_required, field_order in config:
                        if is_required and (field_name not in field_data or field_data[field_name] in [None, '', '']):
                            missing_required.append(field_name.replace('_', ' ').title())
                    
                    if missing_required:
                        error_count += 1
                        continue
                    
                    # Create record
                    self.db.create_record(current_user_id, field_data)
                    imported_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue
            
            # Show results
            message = f"Import completed!\n\n"
            message += f"Successfully imported: {imported_count} records\n"
            if error_count > 0:
                message += f"Failed to import: {error_count} records"
            
            messagebox.showinfo("Import Results", message)
            return True
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import data: {str(e)}")
            return False

class ExcelImportExportWindow:
    def __init__(self, parent, db, current_user):
        self.parent = parent
        self.db = db
        self.current_user = current_user
        self.excel_manager = ExcelManager(db)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Excel Import/Export")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Excel Import/Export", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Export section
        export_frame = ttk.LabelFrame(main_frame, text="Export Data", padding="15")
        export_frame.pack(fill=tk.X, pady=(0, 20))
        
        export_info = ttk.Label(export_frame, text="Export database records to Excel file for backup or analysis.", 
                               font=('Arial', 10), wraplength=400)
        export_info.pack(pady=(0, 10))
        
        # Export options
        self.include_archived_var = tk.BooleanVar()
        archived_check = ttk.Checkbutton(export_frame, text="Include archived records", 
                                         variable=self.include_archived_var)
        archived_check.pack(pady=(0, 10))
        
        export_button = ttk.Button(export_frame, text="Export to Excel", command=self.export_data)
        export_button.pack(pady=5)
        
        # Import section
        import_frame = ttk.LabelFrame(main_frame, text="Import Data", padding="15")
        import_frame.pack(fill=tk.X, pady=(0, 20))
        
        import_info = ttk.Label(import_frame, text="Import data from Excel file. The Excel file must have the correct column names.", 
                               font=('Arial', 10), wraplength=400)
        import_info.pack(pady=(0, 10))
        
        import_warning = ttk.Label(import_frame, text="⚠ Warning: Import will add new records. Make sure to backup your data first.", 
                                  font=('Arial', 9), foreground='orange')
        import_warning.pack(pady=(0, 10))
        
        import_button = ttk.Button(import_frame, text="Import from Excel", command=self.import_data)
        import_button.pack(pady=5)
        
        # Instructions section
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="15")
        instructions_frame.pack(fill=tk.BOTH, expand=True)
        
        instructions_text = """
        Export:
        1. Choose whether to include archived records
        2. Click 'Export to Excel' and save the file
        
        Import:
        1. Prepare Excel file with correct column names
        2. Click 'Import from Excel' and select the file
        3. Review import results
        
        Required columns depend on your database configuration.
        """
        
        instructions_label = ttk.Label(instructions_frame, text=instructions_text, 
                                       font=('Arial', 9), justify=tk.LEFT)
        instructions_label.pack(anchor=tk.W)
        
        # Close button
        close_button = ttk.Button(main_frame, text="Close", command=self.dialog.destroy)
        close_button.pack(pady=(10, 0))
    
    def export_data(self):
        """Handle export button click"""
        include_archived = self.include_archived_var.get()
        self.excel_manager.export_to_excel(include_archived)
    
    def import_data(self):
        """Handle import button click"""
        self.excel_manager.import_from_excel(self.current_user['id'])
