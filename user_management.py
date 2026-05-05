import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class UserManagementWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("User Management")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        self.create_widgets()
        self.load_users()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="User Management", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Toolbar frame
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add user button
        add_button = ttk.Button(toolbar_frame, text="Add User", command=self.add_user)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Edit user button
        self.edit_button = ttk.Button(toolbar_frame, text="Edit User", command=self.edit_user, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete user button
        self.delete_button = ttk.Button(toolbar_frame, text="Delete User", command=self.delete_user, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Toggle active status button
        self.toggle_button = ttk.Button(toolbar_frame, text="Toggle Active Status", command=self.toggle_active, state=tk.DISABLED)
        self.toggle_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh button
        refresh_button = ttk.Button(toolbar_frame, text="Refresh", command=self.load_users)
        refresh_button.pack(side=tk.RIGHT)
        
        # Create treeview for user display
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.user_tree = ttk.Treeview(tree_frame, yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.user_tree.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.user_tree.yview)
        x_scrollbar.config(command=self.user_tree.xview)
        
        # Configure columns
        self.user_tree['columns'] = ('id', 'username', 'role', 'created_at', 'is_active')
        self.user_tree.column('#0', width=0, stretch=tk.NO)
        self.user_tree.heading('#0', text='')
        
        self.user_tree.column('id', width=50, anchor=tk.CENTER)
        self.user_tree.heading('id', text='ID')
        
        self.user_tree.column('username', width=200, anchor=tk.W)
        self.user_tree.heading('username', text='Username')
        
        self.user_tree.column('role', width=100, anchor=tk.CENTER)
        self.user_tree.heading('role', text='Role')
        
        self.user_tree.column('created_at', width=150, anchor=tk.CENTER)
        self.user_tree.heading('created_at', text='Created At')
        
        self.user_tree.column('is_active', width=100, anchor=tk.CENTER)
        self.user_tree.heading('is_active', text='Active')
        
        # Bind selection event
        self.user_tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Bottom button frame
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Close button
        close_button = ttk.Button(bottom_frame, text="Close", command=self.dialog.destroy)
        close_button.pack(side=tk.RIGHT)
    
    def load_users(self):
        """Load users from database"""
        # Clear existing data
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Get users from database
        users = self.db.get_users()
        
        # Insert users into treeview
        for user in users:
            user_id, username, role, created_at, is_active = user
            active_text = "Yes" if is_active else "No"
            created_text = str(created_at)[:19] if created_at else ''
            
            self.user_tree.insert('', tk.END, values=(
                user_id,
                username,
                role,
                created_text,
                active_text
            ))
    
    def on_select(self, event):
        """Handle user selection"""
        selection = self.user_tree.selection()
        if selection:
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.toggle_button.config(state=tk.NORMAL)
        else:
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.toggle_button.config(state=tk.DISABLED)
    
    def add_user(self):
        """Add a new user"""
        dialog = UserEditDialog(self.dialog, "Add User")
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                self.db.create_user(
                    dialog.result['username'],
                    dialog.result['password'],
                    dialog.result['role']
                )
                messagebox.showinfo("Success", "User created successfully!")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create user: {str(e)}")
    
    def edit_user(self):
        """Edit selected user"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = self.user_tree.item(selection[0])
        user_data = item['values']
        user_id = user_data[0]
        
        # Get current user data
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, is_active FROM users WHERE id = ?", (user_id,))
        user_info = cursor.fetchone()
        conn.close()
        
        if user_info:
            current_user = {
                'id': user_id,
                'username': user_info[0],
                'role': user_info[1],
                'is_active': bool(user_info[2])
            }
            
            dialog = UserEditDialog(self.dialog, "Edit User", current_user)
            self.dialog.wait_window(dialog.dialog)
            
            if dialog.result:
                try:
                    self.db.update_user(
                        user_id,
                        dialog.result['username'],
                        dialog.result['role'],
                        dialog.result['is_active']
                    )
                    messagebox.showinfo("Success", "User updated successfully!")
                    self.load_users()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update user: {str(e)}")
    
    def delete_user(self):
        """Delete selected user"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = self.user_tree.item(selection[0])
        user_data = item['values']
        user_id = user_data[0]
        username = user_data[1]
        
        # Prevent deletion of admin user (id = 1)
        if user_id == 1:
            messagebox.showerror("Error", "Cannot delete the admin user!")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}'? This action cannot be undone."):
            try:
                self.db.delete_user(user_id)
                messagebox.showinfo("Success", "User deleted successfully!")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def toggle_active(self):
        """Toggle active status of selected user"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = self.user_tree.item(selection[0])
        user_data = item['values']
        user_id = user_data[0]
        username = user_data[1]
        is_active = user_data[4] == "Yes"
        
        # Prevent deactivation of admin user (id = 1)
        if user_id == 1:
            messagebox.showerror("Error", "Cannot deactivate the admin user!")
            return
        
        new_status = not is_active
        status_text = "activate" if new_status else "deactivate"
        
        if messagebox.askyesno("Confirm Status Change", f"Are you sure you want to {status_text} user '{username}'?"):
            try:
                self.db.update_user(user_id, username, None, new_status)
                messagebox.showinfo("Success", f"User {status_text}d successfully!")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update user status: {str(e)}")

class UserEditDialog:
    def __init__(self, parent, title, current_user=None):
        self.result = None
        self.current_user = current_user
        self.is_editing = current_user is not None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Password (only for new users)
        if not self.is_editing:
            ttk.Label(main_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.password_entry = ttk.Entry(main_frame, width=25, show="*")
            self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
            
            ttk.Label(main_frame, text="Confirm Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
            self.confirm_password_entry = ttk.Entry(main_frame, width=25, show="*")
            self.confirm_password_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
            row_offset = 3
        else:
            row_offset = 1
        
        # Role
        ttk.Label(main_frame, text="Role:").grid(row=row_offset, column=0, sticky=tk.W, pady=5)
        self.role_var = tk.StringVar(value="user")
        self.role_combo = ttk.Combobox(main_frame, textvariable=self.role_var, width=22, state="readonly")
        self.role_combo['values'] = ('admin', 'user')
        self.role_combo.grid(row=row_offset, column=1, pady=5, padx=(10, 0))
        
        # Active status (only for editing)
        if self.is_editing:
            row_offset += 1
            self.active_var = tk.BooleanVar()
            self.active_check = ttk.Checkbutton(main_frame, text="Active", variable=self.active_var)
            self.active_check.grid(row=row_offset, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row_offset + 1, column=0, columnspan=2, pady=(20, 0))
        
        # Save button
        save_button = ttk.Button(button_frame, text="Save", command=self.save_user)
        save_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy)
        cancel_button.pack(side=tk.RIGHT)
        
        # Load current user data if editing
        if self.is_editing:
            self.username_entry.insert(0, self.current_user['username'])
            self.role_var.set(self.current_user['role'])
            self.active_var.set(self.current_user['is_active'])
        
        # Set focus
        self.username_entry.focus()
    
    def save_user(self):
        username = self.username_entry.get().strip()
        role = self.role_var.get()
        
        if not username:
            messagebox.showerror("Error", "Username cannot be empty.")
            return
        
        # Validate username format
        import re
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            messagebox.showerror("Error", "Username must be 3-20 characters long and contain only letters, numbers, and underscores.")
            return
        
        if not self.is_editing:
            password = self.password_entry.get()
            confirm_password = self.confirm_password_entry.get()
            
            if not password:
                messagebox.showerror("Error", "Password cannot be empty.")
                return
            
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long.")
                return
            
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            
            self.result = {
                'username': username,
                'password': password,
                'role': role
            }
        else:
            is_active = self.active_var.get()
            self.result = {
                'username': username,
                'role': role,
                'is_active': is_active
            }
        
        self.dialog.destroy()
