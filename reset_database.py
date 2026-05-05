import os
import sqlite3
from database import DatabaseManager

def reset_database():
    """Reset the database with new name field configuration"""
    db_name = "database_system.db"
    
    # Check if database exists and remove it
    if os.path.exists(db_name):
        print(f"Removing existing database: {db_name}")
        os.remove(db_name)
    
    # Create new database with updated configuration
    print("Creating new database with name field configuration...")
    db = DatabaseManager(db_name)
    
    print("Database reset successfully!")
    print("\nNew field configuration:")
    print("- First Name (Required)")
    print("- Middle Name (Optional)")
    print("- Last Name (Required)")
    print("- Suffix (Optional)")
    
    print("\nDefault admin credentials:")
    print("- Username: admin")
    print("- Password: admin123")

if __name__ == "__main__":
    if input("This will delete all existing data. Continue? (y/n): ").lower() == 'y':
        reset_database()
    else:
        print("Operation cancelled.")
