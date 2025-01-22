# # app.py
# from flask import Flask, render_template, request, jsonify, session, redirect, url_for
# import json
# from datetime import datetime
# import os
# from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.secret_key = 'your-secret-key-here'
# UPLOAD_FOLDER = 'static/uploads'
# ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Database functions
# def load_db():
#     try:
#         with open('database/Catchup.json', 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return {
#             'users': {},
#             'groups': {},
#             'messages': {},
#             'catchup_requests': {}
#         }

# def save_db(db):
#     with open('database/Catchup.json', 'w') as f:
#         json.dump(db, f, indent=4)

# def allowed_file(filename):
#     """
#     Check if the uploaded file has an allowed extension
#     """
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def generate_user_id():
#     db = load_db()
#     existing_ids = set(db['users'].keys())
#     current_id = 1729
#     while f"{current_id:05d}" in existing_ids:
#         current_id += 1
#     return f"{current_id:05d}"

# @app.route('/')
# def index():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     return render_template('index.html')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         try:
#             db = load_db()
            
#             # Handle both JSON and form data
#             if request.is_json:
#                 data = request.json
#             else:
#                 data = request.form
            
#             username = data.get('username')
#             password = data.get('password')

#             if not username or not password:
#                 return jsonify({'success': False, 'error': 'Missing username or password'})

#             # Find the user by username
#             user_id = None
#             for uid, user in db['users'].items():
#                 if user['username'] == username:
#                     # Compare password hashes instead of plain text
#                     if check_password_hash(user['password'], password):
#                         user_id = uid
#                         break

#             if user_id:
#                 session['user_id'] = user_id
                
#                 # If it's a form submission, redirect to index
#                 if not request.is_json:
#                     return redirect(url_for('index'))
                    
#                 return jsonify({'success': True, 'message': 'Login successful', 'user_id': user_id})
#             else:
#                 if not request.is_json:
#                     return render_template('login.html', error='Invalid username or password')
#                 return jsonify({'success': False, 'error': 'Invalid username or password'})

#         except Exception as e:
#             print(f"Login error: {str(e)}")
#             return jsonify({'success': False, 'error': 'An error occurred during login'})

#     return render_template('login.html')
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         try:
#             db = load_db()
            
#             # Handle both JSON and form data
#             if request.is_json:
#                 data = request.json
#             else:
#                 data = request.form
            
#             username = data.get('username')
#             password = data.get('password')
#             email = data.get('email')
            
#             if not username or not password or not email:
#                 return jsonify({'success': False, 'error': 'Missing required fields'})
            
#             # Check if username already exists
#             for user in db['users'].values():
#                 if user['username'] == username:
#                     return jsonify({'success': False, 'error': 'Username already exists'})
            
#             user_id = generate_user_id()
            
#             # Hash the password before storing
#             hashed_password = generate_password_hash(password)
            
#             db['users'][user_id] = {
#                 'username': username,
#                 'password': hashed_password,
#                 'email': email,
#                 'connections': [],
#                 'groups': [],
#                 'profile_pic': 'default.png'
#             }
            
#             save_db(db)
            
#             # If it's a form submission, redirect to login
#             if not request.is_json:
#                 return redirect(url_for('login'))
                
#             return jsonify({'success': True, 'user_id': user_id})
            
#         except Exception as e:
#             print(f"Signup error: {str(e)}")
#             return jsonify({'success': False, 'error': 'An error occurred during signup'})
    
#     return render_template('signup.html')
# @app.route('/send_catchup', methods=['POST'])
# def send_catchup():
#     if 'user_id' not in session:
#         return jsonify({'success': False, 'error': 'Not logged in'})
    
#     db = load_db()
#     data = request.json
#     request_id = f"req_{datetime.now().timestamp()}"
    
#     db['catchup_requests'][request_id] = {
#         'from_user': session['user_id'],
#         'to_user': data['to_user'],
#         'status': 'pending',
#         'timestamp': datetime.now().isoformat()
#     }
    
#     save_db(db)
#     return jsonify({'success': True})

# # Add these new routes to your app.py

# @app.route('/search_users', methods=['POST'])
# def search_users():
#     if 'user_id' not in session:
#         return jsonify({'success': False, 'error': 'Not logged in'})
    
#     db = load_db()
#     data = request.json
#     query = data.get('query', '').lower()
    
#     # Search for users whose username contains the query string
#     matching_users = []
#     for user_id, user in db['users'].items():
#         if user_id != session['user_id']:  # Don't include current user
#             if query in user['username'].lower():
#                 matching_users.append({
#                     'id': user_id,
#                     'username': user['username']
#                 })
    
#     return jsonify({'success': True, 'users': matching_users})

# @app.route('/get_user_groups')
# def get_user_groups():
#     if 'user_id' not in session:
#         return jsonify({'success': False, 'error': 'Not logged in'})
    
