import os

from flask import Flask

# test_config can also be passed to the factory, and will be used instead of
# the instance configuration. This is so the tests you’ll write later in the
# tutorial can be configured independently of any development values you have
# configured.

def create_app(test_config=None):
    # create and configure the app

    # instance_relative_config=True tells the app that configuration files 
    # are relative to the instance folder. The instance folder is located 
    # outside the flaskr package and can hold local data that shouldn’t be
    # committed to version control, such as configuration secrets and the
    # database file.

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'basicblog.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)


    return app
