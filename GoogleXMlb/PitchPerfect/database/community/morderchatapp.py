from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this!

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database files
USERS_DB = 'database/community/users.json'
MESSAGES_DB = 'database/community/messages.json'
GROUPS_DB = 'database/community/groups.json'
FRIENDSHIPS_DB = 'database/community/friendships.json'

# Create database directory if it doesn't exist
if not os.path.exists('database'):
    os.makedirs('database')

FRIEND_REQUESTS_DB = 'database/friend_requests.json'

# Update init_db() function to include new database
def init_db():
    databases = {
        USERS_DB: [],
        MESSAGES_DB: [],
        GROUPS_DB: [],
        FRIENDSHIPS_DB: [],
        FRIEND_REQUESTS_DB: []
    }
    for db_file, initial_data in databases.items():
        if not os.path.exists(db_file):
            with open(db_file, 'w') as f:
                json.dump(initial_data, f)


def load_db(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_db(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('CPitcherCommunity.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        users = load_db(USERS_DB)
        
        if any(u['username'] == data['username'] for u in users):
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        new_user = {
            'id': str(uuid.uuid4()),
            'username': data['username'],
            'password': data['password'],  # In production, hash this!
            'email': data['email'],
            'created_at': datetime.now().isoformat()
        }
        
        users.append(new_user)
        save_db(users, USERS_DB)
        return jsonify({'success': True})
    
    return render_template('Cregister.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        users = load_db(USERS_DB)
        user = next((u for u in users if u['username'] == data['username'] and 
                    u['password'] == data['password']), None)
        
        if user:
            session['username'] = user['username']
            session['user_id'] = user['id']
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('Clogin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/users')
def get_users():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    users = load_db(USERS_DB)
    return jsonify({'success': True, 'users': [u for u in users if u['username'] != session['username']]})

@app.route('/create_group', methods=['POST'])
def create_group():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    groups = load_db(GROUPS_DB)
    
    new_group = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'description': data.get('description', ''),
        'creator': session['username'],
        'members': [session['username']],
        'created_at': datetime.now().isoformat()
    }
    
    groups.append(new_group)
    save_db(groups, GROUPS_DB)
    return jsonify({'success': True, 'group': new_group})

@app.route('/groups')
def get_groups():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    groups = load_db(GROUPS_DB)
    return jsonify({'success': True, 'groups': [g for g in groups if session['username'] in g['members']]})

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    messages = load_db(MESSAGES_DB)
    
    new_message = {
        'id': str(uuid.uuid4()),
        'sender': session['username'],
        'recipient': data['recipient'],
        'content': data['content'],
        'timestamp': datetime.now().isoformat()
    }
    
    messages.append(new_message)
    save_db(messages, MESSAGES_DB)
    return jsonify({'success': True, 'message': new_message})

@app.route('/messages/<recipient>')
def get_messages(recipient):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    messages = load_db(MESSAGES_DB)
    user_messages = [m for m in messages if m['sender'] == session['username'] and m['recipient'] == recipient or
                     m['recipient'] == session['username'] and m['sender'] == recipient]
    return jsonify({'success': True, 'messages': user_messages})

@app.route('/current_user')
def get_current_user():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    return jsonify({'success': True, 'username': session['username']})

@app.route('/friends')
def get_friends():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    friendships = load_db(FRIENDSHIPS_DB)
    friends = []
    for friendship in friendships:
        if friendship['user1'] == session['username']:
            friends.append(friendship['user2'])
        elif friendship['user2'] == session['username']:
            friends.append(friendship['user1'])
    
    return jsonify({'success': True, 'friends': friends})

@app.route('/friend_requests')
def get_friend_requests():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    requests = load_db(FRIEND_REQUESTS_DB)
    
    # Get received requests
    received = [req['sender'] for req in requests 
               if req['recipient'] == session['username'] and req['status'] == 'pending']
    
    # Get sent requests
    sent = [req['recipient'] for req in requests 
            if req['sender'] == session['username'] and req['status'] == 'pending']
    
    return jsonify({
        'success': True,
        'received': received,
        'sent': sent
    })

@app.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    recipient = data.get('username')
    
    if not recipient:
        return jsonify({'success': False, 'message': 'No recipient specified'})
    
    # Load existing requests
    requests = load_db(FRIEND_REQUESTS_DB)
    friendships = load_db(FRIENDSHIPS_DB)
    
    # Check if they're already friends
    if any((friendship['user1'] == session['username'] and friendship['user2'] == recipient) or
           (friendship['user2'] == session['username'] and friendship['user1'] == recipient)
           for friendship in friendships):
        return jsonify({'success': False, 'message': 'Already friends'})
    
    # Check if request already exists
    existing_request = next((req for req in requests 
        if ((req['sender'] == session['username'] and req['recipient'] == recipient) or
            (req['recipient'] == session['username'] and req['sender'] == recipient)) and
            req['status'] == 'pending'), None)
    
    if existing_request:
        return jsonify({'success': False, 'message': 'Friend request already exists'})
    
    # Create new request
    new_request = {
        'id': str(uuid.uuid4()),
        'sender': session['username'],
        'recipient': recipient,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    requests.append(new_request)
    save_db(requests, FRIEND_REQUESTS_DB)
    
    return jsonify({'success': True})

@app.route('/respond_friend_request', methods=['POST'])
def respond_friend_request():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    sender = data.get('username')
    accept = data.get('accept')
    
    if not sender:
        return jsonify({'success': False, 'message': 'No sender specified'})
    
    # Load databases
    requests = load_db(FRIEND_REQUESTS_DB)
    friendships = load_db(FRIENDSHIPS_DB)
    
    # Find the request
    request_index = next((i for i, req in enumerate(requests)
        if req['sender'] == sender and 
        req['recipient'] == session['username'] and
        req['status'] == 'pending'), None)
    
    if request_index is None:
        return jsonify({'success': False, 'message': 'Friend request not found'})
    
    # Update request status
    requests[request_index]['status'] = 'accepted' if accept else 'rejected'
    requests[request_index]['responded_at'] = datetime.now().isoformat()
    
    # If accepted, create friendship
    if accept:
        new_friendship = {
            'id': str(uuid.uuid4()),
            'user1': sender,
            'user2': session['username'],
            'created_at': datetime.now().isoformat()
        }
        friendships.append(new_friendship)
        save_db(friendships, FRIENDSHIPS_DB)
    
    save_db(requests, FRIEND_REQUESTS_DB)
    
    return jsonify({'success': True})

@app.route('/remove_friend', methods=['POST'])
def remove_friend():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    friend = data.get('username')
    
    if not friend:
        return jsonify({'success': False, 'message': 'No friend specified'})
    
    # Load friendships
    friendships = load_db(FRIENDSHIPS_DB)
    
    # Find and remove friendship
    friendship_index = next((i for i, friendship in enumerate(friendships)
        if (friendship['user1'] == session['username'] and friendship['user2'] == friend) or
           (friendship['user2'] == session['username'] and friendship['user1'] == friend)), None)
    
    if friendship_index is None:
        return jsonify({'success': False, 'message': 'Friendship not found'})
    
    friendships.pop(friendship_index)
    save_db(friendships, FRIENDSHIPS_DB)
    
    return jsonify({'success': True})

# Add these new routes to your Flask app

@app.route('/join_group', methods=['POST'])
def join_group():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    group_id = data.get('group_id')
    
    if not group_id:
        return jsonify({'success': False, 'message': 'No group specified'})
    
    groups = load_db(GROUPS_DB)
    group_index = next((i for i, g in enumerate(groups) if g['id'] == group_id), None)
    
    if group_index is None:
        return jsonify({'success': False, 'message': 'Group not found'})
    
    if session['username'] in groups[group_index]['members']:
        return jsonify({'success': False, 'message': 'Already a member'})
    
    groups[group_index]['members'].append(session['username'])
    save_db(groups, GROUPS_DB)
    
    return jsonify({'success': True})

@app.route('/leave_group', methods=['POST'])
def leave_group():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    group_id = data.get('group_id')
    
    if not group_id:
        return jsonify({'success': False, 'message': 'No group specified'})
    
    groups = load_db(GROUPS_DB)
    group_index = next((i for i, g in enumerate(groups) if g['id'] == group_id), None)
    
    if group_index is None:
        return jsonify({'success': False, 'message': 'Group not found'})
    
    if session['username'] not in groups[group_index]['members']:
        return jsonify({'success': False, 'message': 'Not a member'})
    
    if session['username'] == groups[group_index]['creator']:
        return jsonify({'success': False, 'message': 'Creator cannot leave group'})
    
    groups[group_index]['members'].remove(session['username'])
    save_db(groups, GROUPS_DB)
    
    return jsonify({'success': True})

@app.route('/search', methods=['GET'])
def search():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    query = request.args.get('q', '').lower()
    type = request.args.get('type', 'all')  # 'all', 'users', or 'groups'
    
    results = {'users': [], 'groups': []}
    
    if type in ['all', 'users']:
        users = load_db(USERS_DB)
        results['users'] = [u for u in users 
                          if query in u['username'].lower() 
                          and u['username'] != session['username']]
    
    if type in ['all', 'groups']:
        groups = load_db(GROUPS_DB)
        results['groups'] = [g for g in groups 
                           if query in g['name'].lower() 
                           or query in g['description'].lower()]
    
    return jsonify({'success': True, 'results': results})

@app.route('/send_file', methods=['POST'])
def send_file():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'})
    
    file = request.files['file']
    recipient = request.form.get('recipient')
    recipient_type = request.form.get('type')  # 'user' or 'group'
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'File type not allowed'})
    
    # Save the file
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Create message with file attachment
    messages = load_db(MESSAGES_DB)
    new_message = {
        'id': str(uuid.uuid4()),
        'sender': session['username'],
        'recipient': recipient,
        'content': f"Sent a file: {file.filename}",
        'file': {
            'name': file.filename,
            'path': filename
        },
        'timestamp': datetime.now().isoformat(),
        'type': 'file'
    }
    
    messages.append(new_message)
    save_db(messages, MESSAGES_DB)
    
    return jsonify({'success': True, 'message': new_message})

@app.route('/download/<filename>')
def download_file(filename):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        as_attachment=True
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
