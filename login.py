import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.db = DatabaseManager()
        
        self.window = tk.Tk()
        self.window.title("Database System - Login")
        self.window.geometry("350x250")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.window.winfo_screenheight() // 2) - (250 // 2)
        self.window.geometry(f"350x250+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame - compact
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Database System Login", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Username
        username_label = ttk.Label(main_frame, text="Username:")
        username_label.pack(anchor=tk.W, pady=3)
        
        self.username_entry = ttk.Entry(main_frame, width=25)
        self.username_entry.pack(fill=tk.X, pady=3)
        
        # Password
        password_label = ttk.Label(main_frame, text="Password:")
        password_label.pack(anchor=tk.W, pady=3)
        
        self.password_entry = ttk.Entry(main_frame, width=25, show="*")
        self.password_entry.pack(fill=tk.X, pady=3)
        
        # Login button
        login_button = ttk.Button(main_frame, text="Login", command=self.login)
        login_button.pack(pady=10)
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda event: self.login())
        
        # Set focus to username entry
        self.username_entry.focus()
        
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        user = self.db.authenticate_user(username, password)
        
        if user:
            messagebox.showinfo("Success", f"Welcome, {user['username']}!")
            self.window.destroy()
            self.on_login_success(user)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def run(self):
        self.window.mainloop()
