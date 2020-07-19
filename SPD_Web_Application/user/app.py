from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mail import Mail, Message
import nexmo

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

# Initializing MySQL
mysql = MySQL(app)

#Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Register Form Class
class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    mobile = StringField("Mobile", [validators.Length(min = 12, max=12)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')

#User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            name = form.name.data
            email = form.email.data
            mobile = form.mobile.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))

            # Creating the cursor
            cur = mysql.connection.cursor()

            # Executing Query
            cur.execute("INSERT INTO users(name, email, username, mobile, password) VALUES(%s, %s, %s, %s, %s)", (name, email, username, mobile, password))


            # Commit to database
            mysql.connection.commit()

            # Close connection
            cur.close()

            flash("You are now registered.", 'success')

            return redirect(url_for('login'))

        return render_template('register.html', form= form )

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        #Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Get user by Username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:

            # Get the stored hash
            data = cur.fetchone()
            password = data['password']

            # Comparing the Passwords
            if sha256_crypt.verify(password_candidate, password):

                # Password matched
                session['logged_in'] = True
                session['username'] = username

                flash('You have successfully logged in', 'success')
                return redirect(url_for('dashboard'))

            else:
                error = 'Invalid login.'
                return render_template('login.html', error = error)

            #Close connection
            cur.close()

        else:
            error = 'Username not found.'
            return render_template('login.html', error = error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, please Login.', 'danger')
            return redirect(url_for('login'))
    return wrap

# Creating a Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

    # Create Cursor
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute("SELECT * FROM speedRecord")

    speeds = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', speeds=speeds)
    else:
        msg = 'No speeding data found'
        return render_template('dashboard.html', msg= msg)

    # Close connection
    cur.close()

# Warning Form Class
class WarningForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=1)])

# Add Article Form
@app.route('/send_text_email', methods=['GET', 'POST'])
@is_logged_in
def send_text_email():
    form = WarningForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body  = form.body.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        result = cur.execute("SELECT * FROM users")

        emails = cur.fetchall()

        if result > 0:
            for email in emails:
                message = 'Warning you are nearing the speed limit. Auto Generated using SPD'

                response = client.send_message({'from' : enter_your_mobile_no, 'to' : enter_your_mobile_no, 'text' : message})

                #Going to send the message
                response = response['messages'][0]

                # #success if 0
                # if response['status'] == '0':
                #     return 'Send message' , response['message-id']
                # else:
                #     return 'Error', response['error-text']

            with mail.connect() as conn:
                for email in emails:
                    message = 'Congratulations you have been accepted!'
                    subject = "Hello, %s Warning" % email['name']
                    msg = Message(sender="scorpionhackathon@gmail.com", recipients=[email['email']], body=body, subject=subject)

                    conn.send(msg)

        # Close connection
        cur.close()

        flash('Warning Sent', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_warning.html', form= form)



# Articles Form Class
class ArticleForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=10)])

# Add Article Form
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body  = form.body.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

        # Commit to MySQL
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Article created.', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form= form)




# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You have logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
