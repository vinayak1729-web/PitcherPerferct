# Directory structure:
# - app.py
# - database/
#   - fanlink/
#     - users.json
#     - chats.json
#     - friend_requests.json
# - templates/
#   - login.html
#   - register.html
#   - dashboard.html
#   - chat.html
# - static/
#   - style.css

# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime
import secrets
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Ensure database directory exists
os.makedirs('database/fanlink', exist_ok=True)

# Database helper functions
def load_json(filename):
    filepath = f'database/fanlink/{filename}'
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(data, filename):
    with open(f'database/fanlink/{filename}', 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('Chat_dashboard'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    if request.method == 'POST':
        try:
            # Get JSON data from request
            data = request.get_json()
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            # Validate required fields
            if not all([username, email, password]):
                return jsonify({
                    'success': False,
                    'error': 'All fields are required'
                }), 400
            
            # Load existing users
            users = load_json('users.json')
            
            # Check if username already exists
            if username in users:
                return jsonify({
                    'success': False,
                    'error': 'Username already exists'
                }), 400
            
            # Create new user
            users[username] = {
                'email': email,
                'password': password,  # In production, this should be hashed
                'friends': [],
                'profile_pic': '/static/default.png'
            }
            
            # Save updated users
            save_json(users, 'users.json')
            
            return jsonify({
                'success': True,
                'message': 'Signup successful'
            })
            
        except Exception as e:
            print(f"Error during signup: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'An error occurred during signup'
            }), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_json('users.json')
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('Chat_dashboard'))
        return "Invalid credentials"
    
    return render_template('login.html')

@app.route('/Chat_dashboard')
def Chat_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Load all required data
    users = load_json('users.json')
    requests = load_json('friend_requests.json')
    groups = load_json('groups.json')
    
    # Get friend-related data
    pending_requests = [req for req in requests.get(session['username'], [])]
    friends = users[session['username']]['friends']
    
    # Process groups data
    my_groups = []
    available_groups = []
    
    for group_id, group_data in groups.items():
        group_info = {
            'id': group_id,
            'name': group_data['name'],
            'description': group_data['description'],
            'member_count': len(group_data['members']),
            'creator': group_data['creator'],
            'created_at': group_data['created_at']
        }
        
        if session['username'] in group_data['members']:
            # Add joined_at date if the user is not the creator
            if session['username'] != group_data['creator']:
                # In a real app, you'd store join dates. This is a simplification
                group_info['joined_at'] = group_data['created_at']
            my_groups.append(group_info)
        else:
            available_groups.append(group_info)
    
    # Sort groups by creation date (newest first)
    my_groups.sort(key=lambda x: x['created_at'], reverse=True)
    available_groups.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('dashboard.html',
                         pending_requests=pending_requests,
                         friends=friends,
                         my_groups=my_groups,
                         available_groups=available_groups)

