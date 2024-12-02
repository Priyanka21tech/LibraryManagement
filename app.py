from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
import os

app = Flask(__name__)

# # Use a secure secret key
# app.secret_key = 'Priyanka@123'

# Database configuration-- details for connecting to the MySQL database.
db_config = {
    'host': 'localhost',
    'user': 'root', 
    'password': '',  
    'database': 'library'
}

# Create a connection pool
pool = PooledDB(
    creator=pymysql,
    maxconnections=100,
    cursorclass=DictCursor,
    **db_config
)

# Helper function to get a database connection
def get_db_connection():
    return pool.connection()

# Ensure the required table exists
def initialize_database():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS librarydata (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('user', 'admin') NOT NULL DEFAULT 'user'
                )
            ''')
            conn.commit()
    finally:
        conn.close()

initialize_database()

@app.route('/')
def home():
    return render_template('home.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')  # Default role is 'user'

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if username already exists
                cursor.execute('SELECT * FROM librarydata WHERE username = %s', (username,))
                existing_user = cursor.fetchone()

                if existing_user:
                    return render_template('register.html', message="Sorry, the username already exists!")

                # Insert the new user into the database
                cursor.execute('INSERT INTO librarydata (username, password, role) VALUES (%s, %s, %s)', 
                               (username, password, role))
                conn.commit()
                flash("Registration successful! Please log in.")
                return redirect(url_for('home'))
        except pymysql.MySQLError as e:
            return render_template('register.html', message="Database error occurred.")
        finally:
            conn.close()
    return render_template('register.html')

# Admin login
@app.route('/adminLogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']  # Ensure names match the form inputs
        password = request.form['password']

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM librarydata WHERE username = %s AND password = %s AND role = 'admin'",
                    (username, password)
                )
                admin = cursor.fetchone()

                if admin:
                    session['username'] = username
                    session['role'] = 'admin'
                    return redirect(url_for('admin_home'))
                else:
                    flash('Invalid credentials. Please try again.')
                    return redirect(url_for('admin_login'))  # Reload the login page
        finally:
            conn.close()
    return render_template('adminlogin.html')


# User login
@app.route('/userLogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if the user exists
                cursor.execute(
                    "SELECT * FROM librarydata WHERE username = %s AND role = 'user'", 
                    (username,)
                )
                user = cursor.fetchone()

                if user:
                    # If user exists, check password
                    if user['password'] == password:
                        session['username'] = username
                        session['role'] = 'user'
                        return redirect(url_for('user_home'))
                    else:
                        flash('Incorrect password!')
                else:
                    # If user does not exist, redirect to registration
                    flash('User not registered! Please register first.')
                    return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('userlogin.html')


# Admin home page
@app.route('/adminHome')
def admin_home():
    if 'role' in session and session['role'] == 'admin':
        return render_template('adminHome.html')
    return redirect(url_for('home'))

# User home page
@app.route('/userHome')
def user_home():
    if 'role' in session and session['role'] == 'user':
        return render_template('userHome.html')
    return redirect(url_for('home'))

# Transactions page
@app.route('/transactions')
def transactions():
    if 'role' in session:
        return render_template('Transactions.html', role=session['role'])
    return redirect(url_for('home'))


# maintenance page
@app.route('/maintenance')
def maintenance():
    if 'role' in session:
        return render_template('maintenance.html', role=session['role'])
    return redirect(url_for('home'))

# Reports page
@app.route('/reports')
def reports():
    if 'role' in session:
        return render_template('reports.html', role=session['role'])
    return redirect(url_for('home'))

#Logout
@app.route('/logout')
def logout():
    role = session.get('role', None)  # Get the role before clearing the session
    session.clear()  # Clear the session
    if role == 'admin':
        return redirect(url_for('admin_home'))
    elif role == 'user':
        return redirect(url_for('user_home'))
    else:
        flash('You have been logged out.')
        return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)
