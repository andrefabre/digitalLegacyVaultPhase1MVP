from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import uuid
import magic

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

DB_PATH = '/opt/dlv_mvp/app/dlv_mvp.db'
UPLOAD_PATH = '/opt/dlv_mvp/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png'
}

# --- Database ---

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('owner', 'executor', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asset_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS executor_nominations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            executor_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'denied')),
            nominated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id),
            FOREIGN KEY (executor_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_size INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            detail TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Create default admin account if it does not exist
    cursor.execute('SELECT id FROM users WHERE email = ?', ('admin@dlv.local',))
    if not cursor.fetchone():
        cursor.execute(
            'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
            ('admin@dlv.local', generate_password_hash('admin123'), 'admin')
        )

    conn.commit()
    conn.close()

def log_audit(user_id, action, detail=None):
    conn = get_db()
    cursor = conn.cursor()
    ip = request.remote_addr if request else None
    cursor.execute(
        'INSERT INTO audit_log (user_id, action, detail, ip_address) VALUES (?, ?, ?, ?)',
        (user_id, action, detail, ip)
    )
    conn.commit()
    conn.close()

# --- Health ---

@app.route('/health')
def health():
    return 'OK', 200

# --- Auth helpers ---

def login_required(role=None):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return 'Access denied', 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# --- Owner registration and login ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'owner')

        if not email or not password:
            return render_template('register.html', error='Email and password are required')

        if role not in ('owner', 'executor'):
            return render_template('register.html', error='Invalid role')

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
                (email, generate_password_hash(password), role)
            )
            conn.commit()
            user_id = cursor.lastrowid
            log_audit(user_id, 'register', f'New {role} registered: {email}')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Email already registered')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['email'] = user['email']
            log_audit(user['id'], 'login', f'User logged in: {email}')

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'owner':
                return redirect(url_for('owner_dashboard'))
            elif user['role'] == 'executor':
                return redirect(url_for('executor_dashboard'))

        return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    log_audit(user_id, 'logout')
    session.clear()
    return redirect(url_for('login'))

# --- Owner routes ---

@app.route('/owner')
def owner_dashboard():
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM asset_records WHERE owner_id = ?', (session['user_id'],))
    records = cursor.fetchall()
    cursor.execute('SELECT * FROM document_uploads WHERE owner_id = ?', (session['user_id'],))
    uploads = cursor.fetchall()
    cursor.execute('''
        SELECT e.*, u.email as executor_email
        FROM executor_nominations e
        JOIN users u ON e.executor_id = u.id
        WHERE e.owner_id = ?
    ''', (session['user_id'],))
    nominations = cursor.fetchall()
    conn.close()

    return render_template('owner_dashboard.html', records=records, uploads=uploads, nominations=nominations)

@app.route('/owner/records/add', methods=['GET', 'POST'])
def add_record():
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            return render_template('add_record.html', error='Title is required')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO asset_records (owner_id, title, description) VALUES (?, ?, ?)',
            (session['user_id'], title, description)
        )
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        log_audit(session['user_id'], 'add_record', f'Record added: {title}')
        return redirect(url_for('owner_dashboard'))

    return render_template('add_record.html')

@app.route('/owner/records/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM asset_records WHERE id = ? AND owner_id = ?', (record_id, session['user_id']))
    conn.commit()
    conn.close()
    log_audit(session['user_id'], 'delete_record', f'Record deleted: {record_id}')
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/upload', methods=['GET', 'POST'])
def upload_document():
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error='No file selected')

        file = request.files['file']

        if file.filename == '':
            return render_template('upload.html', error='No file selected')

        if file.content_length and file.content_length > MAX_FILE_SIZE:
            return render_template('upload.html', error='File exceeds 10MB limit')

        file_bytes = file.read()

        if len(file_bytes) > MAX_FILE_SIZE:
            return render_template('upload.html', error='File exceeds 10MB limit')

        mime = magic.from_buffer(file_bytes, mime=True)
        if mime not in ALLOWED_MIME_TYPES:
            return render_template('upload.html', error=f'File type not allowed: {mime}')

        stored_filename = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_PATH, stored_filename)

        with open(file_path, 'wb') as f:
            f.write(file_bytes)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO document_uploads (owner_id, original_filename, stored_filename, file_size) VALUES (?, ?, ?, ?)',
            (session['user_id'], file.filename, stored_filename, len(file_bytes))
        )
        conn.commit()
        conn.close()
        log_audit(session['user_id'], 'upload', f'File uploaded: {file.filename}')
        return redirect(url_for('owner_dashboard'))

    return render_template('upload.html')

@app.route('/owner/nominate', methods=['GET', 'POST'])
def nominate_executor():
    if 'user_id' not in session or session.get('role') != 'owner':
        return redirect(url_for('login'))

    if request.method == 'POST':
        executor_email = request.form.get('executor_email', '').strip()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ? AND role = ?', (executor_email, 'executor'))
        executor = cursor.fetchone()

        if not executor:
            conn.close()
            return render_template('nominate.html', error='Executor not found')

        cursor.execute(
            'INSERT INTO executor_nominations (owner_id, executor_id) VALUES (?, ?)',
            (session['user_id'], executor['id'])
        )
        conn.commit()
        conn.close()
        log_audit(session['user_id'], 'nominate', f'Executor nominated: {executor_email}')
        return redirect(url_for('owner_dashboard'))

    return render_template('nominate.html')

# --- Admin routes ---

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.execute('SELECT * FROM executor_nominations')
    nominations = cursor.fetchall()
    cursor.execute('SELECT * FROM document_uploads')
    uploads = cursor.fetchall()
    cursor.execute('SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 50')
    audit = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', users=users, nominations=nominations, uploads=uploads, audit=audit)

@app.route('/admin/nominations/<int:nomination_id>/approve', methods=['POST'])
def approve_nomination(nomination_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE executor_nominations SET status = ? WHERE id = ?',
        ('approved', nomination_id)
    )
    conn.commit()
    conn.close()
    log_audit(session['user_id'], 'approve_nomination', f'Nomination approved: {nomination_id}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/nominations/<int:nomination_id>/deny', methods=['POST'])
def deny_nomination(nomination_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE executor_nominations SET status = ? WHERE id = ?',
        ('denied', nomination_id)
    )
    conn.commit()
    conn.close()
    log_audit(session['user_id'], 'deny_nomination', f'Nomination denied: {nomination_id}')
    return redirect(url_for('admin_dashboard'))

# --- Executor routes ---

@app.route('/executor')
def executor_dashboard():
    if 'user_id' not in session or session.get('role') != 'executor':
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM executor_nominations
        WHERE executor_id = ? AND status = 'approved'
    ''', (session['user_id'],))
    approved_nominations = cursor.fetchall()

    records = []
    for nomination in approved_nominations:
        cursor.execute(
            'SELECT * FROM asset_records WHERE owner_id = ?',
            (nomination['owner_id'],)
        )
        records.extend(cursor.fetchall())

    conn.close()
    log_audit(session['user_id'], 'executor_view', 'Executor viewed approved records')
    return render_template('executor_dashboard.html', records=records, approved=len(approved_nominations) > 0)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)