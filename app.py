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

    # Getting the current user
    user = get_current_user()

    # Return the home page according to the login user
    return render_template('home.html', user=user)


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
        # Login the user
        session['user'] = name
        # Redirecting the loged in user to the home page
        return redirect(url_for('index'))
    else:
        # Getting the current user
        user = get_current_user()
        # Return the user registeration page according to the login user
        return render_template('register.html', user=user)


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
            # Redirecting the loged in user to the home page
            return redirect(url_for('index'))
        else:
            # Temporary returning
            return "Error: {} ==>> {}".format(name, password)

    else:
        # Getting the current user
        user = get_current_user()
        # Return the user login page according to the login user
        return render_template('login.html', user=user)


@app.route('/question')
def question():
    """
    The question page that display question detail
    (question, answer, user, expert).
    """

    # Getting the current user
    user = get_current_user()

    # Return the question page according to the login user
    return render_template('question.html', user=user)


@app.route('/answer')
def answer():
    """The answer page that allows an expert to answer a specific question."""

    # Getting the current user
    user = get_current_user()

    # Return the answer page according to the login user
    return render_template('answer.html', user=user)


@app.route('/ask')
def ask():
    """The ask page that allows the user to ask a question."""

    # Getting the current user
    user = get_current_user()

    # Return the ask page according to the login user
    return render_template('ask.html', user=user)


@app.route('/unanswered')
def unanswered():
    """The unanswered page that list all unanswered question to the expert."""

    # Getting the current user
    user = get_current_user()

    # Return the unanswered page according to the login user
    return render_template('unanswered.html', user=user)


@app.route('/users')
def users():
    """
    The users page that lists all users for the admin
    to be able to promote users.
    """

    # Getting the current user
    user = get_current_user()

    # Getting all users from the DB
    db = get_db()
    cursor = db.execute("select id, name, is_expert from user;")
    users = cursor.fetchall()

    # Return the users page according to the login user
    return render_template('users.html', user=user, users=users)


@app.route('/logout')
def logout():
    """
    The logout page that logs out the user and redirets to the home page.
    """
    session.pop('user')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
