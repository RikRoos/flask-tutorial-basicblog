import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

#from bblog.db import get_db
from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- functions --------------------------------------------------------------


@bp.before_app_request
def load_logged_in_user():
    """
    bp.before_app_request() registers a function that runs before the view 
    function, no matter what URL is requested. load_logged_in_user checks if a 
    user id is stored in the session and gets that user’s data from the 
    database, storing it on g.user, which lasts for the length of the request.
    If there is no user id, or if the id doesn’t exist, g.user will be None.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


def login_required(view):
    """
    This function is used as a decorator for other view-functions which has to
    check for a logged in user, otherwise it redirects to the auth.login view.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# --- VIEUW:  /LOGOUT --------------------------------------------------------

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- VIEUW:  /REGISTER ------------------------------------------------------

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # The database library will take care of escaping the values
                # so you are not vulnerable to a SQL injection attack. 
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')
 
# --- VIEUW: /LOGIN  ------------------------------------------------------

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        r_user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if r_user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(r_user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across requests. When 
            # validation succeeds, the user’s id is stored in a new session.
            # The data is stored in a cookie that is sent to the browser, and
            # the browser then sends it back with subsequent requests. Flask
            # securely signs the data so that it can’t be tampered with.
            session.clear()
            session['user_id'] = r_user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


