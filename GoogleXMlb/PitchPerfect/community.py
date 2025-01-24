# from flask import Flask, render_template, request, jsonify, session, redirect, url_for
# import json
# from datetime import datetime
# import os

# app = Flask(__name__)
# app.secret_key = 'your-secret-key'  # Change this to a secure secret key

# # Database files
# USERS_DB = 'users.json'
# MESSAGES_DB = 'messages.json'
# GROUPS_DB = 'groups.json'

# # Initialize database files if they don't exist
# def init_db():
#     if not os.path.exists(USERS_DB):
#         with open(USERS_DB, 'w') as f:
#             json.dump([], f)
#     if not os.path.exists(MESSAGES_DB):
#         with open(MESSAGES_DB, 'w') as f:
#             json.dump([], f)
#     if not os.path.exists(GROUPS_DB):
#         with open(GROUPS_DB, 'w') as f:
#             json.dump([], f)

# # Database operations
# def load_db(file_path):
#     with open(file_path, 'r') as f:
#         return json.load(f)

# def save_db(data, file_path):
#     with open(file_path, 'w') as f:
#         json.dump(data, f)

# # Routes
# @app.route('/')
# def home():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     return render_template('community.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         data = request.get_json()
#         users = load_db(USERS_DB)
#         user = next((u for u in users if u['username'] == data['username']), None)
        
#         if user and user['password'] == data['password']:
#             session['username'] = data['username']
#             return jsonify({'success': True})
#         return jsonify({'success': False, 'message': 'Invalid credentials'})
#     return render_template('communitylogin.html')

# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     users = load_db(USERS_DB)
    
#     if any(u['username'] == data['username'] for u in users):
#         return jsonify({'success': False, 'message': 'Username already exists'})
    
#     users.append({
#         'username': data['username'],
#         'password': data['password'],
#         'profile': {
#             'name': data.get('name', ''),
#             'bio': data.get('bio', ''),
#             'avatar': data.get('avatar', '')
#         }
#     })
#     save_db(users, USERS_DB)
#     return jsonify({'success': True})

# @app.route('/create_group', methods=['POST'])
# def create_group():
#     if 'username' not in session:
#         return jsonify({'success': False, 'message': 'Not logged in'})
    
#     data = request.get_json()
#     groups = load_db(GROUPS_DB)
    
#     new_group = {
#         'id': len(groups) + 1,
#         'name': data['name'],
#         'creator': session['username'],
#         'members': [session['username']] + data.get('members', []),
#         'created_at': datetime.now().isoformat()
#     }
    
#     groups.append(new_group)
#     save_db(groups, GROUPS_DB)
#     return jsonify({'success': True, 'group': new_group})

# @app.route('/search_users')
# def search_users():
#     query = request.args.get('q', '').lower()
#     users = load_db(USERS_DB)
#     results = [u for u in users if query in u['username'].lower()]
#     return jsonify({'users': results})

# @app.route('/send_message', methods=['POST'])
# def send_message():
#     if 'username' not in session:
#         return jsonify({'success': False, 'message': 'Not logged in'})
    
#     data = request.get_json()
#     messages = load_db(MESSAGES_DB)
    
#     new_message = {
#         'id': len(messages) + 1,
#         'sender': session['username'],
#         'recipient': data['recipient'],
#         'content': data['content'],
#         'timestamp': datetime.now().isoformat(),
#         'group_id': data.get('group_id')
#     }
    
#     messages.append(new_message)
#     save_db(messages, MESSAGES_DB)
#     return jsonify({'success': True, 'message': new_message})

# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True)


from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

# Database files
USERS_DB = 'users.json'
MESSAGES_DB = 'messages.json'
GROUPS_DB = 'groups.json'
FRIEND_REQUESTS_DB = 'friend_requests.json'

# Initialize database files if they don't exist
def init_db():
    if not os.path.exists(USERS_DB):
        with open(USERS_DB, 'w') as f:
            json.dump([], f)
    if not os.path.exists(MESSAGES_DB):
        with open(MESSAGES_DB, 'w') as f:
            json.dump([], f)
    if not os.path.exists(GROUPS_DB):
        with open(GROUPS_DB, 'w') as f:
            json.dump([], f)
    if not os.path.exists(FRIEND_REQUESTS_DB):
        with open(FRIEND_REQUESTS_DB, 'w') as f:
            json.dump([], f)

