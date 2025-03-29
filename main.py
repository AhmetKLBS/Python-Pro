from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'

db = SQLAlchemy(app)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)  # Kullanıcı adı unique
    highest_score = db.Column(db.Integer, nullable=False)  # En yüksek skor
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Sorular ve cevaplar
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
        'options': ['Doğal Dil İşleme', 'Bilgisayarlı Görü', 'Veri analizi', 'Web geliştirme'],
        'correct': 'Bilgisayarlı Görü'
    },
    {
        'id': 5,
        'question': 'NLTK kütüphanesinin temel kullanım amacı nedir?',
        'options': ['Web scraping', 'Doğal Dil İşleme', 'Veri görselleştirme', 'Makine öğrenimi'],
        'correct': 'Doğal Dil İşleme'
    },
    {
        'id': 6,
        'question': 'Web scraping için hangi kütüphane kullanılır?',
        'options': ['beautifulsoup', 'numpy', 'matplotlib', 'keras'],
        'correct': 'beautifulsoup'
    },
    {
        'id': 7,
        'question': "Flask'ta template engine olarak ne kullanılır?",
        'options': ['jinja2', 'handlebars', 'pug', 'ejs'],
        'correct': 'jinja2'
    }
]

@app.context_processor
def inject_scores():
    total_questions = len(questions)
    global_highest = db.session.query(db.func.max(Score.highest_score)).scalar() or 0
    global_highest_percentage = (global_highest / total_questions) * 100 if total_questions else 0

    username = request.cookies.get('username', '')
    user_highest = 0
    if username:
        user_score = Score.query.filter_by(username=username).first()
        if user_score:
            user_highest = user_score.highest_score
    user_highest_percentage = (user_highest / total_questions) * 100 if total_questions else 0

    return {
        'top_score': round(global_highest_percentage, 2),
        'user_highest': round(user_highest_percentage, 2),
        'username': username
    }

@app.route('/')
def index():
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    
    response = make_response(render_template('index.html', questions=questions))
    response.set_cookie('session_id', session_id)
    return response

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username').strip()
    score = 0
    total_questions = len(questions)

    # Skor hesapla
    for q in questions:
        user_answer = request.form.get(f'q{q["id"]}')
        if user_answer == q['correct']:
            score += 1

    # Veritabanını güncelle
    existing_user = Score.query.filter_by(username=username).first()
    if existing_user:
        if score > existing_user.highest_score:
            existing_user.highest_score = score
            existing_user.timestamp = datetime.utcnow()
    else:
        new_user = Score(username=username, highest_score=score)
        db.session.add(new_user)
    
    db.session.commit()

    # Cookie'e kullanıcı adını kaydet
    response = make_response(render_template(
        'result.html',
        last_score=(score / total_questions) * 100 if total_questions else 0,
        total=total_questions
    ))
    response.set_cookie('username', username)
    return response

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/images', 'favicon.ico')

"""
kodun çalıştırılması ve test edilmesi için aşağıdaki siteden deneyin otomatik olarak girecektir.
https://ahmet5414.pythonanywhere.com/
"""
