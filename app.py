from flask import (Flask, g, render_template, request, session,
                   url_for, redirect)
from database import get_db_cursor
from werkzeug.security import generate_password_hash, check_password_hash


# MAke a flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = (
    b'\xc2\xfe\xdc\x16\xecq;\xc1\xef\xc3\x12\x91\x1f\xc6+y^ \x00\x0f\x1duI\n')


# Get the current user helper function
def get_current_user():
    """Return the current user row from the DB if login user, or None"""

    user = None

    if 'user' in session:
        db_cursor = get_db_cursor()
        db_cursor.execute("select * from users where name = %s;",
                          (session['user'], ))
        user = db_cursor.fetchone()

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
    db_cursor = get_db_cursor()
    # Getting all answered questions from the DB
    db_cursor.execute("""select questions.id, question,
                        expert.name as expert, asker.name as asker
                        from questions
                        join users as expert on expert.id = questions.expert_id
                        join users as asker on asker.id = questions.asked_by_id
                        where questions.answer is not null;""")
    questions = db_cursor.fetchall()
    print(questions)
    # Return the home page according to the login user
    return render_template('home.html', user=user, questions=questions)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """The registeration page that allow you to register in the application."""

    # Getting the current user
    user = get_current_user()

    if request.method == 'POST':
        # Getting the form data
        name = request.form['name']
        password = request.form['password']
        # Getting the current DB
        db_cursor = get_db_cursor()
        # Checking that the user is not exist
        db_cursor.execute("select id from users where name = %s", [name])
        found_user = db_cursor.fetchone()
        if found_user:
            return render_template('register.html', user=user,
                                   error="User already exist !")
        # Hashin the password
        password = generate_password_hash(request.form['password'],
                                          method='sha256')
        # Storing the user in the database
        db_cursor.execute("""insert into users (name, password, is_expert, is_admin)
                   values (%s, %s, %s, %s)""", (name, password, False, False))
        # Login the user
        session['user'] = name
        # Redirecting the loged in user to the home page
        return redirect(url_for('index'))
    else:
        # Return the user registeration page according to the login user
        return render_template('register.html', user=user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    """The login page that allow you to login in the application."""

    # Getting the current user
    user = get_current_user()

    if request.method == 'POST':
        # Getting the form data
        name = request.form['name']
        password = request.form['password']
        # Getting the user from the DB
        db_cursor = get_db_cursor()
        db_cursor.execute("""select id, name, password from users
                            where name = %s;""", (name, ))
        user = db_cursor.fetchone()
        # Checking whether the user is exist
        if user:
            # Checking the user password
            hashed_password = user['password']
            if check_password_hash(hashed_password, password):
                # login the user
                session['user'] = user['name']
                # Redirecting the loged in user to the home page
                return redirect(url_for('index'))
        # Return the user login page according to the login user
        # with the error message
        error = "The user name or password is not correct !"
        return render_template('login.html', user=user, error=error)

    else:
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
    db_cursor = get_db_cursor()
    # Getting the question from the DB
    db_cursor.execute("""select question, answer,
                        expert.name as expert, asker.name as asker
                        from questions
                        join users as expert on expert.id = questions.expert_id
                        join users as asker on asker.id = questions.asked_by_id
                        where questions.id = %s;""", (question_id, ))
    question = db_cursor.fetchone()

    # Return the question page according to the login user
    return render_template('question.html', user=user, question=question)


@app.route('/answer/<question_id>', methods=["GET", "POST"])
def answer(question_id):
    """The answer page that allows an expert to answer a specific question."""

    # Getting the current user
    user = get_current_user()

    # Checking if the current user is logedin or redirect to login page
    if not user:
        return redirect(url_for('login'))

    # Allow only experts
    if not user['is_expert']:
        return redirect(url_for('index'))

    # Get the current DB connection
    db_cursor = get_db_cursor()

    if request.method == "POST":
        # Getting form data
        answer = request.form['answer']
        # storing the answer in the DB
        db_cursor.execute("""update questions set answer = %s where
                          id = %s;""",
                          (answer, question_id))
        return redirect(url_for('unanswered'))
    else:
        # Getting the question from the DB
        db_cursor.execute("""select id, question from questions
                            where id = %s;""", (question_id, ))
        question = db_cursor.fetchone()
        # Return the answer page according to the login user
        return render_template('answer.html', user=user, question=question)


@app.route('/ask', methods=["GET", "POST"])
def ask():
    """The ask page that allows the user to ask a question."""

    # Getting the current user
    user = get_current_user()

    # Checking if the current user is logedin or redirect to login page
    if not user:
        return redirect(url_for('login'))

    # Allow only regular users (not expert or admin)
    if user['is_admin'] or user['is_expert']:
        return redirect(url_for('index'))

    # Getting the current DB connection
    db_cursor = get_db_cursor()

    if request.method == "POST":
        # Getting the form data
        question = request.form['question']
        expert = request.form['expert']
        # Storing the question in the DB
        db_cursor.execute("""insert into questions (question, asked_by_id, expert_id)
                    values (%s, %s, %s);""", (question, user['id'], expert))
        # Redirecting to the home page
        return redirect(url_for('index'))
    else:
        # Getting all experts from the DB
        db_cursor.execute("select id, name from users where is_expert = True;")
        experts = db_cursor.fetchall()

        # Return the ask page according to the login user
        return render_template('ask.html', user=user, experts=experts)


@app.route('/unanswered')
def unanswered():
    """The unanswered page that list all unanswered question to the expert."""

    # Getting the current user
    user = get_current_user()

    # Checking if the current user is logedin or redirect to login page
    if not user:
        return redirect(url_for('login'))

    # Allow only experts
    if not user['is_expert']:
        return redirect(url_for('index'))

    # Getting only the unanswered questions for this experts
    db_cursor = get_db_cursor()
    db_cursor.execute("""select questions.id, question, name from questions
                        join users on users.id = questions.asked_by_id
                        where answer is null and expert_id = %s""",
                      (user['id'], ))
    questions = db_cursor.fetchall()
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

    # Checking if the current user is logedin or redirect to login page
    if not user:
        return redirect(url_for('login'))

    # Allow only admins
    if not user['is_admin']:
        return redirect(url_for('index'))

    # Getting all users from the DB
    db_cursor = get_db_cursor()
    db_cursor.execute("select id, name, is_expert from users;")
    users = db_cursor.fetchall()

    # Return the users page according to the login user
    return render_template('users.html', user=user, users=users)


@app.route('/promote/<user_id>')
def promote(user_id):
    """Promote the given user."""

    # Getting the current user
    user = get_current_user()

    # Checking if the current user is logedin or redirect to login page
    if not user:
        return redirect(url_for('login'))

    # Allow only admins
    if not user['is_admin']:
        return redirect(url_for('index'))

    # Settin the user as expert in the DB
    db_cursor = get_db_cursor()
    db_cursor.execute("update users set is_expert = True where id = %s;",
                      (user_id, ))

    # Redirect to the users page
    return redirect(url_for('users'))


@app.route('/logout')
def logout():
    """
    The logout page that logs out the user and redirets to the home page.
    """

    session.pop('user', None)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
