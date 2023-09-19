from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import psycopg2
from dotenv import load_dotenv
import os

secret_key = os.urandom(24)

app = Flask(__name__)
app.secret_key = secret_key

bcrypt = Bcrypt(app)

load_dotenv()
password = os.getenv("password")

# PostgreSQL database configuration
db_config = {
    'database': 'mycrudapp',
    'user': 'postgres',
    'password': password,
    'host': 'localhost'
}

def connect_db():
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    return connection, cursor

# Create user table if not exists
def create_user_table():
    connection, cursor = connect_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password_hash VARCHAR(60) NOT NULL
        );
    ''')
    connection.commit()
    cursor.close()
    connection.close()

# Create user-specific task table
def create_task_table(user_id):
    connection, cursor = connect_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_{}_tasks (
            id SERIAL PRIMARY KEY,
            task VARCHAR(255) NOT NULL
        );
    '''.format(user_id))
    connection.commit()
    cursor.close()
    connection.close()

# Initialize database tables
create_user_table()

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' in session:
        user_id = session['user_id']
        
        if request.method == 'POST':
            new_username = request.form['new_username']
            connection, cursor = connect_db()
            cursor.execute('UPDATE users SET username = %s WHERE id = %s;', (new_username, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            
            flash('Account information updated successfully', 'success')
        
        connection, cursor = connect_db()
        cursor.execute('SELECT username FROM users WHERE id = %s;', (user_id,))
        user_info = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return render_template('account.html', username=user_info[0])
    
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        create_task_table(user_id)
        connection, cursor = connect_db()
        cursor.execute('SELECT * FROM user_{}_tasks;'.format(user_id))
        records = cursor.fetchall()
        
        # Fetch the username of the logged-in user
        cursor.execute('SELECT username FROM users WHERE id = %s;', (user_id,))
        user_info = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Pass the username to the template
        return render_template('index.html', records=records, username=user_info[0])
    
    return redirect(url_for('login'))


@app.route('/add', methods=['POST'])
def add_record():
    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session['user_id']
            data = request.form['data']
            connection, cursor = connect_db()
            cursor.execute('INSERT INTO user_{}_tasks (task) VALUES (%s);'.format(user_id), (data,))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Task added successfully', 'success')
        else:
            flash('You need to log in first', 'error')
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update_record(id):
    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session['user_id']
            updated_data = request.form['data']
            connection, cursor = connect_db()
            cursor.execute('UPDATE user_{}_tasks SET task = %s WHERE id = %s;'.format(user_id), (updated_data, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Task updated successfully', 'success')
        else:
            flash('You need to log in first', 'error')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_record(id):
    if 'user_id' in session:
        user_id = session['user_id']
        connection, cursor = connect_db()
        cursor.execute('DELETE FROM user_{}_tasks WHERE id = %s;'.format(user_id), (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Task deleted successfully', 'success')
    else:
        flash('You need to log in first', 'error')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        connection, cursor = connect_db()
        cursor.execute('SELECT id FROM users WHERE username = %s;', (username,))
        existing_user = cursor.fetchone()
        cursor.close()
        connection.close()

        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
        else:
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            connection, cursor = connect_db()
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s);', (username, password_hash))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection, cursor = connect_db()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = %s;', (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and bcrypt.check_password_hash(user[2], password):
            session['user_id'] = user[0]
            flash('Login successful.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout successful.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run()

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run()
