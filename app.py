import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from login import LoginWindow
from main_app import MainApplication

class DatabaseSystemApp:
    def __init__(self):
        self.current_user = None
        self.main_app = None
        
    def on_login_success(self, user):
        """Called when login is successful"""
        self.current_user = user
        self.start_main_application()
    
    def on_logout(self):
        """Called when user logs out"""
        self.current_user = None
    
    def start_main_application(self):
        """Start the main application"""
        if self.current_user:
            self.main_app = MainApplication(self.current_user, on_logout_callback=self.on_logout)
            self.main_app.run()
    
    def run(self):
        """Run the application"""
        while True:
            # Show login window
            login_window = LoginWindow(self.on_login_success)
            login_window.run()
            
            # If login was successful, start main app
            if self.current_user:
                self.start_main_application()
                
                # After main app closes, check if user logged out
                if self.current_user is None:  # User logged out
                    continue  # Show login screen again
                else:
                    break  # Application closed normally
            else:
                break  # Login window closed without login

if __name__ == "__main__":
    try:
        app = DatabaseSystemApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application error: {str(e)}")
        sys.exit(1)
