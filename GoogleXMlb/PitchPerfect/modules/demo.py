import sqlite3

# Path to your SQLite database file
db_file = "database/db.sqlite"

def fetch_all_data():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Fetch all data from the users table
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()
        
        # Print each row
        for row in data:
            print(row)
        
    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        # Close the database connection
        conn.close()

# Call the function to fetch and display all data
fetch_all_data()
