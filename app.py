from flask import Flask, g, render_template
from database import get_db


# MAke a flask app
app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    """Close the DB connection if exist after appcontext teardown."""

    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def index():
    """The home page of the application that lists all answered questions."""

    return render_template('home.html')


@app.route('/register')
def register():
    """The registeration page that allow you to register in the application."""

    return render_template('register.html')


@app.route('/login')
def login():
    """The login page that allow you to login in the application."""

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


if __name__ == '__main__':
    app.run(debug=True)
