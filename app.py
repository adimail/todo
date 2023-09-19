from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from dotenv import load_dotenv
import os

app = Flask(__name__)

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

@app.route('/')
def index():
    connection, cursor = connect_db()
    cursor.execute('SELECT * FROM your_table;')
    records = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('index.html', records=records)

@app.route('/add', methods=['POST'])
def add_record():
    if request.method == 'POST':
        data = request.form['data']
        connection, cursor = connect_db()
        cursor.execute('INSERT INTO your_table (tasks) VALUES (%s);', (data,))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update_record(id):
    if request.method == 'POST':
        updated_data = request.form['data']
        connection, cursor = connect_db()
        cursor.execute('UPDATE your_table SET tasks = %s WHERE id = %s;', (updated_data, id))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_record(id):
    connection, cursor = connect_db()
    cursor.execute('DELETE FROM your_table WHERE id = %s;', (id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
