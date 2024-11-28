from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB


app = Flask(__name__)
app.secret_key = 'Priyanka@123'  # Replace with a secure key

db_config = {
    'host': 'localhost',
    'user': 'Root',
    'password': '',
    'database': 'library'
}

# Create a connection pool
pool = PooledDB(
    creator=pymysql,
    maxconnections=100,
    **db_config
)
conn = pool.connection()

@app.route('/', methods=['GET', 'POST'])
def index():


    try:
        c = conn.cursor(DictCursor)

        #to delete all the data
        
        # c.execute('DELETE FROM reviews;')
        # c.execute('DELETE FROM websiteusers;')



        # Ensure tables exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS librarydata
             (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            );''')
        
    finally:
        c.close()
        conn.commit()
        print("message:The table is successfully created") 
        return render_template('home.html')
# Register route
#user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')  # Default to user role

        conn = pool.connection()
        cur = conn.cursor()
        try:
          
            
            # Check if email already exists
            sql = 'SELECT * FROM librarydata WHERE name = %s'
            cur.execute(sql, (name,))
            existing_user = cur.fetchone()
            
            if existing_user:
                replies = "Sorry, the ID already exists!"
                return render_template('register.html', message=replies)
            else:
                # Hash the password before storing
                # hashed_password = generate_password_hash(password)
                
                # Add user to database
                sql = 'INSERT INTO librarydata (username, password,role) VALUES (%s, %s,%s)'
                cur.execute(sql, (username,password,role))
                conn.commit()
           
        
        except pymysql.MySQLError as e:
            # logger.error(f"Error executing query: {e}")
            return render_template('register.html', message='Database query error')
        
        finally:
            if conn:
                cur.close()
                conn.close()

    return render_template('register.html')


# Admin Login
@app.route('/adminLogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s AND role='admin'", (username, password))
            admin = cursor.fetchone()
        connection.close()
        if admin:
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('admin_home'))
        else:
            flash('Invalid admin credentials!')
    return render_template('adminLogin.html')

# User Login
@app.route('/userLogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s AND role='user'", (username, password))
            user = cursor.fetchone()
        connection.close()
        if user:
            session['username'] = username
            session['role'] = 'user'
            return redirect(url_for('user_home'))
        else:
            flash('Invalid user credentials!')
    return render_template('userLogin.html')

# Admin Home Page
@app.route('/adminHome')
def admin_home():
    if 'role' in session and session['role'] == 'admin':
        return render_template('adminHome.html')
    return redirect(url_for('home'))

# User Home Page
@app.route('/userHome')
def user_home():
    if 'role' in session and session['role'] == 'user':
        return render_template('userHome.html')
    return redirect(url_for('home'))

# Transactions Page (Shared)
@app.route('/transactions')
def transactions():
    if 'role' in session:
        return render_template('Transactions.html', role=session['role'])
    return redirect(url_for('home'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
