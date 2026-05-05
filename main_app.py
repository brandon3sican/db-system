import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager
from data_crud import DataCRUDWindow
from admin_config import AdminConfigWindow
from user_management import UserManagementWindow
from excel_manager import ExcelImportExportWindow
from search_manager import SearchWindow

class MainApplication:
    def __init__(self, current_user, on_logout_callback=None):
        self.current_user = current_user
        self.db = DatabaseManager()
        self.on_logout_callback = on_logout_callback
        
        self.window = tk.Tk()
        self.window.title("Database System - Main Application")
        self.window.geometry("1200x800")
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.window.winfo_screenheight() // 2) - (800 // 2)
        self.window.geometry(f"1200x800+{x}+{y}")
        
        self.create_widgets()
        self.refresh_data()
        
    def create_widgets(self):
        # Create menu bar
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import/Export Excel", command=self.open_excel_manager)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        
        # Admin menu (only for admin users)
        if self.current_user['role'] == 'admin':
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Admin", menu=admin_menu)
            admin_menu.add_command(label="Database Configuration", command=self.open_admin_config)
            admin_menu.add_command(label="User Management", command=self.open_user_management)
        
        # Main container
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header frame
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # User info
        user_label = ttk.Label(header_frame, text=f"Logged in as: {self.current_user['username']} ({self.current_user['role']})", 
                               font=('Arial', 12, 'bold'))
        user_label.pack(side=tk.LEFT)
        
        # Logout button
        logout_button = ttk.Button(header_frame, text="Logout", command=self.logout)
        logout_button.pack(side=tk.RIGHT)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Data Management tab
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Data Management")
        
        # Archived data tab (only for admin)
        if self.current_user['role'] == 'admin':
            self.archived_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.archived_frame, text="Archived Records")
        
        self.create_data_tab()
        
        if self.current_user['role'] == 'admin':
            self.create_archived_tab()
    
    def create_data_tab(self):
        # Toolbar frame
        toolbar_frame = ttk.Frame(self.data_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add button
        add_button = ttk.Button(toolbar_frame, text="Add Record", command=self.add_record)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Edit button
        self.edit_button = ttk.Button(toolbar_frame, text="Edit Record", command=self.edit_record, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Archive button (users can archive, admins can delete)
        if self.current_user['role'] == 'admin':
            self.delete_button = ttk.Button(toolbar_frame, text="Delete Record", command=self.delete_record, state=tk.DISABLED)
            self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
        else:
            self.archive_button = ttk.Button(toolbar_frame, text="Archive Record", command=self.archive_record, state=tk.DISABLED)
            self.archive_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        separator = ttk.Separator(toolbar_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, padx=(10, 5), fill=tk.Y)
        
        # Search button
        search_button = ttk.Button(toolbar_frame, text="Search", command=self.open_search)
        search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear search button
        self.clear_search_button = ttk.Button(toolbar_frame, text="Clear Search", command=self.clear_search, state=tk.DISABLED)
        self.clear_search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Backup button
        backup_button = ttk.Button(toolbar_frame, text="Backup", command=self.backup_database)
        backup_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Upload DB button
        upload_db_button = ttk.Button(toolbar_frame, text="Upload DB", command=self.upload_database)
        upload_db_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Network Sync button
        sync_button = ttk.Button(toolbar_frame, text="Sync", command=self.network_sync)
        sync_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh button
        refresh_button = ttk.Button(toolbar_frame, text="Refresh", command=self.refresh_data)
        refresh_button.pack(side=tk.RIGHT)
        
        # Create treeview for data display
        tree_frame = ttk.Frame(self.data_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.data_tree = ttk.Treeview(tree_frame, yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.data_tree.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.data_tree.yview)
        x_scrollbar.config(command=self.data_tree.xview)
        
        # Bind selection event
        self.data_tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Configure columns based on table configuration
        self.configure_tree_columns()
    
    def create_archived_tab(self):
        # Toolbar frame
        toolbar_frame = ttk.Frame(self.archived_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Restore button
        self.restore_button = ttk.Button(toolbar_frame, text="Restore Record", command=self.restore_record, state=tk.DISABLED)
        self.restore_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete permanently button
        self.permanent_delete_button = ttk.Button(toolbar_frame, text="Delete Permanently", command=self.permanent_delete_record, state=tk.DISABLED)
        self.permanent_delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh button
        refresh_button = ttk.Button(toolbar_frame, text="Refresh", command=self.refresh_archived_data)
        refresh_button.pack(side=tk.RIGHT)
        
        # Create treeview for archived data
        tree_frame = ttk.Frame(self.archived_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.archived_tree = ttk.Treeview(tree_frame, yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.archived_tree.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.archived_tree.yview)
        x_scrollbar.config(command=self.archived_tree.xview)
        
        # Bind selection event
        self.archived_tree.bind('<<TreeviewSelect>>', self.on_archived_select)
        
        # Configure columns
        self.configure_archived_tree_columns()
    
    def configure_tree_columns(self):
        # Get table configuration
        config = self.db.get_table_config()
        
        # Configure columns (exclude ID from display)
        columns = [f'field_{i+1}' for i in range(len(config))] + ['created_at', 'updated_at', 'created_by']
        self.data_tree['columns'] = columns
        
        # Hide the first column (tree column)
        self.data_tree.column('#0', width=0, stretch=tk.NO)
        self.data_tree.heading('#0', text='')
        
        for i, (field_name, field_type, is_required, field_order) in enumerate(config):
            col_name = f'field_{i+1}'
            self.data_tree.column(col_name, width=150, anchor=tk.W)
            # Convert field names to user-friendly labels
            display_name = field_name.replace('_', ' ').title()
            self.data_tree.heading(col_name, text=display_name)
        
        self.data_tree.column('created_at', width=150, anchor=tk.CENTER)
        self.data_tree.heading('created_at', text='Created At')
        
        self.data_tree.column('updated_at', width=150, anchor=tk.CENTER)
        self.data_tree.heading('updated_at', text='Updated At')
        
        self.data_tree.column('created_by', width=100, anchor=tk.CENTER)
        self.data_tree.heading('created_by', text='Created By')
    
    def configure_archived_tree_columns(self):
        # Same as data tree but for archived records
        config = self.db.get_table_config()
        
        # Configure columns (exclude ID from display)
        columns = [f'field_{i+1}' for i in range(len(config))] + ['created_at', 'updated_at', 'created_by']
        self.archived_tree['columns'] = columns
        
        # Hide the first column
        self.archived_tree.column('#0', width=0, stretch=tk.NO)
        self.archived_tree.heading('#0', text='')
        
        for i, (field_name, field_type, is_required, field_order) in enumerate(config):
            col_name = f'field_{i+1}'
            self.archived_tree.column(col_name, width=150, anchor=tk.W)
            # Convert field names to user-friendly labels
            display_name = field_name.replace('_', ' ').title()
            self.archived_tree.heading(col_name, text=display_name)
        
        self.archived_tree.column('created_at', width=150, anchor=tk.CENTER)
        self.archived_tree.heading('created_at', text='Created At')
        
        self.archived_tree.column('updated_at', width=150, anchor=tk.CENTER)
        self.archived_tree.heading('updated_at', text='Updated At')
        
        self.archived_tree.column('created_by', width=100, anchor=tk.CENTER)
        self.archived_tree.heading('created_by', text='Created By')
    
    def refresh_data(self):
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Get records from database
        records = self.db.get_records()
        
        # Insert records into treeview
        for record in records:
            # Format the record for display (exclude ID)
            # Record structure: [id, field_1, field_2, field_3, field_4, field_5, created_at, updated_at, created_by, is_archived, username]
            # We only have 4 configured fields: first_name, middle_name, last_name, suffix
            display_record = [
                record[1] or '',  # field_1 (First Name)
                record[2] or '',  # field_2 (Middle Name)
                record[3] or '',  # field_3 (Last Name)
                record[4] or '',  # field_4 (Suffix)
                str(record[6])[:19] if record[6] else '',  # created_at (skip field_5)
                str(record[7])[:19] if record[7] else '',  # updated_at
                record[10] or 'Unknown'  # username
            ]
            
            self.data_tree.insert('', tk.END, values=display_record)
    
    def refresh_archived_data(self):
        # Clear existing data
        for item in self.archived_tree.get_children():
            self.archived_tree.delete(item)
        
        # Get archived records from database
        records = self.db.get_records(include_archived=True)
        archived_records = [r for r in records if r[9] == 1]  # is_archived = 1
        
        # Insert archived records into treeview
        for record in archived_records:
            # Record structure: [id, field_1, field_2, field_3, field_4, field_5, created_at, updated_at, created_by, is_archived, username]
            # We only have 4 configured fields: first_name, middle_name, last_name, suffix
            display_record = [
                record[1] or '',  # field_1 (First Name)
                record[2] or '',  # field_2 (Middle Name)
                record[3] or '',  # field_3 (Last Name)
                record[4] or '',  # field_4 (Suffix)
                str(record[6])[:19] if record[6] else '',  # created_at (skip field_5)
                str(record[7])[:19] if record[7] else '',  # updated_at
                record[10] or 'Unknown'  # username
            ]
            
            self.archived_tree.insert('', tk.END, values=display_record)
    
    def on_select(self, event):
        selection = self.data_tree.selection()
        if selection:
            if self.current_user['role'] == 'admin':
                self.edit_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)
            else:
                self.edit_button.config(state=tk.NORMAL)
                self.archive_button.config(state=tk.NORMAL)
        else:
            if self.current_user['role'] == 'admin':
                self.edit_button.config(state=tk.DISABLED)
                self.delete_button.config(state=tk.DISABLED)
            else:
                self.edit_button.config(state=tk.DISABLED)
                self.archive_button.config(state=tk.DISABLED)
    
    def on_archived_select(self, event):
        selection = self.archived_tree.selection()
        if selection:
            self.restore_button.config(state=tk.NORMAL)
            self.permanent_delete_button.config(state=tk.NORMAL)
        else:
            self.restore_button.config(state=tk.DISABLED)
            self.permanent_delete_button.config(state=tk.DISABLED)
    
    def add_record(self):
        dialog = DataCRUDWindow(self.window, self.db, self.current_user, None)
        self.window.wait_window(dialog.dialog)
        self.refresh_data()
    
    def get_record_id_from_selection(self, tree):
        """Get record ID from selected tree item"""
        selection = tree.selection()
        if not selection:
            return None
        
        item = tree.item(selection[0])
        values = item['values']
        
        # Since we removed ID from display, we need to find the record by matching unique values
        # Get all records and find the matching one
        all_records = self.db.get_records()
        
        for record in all_records:
            # Create display version of this record to match
            display_record = [
                record[1] or '',  # field_1 (First Name)
                record[2] or '',  # field_2 (Middle Name)
                record[3] or '',  # field_3 (Last Name)
                record[4] or '',  # field_4 (Suffix)
                str(record[6])[:19] if record[6] else '',  # created_at (skip field_5)
                str(record[7])[:19] if record[7] else '',  # updated_at
                record[10] or 'Unknown'  # username
            ]
            
            # Compare with selected values
            if display_record == list(values):
                return record[0]  # Return the ID
        
        return None
    
    def edit_record(self):
        record_id = self.get_record_id_from_selection(self.data_tree)
        if not record_id:
            return
        
        dialog = DataCRUDWindow(self.window, self.db, self.current_user, record_id)
        self.window.wait_window(dialog.dialog)
        self.refresh_data()
    
    def archive_record(self):
        record_id = self.get_record_id_from_selection(self.data_tree)
        if not record_id:
            return
        
        if messagebox.askyesno("Confirm Archive", "Are you sure you want to archive this record?"):
            self.db.archive_record(record_id)
            messagebox.showinfo("Success", "Record archived successfully")
            self.refresh_data()
    
    def delete_record(self):
        record_id = self.get_record_id_from_selection(self.data_tree)
        if not record_id:
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record permanently?"):
            self.db.delete_record(record_id)
            messagebox.showinfo("Success", "Record deleted successfully")
            self.refresh_data()
    
    def restore_record(self):
        record_id = self.get_record_id_from_selection(self.archived_tree)
        if not record_id:
            return
        
        if messagebox.askyesno("Confirm Restore", "Are you sure you want to restore this record?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE dynamic_data SET is_archived = 0 WHERE id = ?", (record_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Record restored successfully")
            self.refresh_archived_data()
            self.refresh_data()
    
    def permanent_delete_record(self):
        record_id = self.get_record_id_from_selection(self.archived_tree)
        if not record_id:
            return
        
        if messagebox.askyesno("Confirm Permanent Delete", "Are you sure you want to permanently delete this record? This action cannot be undone."):
            self.db.delete_record(record_id)
            messagebox.showinfo("Success", "Record permanently deleted")
            self.refresh_archived_data()
    
    def open_admin_config(self):
        dialog = AdminConfigWindow(self.window, self.db)
        self.window.wait_window(dialog.dialog)
        # Refresh the treeview columns as they might have changed
        self.configure_tree_columns()
        self.configure_archived_tree_columns()
        self.refresh_data()
    
    def open_user_management(self):
        dialog = UserManagementWindow(self.window, self.db)
        self.window.wait_window(dialog.dialog)
    
    def open_excel_manager(self):
        dialog = ExcelImportExportWindow(self.window, self.db, self.current_user)
        self.window.wait_window(dialog.dialog)
        # Refresh data after import/export
        self.refresh_data()
        if self.current_user['role'] == 'admin':
            self.refresh_archived_data()
    
    def open_search(self):
        """Open search window"""
        dialog = SearchWindow(self.window, self.db, self.current_user, self.on_search_results)
        self.window.wait_window(dialog.dialog)
    
    def on_search_results(self, results, search_criteria):
        """Handle search results"""
        # Clear current data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Get field configuration
        config = self.db.get_table_config()
        
        # Insert search results into treeview
        for record in results:
            # Record structure: [id, field_1, field_2, field_3, field_4, field_5, created_at, updated_at, created_by, is_archived, username]
            # We only have 4 configured fields: first_name, middle_name, last_name, suffix
            display_record = [
                record[1] or '',  # field_1 (First Name)
                record[2] or '',  # field_2 (Middle Name)
                record[3] or '',  # field_3 (Last Name)
                record[4] or '',  # field_4 (Suffix)
                str(record[6])[:19] if record[6] else '',  # created_at (skip field_5)
                str(record[7])[:19] if record[7] else '',  # updated_at
                record[10] or 'Unknown'  # username
            ]
            
            self.data_tree.insert('', tk.END, values=display_record)
        
        # Enable clear search button
        self.clear_search_button.config(state=tk.NORMAL)
        
        # Update window title to show search is active
        self.window.title("Database System - Main Application [SEARCH RESULTS]")
    
    def clear_search(self):
        """Clear search results and show all data"""
        # Refresh to show all data
        self.refresh_data()
        
        # Disable clear search button
        self.clear_search_button.config(state=tk.DISABLED)
        
        # Reset window title
        self.window.title("Database System - Main Application")
    
    def backup_database(self):
        """Create a backup of the database"""
        try:
            import shutil
            from datetime import datetime
            
            # Get current timestamp for backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"database_backup_{timestamp}.db"
            
            # Copy the database file
            shutil.copy2("database_system.db", backup_filename)
            
            messagebox.showinfo("Backup Successful", f"Database backed up successfully as:\n{backup_filename}")
            
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Failed to backup database:\n{str(e)}")
    
    def upload_database(self):
        """Upload and restore a database file"""
        try:
            from tkinter import filedialog
            
            # Ask user to select database file
            file_path = filedialog.askopenfilename(
                title="Select Database File",
                filetypes=[("Database Files", "*.db"), ("All Files", "*.*")]
            )
            
            if not file_path:
                return  # User cancelled
            
            # Confirm upload
            if messagebox.askyesno(
                "Confirm Upload", 
                f"Are you sure you want to upload and restore:\n{file_path}\n\nThis will replace the current database!"
            ):
                import shutil
                import os
                
                # Create backup of current database before upload
                if os.path.exists("database_system.db"):
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"pre_upload_backup_{timestamp}.db"
                    shutil.copy2("database_system.db", backup_filename)
                
                # Copy the uploaded database
                shutil.copy2(file_path, "database_system.db")
                
                # Refresh data to show uploaded database
                self.refresh_data()
                if self.current_user['role'] == 'admin':
                    self.refresh_archived_data()
                
                messagebox.showinfo(
                    "Upload Successful", 
                    f"Database uploaded successfully!\n\nPrevious database backed up as:\npre_upload_backup_{timestamp}.db"
                )
                
        except Exception as e:
            messagebox.showerror("Upload Failed", f"Failed to upload database:\n{str(e)}")
    
    def network_sync(self):
        """Network sync options for data transfer between computers"""
        try:
            from tkinter import filedialog, simpledialog
            import os
            
            # Create sync options dialog
            sync_window = tk.Toplevel(self.window)
            sync_window.title("Network Sync Options")
            sync_window.geometry("500x400")
            sync_window.transient(self.window)
            sync_window.grab_set()
            
            # Center the dialog
            sync_window.update_idletasks()
            x = (sync_window.winfo_screenwidth() // 2) - (250)
            y = (sync_window.winfo_screenheight() // 2) - (200)
            sync_window.geometry(f"500x400+{x}+{y}")
            
            main_frame = ttk.Frame(sync_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="Data Transfer Options", font=('Arial', 14, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # Option 1: Export to Network Location
            export_frame = ttk.LabelFrame(main_frame, text="Export to Network/Shared Folder", padding="15")
            export_frame.pack(fill=tk.X, pady=(0, 15))
            
            export_text = """
1. Click 'Export Database' to save current data
2. Choose a network/shared folder location
3. Other computers can import from this location
4. Perfect for office networks or shared drives
            """
            ttk.Label(export_frame, text=export_text, justify=tk.LEFT).pack(anchor=tk.W)
            
            ttk.Button(export_frame, text="Export Database", command=lambda: self.export_to_network(sync_window)).pack(pady=(10, 0))
            
            # Option 2: Import from Network Location
            import_frame = ttk.LabelFrame(main_frame, text="Import from Network/Shared Folder", padding="15")
            import_frame.pack(fill=tk.X, pady=(0, 15))
            
            import_text = """
1. Click 'Import Database' to load data from network
2. Select database file from shared location
3. Current data will be backed up automatically
4. Updates your local database with network data
            """
            ttk.Label(import_frame, text=import_text, justify=tk.LEFT).pack(anchor=tk.W)
            
            ttk.Button(import_frame, text="Import Database", command=lambda: self.import_from_network(sync_window)).pack(pady=(10, 0))
            
            # Option 3: Excel Transfer
            excel_frame = ttk.LabelFrame(main_frame, text="Excel File Transfer", padding="15")
            excel_frame.pack(fill=tk.X, pady=(0, 15))
            
            excel_text = """
1. Use Excel Export to create data file
2. Transfer Excel file via email, USB, or cloud
3. Other computer uses Excel Import
4. Works between any computers, no network needed
            """
            ttk.Label(excel_frame, text=excel_text, justify=tk.LEFT).pack(anchor=tk.W)
            
            excel_button_frame = ttk.Frame(excel_frame)
            excel_button_frame.pack(pady=(10, 0))
            
            ttk.Button(excel_button_frame, text="Excel Export", command=lambda: self.excel_export_sync(sync_window)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(excel_button_frame, text="Excel Import", command=lambda: self.excel_import_sync(sync_window)).pack(side=tk.LEFT)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=sync_window.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to open sync options:\n{str(e)}")
    
    def export_to_network(self, parent_window):
        """Export database to network/shared folder"""
        try:
            from tkinter import filedialog
            import shutil
            from datetime import datetime
            
            # Ask for network location
            file_path = filedialog.asksaveasfilename(
                title="Save Database to Network Location",
                defaultextension=".db",
                filetypes=[("Database Files", "*.db"), ("All Files", "*.*")],
                initialname=f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            
            if file_path:
                shutil.copy2("database_system.db", file_path)
                messagebox.showinfo("Export Successful", f"Database exported to:\n{file_path}")
                parent_window.destroy()
                
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export database:\n{str(e)}")
    
    def import_from_network(self, parent_window):
        """Import database from network/shared folder"""
        self.upload_database()
        parent_window.destroy()
    
    def excel_export_sync(self, parent_window):
        """Excel export for data transfer"""
        self.open_excel_manager()
        parent_window.destroy()
    
    def excel_import_sync(self, parent_window):
        """Excel import for data transfer"""
        self.open_excel_manager()
        parent_window.destroy()
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.window.destroy()
            # Call the logout callback to notify the main app
            if self.on_logout_callback:
                self.on_logout_callback()
    
    def run(self):
        self.window.mainloop()