#     db = load_db()
#     user = db['users'].get(session['user_id'])
    
#     if not user:
#         return jsonify({'success': False, 'error': 'User not found'})
    
#     groups = []
#     for group_id in user['groups']:
#         group = db['groups'].get(group_id)
#         if group:
#             groups.append({
#                 'id': group_id,
#                 'name': group['name'],
#                 'description': group['description'],
#                 'member_count': len(group['members'])
#             })
    
#     return jsonify({'success': True, 'groups': groups})

# @app.route('/get_catchup_requests')
# def get_catchup_requests():
#     if 'user_id' not in session:
#         return jsonify({'success': False, 'error': 'Not logged in'})
    
#     db = load_db()
#     current_user = session['user_id']
    
#     # Get both sent and received requests
#     requests = []
#     for req_id, req in db['catchup_requests'].items():
#         if req['to_user'] == current_user or req['from_user'] == current_user:
#             from_user = db['users'][req['from_user']]['username']
#             to_user = db['users'][req['to_user']]['username']
#             requests.append({
#                 'id': req_id,
#                 'from_user': from_user,
#                 'to_user': to_user,
#                 'status': req['status'],
#                 'timestamp': req['timestamp']
#             })
    
#     return jsonify({'success': True, 'requests': requests})

# @app.route('/accept_catchup', methods=['POST'])
# def accept_catchup():
#     if 'user_id' not in session:
#         return jsonify({'success': False, 'error': 'Not logged in'})
    
#     db = load_db()
#     data = request.json
#     request_id = data.get('request_id')
    
#     if request_id not in db['catchup_requests']:
#         return jsonify({'success': False, 'error': 'Request not found'})
    
#     catchup_request = db['catchup_requests'][request_id]
#     if catchup_request['to_user'] != session['user_id']:
#         return jsonify({'success': False, 'error': 'Not authorized'})
    
#     catchup_request['status'] = 'accepted'
    
#     # Add users to each other's connections
#     from_user = catchup_request['from_user']
#     to_user = catchup_request['to_user']
    
#     if from_user not in db['users'][to_user]['connections']:
#         db['users'][to_user]['connections'].append(from_user)
#     if to_user not in db['users'][from_user]['connections']:
#         db['users'][from_user]['connections'].append(to_user)
    
#     save_db(db)
#     return jsonify({'success': True})

# @app.route('/create_group', methods=['POST'])
# def create_group():
#     if 'user_id' not in session:
#         return jsonify({'success': False, 'error': 'Not logged in'})
    
#     db = load_db()
#     data = request.json
#     group_id = f"group_{datetime.now().timestamp()}"
    
#     db['groups'][group_id] = {
#         'name': data['name'],
#         'description': data['description'],
#         'creator': session['user_id'],
#         'members': [session['user_id']],
#         'messages': []
#     }
    
#     db['users'][session['user_id']]['groups'].append(group_id)
#     save_db(db)
#     return jsonify({'success': True, 'group_id': group_id})

# @app.route('/send_message', methods=['POST'])
# def send_message():
#     if 'user_id' not in session:
#         return jsonify({'success': False, 'error': 'Not logged in'})
    
#     db = load_db()
#     data = request.json
#     message_id = f"msg_{datetime.now().timestamp()}"
    
#     if 'file' in request.files:
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             data['file_url'] = filename

#     db['messages'][message_id] = {
#         'from_user': session['user_id'],
#         'to_user': data.get('to_user'),
#         'to_group': data.get('to_group'),
#         'content': data['content'],
#         'timestamp': datetime.now().isoformat(),
#         'file_url': data.get('file_url')
#     }
    
#     save_db(db)
#     return jsonify({'success': True, 'message_id': message_id})

# if __name__ == '__main__':
#     app.run(debug=True)





# from flask import Flask, render_template
# import requests
# from datetime import datetime, timedelta
# import pytz
# from bs4 import BeautifulSoup

# app = Flask(__name__)


# # Function to scrape the latest news
# def fetch_latest_news():
#     url = "https://www.mlb.com/news/"
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Find the news articles (modify selectors based on website structure)
#     articles = soup.find_all('article', class_='article-item', limit=4)
#     news_list = []

#     for article in articles:
#         title = article.find('h1', class_='article-item__headline').get_text(strip=True)
#         link = article.find('a', href=True)['href']
        
    
#         news_list.append({
#             'title': title,
#             'link': f"https://www.mlb.com/news/",
          
#         })

#     return news_list


# def get_game_content(game_pk):
#     url = f'https://statsapi.mlb.com/api/v1/game/{game_pk}/content'
#     try:
#         response = requests.get(url)
#         return response.json()
#     except:
#         return None

# def get_schedule():
#     season = 2025
#     url = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={season}'
#     try:
#         response = requests.get(url)
#         data = response.json()
#         games = []
        
