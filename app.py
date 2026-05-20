# COMPLETE UPDATED PROFESSIONAL app.py

from flask import Flask, render_template, request, redirect, session, flash, make_response
import sqlite3

app = Flask(__name__)
app.secret_key = "ias_secret_key"


# DATABASE CONNECTION

def get_db_connection():

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    return conn


# CREATE TABLES

def create_tables():

    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            subject TEXT,
            content TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS current_affairs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()


# INSERT DEFAULT CURRENT AFFAIRS

def insert_current_affairs():

    conn = get_db_connection()

    existing = conn.execute(
        'SELECT * FROM current_affairs'
    ).fetchall()

    if len(existing) == 0:

        affairs = [

            (
                'India launches Digital Education Mission',
                'Government introduces AI-based education reforms.',
                '2026-05-19'
            ),

            (
                'ISRO prepares for next moon mission',
                'Advanced lunar mission announced.',
                '2026-05-18'
            ),

            (
                'UPSC Exam Pattern Updated',
                'Analytical reasoning focus increased.',
                '2026-05-17'
            ),

            (
                'Green Energy Policies Introduced',
                'India focuses on renewable energy.',
                '2026-05-16'
            )

        ]

        conn.executemany(
            '''
            INSERT INTO current_affairs(title,content,date)
            VALUES(?,?,?)
            ''',
            affairs
        )

        conn.commit()

    conn.close()


create_tables()
insert_current_affairs()


# HOME PAGE

@app.route('/')
def index():

    return render_template('index.html')


# REGISTER

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        # VALIDATION

        if name == "" or email == "" or password == "":

            flash("All fields are required", "danger")

            return redirect('/register')

        conn = get_db_connection()

        existing_user = conn.execute(
            '''
            SELECT * FROM users
            WHERE email=?
            ''',
            (email,)
        ).fetchone()

        if existing_user:

            flash("Email already registered", "danger")

            conn.close()

            return redirect('/register')

        conn.execute(
            '''
            INSERT INTO users(name,email,password)
            VALUES(?,?,?)
            ''',
            (name, email, password)
        )

        conn.commit()
        conn.close()

        flash("Registration Successful. Please Login.", "success")

        return redirect('/login')

    return render_template('register.html')


# LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if email == "" or password == "":

            flash("Please enter email and password", "danger")

            return redirect('/login')

        conn = get_db_connection()

        user = conn.execute(
            '''
            SELECT * FROM users
            WHERE email=? AND password=?
            ''',
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session['user_id'] = user['id']
            session['user_name'] = user['name']

            flash("Login Successful", "success")

            return redirect('/dashboard')

        else:

            flash("Invalid Email or Password", "danger")

            return redirect('/login')

    return render_template('login.html')


# DASHBOARD

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'dashboard.html',
        name=session['user_name']
    )


# ROADMAP

@app.route('/roadmap')
def roadmap():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template('roadmap.html')


# NOTES

@app.route('/notes', methods=['GET', 'POST'])
def notes():

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':

        title = request.form['title']
        subject = request.form['subject']
        content = request.form['content']

        conn.execute(
            '''
            INSERT INTO notes(user_id,title,subject,content)
            VALUES(?,?,?,?)
            ''',
            (
                session['user_id'],
                title,
                subject,
                content
            )
        )

        conn.commit()

        flash("Note Added Successfully", "success")

    all_notes = conn.execute(
        '''
        SELECT * FROM notes
        WHERE user_id=?
        ''',
        (session['user_id'],)
    ).fetchall()

    conn.close()

    return render_template(
        'notes.html',
        notes=all_notes
    )


# DOWNLOAD NOTES

@app.route('/download_notes')
def download_notes():

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    notes = conn.execute(
        '''
        SELECT * FROM notes
        WHERE user_id=?
        ''',
        (session['user_id'],)
    ).fetchall()

    conn.close()

    content = ""

    for note in notes:

        content += f"Title : {note['title']}\n"
        content += f"Subject : {note['subject']}\n"
        content += f"Content : {note['content']}\n"
        content += "\n-----------------------------\n\n"

    response = make_response(content)

    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=IAS_Notes.txt"

    response.headers[
        "Content-type"
    ] = "text/plain"

    return response


# CURRENT AFFAIRS

@app.route('/affairs')
def affairs():

    conn = get_db_connection()

    news = conn.execute(
        '''
        SELECT * FROM current_affairs
        ORDER BY id DESC
        '''
    ).fetchall()

    conn.close()

    return render_template(
        'affairs.html',
        affairs=news
    )


# MOCK TEST

@app.route('/test')
def test():

    if 'user_id' not in session:
        return redirect('/login')

    questions = [

        {
            'question': 'Who is known as the Father of Indian Constitution?',

            'options': [
                'Mahatma Gandhi',
                'Jawaharlal Nehru',
                'B. R. Ambedkar',
                'Sardar Patel'
            ]
        },

        {
            'question': 'Which Article deals with Fundamental Rights?',

            'options': [
                'Article 12 to 35',
                'Article 40 to 50',
                'Article 51A',
                'Article 370'
            ]
        },

        {
            'question': 'Capital of Andhra Pradesh?',

            'options': [
                'Visakhapatnam',
                'Amaravati',
                'Kurnool',
                'Vijayawada'
            ]
        },

        {
            'question': 'Which planet is called Red Planet?',

            'options': [
                'Earth',
                'Mars',
                'Venus',
                'Jupiter'
            ]
        },

        {
            'question': 'National Animal of India?',

            'options': [
                'Lion',
                'Tiger',
                'Elephant',
                'Leopard'
            ]
        }

    ]

    return render_template(
        'test.html',
        questions=questions
    )


# RESULT PAGE

@app.route('/result')
def result():

    return render_template('result.html')


# ADMIN PANEL

@app.route('/admin')
def admin():

    conn = get_db_connection()

    users = conn.execute(
        'SELECT * FROM users'
    ).fetchall()

    conn.close()

    return render_template(
        'admin.html',
        users=users
    )


# LOGOUT

@app.route('/logout')
def logout():

    session.clear()

    flash("Logged Out Successfully", "info")

    return redirect('/')


# MAIN

if __name__ == '__main__':

    app.run(debug=True)