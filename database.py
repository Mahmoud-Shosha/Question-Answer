from flask import g
import sqlite3


def connect_db():
    """Rerturn a connection to the DB"""
    db = sqlite3.connect('question&answer.db')
    db.row_factory = sqlite3.Row
    return db


def get_db():
    """
    Return the current connection to the DB,
    or create a connection if not exists.
    """
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db
