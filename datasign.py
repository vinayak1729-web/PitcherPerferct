import sqlite3
import json

db_file = "database/db.sqlite"

# Initialize SQLite database connection
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Retrieve all users from the database
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()

# Define a function to convert SQLite user data to the desired JSON format
def convert_to_json(users):
    user_list = []
    for user in users:
        # user[0] = id, user[1] = name, user[2] = email, user[3] = password, user[4] = role, user[5] = team
        user_id = str(1729 + len(user_list)).zfill(6)  # Generates user_id in the required format
        user_json = {
            'user_id': user_id,
            'name': user[1],
            'age': None,  # Age field is not present in the current schema, set it to None or another value if needed
            'email': user[2],
            'password': user[3],
            'team_name': user[5] if user[5] else "None",  # Handle the case when team is None
            'selected_players': []  # initially empty
        }
        user_list.append(user_json)
    return user_list

# Convert user data to JSON format
user_json_data = convert_to_json(users)

# Save the data as a JSON file
with open('database/d.json', 'w') as json_file:
    json.dump(user_json_data, json_file, indent=4)

conn.close()
