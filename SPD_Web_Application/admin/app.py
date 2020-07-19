from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mail import Mail, Message
import nexmo
import matplotlib.pyplot as pyPlot
import requests
import sys
import json

client = nexmo.Client( key = "enter_your_key_here", secret = "enter_your_secret_here")

app = Flask(__name__)

# Config E-Mail settings
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'enter_your_email_here',
	MAIL_PASSWORD = 'enter_your_pswd_here'
	)
mail = Mail(app)

# Config MySQL
app.config['MYSQL_HOST'] = 'enter_your_hostname_here'
app.config['MYSQL_USER'] = 'enter_your_username_here'
app.config['MYSQL_PASSWORD'] = 'enter_your_pswd_here'
app.config['MYSQL_DB'] = 'speed'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Register Form Class


class RegisterForm(Form):
    adminName = StringField(
        "Enter your Name", [validators.Length(min=1, max=50)])
    adminCode = StringField("Enter your Identification Code", [
                            validators.Length(min=1, max=12)])
    adminUsername = StringField(
        'Set your Username', [validators.Length(min=4, max=25)])
    adminPassword = PasswordField('Enter a valid Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Registration


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        adminName = form.adminName.data
        adminCode = form.adminCode.data
        adminUsername = form.adminUsername.data
        adminPassword = sha256_crypt.encrypt(str(form.adminPassword.data))

        # Creating the cursor
        cur = mysql.connection.cursor()

        # Executing Query
        cur.execute("INSERT INTO admin(adminName, adminCode, adminUsername, adminPassword) VALUES(%s, %s, %s, %s)",
                    (adminName, adminCode, adminUsername, adminPassword))

        # Commit to database
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash("You are now registered.", 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# User Login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        # Get form fields
        adminUsername = request.form['adminUsername']
        password_candidate = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Get user by Username
        result = cur.execute(
            "SELECT * FROM admin WHERE adminUsername = %s", [adminUsername])

        if result > 0:

            # Get the stored hash
            data = cur.fetchone()
            password = data['adminPassword']

            # Comparing the Passwords
            if sha256_crypt.verify(password_candidate, password):

                # Password matched
                session['logged_in'] = True
                session['adminUsername'] = adminUsername
                session['name'] = str(data['adminName'])

                flash('You have successfully logged in', 'success')
                return redirect(url_for('dashboard'))

            else:
                error = 'Invalid login.'
                return render_template('login.html', error=error)

            # Close connection
            cur.close()

        else:
            error = 'Username not found.'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please Login.', 'danger')
            return redirect(url_for('login'))
    return wrap

warningCount = 0
offenceCount = 0

# Creating a Dashboard
@app.route('/dashboard')
@is_logged_in

def dashboard():
    
    global warningCount
    global offenceCount

    # Create Cursor
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute(
        "SELECT * FROM speed NATURAL JOIN users ORDER BY recordedTime DESC LIMIT 1")

    speeds = cur.fetchone()

    cur.execute("SELECT * FROM dummySpeedData NATURAL JOIN users")

    dummySpeeds = cur.fetchall()

    if result > 0:

        if(warningCount < speeds['warningsSent']):

            message = 'Hello, Mugdha Bhagwat. Please slow down, you are approaching the speed limit.'

            response = client.send_message({'from' : enter_mobile_no, 'to' : speeds['mobile'], 'text' : message})
            
            #Going to send the message
            response = response['messages'][0]

            with mail.connect() as conn:
                message = 'This is system generated warning for reaching the warning limit. Please slow down before you reach the speed limit of 80 km/ hr.'
                subject = "Hello, %s" % speeds['name']
                msg = Message(sender="scorpionhackathon@gmail.com", recipients=[
                              speeds['email']], body=message, subject=subject)

                conn.send(msg)
            print "sent"
            warningCount += 1
        
        if(offenceCount < speeds['offenceRegistered']):

            message = 'Hello, Mugdha Bhagwat. Contact RTO for overspeeding ticket.'

            response = client.send_message({'from' : enter_mobile_no, 'to' : speeds['mobile'], 'text' : message})
            
            #Going to send the message
            response = response['messages'][0]

            with mail.connect() as conn:
                message = 'This is system generated warning for over- speeding. A offence has been committed. Contact Auth for the fine to be paid.'
                subject = "Hello, %s" % speeds['name']
                msg = Message(sender="scorpionhackathon@gmail.com", recipients=[
                              speeds['email']], body=message, subject=subject)

                conn.send(msg)
            print "sent"
            offenceCount += 1

        return render_template('dashboard.html', speeds=speeds, dummySpeeds = dummySpeeds)
    else:
        msg = 'No data found'
        return render_template('dashboard.html', msg=msg)

    # Close connection
    cur.close()


@app.route('/graphs')
def graphs():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT recordedTime, speedValue FROM speed")
    if result > 0:
        data = cur.fetchall()

        recordedTime = []
        speedValue = []

        for row in data:
            recordedTime.append(row["recordedTime"])
            speedValue.append(row["speedValue"])

    pyPlot.figure('Mugdha Bhagwat')
    pyPlot.plot(recordedTime, speedValue, color='red',
                marker='o', linestyle='solid')

    pyPlot.xlabel('Time')
    pyPlot.ylabel('Speed')
    pyPlot.title('Graph for Speed vs Time view')

    pyPlot.show()

    return redirect(url_for('dashboard'))

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You have logged out.', 'success')
    return redirect(url_for('login'))

# Wireless transmission from RPi
@app.route('/copy', methods=['POST'])
def copy():

    if request.method == 'POST':

        json_data = json.loads(request.data)

        save_speed = float(json_data['speed'])

        print(save_speed)

        cur = mysql.connection.cursor()

        cur.execute("insert into speeds(speed) values("+str(save_speed)+")")

        mysql.connection.commit()

        cur.close()

    return "variable1"


if __name__ == '__main__':
    
    app.secret_key = 'secret123'
    app.run(host= '0.0.0.0', debug=True)
