import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create database object
db = SQLAlchemy()


def create_app():
    # create flask app
    app = Flask(__name__)

    # database connection (local mysql)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "mysql+pymysql://root:changeme@localhost/fyp_db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # link db with app
    db.init_app(app)

    # create tables if not already created
    with app.app_context():
        from . import models
        db.create_all()

    # register routes
    from .routes import main
    app.register_blueprint(main)

    return app