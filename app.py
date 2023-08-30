from flask import Flask, request, redirect, render_template_string, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "5ca0ddc4-d5ea-4b09-815f-cc58f5d236af"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
HEROKU_OAUTH_ID="247f6643-5eaf-4698-b0c4-58e95dde39d6"
HEROKU_OAUTH_SECRET="99e9c958-054a-4e2c-92f6-c6aba8898c25"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    points = db.Column(db.Integer, default=0)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

def initialize_db():
    with app.app_context():
        db.create_all()
        if not Video.query.first():
            db.session.add(Video(title="Ad 1"))
            db.session.add(Video(title="Ad 2"))
            db.session.commit()

initialize_db()

@app.route('/')
def index():
    if "user_id" not in session:
        return redirect('/login')
    user = User.query.get(session["user_id"])
    videos = Video.query.all()
    return render_template_string('''
    Welcome, {{ user.username }}! You have {{ user.points }} points.
    <h2>Watch a video to earn points:</h2>
    {% for video in videos %}
        <div>
            <a href="/watch/{{ video.id }}">{{ video.title }}</a>
        </div>
    {% endfor %}
    ''', user=user, videos=videos)


@app.route('/watch/<int:video_id>')
def watch_video(video_id):
    if "user_id" not in session:
        return redirect('/login')
    
    user = User.query.get(session["user_id"])  # Fetch the user from the database
    video = Video.query.get(video_id)
    
    if not video:
        return "Video not found"
    
    user.points += 5
    # Assuming there's a relationship between User and Video to track watched videos:
    # user.videos_watched.append(video)
    db.session.commit()
    return f"Thanks for watching {video.title}! You earned 5 points. <a href='/'>Back to homepage</a>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    username = request.form['username']
    password = request.form['password']
        
        # Check if the user already exists
    user = User.query.filter_by(username=username).first()
    if user:
        return "Username already exists. Choose a different one."

    hashed_password = generate_password_hash(password, method='sha256')
        
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
        
    return redirect('/')
    return render_template_string('''
<h2>Register</h2>
<form method="post">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <input type="submit" value="Register">
</form>
''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username or password weren't provided
        if not username or not password:
            return "Both username and password are required."

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return "Incorrect username or password."

        session['user_id'] = user.id
        return redirect('/')

    return render_template_string('''
    <h2>Login</h2>
    <form method="post">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    ''')
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
    if 'username' in request.form:
        username = request.form['username']
    else:
    # Handle the error or redirect as necessary
        return "Username not provided", 400

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    watched_videos_count = len(user.videos_watched)
    return render_template_string('''
    <h2>Profile for {{ user.username }}</h2>
    Points: {{ user.points }}<br>
    Videos watched: {{ watched_videos_count }}<br>
    <a href="/">Home</a>
    ''', user=user, watched_videos_count=watched_videos_count)

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found. <a href='/'>Go Home</a>", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