#         if 'dates' in data:
#             for date in data['dates']:
#                 for game in date.get('games', []):
#                     games.append({
#                         'gamePk': game.get('gamePk'),
#                         'gameDate': game.get('gameDate'),
#                         'status': game.get('status', {}).get('abstractGameState'),
#                         'homeTeam': game.get('teams', {}).get('home', {}).get('team', {}).get('name'),
#                         'awayTeam': game.get('teams', {}).get('away', {}).get('team', {}).get('name'),
#                         'venue': game.get('venue', {}).get('name'),
#                         'homeScore': game.get('teams', {}).get('home', {}).get('score', 0),
#                         'awayScore': game.get('teams', {}).get('away', {}).get('score', 0)
#                     })
        
#         # Sort games by date
#         games.sort(key=lambda x: x['gameDate'])
        
#         # Get past, current, and upcoming games
#         past_games = [g for g in games if g['status'] == 'Final'][-2:]  # Last 2 completed games
#         current_games = [g for g in games if g['status'] == 'Live'][:2]
#         upcoming_games = [g for g in games if g['status'] == 'Preview'][:2]
        
#         return past_games, current_games, upcoming_games
#     except:
#         return [], [], []

# @app.route('/')
# def index():
#     past_games, current_games, upcoming_games = get_schedule()
#     news = fetch_latest_news()
    
#     return render_template('home.html', 
#                          past_games=past_games,
#                          current_games=current_games,
#                          upcoming_games=upcoming_games,
#                          news=news)
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
from googletrans import Translator

app = Flask(__name__)

# Translations dictionary
translations = {
    'en': {
        'upcoming_games': 'Upcoming Games',
        'latest_news': 'Latest News',
        'upcoming': 'Upcoming'
    },
    'ja': {
        'upcoming_games': '今後の試合',
        'latest_news': '最新ニュース',
        'upcoming': '近日中'
    },
    'es': {
        'upcoming_games': 'Próximos Juegos',
        'latest_news': 'Últimas Noticias',
        'upcoming': 'Próximo'
    },
    'de': {
        'upcoming_games': 'Kommende Spiele',
        'latest_news': 'Neueste Nachrichten',
        'upcoming': 'Bevorstehend'
    },
    'ko': {
        'upcoming_games': '다가오는 경기',
        'latest_news': '최신 뉴스',
        'upcoming': '예정된'
    },
    'fr': {
        'upcoming_games': 'Matchs à venir',
        'latest_news': 'Dernières nouvelles',
        'upcoming': 'À venir'
    },
    'hi': {
        'upcoming_games': 'आगामी खेल',
        'latest_news': 'ताज़ा खबर',
        'upcoming': 'आगामी'
    }
}

def translate_content(text, target_lang):
    if target_lang == 'en':
        return text
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except:
        return text

def fetch_latest_news():
    url = "https://www.mlb.com/news/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='article-item', limit=4)
    news_list = []
    
    for article in articles:
        title = article.find('h1', class_='article-item__headline').get_text(strip=True)
       
        news_list.append({
            'title': title,
            'link': "https://www.mlb.com/news/"
        })
    
    return news_list

def get_schedule():
    season = 2025
    url = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={season}'
    try:
        response = requests.get(url)
        data = response.json()
        games = []

        if 'dates' in data:
            for date in data['dates']:
                for game in date.get('games', []):
                    games.append({
                        'gamePk': game.get('gamePk'),
                        'gameDate': game.get('gameDate'),
                        'status': game.get('status', {}).get('abstractGameState'),
                        'homeTeam': game.get('teams', {}).get('home', {}).get('team', {}).get('name'),
                        'awayTeam': game.get('teams', {}).get('away', {}).get('team', {}).get('name'),
                        'venue': game.get('venue', {}).get('name'),
                        'homeScore': game.get('teams', {}).get('home', {}).get('score', 0),
                        'awayScore': game.get('teams', {}).get('away', {}).get('score', 0)
                    })

        games.sort(key=lambda x: x['gameDate'])
        upcoming_games = [g for g in games if g['status'] == 'Preview'][:4]  # Show 4 upcoming games
        return upcoming_games
    except:
        return []

@app.route('/')
def index():
    lang = request.args.get('lang', 'en')
    upcoming_games = get_schedule()
    news = fetch_latest_news()
    
    # Translate content if language is not English
    if lang != 'en':
        for game in upcoming_games:
            game['homeTeam'] = translate_content(game['homeTeam'], lang)
            game['awayTeam'] = translate_content(game['awayTeam'], lang)
            game['venue'] = translate_content(game['venue'], lang)
        
        for article in news:
            article['title'] = translate_content(article['title'], lang)

    return render_template('home.html',
                         upcoming_games=upcoming_games,
                         news=news,
                         lang=lang,
                         translations=translations)

if __name__ == '__main__':
    app.run(debug=True)