from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key-here'

# Kullanıcı adı ve şifre bilgileri
AUTHORIZED_USERNAME = 'users'
AUTHORIZED_PASSWORD = 'password'

db = SQLAlchemy(app)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Veritabanını başlat
with app.app_context():
    db.create_all()

questions = [
    {
        'id': 1,
        'question': 'Discord.py kütüphanesinin temel kullanım amacı nedir?',
        'options': ['Web geliştirme', 'Sohbet botu oluşturma', 'Veri analizi', 'Makine öğrenimi'],
        'correct': 'Sohbet botu oluşturma'
    },
    {
        'id': 2,
        'question': 'Flask uygulamasında route tanımlamak için hangi dekoratör kullanılır?',
        'options': ['@app.get', '@app.route', '@flask.endpoint', '@url.path'],
        'correct': '@app.route'
    },
    {
        'id': 3,
        'question': 'TensorFlow temel olarak hangi alanda kullanılır?',
        'options': ['Web scraping', 'Makine öğrenimi', 'Veritabanı yönetimi', 'API geliştirme'],
        'correct': 'Makine öğrenimi'
    },
    {
        'id': 4,
        'question': 'OpenCV kütüphanesi hangi alanda kullanılır?',
        'options': ['Doğal Dil İşleme', 'Bilgisayar Görüşü', 'Veri analizi', 'Web geliştirme'],
        'correct': 'Bilgisayar Görüşü'
    },
    {
        'id': 5,
        'question': 'NLTK kütüphanesinin temel kullanım amacı nedir?',
        'options': ['Web scraping', 'Doğal Dil İşleme', 'Veri görselleştirme', 'Makine öğrenimi'],
        'correct': 'Doğal Dil İşleme'
    }
]

@app.context_processor
def inject_scores():
    total_questions = len(questions)
    global_highest = db.session.query(db.func.max(Score.score)).scalar() or 0
    global_highest_percentage = (global_highest / total_questions) * 100 if total_questions else 0

    session_id = request.cookies.get('session_id')
    username = request.cookies.get('username', '')

    user_highest = 0
    user_highest_percentage = 0
    if session_id:
        user_highest = db.session.query(db.func.max(Score.score)).filter_by(session_id=session_id).scalar() or 0
        user_highest_percentage = (user_highest / total_questions) * 100 if total_questions else 0

    # Genel ortalama skor hesaplama
    all_scores = db.session.query(Score.score).all()
    score_list = [score[0] for score in all_scores]
    global_average = sum(score_list) / len(score_list) if score_list else 0
    global_average_percentage = (global_average / total_questions) * 100 if total_questions else 0

    return {
        'global_highest': round(global_highest_percentage, 2),
        'user_highest': round(user_highest_percentage, 2),
        'global_average': round(global_average_percentage, 2),
        'username': username
    }

@app.route('/')
def index():
    session_id = request.cookies.get('session_id')
    username = request.cookies.get('username', '')

    # Kullanıcı doğrulaması
    request_auth = request.authorization
    if not request_auth or request_auth.username != AUTHORIZED_USERNAME or request_auth.password != AUTHORIZED_PASSWORD:
        return make_response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    
    if not session_id:
        session_id = str(uuid.uuid4())

    response = make_response(render_template('result.html', questions=questions, username=username))
    response.set_cookie('session_id', session_id)
    
    return response

@app.route('/submit', methods=['POST'])
def submit():
    score = 0
    username = request.form.get('username', '').strip()
    
    if not username:
        return redirect(url_for('index'))

    total_questions = len(questions)
    for q in questions:
        if request.form.get(f'q{q["id"]}') == q['correct']:
            score += 1

    score_percentage = (score / total_questions) * 100 if total_questions else 0

    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect(url_for('index'))
    
    new_score = Score(session_id=session_id, username=username, score=score)
    db.session.add(new_score)
    db.session.commit()

    response = make_response(render_template(
        'result.html',
        last_score=round(score_percentage, 2),
        total=len(questions)
    ))
    response.set_cookie('username', username)
    
    return response

@app.route('/favicon.ico')
def favicon():
    return '', 204

"""
kodun çalıştırılması ve test edilmesi için aşağıdaki siteden deneyin otomatik olarak girecektir.
https://ahmet5414.pythonanywhere.com/
"""