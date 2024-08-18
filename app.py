from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
import psycopg2
from dotenv import load_dotenv
from forms import ReceiptForm

# Load environment variables
load_dotenv()

# App configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf'}

# Database functions
def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    with open('schema.sql', 'r') as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully.")

# Helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Fetch receipts for logged-in users
    receipts = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM receipts WHERE user_id = %s", (session['user_id'],))
    receipts = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html', receipts=receipts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash('Username already exists.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        cur.close()
        conn.close()
    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = ReceiptForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO receipts (filename, description, amount, receipt_date, user_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (filename, form.description.data, form.amount.data, form.receipt_date.data, session['user_id']))
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Receipt uploaded successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid file type', 'error')
    return render_template('upload.html', form=form)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Initialize the app
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)