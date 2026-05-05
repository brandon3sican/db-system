import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.db = DatabaseManager()
        
        self.window = tk.Tk()
        self.window.title("Database System - Login")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Database System Login", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=20)
        self.username_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=20, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Login button
        login_button = ttk.Button(main_frame, text="Login", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Default credentials info
        info_frame = ttk.LabelFrame(main_frame, text="Default Credentials", padding="10")
        info_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(info_frame, text="Admin: username: admin, password: admin123", font=('Arial', 9)).pack()
        
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
