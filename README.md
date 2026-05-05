# Database System Desktop Application

A comprehensive desktop database management system with role-based access control, built using Python and Tkinter.

## Features

### Role-Based Access Control
- **Administrator**: Full system access including database configuration and user management
- **User**: Limited access to add, edit, and archive database records

### Core Functionality
- **Database Configuration** (Admin only): Configure custom fields for the database
- **User Management** (Admin only): Create, edit, delete, and manage user accounts
- **CRUD Operations**: Add, edit, and manage database records
- **Archive System**: Users can archive records; admins can restore or permanently delete
- **Data Validation**: Field validation based on configured data types

### Security Features
- Secure password hashing using bcrypt
- Session-based authentication
- Role-based permission enforcement
- Input validation and sanitization

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

#### Method 1: Double-click the batch file
- Double-click `start_database_system.bat` in the folder
- Or double-click `run.bat` for a simple version

#### Method 2: Desktop Shortcut
- Run `python setup.py` to create a desktop shortcut
- Or manually create a shortcut:
  1. Right-click on `start_database_system.bat`
  2. Select "Send to" > "Desktop (create shortcut)"
  3. Rename to "Database System"

#### Method 3: Command Line
```bash
python app.py
```

### Default Login Credentials
- **Username**: admin
- **Password**: admin123

### Administrator Features
1. **Database Configuration**
   - Add, edit, remove database fields
   - Configure field types (TEXT, INTEGER, REAL, BOOLEAN)
   - Set required fields
   - Reorder fields

2. **User Management**
   - Create new users
   - Edit existing users
   - Activate/deactivate users
   - Delete users (except admin)

3. **Data Management**
   - Full CRUD operations on all records
   - Access to archived records
   - Permanent deletion capability
   - Record restoration from archive

### User Features
1. **Data Management**
   - Add new records
   - Edit existing records
   - Archive records (soft delete)
   - View active records only

2. **Search Functionality**
   - Search across all fields or specific fields
   - Partial and exact match options
   - Case-sensitive or case-insensitive search
   - Quick access from toolbar

3. **Excel Integration**
   - Export data to Excel files
   - Import data from Excel files
   - Backup and restore functionality

## Database Schema

The application uses SQLite with the following main tables:

- **users**: User authentication and role management
- **dynamic_data**: Main data table with configurable fields
- **table_config**: Field configuration for the dynamic data table

## File Structure

```
database-system/
├── app.py                 # Main application entry point
├── database.py            # Database management and operations
├── login.py               # Login window and authentication
├── main_app.py            # Main application window
├── data_crud.py           # CRUD operations for data records
├── admin_config.py        # Database configuration interface
├── user_management.py     # User management interface
├── excel_manager.py       # Excel import/export functionality
├── search_manager.py      # Search functionality
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration

The database is automatically created on first run with default settings:
- Default admin user (admin/admin123)
- 4 default fields: First Name, Middle Name, Last Name, Suffix

## Excel Import/Export

### Export Features:
- Export all active records to Excel
- Option to include archived records (admin only)
- Automatic column formatting with user-friendly names
- Metadata included (created/updated dates, created by)

### Import Features:
- Import data from Excel files
- Automatic data type validation
- Required field validation
- Error reporting with import statistics
- Supports .xlsx and .xls formats

### Excel File Format:
The Excel file should have columns matching your database configuration:
- First Name (required)
- Middle Name (optional)  
- Last Name (required)
- Suffix (optional)

### Usage:
1. Go to **File** → **Import/Export Excel**
2. **Export**: Choose to include archived records, select save location
3. **Import**: Select Excel file, review import results
4. Data is automatically refreshed after import/export

## Search Features

### Search Options:
- **Field Selection**: Search in all fields or specific fields
- **Match Type**: Partial match (contains) or exact match
- **Case Sensitivity**: Case-sensitive or case-insensitive search
- **Quick Access**: Search button in main toolbar

### Search Usage:
1. Click **Search** button in toolbar
2. Select field to search in (or "All Fields")
3. Enter search term
4. Choose search options (case sensitivity, exact match)
5. Click **Search** to see results
6. Use **Clear Search** to return to full view

### Search Results:
- Results displayed in main table
- Window title shows "[SEARCH RESULTS]"
- **Clear Search** button becomes active
- All regular operations (edit, archive) work on search results

## Security Notes

- Change the default admin password after first login
- Regular users cannot access admin functions
- All passwords are securely hashed
- Input validation prevents SQL injection
- Role-based access control enforced throughout

## Troubleshooting

### Common Issues
1. **Database locked**: Ensure only one instance of the application is running
2. **Login fails**: Check username and password, ensure user is active
3. **Permission denied**: Verify user role and permissions

### Database Reset
To reset the database to default state:
1. Delete `database_system.db` file
2. Restart the application

## Development

### Adding New Features
1. Database changes: Update `database.py`
2. UI changes: Modify relevant window files
3. New permissions: Update role checks in relevant files

### Field Types
Supported field types:
- TEXT: Text input
- INTEGER: Whole numbers
- REAL: Decimal numbers
- BOOLEAN: True/False checkbox

## License

This project is provided as-is for educational and demonstration purposes.
