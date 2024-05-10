from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from flask import jsonify, request
import pickle
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from flask import flash

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
app.secret_key = "toplevelsecret"

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'bug1'
}

# Function to establish MySQL connection
def connect_to_mysql():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print("Error connecting to MySQL:", err)
        return None

# Function to clean text
def clean_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    return ' '.join(filtered_tokens)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('employee_dashboard.html')


@app.route('/emplogin', methods=['GET', 'POST'])
def emplogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect_to_mysql()
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT id FROM employees WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                employee_id = cursor.fetchone()
                session['employee_id'] = employee_id
                cursor.close()
                conn.close()

                if employee_id:
                    session['employee_id'] = employee_id[0]  
                    return jsonify({"redirect": url_for('dashboard')}) 
                else:
                    return jsonify({"error": "Invalid username or password"}), 401
            except mysql.connector.Error as err:
                print("Database query error:", err)
                return jsonify({"error": "Database query error"}), 500
        else:
            return jsonify({"error": "Database connection error"}), 500
    else:
        return render_template('emplogin.html')


@app.route('/view_bugs')
def view_bugs():
    connection = connect_to_mysql()
    employee_id=session['employee_id']
    bug_data1=[]
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM bugass WHERE Progress = 'open' OR Progress = 'in_progress' and assignedby=%s;"
            cursor.execute(query,(employee_id,))
            bug_data1 = cursor.fetchall()
        except mysql.connector.Error as err:
            print("Error fetching bug details:", err)
        finally:
            cursor.close()
            connection.close()
    return render_template('view_bugs.html', bug_data=bug_data1)

@app.route('/', methods=['GET','POST'])
def manager_dashboard():
    return render_template('manager_dashboard.html')
@app.route('/manager_dashboard1', methods=['GET','POST'])
def manager_dashboard1():
    return render_template('manager_dashboard.html')

