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
    # Getting the DB connection
    db = get_db()
    # Getting all answered questions from the DB
    cursor = db.execute("""select question.id, question,
                        expert.name as expert, asker.name as asker
                        from question
                        join user as expert on expert.id = question.expert_id
                        join user as asker on asker.id = question.asked_by_id
                        where question.answer is not null;""")
    questions = cursor.fetchall()
    # Return the home page according to the login user
    return render_template('home.html', user=user, questions=questions)


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


@app.route('/question/<question_id>')
def question(question_id):
    """
    The question page that display question detail
    (question, answer, user, expert).
    """

    # Getting the current user
    user = get_current_user()
    # Getting the DB connection
    db = get_db()
    # Getting the question from the DB
    cursor = db.execute("""select question, answer,
                        expert.name as expert, asker.name as asker
                        from question
                        join user as expert on expert.id = question.expert_id
                        join user as asker on asker.id = question.asked_by_id
                        where question.id = ?;""", [question_id])
    question = cursor.fetchone()

    # Return the question page according to the login user
    return render_template('question.html', user=user, question=question)


@app.route('/answer/<question_id>', methods=["GET", "POST"])
def answer(question_id):
    """The answer page that allows an expert to answer a specific question."""

    # Get the current DB connection
    db = get_db()

    if request.method == "POST":
        # Getting form data
        answer = request.form['answer']
        # storing the answer in the DB
        db.execute("""update question set answer = ? where id = ?;""",
                   [answer, question_id])
        db.commit()
        return redirect(url_for('unanswered'))
    else:
        # Getting the current user
        user = get_current_user()
        # Getting the question from the DB
        cursor = db.execute("""select id, question from question
                            where id = ?;""", [question_id])
        question = cursor.fetchone()
        # Return the answer page according to the login user
        return render_template('answer.html', user=user, question=question)


@app.route('/ask', methods=["GET", "POST"])
def ask():
    """The ask page that allows the user to ask a question."""

    # Getting the current user
    user = get_current_user()

    # Getting the current DB connection
    db = get_db()

    if request.method == "POST":
        # Getting the form data
        question = request.form['question']
        expert = request.form['expert']
        # Storing the question in the DB
        db.execute("""insert into question (question, asked_by_id, expert_id)
                    values (?, ?, ?);""", [question, user['id'], expert])
        db.commit()
        # Redirecting to the home page
        return redirect(url_for('index'))
    else:
        # Getting all experts from the DB
        cursor = db.execute("select id, name from user where is_expert = 1;")
        experts = cursor.fetchall()

        # Return the ask page according to the login user
        return render_template('ask.html', user=user, experts=experts)


@app.route('/unanswered')
def unanswered():
    """The unanswered page that list all unanswered question to the expert."""

    # Getting the current user
    user = get_current_user()

    # Getting only the unanswered questions for this experts
    db = get_db()
    cursor = db.execute("""select question.id, question, name from question
                        join user on user.id = question.asked_by_id
                        where answer is null and expert_id = ?""",
                        [user['id']])
    questions = cursor.fetchall()
    # Return the unanswered page according to the login user
    return render_template('unanswered.html', user=user, questions=questions)


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


@app.route('/promote/<user_id>')
def promote(user_id):
    """Promote the given user."""

    # Settin the user as expert in the DB
    db = get_db()
    db.execute("update user set is_expert = 1 where id = ?;",
               [user_id])
    db.commit()

    # Redirect to the users page
    return redirect(url_for('users'))


@app.route('/logout')
def logout():
    """
    The logout page that logs out the user and redirets to the home page.
    """
    session.pop('user')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