@app.route('/search_users', methods=['GET'])
def search_users():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    query = request.args.get('query', '').lower()
    
    try:
        users = load_json('users.json')  # Load users data
        groups = load_json('groups.json')  # Load groups data

        # Filter users based on query
        filtered_users = [user for user in users if query in user.lower()]

        # Find groups matching the query
        matching_groups = []
        for group_id, group in groups.items():
            if query in group['name'].lower() or query in group['description'].lower():
                matching_groups.append({
                    'group_id': group_id,
                    'group_name': group['name'],
                    'description': group['description']
                })

        return jsonify({'users': filtered_users, 'groups': matching_groups})
    
    except Exception as e:
        print(f"Error searching users: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to search users'}), 500

@app.route('/send_request', methods=['POST'])
def send_request():
    if 'username' not in session:
        return jsonify({'success': False})
    
    to_user = request.form['to_user']
    requests = load_json('friend_requests.json')
    
    if to_user not in requests:
        requests[to_user] = []
    
    if session['username'] not in requests[to_user]:
        requests[to_user].append(session['username'])
        save_json(requests, 'friend_requests.json')
    
    return jsonify({'success': True})

@app.route('/accept_request', methods=['POST'])
def accept_request():
    if 'username' not in session:
        return jsonify({'success': False})
    
    from_user = request.form['from_user']
    requests = load_json('friend_requests.json')
    users = load_json('users.json')
    
    if from_user in requests.get(session['username'], []):
        requests[session['username']].remove(from_user)
        users[session['username']]['friends'].append(from_user)
        users[from_user]['friends'].append(session['username'])
        
        save_json(requests, 'friend_requests.json')
        save_json(users, 'users.json')
    
    return jsonify({'success': True})

@app.route('/chat/<friend>')
def chat(friend):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    users = load_json('users.json')
    if friend not in users[session['username']]['friends']:
        return "Not friends with this user"
    
    chats = load_json('chats.json')
    chat_id = '_'.join(sorted([session['username'], friend]))
    
    if chat_id not in chats:
        chats[chat_id] = []
    
    return render_template('chat.html', 
                         friend=friend, 
                         messages=chats[chat_id])


@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        friend = data.get('friend')
        message = data.get('message')
        
        if not friend or not message:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Load existing chats
        chats = load_json('chats.json')
        chat_id = '_'.join(sorted([session['username'], friend]))
        
        if chat_id not in chats:
            chats[chat_id] = []
        
        # Add new message
        new_message = {
            'from': session['username'],
            'message': message,
            'timestamp': datetime.now().strftime('%I:%M %p')  # 12-hour format with AM/PM
        }
        
        chats[chat_id].append(new_message)
        save_json(chats, 'chats.json')
        
        return jsonify({'success': True, 'message': new_message})
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500

@app.route('/get_new_messages/<friend>')
def get_new_messages(friend):
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        last_timestamp = request.args.get('last_timestamp')
        
        # Load chats
        chats = load_json('chats.json')
        chat_id = '_'.join(sorted([session['username'], friend]))
        
        if chat_id not in chats:
            return jsonify({'messages': []})
        
        # Get messages after last_timestamp
        new_messages = []
        for msg in chats[chat_id]:
            if not last_timestamp or msg['timestamp'] > last_timestamp:
                new_messages.append(msg)
        
        # Get typing status
        typing_status = load_json('typing_status.json')
        is_typing = typing_status.get(friend, {}).get(session['username'], False)
        
        return jsonify({
            'messages': new_messages,
            'typing_status': is_typing
        })
        
    except Exception as e:
        print(f"Error fetching messages: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch messages'}), 500

@app.route('/typing_status', methods=['POST'])
def typing_status():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        friend = data.get('friend')
        status = data.get('status') == 'typing'
        
        # Load typing status
        typing_status = load_json('typing_status.json')
        
        if friend not in typing_status:
            typing_status[friend] = {}
            
        typing_status[friend][session['username']] = status
        save_json(typing_status, 'typing_status.json')
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error updating typing status: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update typing status'}), 500


# New group-related routes
@app.route('/create_group', methods=['POST'])
def create_group():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        group_name = data.get('group_name')
        description = data.get('description', '')
        
        if not group_name:
            return jsonify({'success': False, 'error': 'Group name is required'}), 400
            
        groups = load_json('groups.json')
        
        # Generate unique group ID
        group_id = str(uuid.uuid4())
        
        # Create new group
        groups[group_id] = {
            'name': group_name,
            'description': description,
            'creator': session['username'],
            'members': [session['username']],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        save_json(groups, 'groups.json')
        
        # Initialize group chat
        chats = load_json('group_chats.json')
        chats[group_id] = []
        save_json(chats, 'group_chats.json')
        
        return jsonify({
            'success': True,
            'group_id': group_id,
            'message': 'Group created successfully'
        })
        
    except Exception as e:
        print(f"Error creating group: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create group'}), 500

@app.route('/join_group/<group_id>', methods=['POST'])
def join_group(group_id):
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        groups = load_json('groups.json')
        
        if group_id not in groups:
            return jsonify({'success': False, 'error': 'Group not found'}), 404
            
        if session['username'] in groups[group_id]['members']:
            return jsonify({'success': False, 'error': 'Already a member'}), 400
            
        # Add user to group
        groups[group_id]['members'].append(session['username'])
        save_json(groups, 'groups.json')
        
        # Add system message to group chat
        chats = load_json('group_chats.json')
        chats[group_id].append({
            'type': 'system',
            'message': f"{session['username']} joined the group",
            'timestamp': datetime.now().strftime('%I:%M %p')
        })
        save_json(chats, 'group_chats.json')
        
        return jsonify({'success': True, 'message': 'Joined group successfully'})
        
    except Exception as e:
        print(f"Error joining group: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to join group'}), 500

@app.route('/leave_group/<group_id>', methods=['POST'])
def leave_group(group_id):
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        groups = load_json('groups.json')
        
        if group_id not in groups:
            return jsonify({'success': False, 'error': 'Group not found'}), 404
            
        if session['username'] not in groups[group_id]['members']:
            return jsonify({'success': False, 'error': 'Not a member'}), 400
            
        # Remove user from group
        groups[group_id]['members'].remove(session['username'])
        
        # If creator leaves and there are other members, assign new creator
        if session['username'] == groups[group_id]['creator'] and groups[group_id]['members']:
            groups[group_id]['creator'] = groups[group_id]['members'][0]
            
        # If no members left, delete group
        if not groups[group_id]['members']:
            del groups[group_id]
            chats = load_json('group_chats.json')
            if group_id in chats:
                del chats[group_id]
            save_json(chats, 'group_chats.json')
        else:
            # Add system message about user leaving
            chats = load_json('group_chats.json')
            chats[group_id].append({
                'type': 'system',
                'message': f"{session['username']} left the group",
                'timestamp': datetime.now().strftime('%I:%M %p')
            })
            save_json(chats, 'group_chats.json')
            
        save_json(groups, 'groups.json')
        
        return jsonify({'success': True, 'message': 'Left group successfully'})
        
    except Exception as e:
        print(f"Error leaving group: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to leave group'}), 500

@app.route('/group_chat/<group_id>')
def group_chat(group_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    groups = load_json('groups.json')
    
    if group_id not in groups:
        return "Group not found", 404
        
    if session['username'] not in groups[group_id]['members']:
        return "Not a member of this group", 403
        
    chats = load_json('group_chats.json')
    group_messages = chats.get(group_id, [])
    
    return render_template('group_chat.html',
                         group=groups[group_id],
                         group_id=group_id,
                         messages=group_messages)

@app.route('/send_group_message', methods=['POST'])
def send_group_message():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        group_id = data.get('group_id')
        message = data.get('message')
        
        if not group_id or not message:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
        groups = load_json('groups.json')
        
        if group_id not in groups:
            return jsonify({'success': False, 'error': 'Group not found'}), 404
            
        if session['username'] not in groups[group_id]['members']:
            return jsonify({'success': False, 'error': 'Not a member'}), 403
            
        # Add message to group chat
        chats = load_json('group_chats.json')
        new_message = {
            'type': 'message',
            'from': session['username'],
            'message': message,
            'timestamp': datetime.now().strftime('%I:%M %p')
        }
        
        chats[group_id].append(new_message)
        save_json(chats, 'group_chats.json')
        
        return jsonify({'success': True, 'message': new_message})
        
    except Exception as e:
        print(f"Error sending group message: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500

if __name__ == '__main__':
    app.run(debug=True)