@app.route('/add-employee', methods=['GET','POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = connect_to_mysql()
        if conn:
            try:
                cursor = conn.cursor()
                # Check if the email is already registered
                cursor.execute("SELECT email FROM employees WHERE email = %s", (email,))
                if cursor.fetchone():
                    return jsonify({"error": "Employee already registered please login"}), 409  # Return error as JSON

                # Proceed to insert new employee if the email is not found
                query = "INSERT INTO employees (username, password, full_name, email) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (username, password, name, email))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"success": "Employee successfully registered"}), 200  # Return success as JSON
            except mysql.connector.Error as err:
                print("Error executing SQL query:", err)
                return jsonify({"error": "Error adding employee to the database"}), 500  # Return error as JSON
        else:
            return jsonify({"error": "Database connection error"}), 500  # Return error as JSON
    return render_template('add_employee.html')  # Serve the form on GET request



@app.route('/add-Tester', methods=['GET', 'POST'])
def add_tester_form():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = connect_to_mysql()
        if conn:
            try:
                cursor = conn.cursor()
                # Ensure no duplicate emails
                cursor.execute("SELECT * FROM testers WHERE email = %s", (email,))
                if cursor.fetchone():
                    return jsonify({"error": "Tester already registered please login"}), 409
                
                query = "INSERT INTO testers (username, password, full_name, email) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (username, password, name, email))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"success": "Tester successfully added"}), 200
            except mysql.connector.Error as err:
                print("Error executing SQL query:", err)
                return jsonify({"error": "Error adding tester to the database"}), 500
        else:
            return jsonify({"error": "Database connection error"}), 500
    else:
        return render_template('add_tester.html')


@app.route('/teslogin', methods=['GET', 'POST'])
def teslogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect_to_mysql()
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT id FROM testers WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                employee_id = cursor.fetchone()
                session['tester_id'] = employee_id
                cursor.close()
                conn.close()

                if employee_id:
                    session['employee_id'] = employee_id[0]  # Managing user session
                    return jsonify({"redirect": url_for('tester_dashboard')})  # Redirect via JSON
                else:
                    return jsonify({"error": "Invalid username or password"}), 401
            except mysql.connector.Error as err:
                print("Database query error:", err)
                return jsonify({"error": "Database query error"}), 500
        else:
            return jsonify({"error": "Database connection error"}), 500
    else:
        return render_template('teslogin.html')

@app.route('/report_bug', methods=['GET'])
def report_bug():
    return render_template('report bug.html')



@app.route('/backend/fetch_testers_endpoint', methods=['GET'])
def fetch_testers_endpoint():
    conn = connect_to_mysql()
    tester_data = []
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT id, full_name FROM testers"
            cursor.execute(query)
            tester_rows = cursor.fetchall()
            for row in tester_rows:
                tester_data.append({"id": row[0], "name": row[1]})
        except mysql.connector.Error as err:
            print("Error fetching testers:", err)
        finally:
            cursor.close()
            conn.close()
    return jsonify(tester_data)

# Load the model
with open('your_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Load the vectorizer
with open('your_vectorizer.pkl', 'rb') as file:
    vectorizer = pickle.load(file)

def assign_priority(category):
    if category in ['blocker', 'critical']:
        return 'High'
    elif category == 'major':
        return 'Medium'
    elif category in ['enhancement', 'normal']:
        return 'Medium'
    else:
        return 'Low'

@app.route('/add_bug', methods=['POST'])
def add_bug():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        bug_description = data['description']
        tester_name = data['assignedTesterId']
    except KeyError:
        return jsonify({"error": "Missing data fields"}), 400

    cleaned_bug_description = clean_text(bug_description)
    bug_description_tfidf = vectorizer.transform([cleaned_bug_description])
    predicted_priority = model.predict(bug_description_tfidf)[0]
    priority=assign_priority(predicted_priority)


    conn = connect_to_mysql()
    employee_id=session['employee_id']
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO BugAss (Description, Priority, AssignedTo, assignedby,pro) VALUES (%s, %s, %s,%s,%s)"
            cursor.execute(query, (bug_description, predicted_priority, tester_name,employee_id,priority))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": "Bug added successfully"}), 200
        except mysql.connector.Error as err:
            print("Error adding bug:", err)
            return jsonify({"error": "Error adding bug to the database"}), 500

    return jsonify({"error": "Database connection failed"}), 500

@app.route('/tsdashboard',methods=['GET','POST'])
def tester_dashboard():
    conn = connect_to_mysql()
    bug_list = []
    tester_id = session['tester_id']
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT bugid, Description, Progress, priority,pro FROM bugass where AssignedTo =%s"
            cursor.execute(query,tester_id)
            bug_list = cursor.fetchall()
        except mysql.connector.Error as err:
            print("Error fetching bug details:", err)
        finally:
            cursor.close()
            conn.close()
    return render_template('bug_list.html', bug_list=bug_list)

@app.route('/work_on_bug/<int:bug_id>')
def work_on_bug(bug_id):
    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT Progress, Suggestion FROM bugass WHERE bugid = %s", (bug_id,))
    bug = cursor.fetchone()
    cursor.close()
    conn.close()
    if bug:
        return render_template('work_on_bug.html', bug_id=bug_id, current_progress=bug[0], current_suggestion=bug[1])
    else:
        return 'Bug not found', 404

@app.route('/update_bug/<int:bug_id>', methods=['POST'])
def update_bug(bug_id):
    progress = request.form['progress']
    suggestion = request.form['suggestion']
    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute("UPDATE bugass SET Progress = %s, Suggestion = %s WHERE bugid = %s", (progress, suggestion, bug_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('tester_dashboard'))  # Redirect to the dashboard after updating

@app.route('/team',methods=['GET'])
def team():
    return render_template('team.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('manager_dashboard')) 

if __name__ == '__main__':
    app.run(debug=True)
