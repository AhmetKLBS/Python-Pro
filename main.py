from flask import Flask, render_template, request, redirect, url_for, make_response
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
    session_id = db.Column(db.String(36), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Sorular ve cevaplar (EN BAŞTA TANIMLANMALI)
questions = [
    {
        'id': 1,
        'question': 'Discord.py kütüphanesi temel olarak hangi amaçla kullanılır?',
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
        'question': 'NLTK kütüphanesinin temel kullanımı nedir?',
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
        'question': 'Flask\'ta template engine olarak ne kullanılır?',
        'options': ['jinja2', 'handlebars', 'pug', 'ejs'],
        'correct': 'jinja2'
    }
]

@app.before_first_request
def create_tables():
    db.create_all()

@app.context_processor
def inject_scores():
    total_questions = len(questions)
    session_id = request.cookies.get('session_id')

    # Tüm Kullanıcıların En Yüksek Skoru
    global_max = db.session.query(db.func.max(Score.score)).scalar() or 0
    global_percent = round((global_max / total_questions) * 100, 2) if total_questions else 0

    # Mevcut Kullanıcının En Yüksek Skoru
    user_max = db.session.query(db.func.max(Score.score)).filter_by(session_id=session_id).scalar() or 0
    user_percent = round((user_max / total_questions) * 100, 2) if total_questions else 0

    return dict(
        top_score=global_percent,
        user_highest=user_percent
    )

@app.route('/')
def index():
    session_id = request.cookies.get('session_id') or str(uuid.uuid4())
    response = make_response(render_template('index.html', questions=questions))
    response.set_cookie('session_id', session_id)
    return response
@app.route('/users')
def list_users():
    all_scores = Score.query.all()
    
    # Toplam soru sayısını hesapla
    total_questions = len(questions)
    
    return render_template('users.html', scores=all_scores, total_questions=total_questions)
@app.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username').strip()
    score = 0
    session_id = request.cookies.get('session_id')

    for q in questions:
        user_answer = request.form.get(f'q{q["id"]}')
        if user_answer == q['correct']:
            score += 1

    if session_id and username:
        new_score = Score(
            session_id=session_id,
            username=username,
            score=score
        )
        db.session.add(new_score)
        db.session.commit()

    return redirect(url_for('result'))

@app.route('/result')
def result():
    session_id = request.cookies.get('session_id')
    last_score = 0
    user_scores = Score.query.filter_by(session_id=session_id).order_by(Score.timestamp.desc()).first()
    if user_scores:
        last_score = user_scores.score

    # Tüm Kullanıcıların En Yüksek Skoru
    global_max = db.session.query(db.func.max(Score.score)).scalar() or 0
    global_percent = round((global_max / len(questions)) * 100, 2)

    # Mevcut Kullanıcının En Yüksek Skoru
    user_max = db.session.query(db.func.max(Score.score)).filter_by(session_id=session_id).scalar() or 0
    user_percent = round((user_max / len(questions)) * 100, 2)

    return render_template(
        'result.html',
        last_score=last_score,
        user_highest=user_percent,
        top_score=global_percent,
        total=len(questions)
    )

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')
