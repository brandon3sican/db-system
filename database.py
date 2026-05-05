import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="database_system.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Users table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Dynamic data table (configurable by admin)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dynamic_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_1 TEXT,
                field_2 TEXT,
                field_3 TEXT,
                field_4 TEXT,
                field_5 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                is_archived BOOLEAN DEFAULT 0,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Table configuration (for admin to configure fields)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS table_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT NOT NULL,
                field_type TEXT NOT NULL DEFAULT 'TEXT',
                is_required BOOLEAN DEFAULT 0,
                field_order INTEGER DEFAULT 0
            )
        ''')
        
        # Insert default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            import bcrypt
            password = b'admin123'
            hashed = bcrypt.hashpw(password, bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ('admin', hashed.decode('utf-8'), 'admin')
            )
        
        # Insert default field configurations
        cursor.execute("SELECT COUNT(*) FROM table_config")
        if cursor.fetchone()[0] == 0:
            default_fields = [
                ('first_name', 'TEXT', 1, 1),
                ('middle_name', 'TEXT', 0, 2),
                ('last_name', 'TEXT', 1, 3),
                ('suffix', 'TEXT', 0, 4)
            ]
            cursor.executemany(
                "INSERT INTO table_config (field_name, field_type, is_required, field_order) VALUES (?, ?, ?, ?)",
                default_fields
            )
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        import bcrypt
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, password_hash, role, is_active FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and result[3]:  # Check if user is active
            user_id, stored_hash, role, is_active = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return {'id': user_id, 'username': username, 'role': role}
        return None
    
    def get_user_by_username(self, username):
        """Get user by username without password verification"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, role, is_active FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and result[3]:  # Check if user is active
            user_id, username, role, is_active = result
            return {'id': user_id, 'username': username, 'role': role}
        return None
    
    def get_table_config(self):
        """Get table field configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT field_name, field_type, is_required, field_order FROM table_config ORDER BY field_order"
        )
        config = cursor.fetchall()
        conn.close()
        return config
    
    def update_table_config(self, field_configs):
        """Update table field configuration (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Clear existing config
        cursor.execute("DELETE FROM table_config")
        
        # Insert new configuration
        for i, config in enumerate(field_configs):
            cursor.execute(
                "INSERT INTO table_config (field_name, field_type, is_required, field_order) VALUES (?, ?, ?, ?)",
                (config['name'], config['type'], config.get('required', False), i + 1)
            )
        
        conn.commit()
        conn.close()
    
    def create_record(self, user_id, data):
        """Create a new record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current field configuration
        config = self.get_table_config()
        
        # Prepare data for insertion
        fields = []
        values = []
        for i, (field_name, field_type, is_required, field_order) in enumerate(config):
            field_key = f'field_{i + 1}'
            fields.append(field_key)
            values.append(data.get(field_name, ''))
        
        # Add metadata
        fields.extend(['created_at', 'updated_at', 'created_by'])
        values.extend([datetime.now(), datetime.now(), user_id])
        
        # Build dynamic SQL based on current config
        placeholders = ', '.join(['?' for _ in values])
        field_names = ', '.join(fields)
        
        cursor.execute(f"INSERT INTO dynamic_data ({field_names}) VALUES ({placeholders})", values)
        record_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return record_id
    
    def get_records(self, include_archived=False):
        """Get all records"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        archive_filter = "" if include_archived else "WHERE is_archived = 0"
        
        cursor.execute(f"""
            SELECT d.*, u.username 
            FROM dynamic_data d 
            LEFT JOIN users u ON d.created_by = u.id 
            {archive_filter}
            ORDER BY d.field_1 ASC
        """)
        
        records = cursor.fetchall()
        conn.close()
        return records
    
    def update_record(self, record_id, data):
        """Update an existing record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current field configuration
        config = self.get_table_config()
        
        # Build update query
        updates = []
        values = []
        for i, (field_name, field_type, is_required, field_order) in enumerate(config):
            field_key = f'field_{i + 1}'
            updates.append(f"{field_key} = ?")
            values.append(data.get(field_name, ''))
        
        # Add updated timestamp
        updates.append("updated_at = ?")
        values.append(datetime.now())
        values.append(record_id)
        
        cursor.execute(f"UPDATE dynamic_data SET {', '.join(updates)} WHERE id = ?", values)
        
        conn.commit()
        conn.close()
    
    def archive_record(self, record_id):
        """Archive a record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE dynamic_data SET is_archived = 1 WHERE id = ?", (record_id,))
        
        conn.commit()
        conn.close()
    
    def delete_record(self, record_id):
        """Delete a record (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM dynamic_data WHERE id = ?", (record_id,))
        
        conn.commit()
        conn.close()
    
    def get_users(self):
        """Get all users (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, role, created_at, is_active FROM users ORDER BY created_at")
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def create_user(self, username, password, role):
        """Create a new user (admin only)"""
        import bcrypt
        conn = self.get_connection()
        cursor = conn.cursor()
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed.decode('utf-8'), role)
        )
        
        conn.commit()
        conn.close()
    
    def update_user(self, user_id, username, role, is_active):
        """Update user (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET username = ?, role = ?, is_active = ? WHERE id = ?",
            (username, role, is_active, user_id)
        )
        
        conn.commit()
        conn.close()
    
    def delete_user(self, user_id):
        """Delete user (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
