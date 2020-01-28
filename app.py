from flask import (Flask, g, render_template, request, session,
                   url_for, redirect)
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

import os


# MAke a flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


# Get the current user helper function
def get_current_user():
    """Return the current user row from the DB if login user, or None"""

    user = None

    if 'user' in session:
        db = get_db()
        cursor = db.execute("select * from user where name = ?;",
                            [session['user']])
        user = cursor.fetchone()

    return user


@app.teardown_appcontext
def close_db(error):
    """Close the DB connection if exist after appcontext teardown."""

    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def index():
    """The home page of the application that lists all answered questions."""

    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """The registeration page that allow you to register in the application."""

    if request.method == 'POST':
        # Getting the form data
        name = request.form['name']
        password = request.form['password']
        # Hashin the password
        password = generate_password_hash(request.form['password'],
                                          method='sha256')
        # Storing the user in the database
        db = get_db()
        db.execute("""insert into user (name, password, is_expert, is_admin)
                   values (?, ?, ?, ?)""", [name, password, 0, 0])
        db.commit()
        # Temporary returning
        return "{} ==>> {}".format(name, password)
    else:
        # Return the user registeration page
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """The login page that allow you to login in the application."""

    if request.method == 'POST':
        # Getting the form data
        name = request.form['name']
        password = request.form['password']
        # Getting the user from the DB
        db = get_db()
        cursor = db.execute("""select id, name, password from user
                            where name = ?;""", [name])
        user = cursor.fetchone()
        # Checking the user password
        hashed_password = user['password']
        if check_password_hash(hashed_password, password):
            # login the user
            session['user'] = user['name']
            # Temporary returning
            return "login: {} ==>> {}".format(name, password)
        else:
            # Temporary returning
            return "Error: {} ==>> {}".format(name, password)

    else:
        # Return the user login page
        return render_template('login.html')


@app.route('/question')
def question():
    """
    The question page that display question detail
    (question, answer, user, expert).
    """

    return render_template('question.html')


@app.route('/answer')
def answer():
    """The answer page that allows an expert to answer a specific question."""

    return render_template('answer.html')


@app.route('/ask')
def ask():
    """The ask page that allows the user to ask a question."""

    return render_template('ask.html')


@app.route('/unanswered')
def unanswered():
    """The unanswered page that list all unanswered question to the expert."""

    return render_template('unanswered.html')


@app.route('/users')
def users():
    """
    The users page that allows the admin user to promote users to an expert.
    """

    return render_template('users.html')


@app.route('/logout')
def logout():
    """
    The logout page that logs out the user and redirets to the home page.
    """
    session.pop('user')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