# Database operations
def load_db(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_db(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)

# Routes
@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('community.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        users = load_db(USERS_DB)
        user = next((u for u in users if u['username'] == data['username']), None)
        
        if user and user['password'] == data['password']:
            session['username'] = data['username']
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    return render_template('communitylogin.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    users = load_db(USERS_DB)
    
    if any(u['username'] == data['username'] for u in users):
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    users.append({
        'username': data['username'],
        'password': data['password'],
        'profile': {
            'name': data.get('name', ''),
            'bio': data.get('bio', ''),
            'avatar': data.get('avatar', '')
        },
        'friends': []  # Add friends list to user profile
    })
    save_db(users, USERS_DB)
    return jsonify({'success': True})

@app.route('/get_messages')
def get_messages():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    messages = load_db(MESSAGES_DB)
    group_id = request.args.get('group_id')
    recipient = request.args.get('recipient')
    
    # Filter messages based on criteria
    filtered_messages = []
    for msg in messages:
        if group_id and str(msg.get('group_id')) == str(group_id):
            filtered_messages.append(msg)
        elif recipient and not group_id:
            if (msg['sender'] == session['username'] and msg['recipient'] == recipient) or \
               (msg['sender'] == recipient and msg['recipient'] == session['username']):
                filtered_messages.append(msg)
    
    return jsonify({
        'success': True, 
        'messages': sorted(filtered_messages, key=lambda x: x['timestamp'])
    })

@app.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    friend_requests = load_db(FRIEND_REQUESTS_DB)
    
    # Check if request already exists
    existing_request = next((r for r in friend_requests 
                           if r['sender'] == session['username'] 
                           and r['recipient'] == data['recipient'] 
                           and r['status'] == 'pending'), None)
    
    if existing_request:
        return jsonify({'success': False, 'message': 'Friend request already sent'})
    
    new_request = {
        'id': len(friend_requests) + 1,
        'sender': session['username'],
        'recipient': data['recipient'],
        'status': 'pending',
        'timestamp': datetime.now().isoformat()
    }
    
    friend_requests.append(new_request)
    save_db(friend_requests, FRIEND_REQUESTS_DB)
    return jsonify({'success': True, 'request': new_request})

@app.route('/handle_friend_request', methods=['POST'])
def handle_friend_request():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    friend_requests = load_db(FRIEND_REQUESTS_DB)
    users = load_db(USERS_DB)
    
    request_id = data['request_id']
    action = data['action']  # 'accept' or 'reject'
    
    friend_request = next((r for r in friend_requests if r['id'] == request_id), None)
    if not friend_request or friend_request['recipient'] != session['username']:
        return jsonify({'success': False, 'message': 'Invalid request'})
    
    friend_request['status'] = 'accepted' if action == 'accept' else 'rejected'
    
    if action == 'accept':
        # Update both users' friend lists
        sender = next((u for u in users if u['username'] == friend_request['sender']), None)
        recipient = next((u for u in users if u['username'] == friend_request['recipient']), None)
        
        if sender and recipient:
            if 'friends' not in sender:
                sender['friends'] = []
            if 'friends' not in recipient:
                recipient['friends'] = []
                
            sender['friends'].append(friend_request['recipient'])
            recipient['friends'].append(friend_request['sender'])
            
            save_db(users, USERS_DB)
    
    save_db(friend_requests, FRIEND_REQUESTS_DB)
    return jsonify({'success': True})

@app.route('/get_friend_requests')
def get_friend_requests():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    friend_requests = load_db(FRIEND_REQUESTS_DB)
    pending_requests = [r for r in friend_requests 
                       if r['recipient'] == session['username'] 
                       and r['status'] == 'pending']
    
    return jsonify({
        'success': True,
        'requests': pending_requests
    })

@app.route('/get_friends')
def get_friends():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    users = load_db(USERS_DB)
    current_user = next((u for u in users if u['username'] == session['username']), None)
    
    if not current_user or 'friends' not in current_user:
        return jsonify({'success': True, 'friends': []})
    
    return jsonify({
        'success': True,
        'friends': current_user['friends']
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True)