import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    # open_resource() opens a file relative to the flaskr package, which is 
    # useful since you won’t necessarily know where that location is when 
    # deploying the application later. get_db returns a database connection,
    # which is used to execute the commands read from the file.

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command() defines a command line command called init-db that calls 
# the init_db function and shows a success message to the user. You can read
# Command Line Interface to learn more about writing commands.

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# The call to sqlite3.register_converter() tells Python how to interpret 
# timestamp values in the database. We convert the value to a datetime.datetime

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)
