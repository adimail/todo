from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# PostgreSQL database configuration
db_config = {
    'database': 'mycrudapp',
    'user': 'postgres',
    'password': 'sonchafa',
    'host': 'localhost'
}

@app.route('/')
def index():
    # Connect to the database and retrieve records
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM your_table;')
    records = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('index.html', records=records)

@app.route('/add', methods=['POST'])
def add_record():
    if request.method == 'POST':
        # Retrieve data from the form
        data = request.form['data']
        
        # Connect to the database and insert a new record
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO your_table (column_name) VALUES (%s);', (data,))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update_record(id):
    if request.method == 'POST':
        # Retrieve updated data from the form
        updated_data = request.form['data']
        
        # Connect to the database and update the record
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute('UPDATE your_table SET column_name = %s WHERE id = %s;', (updated_data, id))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_record(id):
    # Connect to the database and delete the record
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM your_table WHERE id = %s;', (id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
