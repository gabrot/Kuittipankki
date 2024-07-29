from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
from flask_migrate import Migrate
import os

# Määritellään vakiot
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Luodaan Flask-sovellus
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///kuittipankki'
app.config['SECRET_KEY'] = 'salainen_avain'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Määritellään apufunktiot
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['next'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Määritellään tietokantamallit
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Kuitti(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paivamäärä = db.Column(db.Date, nullable=False)
    kauppa = db.Column(db.String(100), nullable=False)
    summa = db.Column(db.Float, nullable=False)
    kategoria = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tiedosto = db.Column(db.String(255))

# Määritellään reitit
@app.route('/')
@login_required
def index():
    kuitit = Kuitti.query.filter_by(user_id=session['user_id']).all()
    return render_template('index.html', kuitit=kuitit)

@app.route('/lisaa_kuitti', methods=['GET', 'POST'])
@login_required
def lisaa_kuitti():
    if request.method == 'POST':
        uusi_kuitti = Kuitti(
            paivamäärä=datetime.strptime(request.form['paivamäärä'], '%Y-%m-%d').date(),
            kauppa=request.form['kauppa'],
            summa=float(request.form['summa']),
            kategoria=request.form['kategoria'],
            user_id=session['user_id']
        )
        
        if 'tiedosto' in request.files:
            file = request.files['tiedosto']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                uusi_kuitti.tiedosto = filename

        db.session.add(uusi_kuitti)
        db.session.commit()
        flash('Kuitti lisätty onnistuneesti!', 'success')
        return redirect(url_for('index'))
    return render_template('lisaa_kuitti.html')

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Käyttäjänimi on jo käytössä.', 'error')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Rekisteröityminen onnistui! Voit nyt kirjautua sisään.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Kirjautuminen onnistui!', 'success')
            next_page = session.pop('next', None)
            return redirect(next_page or url_for('index'))
        else:
            flash('Väärä käyttäjänimi tai salasana.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('Olet kirjautunut ulos.', 'info')
    return redirect(url_for('login'))

@app.errorhandler(401)
def unauthorized(error):
    flash('Sinun täytyy kirjautua sisään nähdäksesi tämän sivun.', 'error')
    return redirect(url_for('login'))

# Käynnitettään sovellus
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    with app.app_context():
        db.create_all()
    app.run(debug=True)