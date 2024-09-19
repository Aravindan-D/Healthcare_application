from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error



app = Flask(__name__)
app.secret_key = 'fdqwe' 

# Error handler for all errors
# @app.errorhandler(Exception)
# def handle_error(error):
#     return render_template('error.html', error=error), 500

# Database connection
def create_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Hida@123',
            database='healthcare'
        )
    except Error as e:
        print(f"Error: '{e}'")
    return connection

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'patient':
                return redirect(url_for('patient_dashboard'))
            elif user['role'] == 'carer':
                return redirect(url_for('carer_dashboard'))
            elif user['role'] == 'manager':
                return redirect(url_for('manager_dashboard'))
        else:
            return 'Incorrect username/password!'

    return redirect(url_for('home'))

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'loggedin' in session and session['role'] == 'patient':
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profiles WHERE user_id=%s", (session['id'],))
        profile = cursor.fetchone()
        cursor.execute("SELECT * FROM care_requirements WHERE user_id=%s", (session['id'],))
        care_requirements = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('patient_dashboard.html', username=session['username'], profile=profile, care_requirements=care_requirements)
    return redirect(url_for('home'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'loggedin' in session:
        name = request.form['name']
        age = request.form['age']
        medical_history = request.form['medical_history']

        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO profiles (user_id, name, age, medical_history) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=%s, age=%s, medical_history=%s", 
                       (session['id'], name, age, medical_history, name, age, medical_history))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('patient_dashboard'))
    return redirect(url_for('home'))


@app.route('/update_profile_carer', methods=['POST'])
def update_profile_carer():
    if 'loggedin' in session:
        availability = request.form['availability']
        skills = request.form['skills']
        qualifications = request.form['qualifications']
        user_name = request.form['user_name']

        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO carer_details (user_name, availability, skills, qualifications) VALUES (%s, %s, %s, %s) ",
                       ( user_name, availability, skills, qualifications))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('carer_dashboard'))
    return redirect(url_for('home'))

@app.route('/update_care_requirements', methods=['POST'])
def update_care_requirements():
    if 'loggedin' in session:
        timing = request.form['timing']
        medications = request.form['medications']
        personal_needs = request.form['personal_needs']

        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO care_requirements (user_id, timing, medications, personal_needs) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE timing=%s, medications=%s, personal_needs=%s", 
                       (session['id'], timing, medications, personal_needs, timing, medications, personal_needs))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('patient_dashboard'))
    return redirect(url_for('home'))

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'loggedin' in session:
        feedback = request.form['feedback']

        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO feedback (user_id, feedback) VALUES (%s, %s)", (session['id'], feedback))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('patient_dashboard'))
    return redirect(url_for('home'))

@app.route('/carer_dashboard')
def carer_dashboard():
    if 'loggedin' in session and session['role'] == 'carer':
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profiles WHERE user_id=%s", (session['id'],))
        profile = cursor.fetchone()
        cursor.execute("SELECT * FROM schedules WHERE carer_id=%s", (session['id'],))
        schedules = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('carer_dashboard.html', username=session['username'], profile=profile, schedules=schedules)
    return redirect(url_for('home'))

@app.route('/add_patient_note', methods=['POST'])
def add_patient_note():
    if 'loggedin' in session and session['role'] == 'carer':
        patient_id = request.form['patient_id']
        note = request.form['note']

        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO notes (carer_id, patient_id, note) VALUES (%s, %s, %s)", (session['id'], patient_id, note))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('carer_dashboard'))
    return redirect(url_for('home'))

@app.route('/manager_dashboard')
def manager_dashboard():
    if 'loggedin' in session and session['role'] == 'manager':
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM care_requirements")
        care_requirements = cursor.fetchall()
        cursor.execute("SELECT user_id, availability FROM profiles WHERE availability IS NOT NULL")
        carers = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('manager_dashboard.html', username=session['username'], care_requirements=care_requirements, carers=carers)
    return redirect(url_for('home'))

@app.route('/optimize_schedule', methods=['POST'])
def optimize_schedule():
    if 'loggedin' in session and session['role'] == 'manager':
        # Here you would implement the optimization logic, potentially using an external library or service
        return redirect(url_for('manager_dashboard'))
    return redirect(url_for('home'))

@app.route('/adjust_schedule', methods=['POST'])
def adjust_schedule():
    if 'loggedin' in session and session['role'] == 'manager':
        carer_id = request.form['carer_id']
        patient_id = request.form['patient_id']
        date = request.form['date']
        time = request.form['time']

        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO schedules (carer_id, patient_id, date, time) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE date=%s, time=%s", 
                       (carer_id, patient_id, date, time, date, time))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('manager_dashboard'))
    return redirect(url_for('home'))


@app.route('/create_patient', methods=['POST'])
def create_patient():
    username = request.form['patient_username']
    password = request.form['patient_password']
    name = request.form['patient_name']
    email = request.form['patient_email']

    # Add code to insert the patient data into the database
    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username,password,role) VALUES (%s, %s, %s) ", 
                    (username, password, "patient"))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('manager_dashboard'))

@app.route('/create_carer', methods=['POST'])
def create_carer():
    username = request.form['carer_username']
    password = request.form['carer_password']
    name = request.form['carer_name']
    email = request.form['carer_email']

    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username,password,role) VALUES (%s, %s, %s) ", 
                    (username, password, "carer"))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('manager_dashboard'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)