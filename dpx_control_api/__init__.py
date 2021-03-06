import os
from flask import Flask

def main():
    app = create_app()
    app.run()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "dosepix.sqlite"),
    )

    # Init database
    from . import db
    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import control
    from . import user
    from . import config
    from . import measure
    app.register_blueprint(control.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(config.bp)
    app.register_blueprint(measure.bp)

    return app

if __name__ == "__main__":
    main()
