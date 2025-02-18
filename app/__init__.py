from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()  # Database instance

def create_app():
    app = Flask(__name__)
    
    # Ensure the instance folder exists
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Database configuration (relative path points to the instance folder)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'smart_inhaler.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)  # Enable Cross-Origin Resource Sharing
    db.init_app(app)  # Initialize database with app

    with app.app_context():
        db.create_all()  # Automatically create tables in the database

    return app

