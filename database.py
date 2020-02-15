from flask import g
import psycopg2


def connect_db():
    """Rerturn a connection to the DB"""
    db = psycopg2.connect(
        """postgres://rpadtrqneamhrd:b434aabbb7a47f74595f69d90d71cf611ef644424ecfa0deb18cd9b75daf40d3@ec2-52-23-14-156.compute-1.amazonaws.com:5432/dfedbcj590bfo7""",
        cursor_factory=psycopg2.extras.DictCursor)
    db.autocommit = True
    return db


def get_db_cursor():
    """
    Return the current connection cursor to the DB,
    or create a connection if not exists.
    """
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db.cursor()
