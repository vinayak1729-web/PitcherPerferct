import sqlite3
import os

# Define the database file path
db_file = "database/db.sqlite"

# Ensure the database directory exists
os.makedirs(os.path.dirname(db_file), exist_ok=True)

# Initialize SQLite database
def init_db():
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT,
                team TEXT
                
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()

# Save a new user to the database
def save_user(user_data):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, email, password, role, team)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_data["name"], user_data["email"], user_data["password"], user_data["role"], user_data.get("team")))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Error: A user with this email already exists.")
    except sqlite3.Error as e:
        print(f"Error saving user: {e}")
    finally:
        conn.close()

# Get user details by email
def get_user(email):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "password": user[3],
                "role": user[4],
                "team": user[5]
            }
    except sqlite3.Error as e:
        print(f"Error fetching user: {e}")
    finally:
        conn.close()
    return None

# Update an existing user's details
def update_user(user):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET name = ?, password = ?, team = ?
            WHERE email = ?
        ''', (user["name"], user["password"], user.get("team"), user["email"]))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating user: {e}")
    finally:
        conn.close()

# Delete a user by email
def delete_user(email):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE email = ?', (email,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting user: {e}")
    finally:
        conn.close()

# Get all users
def get_all_users():
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        return [
            {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "password": user[3],
                "role": user[4],
                "team": user[5]
            } for user in users
        ]
    except sqlite3.Error as e:
        print(f"Error fetching users: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()  # Initialize the database if not already done
    all_users = get_all_users()  # Fetch all users
    for user in all_users:
        print(user)  # Print each user's details
