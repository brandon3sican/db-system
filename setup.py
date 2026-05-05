import sys
import os
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    try:
        print("Installing required dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt"])
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please run: python -m pip install bcrypt")
        return False
    return True

def create_shortcut():
    """Create a desktop shortcut"""
    try:
        import winshell
        from win32com.client import Dispatch
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Database System.lnk")
        target = os.path.join(os.getcwd(), "start_database_system.bat")
        wDir = os.getcwd()
        icon = target
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        print(f"Desktop shortcut created: {path}")
    except ImportError:
        print("Could not create desktop shortcut automatically.")
        print("To create shortcut manually:")
        print("1. Right-click on 'start_database_system.bat'")
        print("2. Select 'Send to' > 'Desktop (create shortcut)'")
        print("3. Rename the shortcut to 'Database System'")

if __name__ == "__main__":
    print("Database System Setup")
    print("====================")
    
    # Install dependencies
    if install_dependencies():
        # Create shortcut
        create_shortcut()
        
        print("\nSetup complete!")
        print("You can now run the application by:")
        print("1. Double-clicking 'start_database_system.bat'")
        print("2. Double-clicking the desktop shortcut 'Database System'")
        print("3. Running 'run.bat' from the folder")
        
        input("\nPress Enter to exit...")
    else:
        input("\nPress Enter to exit...")
